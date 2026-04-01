import requests
from typing import Generator
from app.database.db import SessionLocal, get_all_transactions

OLLAMA_BASE = "http://localhost:11434"
MODEL_NAME = "mistral"

def generate_prompt(question: str, user_id: int, context_transactions: list) -> str:
    """
    Build RAG prompt for financial advisor.
    Context: Top 5 relevant transactions.
    """
    context_text = "\n".join([
        f"- {t['category']}: ₹{t['amount']} on {t['date']} ({t['description'][:50]}...)"
        for t in context_transactions
    ])
    
    prompt = f"""You are a financial advisor analyzing the user's bank transactions. 

USER TRANSACTIONS (most relevant):
{context_text}

USER QUESTION: {question}

Provide a helpful, actionable financial insight. Use exact numbers from transactions. Be concise but specific. Format naturally.

Answer:"""
    
    return prompt

async def ask_llm(question: str, user_id: int) -> Generator[str, None, None]:
    """
    SQL DB context → Ollama streaming response.
    Context from recent transactions.
    """
    # 1. Get recent transactions for context
    db = SessionLocal()
    txns = get_all_transactions(db, user_id, limit=5)
    context = [
        {
            "date": str(t.date),
            "description": t.description,
            "amount": float(t.amount),
            "category": getattr(t, 'category', 'Others') or 'Others'
        }
        for t in txns
    ]
    db.close()
    
    # 2. Build prompt
    prompt = generate_prompt(question, user_id, context)
    
    # 4. Ollama stream
    response = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": 0.1, "top_p": 0.9}
        },
        stream=True
    )
    
    if response.status_code != 200:
        yield "Error calling LLM"
        return
    
    for line in response.iter_lines():
        if line:
            chunk = line.decode('utf-8')
            if 'response' in chunk:
                # Extract response field from JSON line
                resp = chunk.split('"response":"')[1].split('"')[0]
                if resp:
                    yield resp

