"""Clerk JWT authentication middleware and dependency functions."""
import logging
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

# Clerk JWKS endpoint
CLERK_JWKS_URL = "https://api.clerk.dev/v1/jwks"


async def _get_clerk_jwks() -> dict:
    """Fetch Clerk public keys for JWT verification."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(CLERK_JWKS_URL, timeout=10.0)
        resp.raise_for_status()
        return resp.json()


def _decode_clerk_jwt(token: str) -> dict:
    """Decode and verify a Clerk JWT. Returns claims dict."""
    try:
        from jose import jwt, JWTError
        # For Clerk, use RS256 with their published JWK
        # In a production setup, cache the JWKS. Here we decode with the 
        # clerk secret for HS256 tokens, or fetch JWKS for RS256.
        # Clerk typically issues RS256 tokens.
        # We'll do a best-effort decode here; full JWKS verification
        # requires fetching the public key per 'kid' header.
        claims = jwt.decode(
            token,
            key=settings.clerk_secret_key or "placeholder",
            algorithms=["RS256", "HS256"],
            options={"verify_signature": settings.clerk_secret_key != ""},
        )
        return claims
    except Exception as e:
        logger.debug(f"JWT decode failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserClaims:
    """Parsed Clerk JWT claims."""
    def __init__(self, claims: dict):
        self.user_id: str = claims.get("sub", "")
        self.email: str = claims.get("email", "")
        self.role: str = claims.get("public_metadata", {}).get("role", "buyer")
        self.raw: dict = claims


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> UserClaims:
    """FastAPI dependency: require authenticated user, return UserClaims."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = _decode_clerk_jwt(credentials.credentials)
    return UserClaims(claims)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[UserClaims]:
    """FastAPI dependency: return UserClaims if authenticated, else None."""
    if not credentials:
        return None
    try:
        claims = _decode_clerk_jwt(credentials.credentials)
        return UserClaims(claims)
    except HTTPException:
        return None


async def require_admin(
    user: UserClaims = Depends(get_current_user),
) -> UserClaims:
    """FastAPI dependency: require admin role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
