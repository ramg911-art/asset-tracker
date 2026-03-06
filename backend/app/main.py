"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, async_session_maker, Base
from app.routers import (
    auth,
    assets,
    locations,
    categories,
    departments,
    vendors,
    repairs,
    movements,
    maintenance,
    verification,
    documents,
    labels,
    reports,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create upload directories on startup."""
    upload_base = Path(settings.upload_dir)
    for sub in ["documents", "repairs", "verification"]:
        (upload_base / sub).mkdir(parents=True, exist_ok=True)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS: use config list or ["*"]; with "*" avoid credentials to satisfy strict CORS
_cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()] if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Auth (no prefix for /auth)
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Core API
app.include_router(assets.router, prefix="/assets", tags=["assets"])
app.include_router(locations.router, prefix="/locations", tags=["locations"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(departments.router, prefix="/departments", tags=["departments"])
app.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
app.include_router(repairs.router, prefix="/repairs", tags=["repairs"])
app.include_router(movements.router, prefix="/movements", tags=["movements"])
app.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
app.include_router(verification.router, prefix="/verification", tags=["verification"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(labels.router, prefix="/labels", tags=["labels"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
