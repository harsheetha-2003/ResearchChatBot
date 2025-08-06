# api/routes/chat_history_api.py

from fastapi import APIRouter, Query
from services.chat_history import load_chat_history

router = APIRouter()

@router.get("/chat-history")
async def get_chat_history(doc_id: str = Query(...)):
    history = load_chat_history(doc_id)
    return {
        "doc_id": doc_id,
        "chat_history": history
    }
