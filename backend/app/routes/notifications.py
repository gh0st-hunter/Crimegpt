"""Notification and Reminder routes."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.models import User, Notification, Reminder, Case
from app.schemas.schemas import NotificationResponse, ReminderCreate, ReminderResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Notifications"])

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(desc(Notification.created_at)).limit(50).all()
    return [NotificationResponse.model_validate(n) for n in notifs]

@router.put("/notifications/{notif_id}/read")
async def mark_read(notif_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == current_user.id).first()
    if not notif: raise HTTPException(status_code=404, detail="Not found")
    notif.is_read = True; db.commit()
    return {"message": "Marked as read"}

@router.put("/notifications/read-all")
async def mark_all_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "All marked as read"}

@router.get("/notifications/unread-count")
async def unread_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).count()
    return {"count": count}

@router.post("/reminders/{case_id}", response_model=ReminderResponse)
async def create_reminder(case_id: UUID, data: ReminderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case: raise HTTPException(status_code=404, detail="Case not found")
    reminder = Reminder(case_id=case_id, user_id=current_user.id, title=data.title,
        description=data.description, due_date=data.due_date, reminder_type=data.reminder_type)
    db.add(reminder); db.commit(); db.refresh(reminder)
    return ReminderResponse.model_validate(reminder)

@router.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminders = db.query(Reminder).filter(Reminder.user_id == current_user.id).order_by(Reminder.due_date).all()
    return [ReminderResponse.model_validate(r) for r in reminders]

@router.put("/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id).first()
    if not reminder: raise HTTPException(status_code=404, detail="Not found")
    reminder.is_completed = True; db.commit()
    return {"message": "Completed"}
