"""FastAPI dependencies for authentication."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models import User
from .supabase import get_supabase_client


security = HTTPBearer(auto_error=False)


async def get_current_user(
  credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
  """Get current authenticated user. Raises 401 if not authenticated."""
  if not credentials:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Not authenticated",
      headers={"WWW-Authenticate": "Bearer"},
    )

  try:
    supabase = get_supabase_client()
    # Verify token with Supabase
    response = supabase.auth.get_user(credentials.credentials)
    if not response or not response.user:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
      )

    # Get full profile from database
    profile = supabase.table("profiles").select("*").eq(
      "id", response.user.id
    ).single().execute()

    if not profile.data:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User profile not found",
      )

    return User(**profile.data)

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail=f"Authentication failed: {str(e)}",
    )


async def get_optional_user(
  credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
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

  async def check_level(user: User = Depends(get_current_user)) -> User:
    user_level_idx = level_order.index(user.level) if user.level in level_order else 0
    min_level_idx = level_order.index(min_level) if min_level in level_order else 0

    if user_level_idx < min_level_idx:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"This action requires {min_level} level or higher",
      )
    return user

  return check_level
