"""Admin router for Echo - platform metrics and user management."""

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import func

from ..auth.deps import get_current_user
from ..auth.models import User
from ..database import get_db, is_database_configured
from .. import db_models


router = APIRouter(prefix="/admin", tags=["admin"])


# ==================== MODELS ====================

class UserSummary(BaseModel):
  """Summary of a user for admin view."""
  id: UUID
  email: str
  name: Optional[str]
  level: str
  role: str
  institution: Optional[str]
  created_at: datetime
  last_active: datetime
  total_cases: int = 0
  completed_cases: int = 0


class UserDetail(UserSummary):
  """Detailed user info including case history."""
  specialty_interest: Optional[str]
  unique_conditions: int = 0
  avg_case_duration_minutes: Optional[float] = None


class CaseSummary(BaseModel):
  """Summary of a case for admin view."""
  session_id: str
  user_id: Optional[str]
  user_email: Optional[str]
  condition_display: str
  patient_name: str
  status: str
  phase: str
  started_at: datetime
  completed_at: Optional[datetime]
  duration_minutes: Optional[int]
  hints_given: int


class PlatformMetrics(BaseModel):
  """Platform-wide metrics."""
  total_users: int = 0
  active_last_7_days: int = 0
  active_last_30_days: int = 0
  total_cases: int = 0
  completed_cases: int = 0
  active_cases: int = 0
  avg_case_duration_minutes: Optional[float] = None
  avg_hints_per_case: Optional[float] = None
  completion_rate: Optional[float] = None
  most_practiced_conditions: List[dict] = []
  cases_by_day: List[dict] = []


class StruggleMetrics(BaseModel):
  """Metrics about where learners struggle."""
  common_stuck_phases: List[dict] = []
  high_hint_conditions: List[dict] = []
  avg_hints_by_level: List[dict] = []


# ==================== DEPENDENCIES ====================

async def require_admin(user: User = Depends(get_current_user)) -> User:
  """Require admin role for endpoint access."""
  if user.role != "admin":
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Admin access required",
    )
  return user


# ==================== ENDPOINTS ====================

@router.get("/users", response_model=List[UserSummary])
async def list_users(
  limit: int = 50,
  offset: int = 0,
  admin: User = Depends(require_admin),
):
  """List all users with summary stats."""
  if not is_database_configured():
    raise HTTPException(status_code=503, detail="Database not configured")

  db = next(get_db())
  try:
    users = db.query(db_models.User).order_by(
      db_models.User.last_active.desc()
    ).offset(offset).limit(limit).all()

    result = []
    for user in users:
      # Get case counts for this user
      case_counts = db.query(
        func.count(db_models.CaseSession.id).label("total"),
        func.count(db_models.CaseSession.id).filter(
          db_models.CaseSession.status == "completed"
        ).label("completed"),
      ).filter(db_models.CaseSession.user_id == user.id).first()

      result.append(UserSummary(
        id=user.id,
        email=user.email,
        name=user.name,
        level=user.level or "student",
        role=user.role or "learner",
        institution=user.institution,
        created_at=user.created_at,
        last_active=user.last_active,
        total_cases=case_counts.total or 0,
        completed_cases=case_counts.completed or 0,
      ))

    return result
  finally:
    db.close()


@router.get("/users/{user_id}", response_model=UserDetail)
async def get_user_detail(
  user_id: str,
  admin: User = Depends(require_admin),
):
  """Get detailed info for a specific user."""
  if not is_database_configured():
    raise HTTPException(status_code=503, detail="Database not configured")

  db = next(get_db())
  try:
    user = db.query(db_models.User).filter(
      db_models.User.id == user_id
    ).first()

    if not user:
      raise HTTPException(status_code=404, detail="User not found")

    # Get detailed stats
    stats = db.query(
      func.count(db_models.CaseSession.id).label("total"),
      func.count(db_models.CaseSession.id).filter(
        db_models.CaseSession.status == "completed"
      ).label("completed"),
      func.count(func.distinct(db_models.CaseSession.condition_key)).label("unique"),
      func.avg(db_models.CaseSession.duration_seconds).filter(
        db_models.CaseSession.status == "completed"
      ).label("avg_duration"),
    ).filter(db_models.CaseSession.user_id == user.id).first()

    return UserDetail(
      id=user.id,
      email=user.email,
      name=user.name,
      level=user.level or "student",
      role=user.role or "learner",
      institution=user.institution,
      specialty_interest=user.specialty_interest,
      created_at=user.created_at,
      last_active=user.last_active,
      total_cases=stats.total or 0,
      completed_cases=stats.completed or 0,
      unique_conditions=stats.unique or 0,
      avg_case_duration_minutes=float(stats.avg_duration) / 60 if stats.avg_duration else None,
    )
  finally:
    db.close()


