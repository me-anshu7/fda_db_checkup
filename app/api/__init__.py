"""
API package containing all API versions and endpoints.
"""

from .v1 import router as v1_router

__all__ = ["v1_router"] 