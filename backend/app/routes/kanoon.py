from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from app.services.kanoon_service import search_indian_kanoon, KanoonAPIException
from app.services.auth import get_current_user
from app.models.models import User

router = APIRouter(prefix="/api/kanoon", tags=["kanoon"])

@router.get("/search")
async def search_kanoon(
    query: str,
    page: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Search legal cases via Indian Kanoon API.
    """
    try:
        results = await search_indian_kanoon(query, page)
        return results
    except KanoonAPIException as e:
        raise HTTPException(status_code=500, detail=str(e))
