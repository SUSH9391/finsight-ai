from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from .models import Base, TransactionType  # New models file

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finsight.db")  # Fallback to SQLite
if not DATABASE_URL or DATABASE_URL == "sqlite:///./finsight.db":
    print("⚠️ Using SQLite (development). Set DATABASE_URL in .env for PostgreSQL.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"sslmode": "require"} if "postgresql" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_all_transactions(db, user_id: int = None, skip: int = 0, limit: int = 100, **filters):
    """Filter by user_id + pagination"""
    from .models import TransactionModel
    query = db.query(TransactionModel)
    if user_id:
        query = query.filter(TransactionModel.user_id == user_id)
    for key, value in filters.items():
        if hasattr(TransactionModel, key):
            query = query.filter(getattr(TransactionModel, key) == value)
    return query.offset(skip).limit(limit).all()

def delete_all_transactions(db, user_id: int = None):
    """Delete user's transactions"""
    from .models import TransactionModel
    query = db.query(TransactionModel)
    if user_id:
        query = query.filter(TransactionModel.user_id == user_id)
    query.delete()
    db.commit()

def create_transaction(db, txn: dict, user_id: int, upload_id: int):
    """Create transaction with FKs"""
    from .models import TransactionModel, CategoryModel
    from decimal import Decimal
    
    # Find or create category
    category = db.query(CategoryModel).filter(CategoryModel.name == txn.get('category', 'Others')).first()
    if not category:
        category = CategoryModel(name=txn.get('category', 'Others'))
        db.add(category)
        db.commit()
        db.refresh(category)
    
    db_txn = TransactionModel(
        user_id=user_id,
        upload_id=upload_id,
        category_id=category.id,
        date=txn.get('date', date.today()),
        description=txn['description'],
        amount=Decimal(str(txn['amount'])),
        type='credit' if txn['amount'] > 0 else 'debit'
    )
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn


