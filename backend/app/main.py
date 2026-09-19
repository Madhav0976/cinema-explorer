import logging
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.router import api_v1_router
from app.core.logging import setup_backend_logging
from app.db.session import get_db

# Initialize sanitized production logging
setup_backend_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cinema Explorer API",
    description="Explore movies and series through time, language, and culture.",
    version="1.0.0",
)

# Global unhandled exception handler to prevent leaking stack traces or credentials
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )
    logger.error(
        f"Unhandled exception during {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router)


@app.get("/")
def read_root():
    return {
        "message": "Cinema Explorer API",
        "status": "ok",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


def perform_health_check(db: Session):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0",
        }
    except Exception as exc:
        logger.error(f"Database health check failure: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Database connectivity check failed",
        )


@app.get("/health")
def read_health(db: Session = Depends(get_db)):
    return perform_health_check(db)


@app.get("/api/v1/health")
def read_api_v1_health(db: Session = Depends(get_db)):
    return perform_health_check(db)

