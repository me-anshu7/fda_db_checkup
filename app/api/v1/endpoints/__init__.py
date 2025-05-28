"""
API v1 endpoints package containing all endpoint routers.
"""

from .downloads import router as downloads_router

__all__ = ["downloads_router"]
