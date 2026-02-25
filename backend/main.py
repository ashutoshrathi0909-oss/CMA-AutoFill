from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.supabase_client import get_supabase

app = FastAPI(title="CMA AutoFill", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "CMA AutoFill API v1"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "cma-autofill-api"}

@app.get("/health/db")
def health_db():
    try:
        db = get_supabase()
        return {"status": "connected", "database": "cma-autofill"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
