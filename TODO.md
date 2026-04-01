# TODO: Remove ChromaDB to fix slow uvicorn startup

## Steps:
- [x] Step 1: Remove chromadb from requirements.txt
- [x] Step 2: Refactor app/routers/chat.py (remove vectorstore deps, simplify /ask with DB context)
- [x] Step 3: Update app/services/llm.py (SQL context instead of RAG)
- [x] Step 4: Delete app/services/vectorstore.py
- [x] Step 5: Delete app/services/embeddings.py (unused)

- [x] Step 5: Delete app/services/embeddings.py (unused)
- [x] Step 6: Test uvicorn app.main:app --reload (should be instant startup now)
