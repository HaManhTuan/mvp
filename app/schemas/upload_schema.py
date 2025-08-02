from typing import Optional, BinaryIO
from pydantic import BaseModel, Field, validator
from fastapi import UploadFile, HTTPException, status

class ImageUploadResponse(BaseModel):
    """Schema for image upload response"""
    url: str = Field(..., description="URL to access the uploaded image")
    file_key: str = Field(..., description="S3 file key/path")
    original_filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., description="File size in bytes")
    bucket_name: str = Field(..., description="S3 bucket name")
    expires_in: int = Field(..., description="URL expiration time in seconds")

class FileValidationRequest(BaseModel):
    """Schema for file validation data"""
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename for security"""
        if not v or not v.strip():
            raise ValueError('Filename cannot be empty')
        
        # Check for dangerous characters
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f'Filename contains invalid character: {char}')
        
        return v.strip()
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Validate that content type is for images"""
        if not v or not v.startswith('image/'):
            raise ValueError('Only image files are allowed')
        
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/gif', 'image/webp', 'image/bmp'
        ]
        
        if v not in allowed_types:
            raise ValueError(f'Supported image types: {", ".join(allowed_types)}')
        
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        """Validate file size (max 10MB)"""
        if v <= 0:
            raise ValueError('File cannot be empty')
        
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size cannot exceed {max_size} bytes (10MB)')
        
        return v
