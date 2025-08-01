from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.config.database import get_db
from app.services.user_service import user_service
from app.schemas.base_schema import DataResponse
from app.utils.auth import create_access_token
from app.utils.tracing import get_trace_logger
from app.config.settings import settings

router = APIRouter()
logger = get_trace_logger("auth-controller")

@router.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # The logger already has the request ID from our middleware
    auth_logger = get_trace_logger("auth-controller")
    
    # Authenticate user
    user = await user_service.authenticate_user(
        db=db, 
        username=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        auth_logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        auth_logger.warning(f"Login attempt for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    auth_logger.info(f"User {form_data.username} logged in successfully")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register")
async def register(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    """
    # The logger already has the request ID from our middleware
    auth_logger = get_trace_logger("auth-controller")
    
    try:
        # Create user
        user = await user_service.create_user(
            db=db,
            username=form_data.username,
            email=f"{form_data.username}@example.com",  # Placeholder, not ideal
            password=form_data.password
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, 
            expires_delta=access_token_expires
        )
        
        auth_logger.info(f"User {form_data.username} registered successfully")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except ValueError as e:
        auth_logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        auth_logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
