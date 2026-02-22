from fastapi import FastAPI

app = FastAPI(
    title="FinSight AI",
    description="AI-powered personal finance advisor",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "FinSight AI is running"}