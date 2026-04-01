from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import UserModel
from app.routers.auth import get_current_user
from app.models.schemas.request import ChatRequest
from app.services.llm import ask_llm

router = APIRouter()

@router.post("/ask")
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Chat: Mistral response with transaction context from DB (stream)"""
    question = request.question
    
    # Stream LLM response  
    return StreamingResponse(
        ask_llm(question, current_user.id),
        media_type="text/plain"
    )


