from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.middlewares.logging_middleware import LoggingMiddleware
from app.middlewares.context_middleware import RequestContextMiddleware

def setup_middlewares(app: FastAPI) -> None:
    """Setup all middleware for the application"""
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add other middlewares here
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestContextMiddleware)
    
    return None
