"""Evidence management API routes."""
import os, uuid
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, UserRole, Evidence, EvidenceType, Case
from app.schemas.schemas import EvidenceResponse
from app.services.auth import get_current_user
from app.services.ai_service import analyze_evidence
from app.config import settings

router = APIRouter(prefix="/api/evidence", tags=["Evidence"])

@router.post("/{case_id}", response_model=EvidenceResponse)
async def upload_evidence(case_id: UUID, title: str = Form(...), description: str = Form(None),
    evidence_type: EvidenceType = Form(...), file: UploadFile = File(...),
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case: raise HTTPException(status_code=404, detail="Case not found")
    if current_user.role == UserRole.VICTIM and case.complainant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(case_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}{file_ext}")
    content = await file.read()
    with open(file_path, "wb") as f: f.write(content)
    extracted_text, ai_analysis = "", ""
    try:
        if evidence_type in [EvidenceType.DOCUMENT, EvidenceType.EMAIL, EvidenceType.CHAT_LOG]:
            extracted_text = content.decode("utf-8", errors="ignore")[:5000]
            ai_analysis = analyze_evidence(extracted_text, evidence_type.value)
    except Exception: pass
    evidence = Evidence(case_id=case_id, title=title, description=description, evidence_type=evidence_type,
        file_path=file_path, file_name=file.filename, file_size=len(content), mime_type=file.content_type,
        uploaded_by=current_user.id, extracted_text=extracted_text, ai_analysis=ai_analysis)
    db.add(evidence); db.commit(); db.refresh(evidence)
    return EvidenceResponse.model_validate(evidence)

@router.get("/{case_id}", response_model=List[EvidenceResponse])
async def list_evidence(case_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [EvidenceResponse.model_validate(e) for e in db.query(Evidence).filter(Evidence.case_id == case_id).all()]

@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == UserRole.VICTIM: raise HTTPException(status_code=403, detail="Not allowed")
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence: raise HTTPException(status_code=404, detail="Not found")
    if evidence.file_path and os.path.exists(evidence.file_path): os.remove(evidence.file_path)
    db.delete(evidence); db.commit()
    return {"message": "Evidence deleted"}
