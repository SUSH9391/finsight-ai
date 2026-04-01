from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Annotated

# Existing
class TransactionCreate(BaseModel):
    date: Optional[str] = None
    description: str
    amount: float
    category: Optional[str] = "Others"
    type: Optional[str] = None

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

# New for Auth
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
