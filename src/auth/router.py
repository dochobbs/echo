"""Auth router for Echo."""

from fastapi import APIRouter, HTTPException, status, Depends
from gotrue.errors import AuthApiError

from .models import User, UserCreate, UserLogin, UserUpdate, Token, TokenRefresh, UserStats
from .deps import get_current_user
from .supabase import get_supabase_client


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(data: UserCreate):
  """Register a new user."""
  try:
    supabase = get_supabase_client()

    # Create user in Supabase Auth
    response = supabase.auth.sign_up({
      "email": data.email,
      "password": data.password,
      "options": {
        "data": {
          "name": data.name,
          "level": data.level,
          "specialty_interest": data.specialty_interest,
          "institution": data.institution,
        }
      }
    })

    if not response.user:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Registration failed",
      )

    # Profile is auto-created by database trigger
    # Fetch full profile
    profile = supabase.table("profiles").select("*").eq(
      "id", response.user.id
    ).single().execute()

    # Update profile with additional fields (trigger only sets basic fields)
    if data.level != "student" or data.specialty_interest or data.institution:
      supabase.table("profiles").update({
        "level": data.level,
        "specialty_interest": data.specialty_interest,
        "institution": data.institution,
      }).eq("id", response.user.id).execute()

      # Refetch updated profile
      profile = supabase.table("profiles").select("*").eq(
        "id", response.user.id
      ).single().execute()

    return Token(
      access_token=response.session.access_token,
      refresh_token=response.session.refresh_token,
      expires_in=response.session.expires_in,
      user=User(**profile.data),
    )

  except AuthApiError as e:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=str(e),
    )


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
  """Login with email and password."""
  try:
    supabase = get_supabase_client()

    response = supabase.auth.sign_in_with_password({
      "email": data.email,
      "password": data.password,
    })

    if not response.user or not response.session:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
      )

    # Get full profile
    profile = supabase.table("profiles").select("*").eq(
      "id", response.user.id
    ).single().execute()

    # Update last_active
    supabase.table("profiles").update({
      "last_active": "now()"
    }).eq("id", response.user.id).execute()

    return Token(
      access_token=response.session.access_token,
      refresh_token=response.session.refresh_token,
      expires_in=response.session.expires_in,
      user=User(**profile.data),
    )

  except AuthApiError as e:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid credentials",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(data: TokenRefresh):
  """Refresh access token."""
  try:
    supabase = get_supabase_client()

    response = supabase.auth.refresh_session(data.refresh_token)

    if not response.user or not response.session:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
      )

    # Get full profile
    profile = supabase.table("profiles").select("*").eq(
      "id", response.user.id
    ).single().execute()

    return Token(
      access_token=response.session.access_token,
      refresh_token=response.session.refresh_token,
      expires_in=response.session.expires_in,
      user=User(**profile.data),
    )

  except AuthApiError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired refresh token",
    )


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
  """Logout current user."""
  try:
    supabase = get_supabase_client()
    supabase.auth.sign_out()
    return {"message": "Logged out successfully"}
  except Exception:
    # Even if sign out fails, return success
    return {"message": "Logged out"}


@router.get("/me", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
  """Get current user profile."""
  return user


@router.patch("/me", response_model=User)
async def update_me(data: UserUpdate, user: User = Depends(get_current_user)):
  """Update current user profile."""
  try:
    supabase = get_supabase_client()

    update_data = data.model_dump(exclude_none=True)
    if not update_data:
      return user

    result = supabase.table("profiles").update(update_data).eq(
      "id", str(user.id)
    ).execute()

    if not result.data:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Profile not found",
      )

    return User(**result.data[0])

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Update failed: {str(e)}",
    )


@router.get("/me/stats", response_model=UserStats)
async def get_my_stats(user: User = Depends(get_current_user)):
  """Get current user's case statistics."""
  try:
    supabase = get_supabase_client()

    result = supabase.table("user_case_stats").select("*").eq(
      "user_id", str(user.id)
    ).single().execute()

    if not result.data:
      return UserStats()

    return UserStats(**result.data)

  except Exception:
    # No stats yet
    return UserStats()
