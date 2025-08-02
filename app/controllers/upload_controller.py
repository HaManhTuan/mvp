from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional

from app.services.upload_service import upload_service
from app.schemas.upload_schema import ImageUploadResponse
from app.schemas.base_schema import DataResponse
from app.utils.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("upload-controller")

@router.post("/image", response_model=DataResponse[ImageUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload an image file to S3 and return URL
    
    Args:
        file: Image file to upload (max 10MB)
        current_user: Current authenticated user
        
    Returns:
        Image URL and file information (expiration time configured via environment)
        
    Raises:
        HTTPException: If upload fails or file is invalid
    """
    logger.info(f"Image upload request from user: {current_user.username}, file: {file.filename}")
    
    try:
        # Process upload using service layer
        upload_response = await upload_service.process_file_upload(
            file=file,
            username=current_user.username
        )
        
        return DataResponse(
            data=upload_response,
            message="Image uploaded successfully"
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions from service layer
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload controller: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/url/{file_key:path}")
async def get_image_url(
    file_key: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a new presigned URL for an existing file
    
    Args:
        file_key: S3 file key/path
        current_user: Current authenticated user
        
    Returns:
        New presigned URL (expiration time configured via environment)
    """
    logger.debug(f"URL generation request from user: {current_user.username}, file: {file_key}")
    
    try:
        # Generate URL using service layer
        url_response = await upload_service.generate_file_url(
            file_key=file_key,
            username=current_user.username
        )
        
        return JSONResponse(content=url_response)
        
    except HTTPException:
        # Re-raise HTTPExceptions from service layer
        raise
    except Exception as e:
        logger.error(f"Unexpected error in URL generation controller: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )