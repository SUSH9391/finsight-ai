import requests
from typing import Generator
from app.services.embeddings import embed_single
from app.services.vectorstore import search_user_transactions
from app.database.db import SessionLocal

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
    RAG pipeline → Ollama streaming response.
    1. Embed question → 2. ChromaDB search → 3. Mistral generate
    """
    # 1. Embed question
    query_emb = embed_single(question)
    
    # 2. RAG retrieve (per user)
    db = SessionLocal()
    context = search_user_transactions(user_id, query_emb)
    db.close()
    
    # 3. Build prompt
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

