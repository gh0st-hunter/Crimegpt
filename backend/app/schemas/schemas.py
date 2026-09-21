"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.models import (
    UserRole, CaseStatus, CasePriority, CrimeCategory,
    EvidenceType, NotificationType, NotificationChannel
)


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    role: UserRole = UserRole.VICTIM
    badge_number: Optional[str] = None
    station: Optional[str] = None
    rank: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    badge_number: Optional[str]
    station: Optional[str]
    rank: Optional[str]
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


# ─── Case Schemas ────────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=5)
    description: str = Field(..., min_length=20)
    category: CrimeCategory
    incident_location: Optional[str] = None
    incident_date: Optional[datetime] = None
    police_station: Optional[str] = None


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[CrimeCategory] = None
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    assigned_officer_id: Optional[UUID] = None
    incident_location: Optional[str] = None
    police_station: Optional[str] = None


class CaseResponse(BaseModel):
    id: UUID
    fir_number: Optional[str]
    title: str
    description: str
    category: CrimeCategory
    status: CaseStatus
    priority: CasePriority
    ai_fir_text: Optional[str]
    ai_legal_sections: Optional[list]
    ai_investigation_steps: Optional[list]
    ai_required_evidence: Optional[list]
    ai_priority_reasoning: Optional[str]
    incident_location: Optional[str]
    incident_date: Optional[datetime]
    police_station: Optional[str]
    complainant_id: UUID
    assigned_officer_id: Optional[UUID]
    complainant: Optional[UserResponse]
    assigned_officer: Optional[UserResponse]
    filed_at: Optional[datetime]
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    id: UUID
    fir_number: Optional[str]
    title: str
    category: CrimeCategory
    status: CaseStatus
    priority: CasePriority
    complainant: Optional[UserResponse]
    assigned_officer: Optional[UserResponse]
    incident_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Evidence Schemas ────────────────────────────────────────────────────────

class EvidenceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    evidence_type: EvidenceType


class EvidenceResponse(BaseModel):
    id: UUID
    case_id: UUID
    title: str
    description: Optional[str]
    evidence_type: EvidenceType
    file_name: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    ai_analysis: Optional[str]
    extracted_text: Optional[str]
    is_verified: bool
    uploaded_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Timeline Schemas ────────────────────────────────────────────────────────

class TimelineEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime
    event_type: str = "investigation"


class TimelineEventResponse(BaseModel):
    id: UUID
    case_id: UUID
    title: str
    description: Optional[str]
    event_date: datetime
    event_type: str
    is_ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Notification Schemas ────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: UUID
    title: str
    message: str
    notification_type: NotificationType
    channel: NotificationChannel
    is_read: bool
    case_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Reminder Schemas ────────────────────────────────────────────────────────

class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    reminder_type: str = "followup"


class ReminderResponse(BaseModel):
    id: UUID
    case_id: UUID
    title: str
    description: Optional[str]
    due_date: datetime
    is_completed: bool
    reminder_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Chat Schemas ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: Optional[str] = "general"
    language: Optional[str] = "en"  # en | hi | gu


class ChatResponse(BaseModel):
    id: UUID
    message: str
    response: str
    context: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Analytics Schemas ───────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_firs: int
    pending_cases: int
    closed_cases: int
    critical_cases: int
    high_priority: int
    medium_priority: int
    low_priority: int
    categories: dict
    monthly_trend: list
    status_distribution: dict
    recent_cases: List[CaseListResponse]
    pending_reminders: int


class ComplaintInput(BaseModel):
    complaint_text: str = Field(..., min_length=20)
    category: Optional[CrimeCategory] = None


# Rebuild forward refs
TokenResponse.model_rebuild()
CaseResponse.model_rebuild()
