from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from .auth_handler import decode_jwt

logger = logging.getLogger('fantasy-lol')


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: Optional[HTTPAuthorizationCredentials] = \
            await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return decode_jwt(credentials.credentials)
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jw_token: str) -> bool:
        is_token_valid: bool = False

        try:
            payload = decode_jwt(jw_token)
        except Exception as e:
            logger.error(e)
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid
