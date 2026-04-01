from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict
from app.services.parser import parse_csv
from app.services.categorizer import categorize_transactions
from app.database.db import get_db, create_transaction, delete_all_transactions
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.models import TransactionModel, UserModel
from app.routers.auth import get_current_user

router = APIRouter()


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(..., media_type="text/csv"), 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
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

        # ✅ Categorize
        categorized = categorize_transactions(transactions)

        # ✅ Clear old data and save to DB
        delete_all_transactions(db, current_user.id)
        for txn in categorized:
            create_transaction(db, txn, current_user.id, upload_id=1)  # TODO: create proper upload record

        # ✅ Clean preview (only useful fields)
        preview = [
            {
                "date": txn.get("date"),
                "description": txn.get("description"),
                "amount": txn.get("amount"),
                "category": txn.get("category"),
            }
            for txn in categorized[:5]
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
async def get_upload_history(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Get upload history from transaction created_at groups.
    """
    if not db.query(TransactionModel).filter(TransactionModel.user_id == current_user.id).first():
        return {"message": "No uploads yet. Upload a CSV first.", "uploads": []}
    
    # Group by date(created_at)
    history = db.query(
        func.date(TransactionModel.created_at).label('upload_date'),
        func.count().label('transaction_count')
    ).filter(TransactionModel.user_id == current_user.id).group_by(func.date(TransactionModel.created_at)).order_by(func.date(TransactionModel.created_at).desc()).all()
    
    uploads = [
        {
            "upload_date": str(h.upload_date),
            "transaction_count": h.transaction_count,
            "filename": f"statement_{h.upload_date.strftime('%Y%m%d')}.csv"  # proxy
        }
        for h in history
    ]
    
    return {"uploads": uploads, "total_transactions": db.query(func.count(TransactionModel.id)).filter(TransactionModel.user_id == current_user.id).scalar()}
