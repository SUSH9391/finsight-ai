import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from app.services.embeddings import embed_transactions
from app.database.db import get_db
from sqlalchemy.orm import Session

# ChromaDB client (persistent storage)
client = chromadb.PersistentClient(path="./chromadb_data")

def get_user_collection(user_id: int) -> chromadb.Collection:
    """Get per-user transaction collection"""
    name = f"user_{user_id}_transactions"
    return client.get_or_create_collection(
        name=name,
        metadata={"user_id": str(user_id)},
        embedding_function=None  # We'll use pre-computed embeddings
    )

def store_user_transactions(user_id: int):
    """Embed and store user's transactions in ChromaDB (called after upload)"""
    db = next(get_db())
    embeddings = embed_transactions(db, user_id)
    
    if not embeddings:
        print(f"No transactions to embed for user {user_id}")
        return
    
    # Get transaction metadata
    txns = db.query(TransactionModel).filter(TransactionModel.user_id == user_id).all()
    documents = [f"{t.date} | {t.description} | ₹{float(t.amount):.2f} | {t.category or 'Others'}" for t in txns]
    metadatas = [{"id": str(t.id), "date": str(t.date), "amount": float(t.amount), "category": t.category or "Others"} for t in txns]
    ids = [str(t.id) for t in txns]
    
    collection = get_user_collection(user_id)
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"✅ Stored {len(ids)} embeddings for user {user_id}")

def search_user_transactions(user_id: int, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
    """RAG semantic search - find most relevant transactions for question"""
    collection = get_user_collection(user_id)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results['metadatas'][0] if results['metadatas'] else []

