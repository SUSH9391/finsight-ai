from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, analysis, chat, auth
from app.database.db import create_tables

app = FastAPI(
    title="FinSight AI",
    description="AI-powered personal finance advisor",
)

# CORS - allows frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    create_tables()

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "FinSight AI is running "}