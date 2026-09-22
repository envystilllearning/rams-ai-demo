"""Supabase JWT verification via JWKS (asymmetric ECC keys, PRD §6/§27)."""

from dataclasses import dataclass

import jwt
from jwt import PyJWKClient

from app.core.config import get_settings


class AuthError(Exception):
    def __init__(self, message: str = "Invalid or missing authentication token"):
        super().__init__(message)


@dataclass
class AuthUser:
    id: str
    email: str | None


_jwk_client: PyJWKClient | None = None


def _get_jwk_client() -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        settings = get_settings()
        jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
        _jwk_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
    return _jwk_client


def verify_token(token: str) -> AuthUser:
    """Verify a Supabase access token against the project JWKS.

    Works with both asymmetric (ECC/RS) and legacy HS256 secrets.
    Raises AuthError on any failure.
    """
    if not token:
        raise AuthError("Missing authorization header")

    settings = get_settings()
    try:
        # Try asymmetric keys first (JWKS)
        signing_key = _get_jwk_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "ES384", "ES512", "RS256", "EdDSA"],
            audience="authenticated",
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWKError as exc:
        # Fall back to legacy symmetric secret if configured
        if not settings.supabase_jwt_secret:
            raise AuthError() from exc
        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
                options={"require": ["exp", "sub"]},
            )
        except jwt.InvalidTokenError as exc:
            raise AuthError() from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError() from exc

    return AuthUser(id=payload["sub"], email=payload.get("email"))
