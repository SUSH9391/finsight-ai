import pandas as pd
import io
import numpy as np
from typing import List, Dict

def parse_csv(contents: bytes) -> List[Dict]:
    """
    Parse bank statement CSV into list of transactions.
    Handles common bank CSV formats.
    """
    MAX_CSV_SIZE = 10 * 1024 * 1024  # 10 MB limit
    
    if len(contents) > MAX_CSV_SIZE:
        raise ValueError(f"CSV file too large: {len(contents)} bytes exceeds {MAX_CSV_SIZE} byte limit")
    
    try:
        df = pd.read_csv(
    io.BytesIO(contents),
    encoding="utf-8",
    sep=None,
    engine="python"
)        
        # Normalize column names to lowercase
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        
        # CRITICAL FIX: Convert ALL problematic float values for JSON compatibility
        # Replace: NaN, inf, -inf with empty string "" using a dictionary
        df = df.replace({np.nan: "", np.inf: "", -np.inf: ""})
        
        # Also handle pandas NA specifically
        df = df.replace({pd.NA: ""})
        
        # Convert any remaining problematic types to strings
        # First convert to dict, then clean up any remaining non-serializable values
        transactions = df.to_dict(orient="records")
        
        # Final pass: clean any remaining problematic values
        cleaned_transactions = []

        for txn in transactions:
            cleaned_txn = {}
            for key, value in txn.items():
                if isinstance(value, float):
                    if np.isnan(value) or np.isinf(value):
                        cleaned_txn[key] = ""
                    else:
                        cleaned_txn[key] = value
                else:
                    cleaned_txn[key] = value

            cleaned_transactions.append(cleaned_txn)

        return cleaned_transactions
        
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}") from e
    
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}") from e


##parser function is final