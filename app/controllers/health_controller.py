from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.config.database import get_db
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("health-controller")

@router.get("/health")
def health_check():
    """
    Health check endpoint for the API
    
    Returns a simple response to indicate the API is running.
    """
    logger.debug("Health check called")
    return {
        "status": "ok",
        "message": "Service is running"
    }

@router.get("/health/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """
    Database health check endpoint
    
    Tests the database connection by executing a simple query.
    """
    logger.debug("Database health check called")
    try:
        # Execute a simple query to check DB connection
        result = await db.execute(text("SELECT 1"))
        return {
            "status": "ok", 
            "message": "Database connection is healthy"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