@router.get("/cases", response_model=List[CaseSummary])
async def list_cases(
  limit: int = 50,
  offset: int = 0,
  user_id: Optional[str] = None,
  condition: Optional[str] = None,
  status: Optional[str] = None,
  admin: User = Depends(require_admin),
):
  """List all cases with optional filters."""
  if not is_database_configured():
    raise HTTPException(status_code=503, detail="Database not configured")

  db = next(get_db())
  try:
    query = db.query(db_models.CaseSession).order_by(
      db_models.CaseSession.created_at.desc()
    )

    if user_id:
      query = query.filter(db_models.CaseSession.user_id == user_id)
    if condition:
      query = query.filter(db_models.CaseSession.condition_key == condition)
    if status:
      query = query.filter(db_models.CaseSession.status == status)

    sessions = query.offset(offset).limit(limit).all()

    result = []
    for session in sessions:
      # Get user email if available
      user_email = None
      if session.user_id:
        user = db.query(db_models.User).filter(
          db_models.User.id == session.user_id
        ).first()
        user_email = user.email if user else None

      patient_data = session.patient_data or {}
      duration = None
      if session.duration_seconds:
        duration = session.duration_seconds // 60

      result.append(CaseSummary(
        session_id=str(session.id),
        user_id=str(session.user_id) if session.user_id else None,
        user_email=user_email,
        condition_display=session.condition_display or "Unknown",
        patient_name=patient_data.get("name", "Unknown"),
        status=session.status or "unknown",
        phase=session.phase or "unknown",
        started_at=session.started_at,
        completed_at=session.completed_at,
        duration_minutes=duration,
        hints_given=session.hints_given or 0,
      ))

    return result
  finally:
    db.close()


@router.get("/cases/{session_id}")
async def get_case_detail(
  session_id: str,
  admin: User = Depends(require_admin),
):
  """Get full case detail including transcript."""
  if not is_database_configured():
    raise HTTPException(status_code=503, detail="Database not configured")

  db = next(get_db())
  try:
    session = db.query(db_models.CaseSession).filter(
      db_models.CaseSession.id == session_id
    ).first()

    if not session:
      raise HTTPException(status_code=404, detail="Case not found")

    # Get messages
    messages = db.query(db_models.Message).filter(
      db_models.Message.session_id == session_id
    ).order_by(db_models.Message.created_at).all()

    conversation = [
      {"role": msg.role, "content": msg.content, "created_at": msg.created_at.isoformat()}
      for msg in messages
    ]

    # Get user info
    user_info = None
    if session.user_id:
      user = db.query(db_models.User).filter(
        db_models.User.id == session.user_id
      ).first()
      if user:
        user_info = {
          "id": str(user.id),
          "email": user.email,
          "name": user.name,
          "level": user.level,
        }

    return {
      "session_id": str(session.id),
      "user": user_info,
      "condition_key": session.condition_key,
      "condition_display": session.condition_display,
      "patient_data": session.patient_data,
      "status": session.status,
      "phase": session.phase,
      "started_at": session.started_at.isoformat() if session.started_at else None,
      "completed_at": session.completed_at.isoformat() if session.completed_at else None,
      "duration_seconds": session.duration_seconds,
      "history_gathered": session.history_gathered or [],
      "exam_performed": session.exam_performed or [],
      "differential": session.differential or [],
      "plan_proposed": session.plan_proposed or [],
      "hints_given": session.hints_given,
      "teaching_moments": session.teaching_moments or [],
      "debrief_summary": session.debrief_summary,
      "learning_materials": session.learning_materials,
      "conversation": conversation,
    }
  finally:
    db.close()


