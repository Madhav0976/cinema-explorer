from fastapi import APIRouter

from app.api.v1.discovery import router as discovery_router
from app.api.v1.taxonomies import router as taxonomies_router
from app.api.v1.titles import router as titles_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(titles_router)
api_v1_router.include_router(taxonomies_router)
api_v1_router.include_router(discovery_router)

