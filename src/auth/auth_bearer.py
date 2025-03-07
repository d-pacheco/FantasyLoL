from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
import logging

from .auth_handler import decode_jwt  # type: ignore

logger = logging.getLogger('fantasy-lol')


class JWTBearer(HTTPBearer):
    def __init__(self, required_permissions: list[str] | None = None, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.required_permissions = required_permissions or []

    async def __call__(self, request: Request):
        credentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")

            payload = decode_jwt(credentials.credentials)
            if not self.has_permissions(payload):
                raise HTTPException(status_code=403, detail="Insufficient permissions.")

            return payload
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

    def has_permissions(self, payload: dict) -> bool:
        user_permissions = payload.get("permissions", [])
        if not user_permissions:
            return False
        return all(permission in user_permissions for permission in self.required_permissions)
