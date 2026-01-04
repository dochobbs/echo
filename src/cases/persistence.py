"""Case persistence service using local PostgreSQL database."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from ..database import get_db, is_database_configured
from .. import db_models
from .models import (
    CaseState,
    CaseExport,
    CompletedCaseSummary,
    LearningMaterials,
)


def _to_uuid(value: str) -> UUID:
    """Convert string to UUID."""
    return UUID(value) if isinstance(value, str) else value


def is_db_configured() -> bool:
    """Check if database is configured."""
    return is_database_configured()


class CasePersistence:
    """Persist case sessions to PostgreSQL database."""

    def save_session(
        self,
        case_state: CaseState,
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """Save or update a case session in the database."""
        if not is_db_configured():
            return None

        db = next(get_db())
        try:
            session_uuid = _to_uuid(case_state.session_id)
            existing = db.query(db_models.CaseSession).filter(
                db_models.CaseSession.id == session_uuid
            ).first()

            if existing:
                existing.status = "active" if case_state.phase.value != "complete" else "completed"
                existing.phase = case_state.phase.value
                existing.history_gathered = case_state.history_gathered
                existing.exam_performed = case_state.exam_performed
                existing.differential = case_state.differential
                existing.plan_proposed = case_state.plan_proposed
                existing.hints_given = case_state.hints_given
                existing.teaching_moments = case_state.teaching_moments
                db.commit()
            else:
                session = db_models.CaseSession(
                    id=session_uuid,
                    user_id=_to_uuid(user_id) if user_id else None,
                    condition_key=case_state.patient.condition_key,
                    condition_display=case_state.patient.condition_display,
                    patient_data=case_state.patient.model_dump(),
                    status="active" if case_state.phase.value != "complete" else "completed",
                    phase=case_state.phase.value,
                    history_gathered=case_state.history_gathered,
                    exam_performed=case_state.exam_performed,
                    differential=case_state.differential,
                    plan_proposed=case_state.plan_proposed,
                    hints_given=case_state.hints_given,
                    teaching_moments=case_state.teaching_moments,
                )
                db.add(session)
                db.commit()

            self._save_conversation(db, session_uuid, case_state.conversation)
            return case_state.session_id
        except Exception as e:
            print(f"Error saving case session: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    def _save_conversation(self, db, session_id: UUID, conversation: list[dict]) -> None:
        """Save conversation messages."""
        if not conversation:
            return

        try:
            existing_count = db.query(db_models.Message).filter(
                db_models.Message.session_id == session_id
            ).count()

            new_messages = conversation[existing_count:]
            if not new_messages:
                return

            for msg in new_messages:
                message = db_models.Message(
                    session_id=session_id,
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                )
                db.add(message)

            db.commit()
        except Exception as e:
            print(f"Error saving conversation: {e}")
            db.rollback()

    def complete_session(
        self,
        case_state: CaseState,
        debrief_summary: str,
        learning_materials: Optional[LearningMaterials] = None,
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """Mark a case session as completed."""
        if not is_db_configured():
            return None

        db = next(get_db())
        try:
            session_uuid = _to_uuid(case_state.session_id)
            session = db.query(db_models.CaseSession).filter(
                db_models.CaseSession.id == session_uuid
            ).first()

            if not session:
                return None

            session.status = "completed"
            session.phase = "complete"
            session.completed_at = datetime.utcnow()
            session.history_gathered = case_state.history_gathered
            session.exam_performed = case_state.exam_performed
            session.differential = case_state.differential
            session.plan_proposed = case_state.plan_proposed
            session.hints_given = case_state.hints_given
            session.teaching_moments = case_state.teaching_moments
            session.debrief_summary = debrief_summary

            if learning_materials:
                session.learning_materials = learning_materials.model_dump()

            if session.started_at and session.completed_at:
                session.duration_seconds = int((session.completed_at - session.started_at).total_seconds())

            db.commit()

            self._save_conversation(db, session_uuid, case_state.conversation)
            return case_state.session_id
        except Exception as e:
            print(f"Error completing case session: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    def get_session(self, session_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Get a case session by ID."""
        if not is_db_configured():
            return None

        db = next(get_db())
        try:
            session_uuid = _to_uuid(session_id)
            query = db.query(db_models.CaseSession).filter(
                db_models.CaseSession.id == session_uuid
            )
            if user_id:
                query = query.filter(db_models.CaseSession.user_id == _to_uuid(user_id))

            session = query.first()
            if not session:
                return None

            return {
                "id": str(session.id),
                "user_id": str(session.user_id) if session.user_id else None,
                "condition_key": session.condition_key,
                "condition_display": session.condition_display,
                "patient_data": session.patient_data,
                "status": session.status,
                "phase": session.phase,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "history_gathered": session.history_gathered or [],
                "exam_performed": session.exam_performed or [],
                "differential": session.differential or [],
                "plan_proposed": session.plan_proposed or [],
                "hints_given": session.hints_given or 0,
                "teaching_moments": session.teaching_moments or [],
                "learning_materials": session.learning_materials,
                "debrief_summary": session.debrief_summary,
            }
        except Exception as e:
            print(f"Error getting case session: {e}")
            return None
        finally:
            db.close()

    def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> list[CompletedCaseSummary]:
        """Get case history for a user."""
        if not is_db_configured():
            return []

        db = next(get_db())
        try:
            user_uuid = _to_uuid(user_id)
            query = db.query(db_models.CaseSession).filter(
                db_models.CaseSession.user_id == user_uuid
            ).order_by(db_models.CaseSession.created_at.desc()).limit(limit)

            if status:
                query = query.filter(db_models.CaseSession.status == status)

            sessions = query.all()

            summaries = []
            for session in sessions:
                patient_data = session.patient_data or {}
                started_at = session.started_at
                completed_at = session.completed_at
                duration = None

                if completed_at and started_at:
                    duration = int((completed_at - started_at).total_seconds() / 60)

                summaries.append(CompletedCaseSummary(
                    session_id=str(session.id),
                    condition_display=session.condition_display or "Unknown",
                    patient_name=patient_data.get("name", "Unknown"),
                    patient_age=f"{patient_data.get('age', '?')} {patient_data.get('age_unit', '')}",
                    learner_level=session.phase or "student",
                    completed_at=completed_at or started_at,
                    duration_minutes=duration,
                    teaching_moments_count=len(session.teaching_moments or []),
                ))

            return summaries
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []
        finally:
            db.close()

    def get_case_export(self, session_id: str, user_id: Optional[str] = None) -> Optional[CaseExport]:
        """Get a full case export."""
        if not is_db_configured():
            return None

        db = next(get_db())
        try:
            session_uuid = _to_uuid(session_id)
            query = db.query(db_models.CaseSession).filter(
                db_models.CaseSession.id == session_uuid
            )
            if user_id:
                query = query.filter(db_models.CaseSession.user_id == _to_uuid(user_id))

            session = query.first()
            if not session:
                return None

            messages = db.query(db_models.Message).filter(
                db_models.Message.session_id == session_uuid
            ).order_by(db_models.Message.created_at).all()

            conversation = []
            for msg in messages:
                conversation.append({
                    "role": msg.role,
                    "content": msg.content,
                })

            patient_data = session.patient_data or {}
            learning_materials_data = session.learning_materials or {}

            return CaseExport(
                session_id=str(session.id),
                condition=session.condition_key or "unknown",
                condition_display=session.condition_display or "Unknown",
                patient_summary=patient_data,
                case_summary={
                    "history_gathered": session.history_gathered or [],
                    "exam_performed": session.exam_performed or [],
                    "differential": session.differential or [],
                    "plan_proposed": session.plan_proposed or [],
                    "phase": session.phase or "complete",
                    "hints_given": session.hints_given or 0,
                },
                teaching_moments=session.teaching_moments or [],
                learning_materials=LearningMaterials(**learning_materials_data) if learning_materials_data else LearningMaterials(),
                conversation_transcript=conversation,
                completed_at=session.completed_at or datetime.utcnow(),
            )
        except Exception as e:
            print(f"Error getting case export: {e}")
            return None
        finally:
            db.close()


_persistence: Optional[CasePersistence] = None


def get_case_persistence() -> CasePersistence:
    """Get case persistence singleton."""
    global _persistence
    if _persistence is None:
        _persistence = CasePersistence()
    return _persistence
