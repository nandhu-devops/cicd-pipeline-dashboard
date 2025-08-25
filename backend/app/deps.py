from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .db import get_db
from .models import Settings


def _mask_token(token: Optional[str]) -> str:
    if not token:
        return "<empty>"
    return f"***{token[-4:]}"

async def get_current_user(session: AsyncSession = Depends(get_db)):
    """Dependency to get current authenticated user"""
    # TODO: Implement actual authentication
    # For now, return a mock user
    return {"id": 1, "username": "admin", "email": "admin@example.com"}

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Dependency to get current active user"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def get_pagination_params(
    skip: int = 0,
    limit: int = 50
):
    """Dependency to get pagination parameters"""
    if skip < 0:
        skip = 0
    if limit < 1 or limit > 100:
        limit = 50
    return {"skip": skip, "limit": limit}

async def verify_write_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-KEY"),
    session: AsyncSession = Depends(get_db)
) -> bool:
    """Verify API write key from header against Settings.
    If Settings.api_write_key is not configured (demo mode), allow without a key.
    """
    # Fetch settings
    result = await session.execute(select(Settings).where(Settings.id == 1))
    settings = result.scalar_one_or_none()

    # Demo mode: allow if no settings or no api_write_key configured
    if not settings or not settings.api_write_key:
        return True

    # Enforce header if key configured
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-KEY header required for write operations"
        )

    if x_api_key != settings.api_write_key:
        # Redact token in any potential logs (not raising with token content)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API write key"
        )

    return True
