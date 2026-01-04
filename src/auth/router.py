"""Auth router for Echo - uses local PostgreSQL database."""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from .models import User as UserSchema, UserCreate, UserLogin, UserUpdate, Token, TokenRefresh, UserStats
from .deps import get_current_user
from ..database import get_db, is_database_configured
from .. import models as db_models


router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = os.environ.get("JWT_SECRET", "echo-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"sub": user_id, "exp": expire, "type": "access"}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": user_id, "exp": expire, "type": "refresh"}, JWT_SECRET, algorithm=JWT_ALGORITHM)


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


@router.post("/register", response_model=Token)
async def register(data: UserCreate):
    """Register a new user."""
    if not is_database_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )

    db = next(get_db())
    try:
        existing = db.query(db_models.User).filter(db_models.User.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = db_models.User(
            email=data.email,
            password_hash=hash_password(data.password),
            name=data.name,
            level=data.level,
            specialty_interest=data.specialty_interest,
            institution=data.institution,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=db_user_to_schema(user),
        )
    finally:
        db.close()


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    """Login with email and password."""
    if not is_database_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )

    db = next(get_db())
    try:
        user = db.query(db_models.User).filter(db_models.User.email == data.email).first()
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        user.last_active = datetime.utcnow()
        db.commit()
        db.refresh(user)

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=db_user_to_schema(user),
        )
    finally:
        db.close()


@router.post("/refresh", response_model=Token)
async def refresh_token(data: TokenRefresh):
    """Refresh access token."""
    if not is_database_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )

    try:
        payload = jwt.decode(data.refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    db = next(get_db())
    try:
        user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=db_user_to_schema(user),
        )
    finally:
        db.close()


@router.post("/logout")
async def logout(user: UserSchema = Depends(get_current_user)):
    """Logout current user."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserSchema)
async def get_me(user: UserSchema = Depends(get_current_user)):
    """Get current user profile."""
    return user


@router.patch("/me", response_model=UserSchema)
async def update_me(data: UserUpdate, user: UserSchema = Depends(get_current_user)):
    """Update current user profile."""
    if not is_database_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )

    db = next(get_db())
    try:
        db_user = db.query(db_models.User).filter(db_models.User.id == user.id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        update_data = data.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)

        return db_user_to_schema(db_user)
    finally:
        db.close()


@router.get("/me/stats", response_model=UserStats)
async def get_my_stats(user: UserSchema = Depends(get_current_user)):
    """Get current user's case statistics."""
    if not is_database_configured():
        return UserStats()

    db = next(get_db())
    try:
        from sqlalchemy import func
        
        stats = db.query(
            func.count(db_models.CaseSession.id).label("total_cases"),
            func.count(db_models.CaseSession.id).filter(db_models.CaseSession.status == "completed").label("completed_cases"),
            func.count(func.distinct(db_models.CaseSession.condition_key)).label("unique_conditions"),
            func.avg(db_models.CaseSession.duration_seconds).filter(db_models.CaseSession.status == "completed").label("avg_duration_seconds"),
            func.max(db_models.CaseSession.completed_at).label("last_case_completed"),
        ).filter(db_models.CaseSession.user_id == user.id).first()

        return UserStats(
            total_cases=stats.total_cases or 0,
            completed_cases=stats.completed_cases or 0,
            unique_conditions=stats.unique_conditions or 0,
            avg_duration_seconds=float(stats.avg_duration_seconds) if stats.avg_duration_seconds else None,
            last_case_completed=stats.last_case_completed,
        )
    except Exception:
        return UserStats()
    finally:
        db.close()
