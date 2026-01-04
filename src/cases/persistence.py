"""Case persistence service for Supabase storage."""

from datetime import datetime
from typing import Optional
from uuid import UUID
import json

from ..auth.supabase import get_supabase_client
from ..config import get_settings
from .models import (
    CaseState,
    CaseExport,
    CompletedCaseSummary,
    LearningMaterials,
)


def is_supabase_configured() -> bool:
    """Check if Supabase is configured."""
    settings = get_settings()
    return bool(settings.supabase_url and settings.supabase_anon_key)


class CasePersistence:
    """Persist case sessions to Supabase."""

    def save_session(
        self,
        case_state: CaseState,
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """Save or update a case session in the database."""
        if not is_supabase_configured():
            return None

        try:
            supabase = get_supabase_client()
            
            session_data = {
                "id": case_state.session_id,
                "condition_key": case_state.patient.condition_key,
                "condition_display": case_state.patient.condition_display,
                "patient_data": case_state.patient.model_dump(),
                "status": "active" if case_state.phase.value != "complete" else "completed",
                "phase": case_state.phase.value,
                "history_gathered": case_state.history_gathered,
                "exam_performed": case_state.exam_performed,
                "differential": case_state.differential,
                "plan_proposed": case_state.plan_proposed,
                "hints_given": case_state.hints_given,
                "teaching_moments": case_state.teaching_moments,
            }
            
            if user_id:
                session_data["user_id"] = user_id

            result = supabase.table("case_sessions").upsert(
                session_data,
                on_conflict="id"
            ).execute()

            if result.data:
                self._save_conversation(case_state.session_id, case_state.conversation)
                return case_state.session_id

            return None
        except Exception as e:
            print(f"Error saving case session: {e}")
            return None

    def _save_conversation(self, session_id: str, conversation: list[dict]) -> None:
        """Save conversation messages."""
        if not conversation:
            return

        try:
            supabase = get_supabase_client()
            
            existing = supabase.table("messages").select("id").eq(
                "session_id", session_id
            ).execute()
            existing_count = len(existing.data) if existing.data else 0

            new_messages = conversation[existing_count:]
            if not new_messages:
                return

            messages_to_insert = []
            for msg in new_messages:
                messages_to_insert.append({
                    "session_id": session_id,
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

            if messages_to_insert:
                supabase.table("messages").insert(messages_to_insert).execute()
        except Exception as e:
            print(f"Error saving conversation: {e}")

    def complete_session(
        self,
        case_state: CaseState,
        debrief_summary: str,
        learning_materials: Optional[LearningMaterials] = None,
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """Mark a case session as completed."""
        if not is_supabase_configured():
            return None

        try:
            supabase = get_supabase_client()
            
            update_data = {
                "status": "completed",
                "phase": "complete",
                "completed_at": datetime.now().isoformat(),
                "history_gathered": case_state.history_gathered,
                "exam_performed": case_state.exam_performed,
                "differential": case_state.differential,
                "plan_proposed": case_state.plan_proposed,
                "hints_given": case_state.hints_given,
                "teaching_moments": case_state.teaching_moments,
                "debrief_summary": debrief_summary,
            }

            if learning_materials:
                update_data["learning_materials"] = learning_materials.model_dump()

            result = supabase.table("case_sessions").update(update_data).eq(
                "id", case_state.session_id
            ).execute()

            if result.data:
                self._save_conversation(case_state.session_id, case_state.conversation)
                return case_state.session_id

            return None
        except Exception as e:
            print(f"Error completing case session: {e}")
            return None

    def get_session(self, session_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Get a case session by ID."""
        if not is_supabase_configured():
            return None

        try:
            supabase = get_supabase_client()
            
            query = supabase.table("case_sessions").select("*").eq("id", session_id)
            if user_id:
                query = query.eq("user_id", user_id)
            
            result = query.single().execute()
            return result.data if result.data else None
        except Exception as e:
            print(f"Error getting case session: {e}")
            return None

    def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> list[CompletedCaseSummary]:
        """Get case history for a user."""
        if not is_supabase_configured():
            return []

        try:
            supabase = get_supabase_client()
            
            query = supabase.table("case_sessions").select("*").eq(
                "user_id", user_id
            ).order("created_at", desc=True).limit(limit)
            
            if status:
                query = query.eq("status", status)
            
            result = query.execute()

            if not result.data:
                return []

            summaries = []
            for row in result.data:
                patient_data = row.get("patient_data", {})
                started_at = datetime.fromisoformat(row["started_at"].replace("Z", "+00:00"))
                completed_at = None
                duration = None
                
                if row.get("completed_at"):
                    completed_at = datetime.fromisoformat(row["completed_at"].replace("Z", "+00:00"))
                    duration = int((completed_at - started_at).total_seconds() / 60)

                summaries.append(CompletedCaseSummary(
                    session_id=row["id"],
                    condition_display=row.get("condition_display", "Unknown"),
                    patient_name=patient_data.get("name", "Unknown"),
                    patient_age=f"{patient_data.get('age', '?')} {patient_data.get('age_unit', '')}",
                    learner_level=row.get("phase", "student"),
                    completed_at=completed_at or started_at,
                    duration_minutes=duration,
                    teaching_moments_count=len(row.get("teaching_moments", [])),
                ))

            return summaries
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []

    def get_case_export(self, session_id: str, user_id: Optional[str] = None) -> Optional[CaseExport]:
        """Get a full case export."""
        if not is_supabase_configured():
            return None

        try:
            supabase = get_supabase_client()
            
            query = supabase.table("case_sessions").select("*").eq("id", session_id)
            if user_id:
                query = query.eq("user_id", user_id)
            
            session_result = query.single().execute()
            if not session_result.data:
                return None

            session = session_result.data

            messages_result = supabase.table("messages").select("*").eq(
                "session_id", session_id
            ).order("created_at").execute()

            conversation = []
            if messages_result.data:
                for msg in messages_result.data:
                    conversation.append({
                        "role": msg["role"],
                        "content": msg["content"],
                    })

            patient_data = session.get("patient_data", {})
            learning_materials_data = session.get("learning_materials", {})

            return CaseExport(
                session_id=session["id"],
                condition=session.get("condition_key", "unknown"),
                condition_display=session.get("condition_display", "Unknown"),
                patient_summary=patient_data,
                case_summary={
                    "history_gathered": session.get("history_gathered", []),
                    "exam_performed": session.get("exam_performed", []),
                    "differential": session.get("differential", []),
                    "plan_proposed": session.get("plan_proposed", []),
                    "phase": session.get("phase", "complete"),
                    "hints_given": session.get("hints_given", 0),
                },
                teaching_moments=session.get("teaching_moments", []),
                learning_materials=LearningMaterials(**learning_materials_data) if learning_materials_data else LearningMaterials(),
                conversation_transcript=conversation,
                completed_at=datetime.fromisoformat(session["completed_at"].replace("Z", "+00:00")) if session.get("completed_at") else datetime.now(),
            )
        except Exception as e:
            print(f"Error getting case export: {e}")
            return None


_persistence: Optional[CasePersistence] = None


def get_case_persistence() -> CasePersistence:
    """Get case persistence singleton."""
    global _persistence
    if _persistence is None:
        _persistence = CasePersistence()
    return _persistence
