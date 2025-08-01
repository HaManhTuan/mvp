
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config.settings import settings


# Create a Base class for declarative models
Base = declarative_base()


def get_database_url():
    """Get the appropriate database URL based on environment."""
    if os.getenv("APP_ENV") == "test":
        # Use SQLite for testing
        return "sqlite+aiosqlite:///file:mem_db?mode=memory&cache=shared&uri=true"
    else:
        # Use the configured database URL for production/development
        return str(settings.DATABASE_URL)


# Create the SQLAlchemy async engine
engine = create_async_engine(
    get_database_url(),
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    # SQLite-specific settings for testing
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
)


# Create an async SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


# Async dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()