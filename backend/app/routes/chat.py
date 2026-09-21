"""AI Chatbot API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, ChatMessage
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.auth import get_current_user
from app.services.ai_service import chat_response

router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])

@router.post("/", response_model=ChatResponse)
async def send_message(req: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    response = chat_response(req.message, req.context or "general", current_user.role.value, req.language or "en")
    msg = ChatMessage(user_id=current_user.id, message=req.message, response=response, context=req.context)
    db.add(msg); db.commit(); db.refresh(msg)
    return ChatResponse.model_validate(msg)

@router.get("/history")
async def chat_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msgs = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id).order_by(ChatMessage.created_at.desc()).limit(50).all()
    return [ChatResponse.model_validate(m) for m in msgs]
