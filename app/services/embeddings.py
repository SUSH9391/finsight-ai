from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.database.db import get_db
from app.database.models import TransactionModel
from sqlalchemy.orm import Session

# Load embedding model (all-MiniLM-L6-v2 = 384 dim, fast)
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_transactions(db: Session, user_id: int) -> List[np.ndarray]:
    """
    Embed user's transactions for RAG. 
    Text format: "date + description + amount + category"
    """
    txns = db.query(TransactionModel).filter(TransactionModel.user_id == user_id).all()
    
    texts = []
    for txn in txns:
        text = f"{txn.date} | {txn.description} | ₹{float(txn.amount):.2f} | {txn.category or 'Others'}"
        texts.append(text)
    
    if not texts:
        return []
    
    embeddings = model.encode(texts)
    return embeddings.tolist()

def embed_single(text: str) -> List[float]:
    """Embed single text (question)"""
    embedding = model.encode([text])
    return embedding[0].tolist()

