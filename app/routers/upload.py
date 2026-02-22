from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import parse_csv

router = APIRouter()

@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a bank statement CSV file"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    contents = await file.read()
    result = parse_csv(contents)
    
    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "transactions_count": len(result),
        "preview": result[:5]  # return first 5 rows as preview
    }