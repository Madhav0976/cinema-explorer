import logging
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.router import api_v1_router
from app.core.config import settings
from app.core.logging import setup_backend_logging
from app.db.session import get_db

# Initialize sanitized production logging
setup_backend_logging()
logger = logging.getLogger(__name__)


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


def create_app(cors_origins: list[str] | None = None) -> FastAPI:
    application = FastAPI(
        title="Cinema Explorer API",
        description="Explore movies and series through time, language, and culture.",
        version="1.0.0",
    )

    # Global unhandled exception handler to prevent leaking stack traces or credentials
    @application.exception_handler(Exception)
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

    # Configure CORS for Next.js frontend with exact allowed origins
    allowed = cors_origins if cors_origins is not None else settings.cors_origins
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API v1 router
    application.include_router(api_v1_router)

    @application.get("/")
    def read_root():
        return {
            "message": "Cinema Explorer API",
            "status": "ok",
            "version": "1.0.0",
            "docs_url": "/docs",
        }

    @application.get("/health")
    def read_health(db: Session = Depends(get_db)):
        return perform_health_check(db)

    @application.get("/api/v1/health")
    def read_api_v1_health(db: Session = Depends(get_db)):
        return perform_health_check(db)

    return application


app = create_app()

