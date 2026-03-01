# 💰 FinSight AI

> AI-powered personal finance advisor built with FastAPI, Mistral 7B, and RAG

## Features
- [ ] Upload bank statements (CSV/PDF)
- [ ] Auto transaction categorization
- [ ] AI-powered spending insights
- [ ] Natural language Q&A over your finances
- [ ] Interactive dashboard with charts

## Tech Stack
- **Backend:** FastAPI + Python
- **LLM:** Mistral 7B via Ollama (runs locally, free)
- **Embeddings:** sentence-transformers
- **Vector DB:** ChromaDB
- **Frontend:** Streamlit

## Setup
_Coming soon_

## Architecture
_Coming soon_
```

**`requirements.txt`** — just the basics for now, we'll add as we build:
```
fastapi==0.111.0
uvicorn==0.30.1
python-dotenv==1.0.1
pydantic==2.7.1
```

**`.env.example`** — template so others know what vars are needed (never commit `.env`!):
```
APP_NAME=FinSight AI
APP_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./finsight.db
OLLAMA_BASE_URL=http://localhost:11434

## Notes
# Make sure venv is activated FIRST
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Then install
pip install -r requirements.txt

uvicorn app.main:app --reload

# Open a SECOND terminal (keep uvicorn running in the first one)
streamlit run frontend/streamlit_app.py
```
✅ Runs on → `http://localhost:8501`

---

### 🗂️ So you need 2 terminals open at all times
```
Terminal 1                        Terminal 2
─────────────────────────────     ─────────────────────────────
source venv/bin/activate          source venv/bin/activate
uvicorn app.main:app --reload     streamlit run frontend/streamlit_app.py
→ http://localhost:8000           → http://localhost:8501

