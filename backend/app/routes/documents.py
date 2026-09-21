"""Document generation API routes for CrimeGPT."""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.models import Case, User, UserRole
from app.services.auth import get_current_user
from app.services.document_service import generate_legal_document

router = APIRouter(prefix="/api/documents", tags=["Documents"])


class DocumentRequest(BaseModel):
    doc_type: str  # remand_request | seizure_receipt | medical_letter | court_custody
    officer_name: Optional[str] = None
    officer_rank: Optional[str] = None
    officer_badge: Optional[str] = None
    police_station: Optional[str] = None
    magistrate_name: Optional[str] = None
    court_name: Optional[str] = None
    accused_name: Optional[str] = None
    accused_age: Optional[str] = None
    accused_address: Optional[str] = None
    arrest_date: Optional[str] = None
    items_seized: Optional[str] = None
    hospital_name: Optional[str] = None
    doctor_name: Optional[str] = None
    additional_notes: Optional[str] = None


VALID_DOC_TYPES = ["remand_request", "seizure_receipt", "medical_letter", "court_custody"]


@router.post("/{case_id}/generate")
async def generate_document(
    case_id: UUID,
    req: DocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a legal document for a case."""
    if req.doc_type not in VALID_DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid doc_type. Must be one of: {VALID_DOC_TYPES}")

    case = db.query(Case).options(
        joinedload(Case.complainant),
        joinedload(Case.assigned_officer)
    ).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Access control: victims can only see their own cases
    if current_user.role == UserRole.VICTIM and case.complainant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Auto-fill officer details from current user if officer
    officer_data = {
        "officer_name": req.officer_name or (
            current_user.full_name if current_user.role in [UserRole.OFFICER, UserRole.ADMIN] else "Investigating Officer"
        ),
        "officer_rank": req.officer_rank or current_user.rank or "Sub-Inspector",
        "officer_badge": req.officer_badge or current_user.badge_number or "N/A",
        "police_station": req.police_station or case.police_station or current_user.station or "Crime Branch",
        "magistrate_name": req.magistrate_name or "The Learned Magistrate",
        "court_name": req.court_name or "Chief Judicial Magistrate Court",
        "accused_name": req.accused_name or "Unknown (Under Investigation)",
        "accused_age": req.accused_age or "—",
        "accused_address": req.accused_address or "As per FIR",
        "arrest_date": req.arrest_date or datetime.now().strftime("%d/%m/%Y"),
        "items_seized": req.items_seized or "As per seizure list",
        "hospital_name": req.hospital_name or "Government District Hospital",
        "doctor_name": req.doctor_name or "Medical Officer",
        "additional_notes": req.additional_notes or "",
    }

    html_content = generate_legal_document(case, req.doc_type, officer_data)
    return {"html": html_content, "doc_type": req.doc_type, "case_id": str(case_id)}


@router.get("/{case_id}/preview/{doc_type}", response_class=HTMLResponse)
async def preview_document(
    case_id: UUID,
    doc_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview a document as rendered HTML."""
    if doc_type not in VALID_DOC_TYPES:
        raise HTTPException(status_code=400, detail="Invalid doc_type")

    case = db.query(Case).options(
        joinedload(Case.complainant),
        joinedload(Case.assigned_officer)
    ).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    officer_data = {
        "officer_name": current_user.full_name if current_user.role != UserRole.VICTIM else "Investigating Officer",
        "officer_rank": current_user.rank or "Sub-Inspector",
        "officer_badge": current_user.badge_number or "—",
        "police_station": case.police_station or current_user.station or "Crime Branch",
        "magistrate_name": "The Learned Magistrate",
        "court_name": "Chief Judicial Magistrate Court",
        "accused_name": "Unknown (Under Investigation)",
        "accused_age": "—",
        "accused_address": "As per FIR",
        "arrest_date": datetime.now().strftime("%d/%m/%Y"),
        "items_seized": "As per seizure list",
        "hospital_name": "Government District Hospital",
        "doctor_name": "Medical Officer",
        "additional_notes": "",
    }

    return generate_legal_document(case, doc_type, officer_data)


@router.get("/types")
async def list_document_types():
    """List available document types."""
    return {
        "types": [
            {
                "id": "remand_request",
                "name": "Remand Request Letter",
                "description": "Formal petition to the Magistrate for extension of police custody",
                "icon": "⚖️",
                "color": "blue"
            },
            {
                "id": "seizure_receipt",
                "name": "Seizure Receipt (Panchnama)",
                "description": "Official acknowledgement of items seized during investigation",
                "icon": "📋",
                "color": "orange"
            },
            {
                "id": "medical_letter",
                "name": "Medical Treatment Letter",
                "description": "Request letter for medical examination of accused or victim",
                "icon": "🏥",
                "color": "green"
            },
            {
                "id": "court_custody",
                "name": "Court Custody Letter",
                "description": "Formal production warrant and custody transfer document",
                "icon": "🏛️",
                "color": "purple"
            }
        ]
    }
