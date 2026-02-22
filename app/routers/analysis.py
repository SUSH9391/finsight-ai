from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
def get_summary():
    """Get spending summary — coming in Day 2"""
    return {"message": "Analysis endpoint — coming soon"}

@router.get("/categories")
def get_categories():
    """Get spending by category — coming in Day 2"""
    return {"message": "Categories endpoint — coming soon"}