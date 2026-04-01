from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from datetime import date
from decimal import Decimal
from .models import Base, TransactionModel, CategoryModel

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finsight.db")

# SQLAlchemy 1.4+ (and 2.0) removed support for the 'postgres://' prefix, 
# but many providers (like Supabase/Heroku) still use it.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Using DATABASE_URL: {DATABASE_URL}")

if DATABASE_URL and "postgresql" in DATABASE_URL.lower():
    connect_args = {"sslmode": "require"}
else:
    connect_args = {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created!")

def get_all_transactions(db, user_id: int = None, skip: int = 0, limit: int = 100, **filters):
    query = db.query(TransactionModel)
    if user_id:
        query = query.filter(TransactionModel.user_id == user_id)
    for key, value in filters.items():
        if hasattr(TransactionModel, key):
            query = query.filter(getattr(TransactionModel, key) == value)
    return query.offset(skip).limit(limit).all()

def delete_all_transactions(db, user_id: int = None):
    query = db.query(TransactionModel)
    if user_id:
        query = query.filter(TransactionModel.user_id == user_id)
    query.delete()
    db.commit()

def create_transaction(db, txn: dict, user_id: int, upload_id: int):
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
        type='credit' if float(txn['amount']) > 0 else 'debit'
    )
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn

