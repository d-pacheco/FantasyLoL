from unittest.mock import patch

from tests.test_base import TestBase

from src.auth import sign_jwt, decode_jwt


class TestAuthHandler(TestBase):
    permissions = ["test:Permission"]

    def test_sign_jwt(self):
        user_id = "123"
        with patch("time.time", return_value=0):  # Mocking time to ensure a fixed expiration time
            result = sign_jwt(user_id, self.permissions)
        self.assertTrue("access_token" in result)
        self.assertIsNotNone(result["access_token"])

    def test_decode_valid_jwt(self):
        user_id = "123"
        token = sign_jwt(user_id, self.permissions)["access_token"]
        result = decode_jwt(token)
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(result["permissions"], self.permissions)

    def test_decode_expired_jwt(self):
        user_id = "123"
        with patch("time.time", return_value=86401):  # Mocking time to create an expired token
            token = sign_jwt(user_id, self.permissions)["access_token"]
        result = decode_jwt(token)
        self.assertEqual(result, {})

    def test_decode_invalid_jwt(self):
        token = "invalid_token"
        result = decode_jwt(token)
        self.assertEqual(result, {})
