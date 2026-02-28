from fastapi import APIRouter
from app.api.v1.endpoints import auth, clients, projects, files, dashboard, extraction, classification, generation, review, precedents, metrics

api_router = APIRouter()

# Group endpoints
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(files.router, tags=["files"])
api_router.include_router(extraction.router, prefix="/projects", tags=["extraction"])
api_router.include_router(classification.router, prefix="/projects", tags=["classification"])
api_router.include_router(generation.router, prefix="/projects", tags=["generation"])
api_router.include_router(review.router, tags=["review"])
api_router.include_router(precedents.router, prefix="/precedents", tags=["precedents"])
api_router.include_router(metrics.router, tags=["metrics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
