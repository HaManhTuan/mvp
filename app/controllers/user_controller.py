from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import timedelta

from app.config.database import get_db
from app.services.user_service import user_service
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.schemas.base_schema import DataResponse, ListResponse
from app.utils.auth import create_access_token, get_current_user, get_current_active_user
from app.utils.logger import get_logger
from app.config.settings import settings

router = APIRouter()
logger = get_logger("user-controller")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/", response_model=DataResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user
    """
    try:
        user = await user_service.create_user(
            db=db,
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
            gender=user_in.gender,
            full_name=user_in.full_name
        )
        return DataResponse(data=user)
    except ValueError as e:
        logger.warning(f"User creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/", response_model=ListResponse[UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all users (requires authentication)
    """
    users = await user_service.get_all(db, skip=skip, limit=limit)
    total = await user_service.count(db)
    return ListResponse(
        data=users,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/me", response_model=DataResponse[UserResponse])
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return DataResponse(data=current_user)

@router.get("/{user_id}", response_model=DataResponse[UserResponse])
async def get_user(
    user_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get user by ID (requires authentication)
    """
    user = await user_service.get_by_id(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return DataResponse(data=user)

@router.put("/{user_id}", response_model=DataResponse[UserResponse])
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update user information (requires authentication)
    """
    # Check if user exists
    user = await user_service.get_by_id(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions (only self or superuser)
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update user
    updated_user = await user_service.update(db, id=user_id, obj_in=user_in.dict(exclude_unset=True))
    return DataResponse(data=updated_user)

@router.delete("/{user_id}", response_model=DataResponse)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete user (requires superuser)
    """
    # Check if user exists
    user = await user_service.get_by_id(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions (only superuser)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete user
    await user_service.delete(db, id=user_id)
    return DataResponse(message=f"User {user_id} deleted successfully")
