"""
Tests for health endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status


def test_health_check(client: TestClient):
    """
    Test the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "Service is running"


def test_db_health_check(client: TestClient):
    """
    Test the database health check endpoint.
    """
    response = client.get("/health/db")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "Database connection is healthy"
