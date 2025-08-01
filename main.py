import uvicorn
from fastapi import FastAPI
from app.config.settings import settings
from app.controllers import api_router
from app.config.middlewares import setup_middlewares

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup middlewares
setup_middlewares(app)  # This middleware handles CORS and other middlewares

# Include API router
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
    )
