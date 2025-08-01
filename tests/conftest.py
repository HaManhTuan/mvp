"""
Test configuration and fixtures for the FastAPI application.
"""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
import httpx
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Set the environment to test
os.environ["APP_ENV"] = "test"

# Import after setting APP_ENV
from app.config.database import get_db, Base, engine
from app.config.settings import settings
from main import app as application

# Import all models to ensure they're registered with SQLAlchemy metadata
from tests.utils.models import *  # This is critical for table creation

# Create session factory using the shared engine
TestingSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False, 
    autoflush=False
)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for tests.
    Uses the tables created by setup_test_db.
    """
    # Create session using the existing database with tables already created
    async with TestingSessionLocal() as session:
        try:
            yield session
        except Exception:
            # Roll back in case of error
            await session.rollback()
            raise
        finally:
            # Close the session
            await session.close()


@pytest.fixture
def event_loop() -> Generator:
    """
    Create an instance of the default event loop for each test case.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Return the test database instead of the production database.
    """
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
def app() -> FastAPI:
    """
    Create a fresh app instance for testing.
    """
    # Replace the production database dependency with the test database
    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Setup function that runs once before all tests.
    Creates tables and prepares the test database.
    This replaces the need for Alembic migrations in the test environment.
    """
    # Import all models to ensure they're properly registered with Base.metadata
    from app.models.user import User
    from app.models.base_model import BaseModel
    # Import any other models here
    
    # Log that we're setting up the test database
    print("\nSetting up test database and creating all tables...")
    
    # Create all tables at the beginning of the test session
    async with engine.begin() as conn:
        # Drop all tables first to ensure a clean state
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables based on the imported models
        await conn.run_sync(Base.metadata.create_all)
        print(f"Created tables: {', '.join(Base.metadata.tables.keys())}")
    
    yield
    
    # Clean up after all tests are done
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(app: FastAPI) -> Generator:
    """
    Create a test client for the app.
    """
    # Using TestClient for synchronous testing
    with TestClient(app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator:
    """
    Create an async test client for the app.
    """
    # Using httpx.AsyncClient for async testing
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
