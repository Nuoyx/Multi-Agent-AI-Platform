import unittest
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import HTTPException
from starlette.requests import Request

from app.utils.proxy import proxy_request


def make_request():
    async def receive():
        return {"type": "http.request", "body": b'{"token":"test"}'}

    return Request({
        "type": "http", "method": "POST", "path": "/api/auth/login",
        "query_string": b"tag=one&tag=two",
        "headers": [
            (b"content-type", b"application/json"),
            (b"cookie", b"session_id=test"),
            (b"authorization", b"Bearer test"),
            (b"x-user-id", b"forged"),
            (b"x-request-id", b"forged-request"),
            (b"host", b"untrusted.example"),
            (b"connection", b"keep-alive"),
        ],
    }, receive)


class ProxyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        client_patch = patch("app.utils.proxy.httpx.AsyncClient")
        self.client_class = client_patch.start()
        self.addCleanup(client_patch.stop)
        self.client = AsyncMock()
        self.client_class.return_value.__aenter__.return_value = self.client
        self.client.request.return_value = httpx.Response(
            201, content=b'{"ok":true}', headers=[
                ("Content-Type", "application/json"),
                ("Set-Cookie", "session_id=new; HttpOnly"),
                ("Set-Cookie", "other=value"),
            ],
        )

    async def test_auth_forwarding_and_multiple_cookies(self):
        response = await proxy_request(
            make_request(), "http://auth/login", service_name="Auth",
            forward_credentials=True,
        )
        sent = self.client.request.call_args.kwargs
        self.assertEqual(sent["method"], "POST")
        self.assertEqual(sent["content"], b'{"token":"test"}')
        self.assertEqual(sent["params"], [("tag", "one"), ("tag", "two")])
        self.assertEqual(sent["headers"]["cookie"], "session_id=test")
        self.assertEqual(sent["headers"]["authorization"], "Bearer test")
        self.assertNotIn("X-User-ID", sent["headers"])
        self.assertNotIn("host", sent["headers"])
        self.assertNotIn("connection", sent["headers"])
        self.assertNotEqual(sent["headers"]["X-Request-ID"], "forged-request")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.body, b'{"ok":true}')
        self.assertEqual(len(response.headers.getlist("set-cookie")), 2)
        self.assertEqual(response.headers["x-request-id"], sent["headers"]["X-Request-ID"])

    async def test_verified_identity_replaces_client_header(self):
        request = make_request()
        request.state.user = {"userId": "verified-user"}
        response = await proxy_request(
            request, "http://chat/messages", service_name="Chat", forward_user=True
        )
        headers = self.client.request.call_args.kwargs["headers"]
        self.assertEqual(headers["X-User-ID"], "verified-user")
        self.assertNotIn("cookie", headers)
        self.assertNotIn("authorization", headers)
        self.assertNotIn("set-cookie", response.headers)

    async def test_identity_requires_authenticated_state(self):
        with self.assertRaises(HTTPException) as caught:
            await proxy_request(
                make_request(), "http://chat/messages", service_name="Chat",
                forward_user=True,
            )
        self.assertEqual(caught.exception.status_code, 401)
        self.client.request.assert_not_called()

    async def test_upstream_errors(self):
        for error in (httpx.ConnectError("offline"), httpx.ReadTimeout("timeout")):
            with self.subTest(error=type(error).__name__):
                self.client.request.side_effect = error
                response = await proxy_request(
                    make_request(), "http://auth/login", service_name="Auth"
                )
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.headers["cache-control"], "no-store")
                self.assertIn(b"Auth service is unreachable", response.body)


if __name__ == "__main__":
    unittest.main()
