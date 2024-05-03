from unittest.mock import patch

from tests.test_base import FantasyLolTestBase

from src.auth.auth_handler import sign_jwt, decode_jwt


class TestAuthHandler(FantasyLolTestBase):

    def test_sign_jwt(self):
        user_id = "123"
        with patch("time.time", return_value=0):  # Mocking time to ensure a fixed expiration time
            result = sign_jwt(user_id)
        self.assertTrue("access_token" in result)
        self.assertIsNotNone(result["access_token"])

    def test_decode_valid_jwt(self):
        user_id = "123"
        token = sign_jwt(user_id)["access_token"]
        result = decode_jwt(token)
        self.assertEqual(result["user_id"], user_id)

    def test_decode_expired_jwt(self):
        user_id = "123"
        with patch("time.time", return_value=86401):  # Mocking time to create an expired token
            token = sign_jwt(user_id)["access_token"]
        result = decode_jwt(token)
        self.assertEqual(result, {})

    def test_decode_invalid_jwt(self):
        token = "invalid_token"
        result = decode_jwt(token)
        self.assertEqual(result, {})
