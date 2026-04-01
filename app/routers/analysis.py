from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.routers.auth import get_current_user
from app.database.models import UserModel, TransactionModel
from app.database.db import get_all_transactions
from decimal import Decimal

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/summary")
async def get_summary(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get spending summary for current user"""
    transactions = get_all_transactions(
        db, 
        user_id=current_user.id, 
        limit=1000
    )
    
    total_income = sum(t.amount for t in transactions if t.type == 'credit')
    total_expense = sum(t.amount for t in transactions if t.type == 'debit')
    
    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "net": float(total_income - total_expense),
        "transaction_count": len(transactions)
    }

@router.get("/transactions")
async def get_transactions(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    category: str = None,
    type: str = None
):
    """Get filtered transactions for current user"""
    transactions = get_all_transactions(
        db, 
        user_id=current_user.id,
        category=category,
        type=type
    )
    return [
        {
            "id": t.id,
            "date": t.date.isoformat(),
            "description": t.description,
            "amount": float(t.amount),
            "category": t.category.name if t.category else None,
            "type": t.type.value
        }
        for t in transactions
    ]

@router.get("/category-breakdown")
async def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Category spending breakdown"""
    transactions = get_all_transactions(
        db, 
        user_id=current_user.id,
        limit=1000
    )
    
    category_totals = {}
    for t in transactions:
        if t.type == 'debit':
            cat_name = t.category.name if t.category else 'Others'
            category_totals[cat_name] = category_totals.get(cat_name, 0) + float(t.amount)
    
    return sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

@router.get("/trends")
async def get_trends(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    days: int = 30
):
    """30-day spending trends"""
    from datetime import datetime, timedelta
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    transactions = get_all_transactions(
        db, 
        user_id=current_user.id,
        skip=0, limit=1000  # Recent transactions
    )
    
    daily_totals = {}
    for t in [t for t in transactions if t.date >= cutoff_date and t.type == 'debit']:
        date_str = t.date.isoformat()
        daily_totals[date_str] = daily_totals.get(date_str, 0) + float(t.amount)
    
    return daily_totals

