"""FastAPI dependencies for authenticated routes (PRD §6)."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.core.auth import AuthError, AuthUser, verify_token


def get_current_user(request: Request) -> AuthUser:
    """Extract and verify the Bearer token on the request."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        return verify_token(token)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


UserAuth = Annotated[AuthUser, Depends(get_current_user)]
