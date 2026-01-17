import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, ARRAY, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    level = Column(String(50), default="student")
    role = Column(String(50), default="learner")  # learner or admin
    specialty_interest = Column(String(255))
    institution = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    preferences = Column(JSON, default=dict)

    case_sessions = relationship("CaseSession", back_populates="user", cascade="all, delete-orphan")


class CaseSession(Base):
    __tablename__ = "case_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    condition_key = Column(String(255), nullable=False)
    condition_display = Column(String(255), nullable=False)
    patient_data = Column(JSON, nullable=False)
    status = Column(String(50), default="active")
    phase = Column(String(50), default="intro")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    history_gathered = Column(ARRAY(Text), default=list)
    exam_performed = Column(ARRAY(Text), default=list)
    differential = Column(ARRAY(Text), default=list)
    plan_proposed = Column(ARRAY(Text), default=list)
    hints_given = Column(Integer, default=0)
    teaching_moments = Column(ARRAY(Text), default=list)
    learning_materials = Column(JSON, nullable=True)
    debrief_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="case_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("case_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    phase = Column(String(50), nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("CaseSession", back_populates="messages")
