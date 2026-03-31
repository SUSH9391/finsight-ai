from pydantic import BaseModel
from typing import Annotated
from pydantic import Field
from typing import Optional

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

# New for Auth Phase 2
class UserCreate(BaseModel):
    email: Annotated[str, Field(pattern=r'^[^@]+@[^@]+\.[^@]+$', strict=True)]
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

UserCreate.model_config = {"from_attributes": True}
UserResponse.model_config = {"from_attributes": True}
