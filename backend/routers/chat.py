"""
Chat router — message handling, history, clear.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

import store
from services.llm import chat
from models.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryItem,
)

router = APIRouter()


# send message

@router.post("/message", response_model=ChatMessageResponse)
def send_message(req: ChatMessageRequest):
    """Send a message to the Lab Co-Pilot and get a response."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        result = chat(req.message)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {e}")

    return ChatMessageResponse(
        text=result["text"],
        plot_json=result.get("plot_json"),
        table_data=result.get("table_data"),
        table_columns=result.get("table_columns"),
    )


# history

@router.get("/history")
def get_history():
    """Return conversation history."""
    items = []
    for h in store.conversation_history:
        items.append(ChatHistoryItem(
            role=h["role"],
            content=h["content"],
            plot_json=h.get("plot_json"),
            table_data=h.get("table_data"),
            table_columns=h.get("table_columns"),
        ))
    return {"history": items}


# clear

@router.post("/clear")
def clear_history():
    """Clear conversation history."""
    store.conversation_history.clear()
    return {"status": "cleared"}
