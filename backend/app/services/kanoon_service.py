import httpx
from typing import Dict, Any, Optional
from app.config import settings
import json

class KanoonAPIException(Exception):
    pass

async def search_indian_kanoon(query: str, page: int = 0) -> Dict[str, Any]:
    """
    Search legal documents via Indian Kanoon API.
    If KANOON_API_TOKEN is not set, returns mock data for demonstration.
    """
    if not settings.KANOON_API_TOKEN:
        # Return mock response
        return {
            "status": "success",
            "mocked": True,
            "docs": [
                {
                    "tid": "12345",
                    "title": "State of Maharashtra vs. Fake Company",
                    "author": "Supreme Court of India",
                    "publishdate": "2024-01-15",
                    "snippet": "...the accused committed <b>fraud</b> by creating fake documents...",
                    "url": "https://indiankanoon.org/doc/12345/"
                },
                {
                    "tid": "67890",
                    "title": "XYZ vs. Union of India",
                    "author": "Delhi High Court",
                    "publishdate": "2023-11-20",
                    "snippet": "...The issue of <b>cybercrime</b> was discussed in detail regarding Section 66C...",
                    "url": "https://indiankanoon.org/doc/67890/"
                }
            ],
            "founddocs": 2,
            "page": page
        }

    url = f"https://api.indiankanoon.org/search/?formInput={query}&pagenum={page}"
    headers = {
        "Authorization": f"Token {settings.KANOON_API_TOKEN}",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "mocked": False,
                    "docs": data.get("docs", []),
                    "founddocs": data.get("founddocs", 0),
                    "page": page
                }
            else:
                raise KanoonAPIException(f"API returned status {response.status_code}")
                
    except Exception as e:
        raise KanoonAPIException(str(e))
