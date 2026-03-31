from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.services.categorizer import (
    get_spending_summary,
    get_monthly_trend,
)
from app.database.db import get_db, get_all_transactions
from app.database.models import TransactionModel, TransactionType

router = APIRouter()

def model_to_dict(t):
    """Convert TransactionModel to dict for service compatibility"""
    return {
        "date": str(t.date),
        "description": t.description,
        "amount": float(t.amount),
        "category": t.category or "Others",
        "type": str(t.type),
    }

@router.get("/summary") 
async def get_summary(db: Session = Depends(get_db)):
    # TODO Phase 3: current_user: UserModel = Depends(get_current_user)
    """
    Returns total income, expenses, net savings,
    top spending category, and full category breakdown.
    Call this on dashboard load after CSV upload.
    """
    db_txns = get_all_transactions(db)
    transactions = [model_to_dict(t) for t in db_txns]
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found. Please upload a CSV first.")
    total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    total_expenses = abs(sum(t["amount"] for t in transactions if t["amount"] < 0))
    net_savings = total_income - total_expenses
    summary = get_spending_summary(transactions)
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(net_savings, 2),
        **summary
    }

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """
    Returns spending grouped by category with totals.
    Use this to render the pie chart.
    """
    db_txns = get_all_transactions(db)
    transactions = [model_to_dict(t) for t in db_txns]
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found. Please upload a CSV first.")
    summary = get_spending_summary(transactions)
    return {
        "categories": summary.get("category_breakdown", {}),
        "top_category": summary.get("top_category")
    }

@router.get("/monthly")
async def get_monthly(db: Session = Depends(get_db)):
    """
    Returns month-over-month income vs expense trend.
    Use this to render the line/bar chart.
    """
    db_txns = get_all_transactions(db)
    transactions = [model_to_dict(t) for t in db_txns]
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found. Please upload a CSV first.")
    trend = get_monthly_trend(transactions)
    return {"monthly_trend": trend}

@router.get("/transactions")
async def get_transactions(
    category: Optional[str] = Query(None, description="Filter by category"),
    txn_type: Optional[str] = Query(None, description="Filter by credit or debit"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Returns paginated transaction list.
    Supports filtering by category and type.
    """
    skip = (page - 1) * page_size
    db_txns = get_all_transactions(db, skip=skip, limit=page_size, category=category, txn_type=txn_type)
    transactions = [model_to_dict(t) for t in db_txns]

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found. Please upload a CSV first.")

    # Get total count with same filters
    total_query = db.query(func.count(TransactionModel.id))
    if category:
        total_query = total_query.filter(TransactionModel.category == category)
    if txn_type:
        total_query = total_query.filter(TransactionModel.type == TransactionType(txn_type.lower()))
    total = total_query.scalar()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "transactions": transactions,
    }
