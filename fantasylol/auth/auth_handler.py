import time
from typing import Dict
import jwt
import logging

from fantasylol.util.config import Config

logger = logging.getLogger('fantasy-lol')

JWT_SECRET = Config.SECRET
JWT_ALGORITHM = Config.ALGORITHM


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
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
