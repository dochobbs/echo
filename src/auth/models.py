"""Auth models for Echo."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


LearnerLevel = Literal["student", "resident", "np_student", "fellow", "attending"]


class UserBase(BaseModel):
  """Base user fields."""
  email: EmailStr
  name: Optional[str] = None
  level: LearnerLevel = "student"
  specialty_interest: Optional[str] = None
  institution: Optional[str] = None


class UserCreate(UserBase):
  """User registration request."""
  password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
  """User login request."""
  email: EmailStr
  password: str


class UserUpdate(BaseModel):
  """User profile update."""
  name: Optional[str] = None
  level: Optional[LearnerLevel] = None
  specialty_interest: Optional[str] = None
  institution: Optional[str] = None
  preferences: Optional[dict] = None


class User(UserBase):
  """User model (returned from API)."""
  id: UUID
  created_at: datetime
  last_active: datetime
  preferences: dict = Field(default_factory=dict)

  class Config:
    from_attributes = True


class Token(BaseModel):
  """Auth token response."""
  access_token: str
  refresh_token: str
  token_type: str = "bearer"
  expires_in: int
  user: User


class TokenRefresh(BaseModel):
  """Token refresh request."""
  refresh_token: str


class UserStats(BaseModel):
  """User case statistics."""
  total_cases: int = 0
  completed_cases: int = 0
  unique_conditions: int = 0
  avg_duration_seconds: Optional[float] = None
  last_case_completed: Optional[datetime] = None
