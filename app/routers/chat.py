from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import UserModel
from app.routers.auth import get_current_user
from app.models.schemas.request import ChatRequest
from app.services.llm import ask_llm
from app.services.embeddings import embed_single
from app.services.vectorstore import search_user_transactions

router = APIRouter()

@router.post("/ask")
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """RAG Chat: Embed question → ChromaDB search → Mistral response (stream)"""
    question = request.question
    
    # RAG Pipeline
    query_emb = embed_single(question)
    context = search_user_transactions(current_user.id, query_emb)
    
    # Stream LLM response  
    return StreamingResponse(
        ask_llm(question, current_user.id),
        media_type="text/plain"
    )

@router.post("/embed")
async def trigger_embedding(
    current_user: UserModel = Depends(get_current_user)
):
    """Call after upload - embed user's transactions"""
    from app.services.vectorstore import store_user_transactions
    store_user_transactions(current_user.id)
    return {"message": "✅ Transactions embedded! Ready for chat."}
