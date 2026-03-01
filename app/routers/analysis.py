from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.categorizer import (
    categorize_transactions,
    get_spending_summary,
    get_monthly_trend,
)

router = APIRouter()

# In-memory store for now — will move to DB in next step
_transactions_store: list = []

def get_stored_transactions():
    """Get current in-memory transactions"""
    if not _transactions_store:
        raise HTTPException(
            status_code=404,
            detail="No transactions found. Please upload a CSV first."
        )
    return _transactions_store

def set_transactions(transactions: list):
    """Called by upload router after parsing CSV"""
    global _transactions_store
    _transactions_store = categorize_transactions(transactions)

@router.get("/summary")
def get_summary():
    """
    Returns total income, expenses, net savings,
    top spending category, and full category breakdown.
    Call this on dashboard load after CSV upload.
    """
    transactions = get_stored_transactions()
    summary = get_spending_summary(transactions)
    return summary

@router.get("/categories")
def get_categories():
    """
    Returns spending grouped by category with totals.
    Use this to render the pie chart.
    """
    transactions = get_stored_transactions()
    summary = get_spending_summary(transactions)
    return {
        "categories": summary.get("category_breakdown", {}),
        "top_category": summary.get("top_category")
    }

@router.get("/monthly")
def get_monthly():
    """
    Returns month-over-month income vs expense trend.
    Use this to render the line/bar chart.
    """
    transactions = get_stored_transactions()
    trend = get_monthly_trend(transactions)
    return {"monthly_trend": trend}

@router.get("/transactions")
def get_transactions(
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by credit or debit"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Returns paginated transaction list.
    Supports filtering by category and type.
    """
    transactions = get_stored_transactions()

    # Apply filters
    filtered = transactions
    if category:
        filtered = [t for t in filtered if t.get("category", "").lower() == category.lower()]
    if type:
        filtered = [t for t in filtered if t.get("type", "").lower() == type.lower()]

    # Paginate
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "transactions": paginated,
    }