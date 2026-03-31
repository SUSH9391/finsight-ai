from pydantic import BaseModel
from typing import Optional

class TransactionCreate(BaseModel):
    date: Optional[str] = None
    description: str
    amount: float
    category: Optional[str] = "Others"
    type: Optional[str] = None

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
