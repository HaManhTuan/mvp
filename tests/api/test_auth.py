"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.helpers import create_test_user


@pytest.mark.asyncio
async def test_login(client: TestClient, db: AsyncSession):
    """
    Test login endpoint.
    """
    # Arrange
    email = "testlogin@example.com"
    password = "password123"
    username = "testlogin"
    
    user = await create_test_user(
        db,
        email=email,
        password=password,
        username=username
    )
    
    login_data = {"username": username, "password": password}
    
    # Act
    response = client.post(
        "/api/v1/auth/token",
        data=login_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: TestClient, db: AsyncSession):
    """
    Test login with wrong password.
    """
    # Arrange
    email = "testlogin@example.com"
    password = "password123"
    username = "testlogin"
    
    user = await create_test_user(
        db,
        email=email,
        password=password,
        username=username
    )
    
    wrong_password_data = {"username": username, "password": "wrongpassword"}
    
    # Act
    response = client.post(
        "/api/v1/auth/token",
        data=wrong_password_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_inactive_user(client: TestClient, db: AsyncSession):
    """
    Test login with an inactive user.
    """
    # Arrange
    email = "inactive@example.com"
    password = "password123"
    username = "inactive"
    
    user = await create_test_user(
        db,
        email=email,
        password=password,
        username=username,
        is_active=False
    )
    
    login_data = {"username": username, "password": password}
    
    # Act
    response = client.post(
        "/api/v1/auth/token",
        data=login_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_register(client: TestClient, db: AsyncSession):
    """
    Test user registration.
    """
    # Arrange
    username = "newregister"
    password = "password123"
    
    register_data = {"username": username, "password": password}
    
    # Act
    response = client.post(
        "/api/v1/auth/register",
        data=register_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_existing_user(client: TestClient, db: AsyncSession):
    """
    Test registering a user that already exists.
    """
    # Arrange
    email = "existing@example.com"
    password = "password123"
    username = "existing"
    
    user = await create_test_user(
        db,
        email=email,
        password=password,
        username=username
    )
    
    register_data = {"username": username, "password": password}
    
    # Act
    response = client.post(
        "/api/v1/auth/register",
        data=register_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
