from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from decimal import Decimal
from datetime import datetime, date
import enum

Base = declarative_base()

class TransactionType(enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # relationships
    uploads = relationship("UploadModel", back_populates="user")
    transactions = relationship("TransactionModel", back_populates="user")
    chat_history = relationship("ChatHistoryModel", back_populates="user")
    budgets = relationship("BudgetModel", back_populates="user")

class UploadModel(Base):
    __tablename__ = "uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String)
    row_count = Column(Integer, default=0)
    is_embedded = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # relationships
    user = relationship("UserModel", back_populates="uploads")
    transactions = relationship("TransactionModel", back_populates="upload")

class CategoryModel(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    icon = Column(String)
    color = Column(String)
    is_income = Column(Boolean, default=False)
    
    transactions = relationship("TransactionModel", back_populates="category")

class ChatHistoryModel(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String)  # UUID
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    sources = Column(String)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("UserModel", back_populates="chat_history")

class BudgetModel(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    monthly_limit = Column(Numeric(12, 2), nullable=False)
    month = Column(String)  # YYYY-MM
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("UserModel", back_populates="budgets")

class TransactionModel(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # relationships
    user = relationship("UserModel", back_populates="transactions")
    upload = relationship("UploadModel", back_populates="transactions")
    category = relationship("CategoryModel", back_populates="transactions")

