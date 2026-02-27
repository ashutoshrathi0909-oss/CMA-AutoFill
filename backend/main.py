import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.db.supabase_client import get_supabase
import google.generativeai as genai

app = FastAPI(title="CMA AutoFill", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

# CORS: allow localhost + production frontend URL from env
allowed_origins = ["http://localhost:3000"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "CMA AutoFill API v1"}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }

@app.get("/health/db")
def health_db():
    try:
        db = get_supabase()
        return {"status": "connected", "database": "cma-autofill"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health/llm")
def health_llm():
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"status": "error", "message": "GOOGLE_API_KEY not found"}
        genai.configure(api_key=api_key)
        model_name = os.getenv("LLM_CLASSIFICATION_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi", generation_config={"max_output_tokens": 5})
        if response and response.text:
            return {"status": "ok", "model": model_name}
        else:
            return {"status": "error", "message": "Empty response from Gemini"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

