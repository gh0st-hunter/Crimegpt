"""SQLAlchemy database models for CrimeGPT."""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Integer, Float,
    ForeignKey, Enum as SQLEnum, JSON, Table, TypeDecorator
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# UUID type that works with both SQLite and PostgreSQL
class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses String(36) for storage."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value) if not isinstance(value, uuid.UUID) else value
        return value



# ─── Enums ───────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    VICTIM = "victim"
    OFFICER = "officer"
    ADMIN = "admin"


class CaseStatus(str, enum.Enum):
    DRAFT = "draft"
    FILED = "filed"
    UNDER_INVESTIGATION = "under_investigation"
    EVIDENCE_COLLECTION = "evidence_collection"
    CHARGESHEET_FILED = "chargesheet_filed"
    COURT_PROCEEDINGS = "court_proceedings"
    CLOSED = "closed"
    REOPENED = "reopened"


class CasePriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceType(str, enum.Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CHAT_LOG = "chat_log"
    EMAIL = "email"
    SCREENSHOT = "screenshot"
    OTHER = "other"


class NotificationType(str, enum.Enum):
    FIR_STATUS = "fir_status"
    INVESTIGATION_DEADLINE = "investigation_deadline"
    EVIDENCE_SUBMISSION = "evidence_submission"
    COURT_DATE = "court_date"
    REMINDER = "reminder"
    SYSTEM = "system"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class CrimeCategory(str, enum.Enum):
    CYBERCRIME = "cybercrime"
    THEFT = "theft"
    FRAUD = "fraud"
    ASSAULT = "assault"
    DOMESTIC_VIOLENCE = "domestic_violence"
    SEXUAL_HARASSMENT = "sexual_harassment"
    MURDER = "murder"
    KIDNAPPING = "kidnapping"
    DRUG_OFFENSE = "drug_offense"
    PROPERTY_CRIME = "property_crime"
    WHITE_COLLAR = "white_collar"
    OTHER = "other"


# ─── Models ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.VICTIM, nullable=False)
    badge_number = Column(String(50), nullable=True)  # For officers
    station = Column(String(255), nullable=True)  # For officers
    rank = Column(String(100), nullable=True)  # For officers
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    filed_complaints = relationship("Case", back_populates="complainant", foreign_keys="Case.complainant_id")
    assigned_cases = relationship("Case", back_populates="assigned_officer", foreign_keys="Case.assigned_officer_id")
    notifications = relationship("Notification", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Case(Base):
    __tablename__ = "cases"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    fir_number = Column(String(50), unique=True, nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(CrimeCategory), nullable=False)
    status = Column(SQLEnum(CaseStatus), default=CaseStatus.DRAFT)
    priority = Column(SQLEnum(CasePriority), default=CasePriority.MEDIUM)
    
    # AI-Generated Content
    ai_fir_text = Column(Text, nullable=True)
    ai_legal_sections = Column(JSON, nullable=True)
    ai_investigation_steps = Column(JSON, nullable=True)
    ai_required_evidence = Column(JSON, nullable=True)
    ai_priority_reasoning = Column(Text, nullable=True)
    
    # Location
    incident_location = Column(String(500), nullable=True)
    incident_date = Column(DateTime, nullable=True)
    police_station = Column(String(255), nullable=True)
    
    # Relations
    complainant_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    assigned_officer_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    filed_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    complainant = relationship("User", back_populates="filed_complaints", foreign_keys=[complainant_id])
    assigned_officer = relationship("User", back_populates="assigned_cases", foreign_keys=[assigned_officer_id])
    evidence = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="case", cascade="all, delete-orphan", order_by="TimelineEvent.event_date")
    reminders = relationship("Reminder", back_populates="case", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    case_id = Column(GUID, ForeignKey("cases.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # AI Analysis
    ai_analysis = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    
    uploaded_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="evidence")
    uploader = relationship("User")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    case_id = Column(GUID, ForeignKey("cases.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False)
    event_type = Column(String(50), nullable=False)  # e.g., "incident", "investigation", "evidence", "court"
    created_by = Column(GUID, ForeignKey("users.id"), nullable=True)
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="timeline_events")
    creator = relationship("User")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    channel = Column(SQLEnum(NotificationChannel), default=NotificationChannel.IN_APP)
    is_read = Column(Boolean, default=False)
    case_id = Column(GUID, ForeignKey("cases.id"), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
    case = relationship("Case")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    case_id = Column(GUID, ForeignKey("cases.id"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
    reminder_type = Column(String(50), nullable=False)  # deadline, evidence, court, followup
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="reminders")
    user = relationship("User")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    context = Column(String(50), nullable=True)  # victim_guidance, investigation, cybercrime, general
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")
