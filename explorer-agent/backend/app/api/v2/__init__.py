"""
API v2 - 5-Agent System
"""
from fastapi import APIRouter
from app.api.v2 import endpoints

router = APIRouter(prefix="/api/v2", tags=["v2"])

# Include all endpoints
router.include_router(endpoints.router)

__all__ = ["router"]
