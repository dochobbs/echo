"""FastAPI dependencies for authentication - uses local PostgreSQL database."""

import os
import jwt
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models import User as UserSchema
from ..database import get_db, is_database_configured
from .. import db_models


security = HTTPBearer(auto_error=False)

JWT_SECRET = os.environ.get("JWT_SECRET", "echo-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


def db_user_to_schema(user: db_models.User) -> UserSchema:
    return UserSchema(
        id=user.id,
        email=user.email,
        name=user.name,
        level=user.level or "student",
        specialty_interest=user.specialty_interest,
        institution=user.institution,
        created_at=user.created_at,
        last_active=user.last_active,
        preferences=user.preferences or {},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserSchema:
    """Get current authenticated user. Raises 401 if not authenticated."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not is_database_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )

    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    db = next(get_db())
    try:
        user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return db_user_to_schema(user)
    finally:
        db.close()


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[UserSchema]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_level(min_level: str):
    """Dependency to require minimum learner level."""
    level_order = ["student", "resident", "np_student", "fellow", "attending"]

    async def check_level(user: UserSchema = Depends(get_current_user)) -> UserSchema:
        user_level_idx = level_order.index(user.level) if user.level in level_order else 0
        min_level_idx = level_order.index(min_level) if min_level in level_order else 0

        if user_level_idx < min_level_idx:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires {min_level} level or higher",
            )
        return user

    return check_level
