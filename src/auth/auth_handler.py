import time
import jwt
import logging

from src.common import app_config

logger = logging.getLogger('fantasy-lol')

JWT_SECRET = app_config.AUTH_SECRET
JWT_ALGORITHM = app_config.AUTH_ALGORITHM


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(user_id: str, permissions: list[str]) -> dict[str, str]:
    payload = {
        "user_id": user_id,
        "permissions": permissions,
        "exp": time.time() + 86400,  # Token is valid for 24 hours
        "iat": time.time()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["exp"] >= time.time() else {}
    except Exception as e:
        logger.error(e)
        return {}
