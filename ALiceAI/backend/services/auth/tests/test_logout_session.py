import json
import unittest
from http.cookies import SimpleCookie
from types import SimpleNamespace
from unittest.mock import Mock, patch

from redis.exceptions import ConnectionError

from app.routes.auth import logout


class LogoutSessionTests(unittest.TestCase):
    def setUp(self):
        self.redis = Mock()
        self.request = SimpleNamespace(
            cookies={"session_id": "test-session"},
            app=SimpleNamespace(state=SimpleNamespace(redis=self.redis)),
        )

    def assert_logged_out(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body), {"message": "logout successfully."})
        cookie = SimpleCookie(response.headers["set-cookie"])["session_id"]
        self.assertEqual(cookie.value, "")
        self.assertEqual(cookie["max-age"], "0")
        self.assertEqual(cookie["path"], "/")
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "strict")

    def test_deletes_session_and_clears_cookie(self):
        self.redis.delete.return_value = 1
        self.assert_logged_out(logout(self.request))
        self.redis.delete.assert_called_once_with("session-test-session")

    def test_expired_session_still_clears_cookie(self):
        self.redis.delete.return_value = 0
        self.assert_logged_out(logout(self.request))

    def test_missing_cookie_is_already_logged_out(self):
        self.request.cookies = {}
        self.assert_logged_out(logout(self.request))
        self.redis.delete.assert_not_called()

    def test_redis_failure_returns_500_without_clearing_cookie(self):
        self.redis.delete.side_effect = ConnectionError("unavailable")
        response = logout(self.request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.body), {"message": "Logout failed."})
        self.assertNotIn("set-cookie", response.headers)

    def test_cookie_deletion_failure_returns_500(self):
        with patch(
            "app.routes.auth.JSONResponse.delete_cookie",
            side_effect=RuntimeError("cookie header creation failed"),
        ) as delete_cookie:
            response = logout(self.request)

        self.redis.delete.assert_called_once_with("session-test-session")
        delete_cookie.assert_called_once_with(
            key="session_id", path="/", httponly=True,
            secure=False, samesite="strict",
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.body), {"message": "Logout failed."})
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertNotIn("set-cookie", response.headers)

    def test_cookie_deletion_failure_without_session_returns_500(self):
        self.request.cookies = {}
        with patch(
            "app.routes.auth.JSONResponse.delete_cookie",
            side_effect=RuntimeError("cookie header creation failed"),
        ):
            response = logout(self.request)

        self.redis.delete.assert_not_called()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.body), {"message": "Logout failed."})
        self.assertNotIn("set-cookie", response.headers)


if __name__ == "__main__":
    unittest.main()
