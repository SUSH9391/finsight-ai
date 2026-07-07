import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from app.database.db import SessionLocal, get_all_transactions

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
# Qwen2.5-7B-Instruct — confirmed working on HF free Inference API
MODEL_NAME = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")

# Initialise once at module level
client = InferenceClient(token=HF_TOKEN)


def build_messages(question: str, context_transactions: list) -> list:
    """
    Build OpenAI-style chat messages for the HuggingFace chat_completion API.
    Includes top-N transaction context for RAG-style grounding.
    """
    if context_transactions:
        context_lines = "\n".join([
            f"- {t['category']}: ₹{t['amount']} on {t['date']} "
            f"({str(t['description'])[:60]})"
            for t in context_transactions
        ])
        system_content = (
            "You are FinSight AI, an expert personal finance advisor. "
            "Analyse the user's real bank transactions below and answer their question "
            "with specific numbers and actionable advice. Be concise.\n\n"
            f"USER TRANSACTIONS (most relevant):\n{context_lines}"
        )
    else:
        system_content = (
            "You are FinSight AI, an expert personal finance advisor. "
            "The user has not uploaded any transactions yet. "
            "Give general financial advice and encourage them to upload their bank statement."
        )

    return [
        {"role": "system", "content": system_content},
        {"role": "user",   "content": question},
    ]


async def ask_llm(question: str, user_id: int) -> AsyncGenerator[str, None]:
    """
    Fetch transaction context from DB → stream a response from
    HuggingFace Inference API (Mistral-7B-Instruct).
    """
    # 1. Pull recent transactions for context
    db = SessionLocal()
    try:
        txns = get_all_transactions(db, user_id, limit=10)
        context = [
            {
                "date":        str(t.date),
                "description": t.description,
                "amount":      float(t.amount),
                "category":    (getattr(t, "category", None) or "Others"),
            }
            for t in txns
        ]
    finally:
        db.close()

    # 2. Build prompt messages
    messages = build_messages(question, context)

    # 3. Stream from HuggingFace Inference API
    try:
        stream = client.chat_completion(
            messages=messages,
            model=MODEL_NAME,
            max_tokens=600,
            temperature=0.2,
            top_p=0.9,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        yield f"\n⚠️ Error calling HuggingFace API: {str(e)}"
