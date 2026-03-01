import pandas as pd
from typing import List, Dict

CATEGORY_KEYWORDS = {
    "Food & Dining": ["swiggy", "zomato", "restaurant", "cafe", "mcdonald", "subway", "pizza", "burger", "dominos", "kfc"],
    "Transport": ["uber", "ola", "rapido", "petrol", "fuel", "metro", "irctc", "redbus", "bus", "auto"],
    "Shopping": ["amazon", "flipkart", "myntra", "meesho", "mall", "shop", "store", "retail", "nykaa"],
    "Utilities": ["electricity", "water", "gas", "broadband", "wifi", "airtel", "jio", "bsnl", "bill", "recharge"],
    "Entertainment": ["netflix", "spotify", "youtube", "prime", "hotstar", "cinema", "pvr", "inox", "game"],
    "Health": ["pharmacy", "hospital", "clinic", "medplus", "apollo", "doctor", "medicine", "health", "lab"],
    "Rent": ["rent", "maintenance", "society", "landlord", "lease"],
    "Salary": ["salary", "payroll", "stipend", "bonus", "income"],
    "Investment": ["mutual fund", "sip", "zerodha", "groww", "stock", "nps", "fd", "deposit"],
    "Education": ["udemy", "coursera", "college", "fees", "school", "tuition", "book"],
}

def categorize_transaction(description: str) -> str:
    description_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    return "Others"

def categorize_transactions(transactions: List[Dict]) -> List[Dict]:
    """Add category field to each transaction in the list"""
    for txn in transactions:
        desc = txn.get("description") or txn.get("narration") or txn.get("details") or ""
        txn["category"] = categorize_transaction(str(desc))
    return transactions

def get_spending_summary(transactions: List[Dict]) -> Dict:
    """Compute income, expenses, savings, and per-category totals"""
    df = pd.DataFrame(transactions)

    # Normalize amount column
    if "amount" not in df.columns:
        return {"error": "No amount column found"}

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    income_categories = ["Salary", "Investment"]
    df["type"] = df["category"].apply(
        lambda c: "credit" if c in income_categories else "debit"
    )

    total_income = df[df["type"] == "credit"]["amount"].sum()
    total_expenses = df[df["type"] == "debit"]["amount"].sum()
    net_savings = total_income - total_expenses

    category_breakdown = (
        df[df["type"] == "debit"]
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    top_category = max(category_breakdown, key=category_breakdown.get) if category_breakdown else "N/A"

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(net_savings, 2),
        "top_category": top_category,
        "category_breakdown": {k: round(v, 2) for k, v in category_breakdown.items()},
    }

def get_monthly_trend(transactions: List[Dict]) -> List[Dict]:
    """Return month-over-month income vs expense for charts"""
    df = pd.DataFrame(transactions)

    # Try to find a date column
    date_col = next((c for c in df.columns if "date" in c.lower()), None)
    if not date_col:
        return []

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["month"] = pd.to_datetime(df[date_col], errors="coerce").dt.to_period("M").astype(str)

    income_categories = ["Salary", "Investment"]
    df["type"] = df["category"].apply(lambda c: "credit" if c in income_categories else "debit")

    monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    monthly.columns.name = None

    result = []
    for _, row in monthly.iterrows():
        result.append({
            "month": row.get("month"),
            "income": round(row.get("credit", 0), 2),
            "expenses": round(row.get("debit", 0), 2),
        })

    return sorted(result, key=lambda x: x["month"])
