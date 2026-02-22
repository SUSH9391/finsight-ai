from fastapi import APIRouter

router = APIRouter()

@router.post("/ask")
def ask_question(question: str):
    """Ask AI a question about your finances — coming in Day 3"""
    return {"message": "Chat endpoint — coming soon", "question": question}