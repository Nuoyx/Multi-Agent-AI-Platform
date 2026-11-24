import json
import unittest
from http.cookies import SimpleCookie
from types import SimpleNamespace
from unittest.mock import Mock, patch

from redis.exceptions import ConnectionError

from app.routes.auth import SESSION_TTL_SECONDS, login
from app.schemas import LoginRequest


class LoginSessionTests(unittest.TestCase):
    def setUp(self):
        self.redis = Mock()
        self.request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(
            redis=self.redis, firebase_app=Mock(),
        )))
        self.user = {
            "firebaseUid": "test-user", "name": "Test User",
            "email": "test@example.com", "avatar": None,
        }

    def call_login(self):
        with patch("app.routes.auth.verify_firebase_token", return_value={"uid": "test-user"}), \
             patch("app.routes.auth.get_user", return_value=self.user):
            return login(LoginRequest(token="test-token"), self.request)

    def test_cookie_matches_stored_session_and_expiry(self):
        response = self.call_login()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body), self.user)
        cookie = SimpleCookie(response.headers["set-cookie"])["session_id"]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "strict")
        self.assertEqual(int(cookie["max-age"]), SESSION_TTL_SECONDS)
        self.redis.set.assert_called_once()
        args, kwargs = self.redis.set.call_args
        self.assertEqual(args[0], f"session-{cookie.value}")
        self.assertEqual(json.loads(args[1]), {
            "userId": "test-user", "name": "Test User",
            "email": "test@example.com", "avatar": None,
        })
        self.assertEqual(kwargs, {"ex": SESSION_TTL_SECONDS})

    def test_redis_failure_does_not_issue_cookie(self):
        self.redis.set.side_effect = ConnectionError("unavailable")
        response = self.call_login()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("set-cookie", response.headers)


if __name__ == "__main__":
    unittest.main()
