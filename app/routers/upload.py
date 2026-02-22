from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import parse_csv

router = APIRouter()

@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a bank statement CSV file"""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")    
    contents = await file.read()
    # Optional: limit file size (e.g., 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    try:
        result = parse_csv(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
    
    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "transactions_count": len(result),
        "preview": result[:5]  # return first 5 rows as preview
    }
