"""Case history tracking for Echo.

Provides in-memory storage of completed cases for the current session.
In production, this would persist to Supabase.
"""

from datetime import datetime
from typing import Optional
from .models import CaseState, CompletedCaseSummary, CaseExport, LearningMaterials


class CaseHistory:
  """Track completed cases (in-memory for now, database later)."""

  def __init__(self):
    self._completed_cases: list[CaseExport] = []

  def add_completed_case(self, case_export: CaseExport) -> None:
    """Add a completed case to history."""
    self._completed_cases.append(case_export)

  def get_all(self) -> list[CompletedCaseSummary]:
    """Get summaries of all completed cases."""
    summaries = []
    for export in self._completed_cases:
      # Calculate duration if we have timestamps
      duration = None
      if export.case_summary.get("started_at"):
        try:
          start = datetime.fromisoformat(export.case_summary["started_at"])
          duration = int((export.completed_at - start).total_seconds() / 60)
        except (ValueError, TypeError):
          pass

      summaries.append(CompletedCaseSummary(
        session_id=export.session_id,
        condition_display=export.condition_display,
        patient_name=export.patient_summary.get("name", "Unknown"),
        patient_age=f"{export.patient_summary.get('age', '?')} {export.patient_summary.get('age_unit', '')}",
        learner_level=export.case_summary.get("learner_level", "student"),
        completed_at=export.completed_at,
        duration_minutes=duration,
        teaching_moments_count=len(export.teaching_moments),
      ))

    return summaries

  def get_by_session_id(self, session_id: str) -> Optional[CaseExport]:
    """Get a specific case export by session ID."""
    for export in self._completed_cases:
      if export.session_id == session_id:
        return export
    return None

  def get_by_condition(self, condition_key: str) -> list[CaseExport]:
    """Get all cases for a specific condition."""
    return [e for e in self._completed_cases if e.condition == condition_key]

  def count(self) -> int:
    """Get total count of completed cases."""
    return len(self._completed_cases)

  def clear(self) -> None:
    """Clear all history (for testing)."""
    self._completed_cases = []


# Singleton instance
case_history = CaseHistory()


def get_case_history() -> CaseHistory:
  """Get the case history singleton."""
  return case_history
