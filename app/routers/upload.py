from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import parse_csv
from app.routers.analysis import set_transactions  # ← wire the two together

router = APIRouter()

@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a bank statement CSV.
    Parses → categorizes → stores in memory.
    Automatically triggers categorization.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()

    try:
        transactions = parse_csv(contents)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # ← This is where categorizer gets called
    set_transactions(transactions)

    return {
        "message": "File uploaded and categorized successfully ✅",
        "filename": file.filename,
        "transactions_count": len(transactions),
        "preview": transactions[:5],
    }

@router.get("/history")
def get_upload_history():
    """Placeholder — will connect to DB in next step"""
    return {"message": "Upload history coming when DB is wired"}