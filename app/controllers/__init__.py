from fastapi import APIRouter
from app.config.constants import API_V1_PREFIX
from app.controllers import (
    auth_controller,
    user_controller,
    health_controller,
    upload_controller,
)

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_controller.router, tags=["Health"])
api_router.include_router(auth_controller.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
api_router.include_router(user_controller.router, prefix=f"{API_V1_PREFIX}/users", tags=["Users"])
api_router.include_router(upload_controller.router, prefix=f"{API_V1_PREFIX}/upload", tags=["File Upload"])
