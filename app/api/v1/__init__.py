"""
API v1 package containing all v1 endpoints.
"""

from fastapi import APIRouter
from .endpoints import downloads

router = APIRouter(prefix="/v1")
router.include_router(downloads.router, prefix="/downloads", tags=["downloads"])

__all__ = ["router"] 