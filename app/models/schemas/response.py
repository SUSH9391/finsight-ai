from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date: Optional[str]
    description: str
    amount: float
    category: Optional[str]
    type: Optional[str]

class UploadResponse(BaseModel):
    message: str
    filename: str
    transactions_count: int
    preview: List[dict]

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = []

class SpendingSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    top_category: str
    categories: dict