from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Date
from datetime import datetime
import os
from dotenv import load_dotenv
import enum
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # avoids stale connections
    pool_size=5,          # connection pool
    max_overflow=10,
    connect_args={"sslmode":"require"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TransactionType(enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionModel(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(String, default="Others")
    type = Column(Enum(TransactionType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
