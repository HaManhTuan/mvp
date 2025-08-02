from typing import Optional
from fastapi import UploadFile, HTTPException, status
from pydantic import ValidationError
import io

from app.services.s3_service import s3_service
from app.schemas.upload_schema import FileValidationRequest, ImageUploadResponse
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger("upload-service")

class UploadService:
    """Service layer for file upload operations"""
    
    def __init__(self):
        self.s3_service = s3_service
    
    def validate_upload_file(self, file: UploadFile, file_content: bytes) -> FileValidationRequest:
        """
        Validate uploaded file using Pydantic schema
        
        Args:
            file: FastAPI UploadFile object
            file_content: Raw file content bytes
            
        Returns:
            Validated FileValidationRequest object
            
        Raises:
            HTTPException: If validation fails
        """
        try:
            # Create validation data
            validation_data = {
                'filename': file.filename or '',
                'content_type': file.content_type or '',
                'file_size': len(file_content)
            }
            
            # Validate using Pydantic schema
            validated_file = FileValidationRequest(**validation_data)
            
            logger.debug(f"File validation passed: {validated_file.filename}")
            return validated_file
            
        except ValidationError as e:
            # Extract the first validation error message
            error_msg = str(e.errors()[0]['msg']) if e.errors() else "Invalid file"
            logger.warning(f"File validation failed: {error_msg}")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        except Exception as e:
            logger.error(f"Unexpected error during file validation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File validation error"
            )
    
    async def process_file_upload(
        self, 
        file: UploadFile, 
        username: Optional[str] = None
    ) -> ImageUploadResponse:
        """
        Process complete file upload workflow
        
        Args:
            file: FastAPI UploadFile object
            username: Username for logging purposes
            
        Returns:
            ImageUploadResponse with URL and file information
            
        Raises:
            HTTPException: If any step fails
        """
        logger.info(f"Processing file upload: {file.filename}, user: {username}")
        
        # Basic file checks
        if not file.filename:
            logger.warning("Upload attempt with no filename")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read file content"
            )
        
        # Validate file using schema
        validated_file = self.validate_upload_file(file, file_content)
        
        # Get expiration from settings
        expiration = settings.S3_PRESIGNED_URL_EXPIRATION
        
        try:
            # Create BytesIO object from file content
            file_obj = io.BytesIO(file_content)
            
            # Upload to S3
            file_key = await self.s3_service.upload_file(
                file_obj=file_obj,
                original_filename=validated_file.filename,
                content_type=validated_file.content_type
            )
            
            if not file_key:
                logger.error(f"Failed to upload file to S3: {validated_file.filename}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload file to S3"
                )
            
            # Generate presigned URL
            presigned_url = self.s3_service.generate_presigned_url(
                file_key, 
                expiration
            )
            
            if not presigned_url:
                logger.error(f"Failed to generate presigned URL for: {file_key}")
                # Clean up uploaded file if URL generation fails
                # Note: In production, you might want to implement cleanup in a background task
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate file URL"
                )
            
            # Create response object
            upload_response = ImageUploadResponse(
                url=presigned_url,
                file_key=file_key,
                original_filename=validated_file.filename,
                content_type=validated_file.content_type,
                file_size=validated_file.file_size,
                bucket_name=settings.S3_BUCKET_NAME,
                expires_in=expiration
            )
            
            logger.info(f"Successfully processed upload: {file_key}, user: {username}")
            return upload_response
            
        except HTTPException:
            # Re-raise HTTPExceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload processing: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during file upload"
            )
    
    async def generate_file_url(
        self, 
        file_key: str, 
        username: Optional[str] = None
    ) -> dict:
        """
        Generate presigned URL for existing file
        
        Args:
            file_key: S3 file key/path
            username: Username for logging purposes
            
        Returns:
            Dictionary with URL and metadata
            
        Raises:
            HTTPException: If URL generation fails
        """
        logger.debug(f"Generating URL for file: {file_key}, user: {username}")
        
        # Get expiration from settings
        expiration = settings.S3_PRESIGNED_URL_EXPIRATION
        
        try:
            # Generate presigned URL
            presigned_url = self.s3_service.generate_presigned_url(
                file_key, 
                expiration
            )
            
            if not presigned_url:
                logger.error(f"Failed to generate presigned URL for: {file_key}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or failed to generate URL"
                )
            
            return {
                "url": presigned_url,
                "file_key": file_key,
                "expires_in": expiration,
                "message": "Presigned URL generated successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating URL for file {file_key}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate file URL"
            )

# Create instance for dependency injection
upload_service = UploadService()