@router.get("/metrics", response_model=PlatformMetrics)
async def get_platform_metrics(
  admin: User = Depends(require_admin),
):
  """Get platform-wide metrics."""
  if not is_database_configured():
    raise HTTPException(status_code=503, detail="Database not configured")

  db = next(get_db())
  try:
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # User counts
    total_users = db.query(func.count(db_models.User.id)).scalar()
    active_7d = db.query(func.count(db_models.User.id)).filter(
      db_models.User.last_active >= week_ago
    ).scalar()
    active_30d = db.query(func.count(db_models.User.id)).filter(
      db_models.User.last_active >= month_ago
    ).scalar()

    # Case counts
    total_cases = db.query(func.count(db_models.CaseSession.id)).scalar()
    completed_cases = db.query(func.count(db_models.CaseSession.id)).filter(
      db_models.CaseSession.status == "completed"
    ).scalar()
    active_cases = db.query(func.count(db_models.CaseSession.id)).filter(
      db_models.CaseSession.status == "active"
    ).scalar()

    # Averages
    avg_duration = db.query(func.avg(db_models.CaseSession.duration_seconds)).filter(
      db_models.CaseSession.status == "completed"
    ).scalar()
    avg_hints = db.query(func.avg(db_models.CaseSession.hints_given)).filter(
      db_models.CaseSession.status == "completed"
    ).scalar()

    # Completion rate
    completion_rate = None
    if total_cases > 0:
      completion_rate = completed_cases / total_cases

    # Most practiced conditions
    condition_counts = db.query(
      db_models.CaseSession.condition_display,
      func.count(db_models.CaseSession.id).label("count")
    ).group_by(
      db_models.CaseSession.condition_display
    ).order_by(
      func.count(db_models.CaseSession.id).desc()
    ).limit(10).all()

    most_practiced = [
      {"condition": c.condition_display, "count": c.count}
      for c in condition_counts
    ]

    # Cases by day (last 30 days)
    cases_by_day = db.query(
      func.date(db_models.CaseSession.started_at).label("date"),
      func.count(db_models.CaseSession.id).label("count")
    ).filter(
      db_models.CaseSession.started_at >= month_ago
    ).group_by(
      func.date(db_models.CaseSession.started_at)
    ).order_by(
      func.date(db_models.CaseSession.started_at)
    ).all()

    daily_counts = [
      {"date": str(d.date), "count": d.count}
      for d in cases_by_day
    ]

    return PlatformMetrics(
      total_users=total_users or 0,
      active_last_7_days=active_7d or 0,
      active_last_30_days=active_30d or 0,
      total_cases=total_cases or 0,
      completed_cases=completed_cases or 0,
      active_cases=active_cases or 0,
      avg_case_duration_minutes=float(avg_duration) / 60 if avg_duration else None,
      avg_hints_per_case=float(avg_hints) if avg_hints else None,
      completion_rate=completion_rate,
      most_practiced_conditions=most_practiced,
      cases_by_day=daily_counts,
    )
  finally:
    db.close()


@router.get("/metrics/struggles", response_model=StruggleMetrics)
async def get_struggle_metrics(
  admin: User = Depends(require_admin),
):
  """Get metrics about where learners struggle."""
  if not is_database_configured():
    raise HTTPException(status_code=503, detail="Database not configured")

  db = next(get_db())
  try:
    # Phases where cases get abandoned (not completed)
    stuck_phases = db.query(
      db_models.CaseSession.phase,
      func.count(db_models.CaseSession.id).label("count")
    ).filter(
      db_models.CaseSession.status == "active"
    ).group_by(
      db_models.CaseSession.phase
    ).order_by(
      func.count(db_models.CaseSession.id).desc()
    ).all()

    common_stuck = [
      {"phase": p.phase, "abandoned_count": p.count}
      for p in stuck_phases
    ]

    # Conditions with highest hint usage
    hint_conditions = db.query(
      db_models.CaseSession.condition_display,
      func.avg(db_models.CaseSession.hints_given).label("avg_hints"),
      func.count(db_models.CaseSession.id).label("case_count")
    ).filter(
      db_models.CaseSession.status == "completed"
    ).group_by(
      db_models.CaseSession.condition_display
    ).having(
      func.count(db_models.CaseSession.id) >= 3  # At least 3 cases
    ).order_by(
      func.avg(db_models.CaseSession.hints_given).desc()
    ).limit(10).all()

    high_hint = [
      {
        "condition": h.condition_display,
        "avg_hints": round(float(h.avg_hints), 2) if h.avg_hints else 0,
        "case_count": h.case_count
      }
      for h in hint_conditions
    ]

    # Average hints by learner level
    # Join with users to get level
    hints_by_level = db.query(
      db_models.User.level,
      func.avg(db_models.CaseSession.hints_given).label("avg_hints"),
      func.count(db_models.CaseSession.id).label("case_count")
    ).join(
      db_models.User,
      db_models.CaseSession.user_id == db_models.User.id
    ).filter(
      db_models.CaseSession.status == "completed"
    ).group_by(
      db_models.User.level
    ).all()

    level_hints = [
      {
        "level": l.level or "unknown",
        "avg_hints": round(float(l.avg_hints), 2) if l.avg_hints else 0,
        "case_count": l.case_count
      }
      for l in hints_by_level
    ]

    return StruggleMetrics(
      common_stuck_phases=common_stuck,
      high_hint_conditions=high_hint,
      avg_hints_by_level=level_hints,
    )
  finally:
    db.close()
