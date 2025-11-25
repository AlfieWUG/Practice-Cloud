"""Security dependencies for Quick Assess APIs."""
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(dict):
    """Simple user context."""

    @property
    def user_id(self) -> str:
        return self.get("user_id", settings.default_user_id)


async def get_current_user(
    api_key: str | None = Depends(api_key_header),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> AuthenticatedUser:
    token = api_key or (credentials.credentials if credentials else None)
    if not token or token != settings.quick_assess_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Invalid or missing API token"},
        )
    return AuthenticatedUser({"user_id": x_user_id or settings.default_user_id})

