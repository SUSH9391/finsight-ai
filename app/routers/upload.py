from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict
from app.services.parser import parse_csv

router = APIRouter()


@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a bank statement CSV.
    Parses → categorizes → stores in memory.
    """

    # ✅ Validate file type
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        contents = await file.read()

        # ✅ Parse CSV
        transactions: List[Dict] = parse_csv(contents)

        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in file")

        # ✅ Avoid circular import (IMPORTANT)
        from app.routers.analysis import set_transactions

        # ✅ Store transactions (for analysis module)
        set_transactions(transactions)

        # ✅ Clean preview (only useful fields)
        preview = [
            {
                "date": txn.get("date"),
                "description": txn.get("description"),
                "amount": txn.get("amount"),
                "category": txn.get("category"),
            }
            for txn in transactions[:5]
        ]

        return {
            "message": "File uploaded and processed successfully ✅",
            "filename": file.filename,
            "transactions_count": len(transactions),
            "preview": preview,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/history")
def get_upload_history():
    """
    Placeholder endpoint.
    Later: connect to DB and return uploaded files history.
    """
    return {
        "message": "Upload history will be available once DB is connected"
    }