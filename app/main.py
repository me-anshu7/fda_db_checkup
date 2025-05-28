from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.endpoints import downloads_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.include_router(downloads_router, prefix="/api/v1")
