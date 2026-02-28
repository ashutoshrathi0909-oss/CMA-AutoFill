import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.security import limiter, ALLOWED_METHODS, ALLOWED_HEADERS
from app.db.supabase_client import get_supabase

logger = logging.getLogger(__name__)

app = FastAPI(title="CMA AutoFill", version="1.0.0")

# ── Rate Limiter ─────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── API Router ───────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")

# ── CORS (tightened) ─────────────────────────────────────────────────────
allowed_origins = ["http://localhost:3000"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)


# ── Global Exception Handler ────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions so stack traces are never leaked to clients."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {"message": "An internal error occurred. Please try again later."},
        },
    )


# ── Root ─────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "CMA AutoFill API v1"}


# ── Health Endpoints (safe — no internal details leaked) ─────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/health/db")
def health_db():
    try:
        get_supabase()
        return {"status": "connected"}
    except Exception:
        return {"status": "error"}


@app.get("/health/llm")
def health_llm():
    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"status": "error"}
        genai.configure(api_key=api_key)
        model_name = os.getenv("LLM_CLASSIFICATION_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi", generation_config={"max_output_tokens": 5})
        if response and response.text:
            return {"status": "ok"}
        return {"status": "error"}
    except Exception:
        return {"status": "error"}
