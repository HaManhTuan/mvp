"""
Tests for user endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.helpers import create_test_user, create_test_token_for_user, get_auth_headers


@pytest.mark.asyncio
async def test_create_user(client: TestClient, db: AsyncSession):
    """
    Test creating a new user.
    """
    # Arrange
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "password_confirm":"password123",
        "full_name": "New User"
    }
    
    # Act
    response = client.post("/api/v1/users/", json=user_data)
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert "data" in data
    assert data["data"]["email"] == user_data["email"]
    assert data["data"]["username"] == user_data["username"]
    assert data["data"]["full_name"] == user_data["full_name"]
    assert "id" in data["data"]
    # Password should not be returned
    assert "password" not in data["data"]


@pytest.mark.asyncio
async def test_get_users_unauthorized(client: TestClient, db: AsyncSession):
    """
    Test getting users without authentication.
    """
    # Arrange
    # No authentication header
    
    # Act
    response = client.get("/api/v1/users/")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_users_authenticated(client: TestClient, db: AsyncSession):
    """
    Test getting users with authentication.
    """
    # Arrange
    user = await create_test_user(
        db,
        email="testuser@example.com",
        password="password123",
        is_admin=True
    )

    token = create_test_token_for_user(user)
    auth_headers = get_auth_headers(token)

    # Act
    response = client.get("/api/v1/users/", headers=auth_headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_user_by_id(client: TestClient, db: AsyncSession):
    """
    Test getting a user by ID.
    """
    # Arrange
    user = await create_test_user(
        db,
        email="testuser@example.com",
        password="password123"
    )

    token = create_test_token_for_user(user)
    auth_headers = get_auth_headers(token)

    # Act
    response = client.get(f"/api/v1/users/{user.id}", headers=auth_headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == user.id
    assert data["data"]["email"] == user.email


@pytest.mark.asyncio
async def test_get_user_not_found(client: TestClient, db: AsyncSession):
    """
    Test getting a non-existent user.
    """
    # Arrange
    user = await create_test_user(
        db,
        email="testuser@example.com",
        password="password123"
    )

    token = create_test_token_for_user(user)
    auth_headers = get_auth_headers(token)
    non_existent_id = 999999

    # Act
    response = client.get(f"/api/v1/users/{non_existent_id}", headers=auth_headers)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_user(client: TestClient, db: AsyncSession):
    """
    Test updating a user.
    """
    # Arrange
    user = await create_test_user(
        db,
        email="testuser@example.com",
        password="password123"
    )

    token = create_test_token_for_user(user)
    auth_headers = get_auth_headers(token)

    update_data = {
        "full_name": "Updated Name",
        "email": "updated@example.com"
    }

    # Act
    response = client.put(
        f"/api/v1/users/{user.id}",
        json=update_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert data["data"]["full_name"] == update_data["full_name"]
    assert data["data"]["email"] == update_data["email"]


@pytest.mark.asyncio
async def test_me_endpoint(client: TestClient, db: AsyncSession):
    """
    Test the /me endpoint.
    """
    # Arrange
    user = await create_test_user(
        db,
        email="testuser_me@example.com",
        password="password123"
    )

    token = create_test_token_for_user(user)
    auth_headers = get_auth_headers(token)

    # Act
    response = client.get("/api/v1/users/me", headers=auth_headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == user.id
    assert data["data"]["email"] == user.email
