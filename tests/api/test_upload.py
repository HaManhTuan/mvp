import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io

def test_upload_image_success(client: TestClient, auth_headers: dict):
    """Test successful image upload"""
    # Create a fake image file
    fake_image = io.BytesIO(b"fake image content")
    
    with patch('app.services.s3_service.s3_service.upload_file') as mock_upload, \
         patch('app.services.s3_service.s3_service.generate_presigned_url') as mock_url:
        
        mock_upload.return_value = "uploads/20250802_12345678_test.jpg"
        mock_url.return_value = "https://test-bucket.s3.amazonaws.com/uploads/20250802_12345678_test.jpg?presigned=true"
        
        response = client.post(
            "/api/v1/upload/image",
            files={"file": ("test_image.jpg", fake_image, "image/jpeg")},
            headers=auth_headers
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Image uploaded successfully"
    assert "data" in data
    assert "url" in data["data"]
    assert "file_key" in data["data"]

def test_upload_invalid_file_type(client: TestClient, auth_headers: dict):
    """Test upload with invalid file type"""
    fake_file = io.BytesIO(b"fake text content")
    
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.txt", fake_file, "text/plain")},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "Only image files are allowed" in response.json()["detail"]

def test_upload_file_too_large(client: TestClient, auth_headers: dict):
    """Test upload with file too large"""
    # Create a large fake file (11MB)
    large_content = b"x" * (11 * 1024 * 1024)
    large_file = io.BytesIO(large_content)
    
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("large_image.jpg", large_file, "image/jpeg")},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "File size cannot exceed" in response.json()["detail"]

def test_upload_empty_file(client: TestClient, auth_headers: dict):
    """Test upload with empty file"""
    empty_file = io.BytesIO(b"")
    
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("empty.jpg", empty_file, "image/jpeg")},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "File is empty" in response.json()["detail"]

def test_upload_unsupported_image_type(client: TestClient, auth_headers: dict):
    """Test upload with unsupported image type"""
    fake_file = io.BytesIO(b"fake image content")
    
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.tiff", fake_file, "image/tiff")},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "Supported image types" in response.json()["detail"]

def test_get_image_url_success(client: TestClient, auth_headers: dict):
    """Test getting presigned URL for existing file"""
    with patch('app.services.s3_service.s3_service.generate_presigned_url') as mock_url:
        mock_url.return_value = "https://test-bucket.s3.amazonaws.com/uploads/test.jpg?presigned=true"
        
        response = client.get(
            "/api/v1/upload/url/uploads/test.jpg",
            headers=auth_headers
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "expires_in" in data

def test_get_image_url_not_found(client: TestClient, auth_headers: dict):
    """Test getting URL for non-existent file"""
    with patch('app.services.s3_service.s3_service.generate_presigned_url') as mock_url:
        mock_url.return_value = None
        
        response = client.get(
            "/api/v1/upload/url/uploads/nonexistent.jpg",
            headers=auth_headers
        )
    
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]

def test_unauthorized_upload(client: TestClient):
    """Test unauthorized upload attempt"""
    fake_image = io.BytesIO(b"fake image content")
    
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("test_image.jpg", fake_image, "image/jpeg")}
    )
    
    assert response.status_code == 401

def test_unauthorized_get_url(client: TestClient):
    """Test unauthorized URL generation attempt"""
    response = client.get("/api/v1/upload/url/uploads/test.jpg")
    assert response.status_code == 401
