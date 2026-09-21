"""Case management API routes."""
import random
import string
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from app.database import get_db
from app.models.models import (
    User, UserRole, Case, CaseStatus, CasePriority, CrimeCategory,
    TimelineEvent, Notification, NotificationType, NotificationChannel
)
from app.schemas.schemas import (
    CaseCreate, CaseUpdate, CaseResponse, CaseListResponse,
    ComplaintInput, TimelineEventCreate, TimelineEventResponse,
    DashboardStats
)
from app.services.auth import get_current_user, require_role
from app.services.ai_service import (
    generate_fir, get_legal_suggestions, classify_priority,
    get_landmark_judgments, classify_crime_nlp, get_multilingual_guidance
)

router = APIRouter(prefix="/api/cases", tags=["Cases"])


def _generate_fir_number():
    year = datetime.now().year
    num = ''.join(random.choices(string.digits, k=6))
    return f"FIR/{year}/{num}"


@router.post("/", response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new case/complaint."""
    # AI Priority Classification
    priority_result = classify_priority(case_data.description, case_data.category.value)
    
    case = Case(
        title=case_data.title,
        description=case_data.description,
        category=case_data.category,
        incident_location=case_data.incident_location,
        incident_date=case_data.incident_date,
        police_station=case_data.police_station,
        complainant_id=current_user.id,
        priority=CasePriority(priority_result["priority"]),
        ai_priority_reasoning=priority_result["reasoning"],
        status=CaseStatus.DRAFT
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    # Create initial timeline event
    timeline_event = TimelineEvent(
        case_id=case.id,
        title="Complaint Filed",
        description=f"Complaint submitted by {current_user.full_name}",
        event_date=datetime.utcnow(),
        event_type="complaint",
        created_by=current_user.id
    )
    db.add(timeline_event)
    db.commit()
    
    return _load_case(db, case.id)


@router.post("/generate-fir/{case_id}", response_model=CaseResponse)
async def generate_fir_for_case(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered FIR for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check permission
    if current_user.role == UserRole.VICTIM and case.complainant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Generate FIR using AI
    fir_result = generate_fir(case.description, case.category.value)
    
    case.ai_fir_text = fir_result.get("fir_text", "")
    case.ai_legal_sections = fir_result.get("legal_sections", [])
    case.ai_investigation_steps = fir_result.get("investigation_steps", [])
    case.ai_required_evidence = fir_result.get("required_evidence", [])
    case.fir_number = _generate_fir_number()
    case.status = CaseStatus.FILED
    case.filed_at = datetime.utcnow()
    
    # Update priority from AI
    if fir_result.get("priority"):
        case.priority = CasePriority(fir_result["priority"])
        case.ai_priority_reasoning = fir_result.get("priority_reasoning", "")
    
    db.commit()
    
    # Add timeline event
    timeline_event = TimelineEvent(
        case_id=case.id,
        title="FIR Generated",
        description=f"AI-generated FIR #{case.fir_number}",
        event_date=datetime.utcnow(),
        event_type="fir",
        created_by=current_user.id,
        is_ai_generated=True
    )
    db.add(timeline_event)
    
    # Create notification
    notification = Notification(
        user_id=case.complainant_id,
        title="FIR Generated Successfully",
        message=f"Your FIR #{case.fir_number} has been generated. Track its status in your dashboard.",
        notification_type=NotificationType.FIR_STATUS,
        channel=NotificationChannel.IN_APP,
        case_id=case.id
    )
    db.add(notification)
    db.commit()
    
    return _load_case(db, case.id)


@router.post("/from-complaint", response_model=CaseResponse)
async def create_from_complaint(
    complaint: ComplaintInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a case directly from natural language complaint with AI FIR generation."""
    fir_result = generate_fir(complaint.complaint_text, (complaint.category or CrimeCategory.OTHER).value)
    
    priority = CasePriority(fir_result.get("priority", "medium"))
    
    case = Case(
        title=complaint.complaint_text[:100] + ("..." if len(complaint.complaint_text) > 100 else ""),
        description=complaint.complaint_text,
        category=complaint.category or CrimeCategory.OTHER,
        complainant_id=current_user.id,
        fir_number=_generate_fir_number(),
        status=CaseStatus.FILED,
        priority=priority,
        filed_at=datetime.utcnow(),
        ai_fir_text=fir_result.get("fir_text", ""),
        ai_legal_sections=fir_result.get("legal_sections", []),
        ai_investigation_steps=fir_result.get("investigation_steps", []),
        ai_required_evidence=fir_result.get("required_evidence", []),
        ai_priority_reasoning=fir_result.get("priority_reasoning", "")
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    # Timeline
    for evt in [
        ("Complaint Filed", "complaint", False),
        ("FIR Auto-Generated by AI", "fir", True),
        ("Legal Sections Identified", "legal", True)
    ]:
        db.add(TimelineEvent(
            case_id=case.id, title=evt[0], event_date=datetime.utcnow(),
            event_type=evt[1], created_by=current_user.id, is_ai_generated=evt[2]
        ))
    db.commit()
    
    return _load_case(db, case.id)


@router.get("/", response_model=List[CaseListResponse])
async def list_cases(
    status: Optional[CaseStatus] = None,
    priority: Optional[CasePriority] = None,
    category: Optional[CrimeCategory] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List cases with filtering and pagination."""
    query = db.query(Case).options(
        joinedload(Case.complainant),
        joinedload(Case.assigned_officer)
    )
    
    # Role-based filtering
    if current_user.role == UserRole.VICTIM:
        query = query.filter(Case.complainant_id == current_user.id)
    elif current_user.role == UserRole.OFFICER:
        # Officers see cases assigned to them + unassigned
        query = query.filter(
            (Case.assigned_officer_id == current_user.id) | 
            (Case.assigned_officer_id.is_(None))
        )
    
    if status:
        query = query.filter(Case.status == status)
    if priority:
        query = query.filter(Case.priority == priority)
    if category:
        query = query.filter(Case.category == category)
    if search:
        query = query.filter(
            (Case.title.ilike(f"%{search}%")) | 
            (Case.fir_number.ilike(f"%{search}%"))
        )
    
    cases = query.order_by(desc(Case.created_at)).offset(skip).limit(limit).all()
    return [CaseListResponse.model_validate(c) for c in cases]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics statistics."""
    base_query = db.query(Case)
    
    if current_user.role == UserRole.VICTIM:
        base_query = base_query.filter(Case.complainant_id == current_user.id)
    elif current_user.role == UserRole.OFFICER:
        base_query = base_query.filter(
            (Case.assigned_officer_id == current_user.id) | 
            (Case.assigned_officer_id.is_(None))
        )
    
    total = base_query.count()
    pending = base_query.filter(Case.status.in_([
        CaseStatus.FILED, CaseStatus.UNDER_INVESTIGATION, CaseStatus.EVIDENCE_COLLECTION
    ])).count()
    closed = base_query.filter(Case.status == CaseStatus.CLOSED).count()
    
    # Priority counts
    critical = base_query.filter(Case.priority == CasePriority.CRITICAL).count()
    high = base_query.filter(Case.priority == CasePriority.HIGH).count()
    medium = base_query.filter(Case.priority == CasePriority.MEDIUM).count()
    low = base_query.filter(Case.priority == CasePriority.LOW).count()
    
    # Category distribution
    categories = {}
    cat_results = db.query(Case.category, func.count(Case.id)).group_by(Case.category).all()
    for cat, count in cat_results:
        categories[cat.value] = count
    
    # Status distribution
    status_dist = {}
    stat_results = db.query(Case.status, func.count(Case.id)).group_by(Case.status).all()
    for s, count in stat_results:
        status_dist[s.value] = count
    
    # Monthly trend (last 6 months)
    monthly = []
    for i in range(5, -1, -1):
        month_start = datetime(datetime.now().year, max(1, datetime.now().month - i), 1)
        if datetime.now().month - i > 0:
            month_count = base_query.filter(
                func.extract('month', Case.created_at) == month_start.month,
                func.extract('year', Case.created_at) == month_start.year
            ).count()
            monthly.append({"month": month_start.strftime("%b %Y"), "count": month_count})
    
    if not monthly:
        monthly = [{"month": "Current", "count": total}]
    
    # Recent cases
    recent = base_query.options(
        joinedload(Case.complainant),
        joinedload(Case.assigned_officer)
    ).order_by(desc(Case.created_at)).limit(5).all()
    
    # Pending reminders
    from app.models.models import Reminder
    pending_reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_completed == False
    ).count()
    
    return DashboardStats(
        total_firs=total,
        pending_cases=pending,
        closed_cases=closed,
        critical_cases=critical,
        high_priority=high,
        medium_priority=medium,
        low_priority=low,
        categories=categories,
        monthly_trend=monthly,
        status_distribution=status_dist,
        recent_cases=[CaseListResponse.model_validate(c) for c in recent],
        pending_reminders=pending_reminders
    )


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get case details."""
    case = _load_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if current_user.role == UserRole.VICTIM and case.complainant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return case


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: UUID,
    update_data: CaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update case details (officers and admins)."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if current_user.role == UserRole.VICTIM:
        raise HTTPException(status_code=403, detail="Victims cannot update case details")
    
    old_status = case.status
    
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    
    if update_data.status and update_data.status != old_status:
        # Add timeline event for status change
        db.add(TimelineEvent(
            case_id=case.id,
            title=f"Status changed to {update_data.status.value.replace('_', ' ').title()}",
            event_date=datetime.utcnow(),
            event_type="status_change",
            created_by=current_user.id
        ))
        
        # Notify complainant
        db.add(Notification(
            user_id=case.complainant_id,
            title=f"Case Status Updated",
            message=f"Your case {case.fir_number or case.id} status has been updated to: {update_data.status.value.replace('_', ' ').title()}",
            notification_type=NotificationType.FIR_STATUS,
            channel=NotificationChannel.IN_APP,
            case_id=case.id
        ))
        
        if update_data.status == CaseStatus.CLOSED:
            case.closed_at = datetime.utcnow()
    
    db.commit()
    return _load_case(db, case.id)


@router.get("/{case_id}/timeline", response_model=List[TimelineEventResponse])
async def get_case_timeline(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get case investigation timeline."""
    events = db.query(TimelineEvent).filter(
        TimelineEvent.case_id == case_id
    ).order_by(TimelineEvent.event_date).all()
    return [TimelineEventResponse.model_validate(e) for e in events]


@router.post("/{case_id}/timeline", response_model=TimelineEventResponse)
async def add_timeline_event(
    case_id: UUID,
    event_data: TimelineEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a timeline event to a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    event = TimelineEvent(
        case_id=case_id,
        title=event_data.title,
        description=event_data.description,
        event_date=event_data.event_date,
        event_type=event_data.event_type,
        created_by=current_user.id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return TimelineEventResponse.model_validate(event)


@router.post("/{case_id}/legal-suggestions")
async def get_case_legal_suggestions(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered legal suggestions for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    suggestions = get_legal_suggestions(case.description, case.category.value)
    
    # Update case with legal sections
    case.ai_legal_sections = suggestions.get("sections", [])
    case.ai_investigation_steps = suggestions.get("procedures", [])
    db.commit()
    
    return suggestions


def _load_case(db: Session, case_id: UUID):
    """Load case with relationships."""
    case = db.query(Case).options(
        joinedload(Case.complainant),
        joinedload(Case.assigned_officer)
    ).filter(Case.id == case_id).first()
    if case:
        return CaseResponse.model_validate(case)
    return None


@router.get("/{case_id}/landmark-judgments")
async def get_case_landmark_judgments(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get landmark judgments relevant to a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    judgments = get_landmark_judgments(case.category.value, case.ai_legal_sections)
    return {"judgments": judgments, "category": case.category.value}


@router.post("/classify-nlp")
async def classify_crime_with_nlp(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """Classify crime category from free text using NLP."""
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text field is required")
    return classify_crime_nlp(text)


@router.get("/guidance/{topic}")
async def get_victim_guidance(
    topic: str,
    lang: str = "en"
):
    """Get multilingual victim guidance."""
    content = get_multilingual_guidance(topic, lang)
    return {"topic": topic, "lang": lang, "content": content}
