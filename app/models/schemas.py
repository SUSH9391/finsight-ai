from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class Transaction(BaseModel):
    id: Optional[int] = None
    date: Optional[str] = None
    description: str
    amount: float
    category: Optional[str] = "Others"
    type: Optional[str] = None  # "credit" or "debit"

class UploadResponse(BaseModel):
    message: str
    filename: str
    transactions_count: int
    preview: List[dict]

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = []

class SpendingSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    top_category: str
    categories: dict