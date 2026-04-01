from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
from app.database.db import get_db
from app.database.models import TransactionModel
from sqlalchemy.orm import Session

# Global variable to hold the model (lazy-loaded)
_model: Optional[SentenceTransformer] = None

def get_model() -> SentenceTransformer:
    """Lazy-load the embedding model"""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def embed_transactions(db: Session, user_id: int) -> List[np.ndarray]:
    """
    Embed user's transactions for RAG. 
    Text format: "date + description + amount + category"
    """
    model = get_model()
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
    model = get_model()
    embedding = model.encode([text])
    return embedding[0].tolist()

