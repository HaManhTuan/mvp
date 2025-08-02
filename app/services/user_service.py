from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import BaseService
from app.repositories.user_repository import user_repository
from app.models.user import GenderEnum, User
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("user-service")

class UserService(BaseService[User, type(user_repository)]):
    """Service for user-related operations"""
    
    def __init__(self):
        super().__init__(user_repository)
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        logger.debug(f"Looking up user by email: {email}")
        return await user_repository.get_by_email(db, email=email)
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        logger.debug(f"Looking up user by username: {username}")
        return await user_repository.get_by_username(db, username=username)

    async def create_user(self, db: AsyncSession, username: str, email: str, password: str, gender: GenderEnum, full_name: str = None, is_superuser: bool = False) -> User:
        """Create a new user"""
        logger.info(f"Creating new user with username: {username}, email: {email}")
        
        # Check if email already exists
        if await self.get_by_email(db, email=email):
            logger.warning(f"Attempt to create user with existing email: {email}")
            raise ValueError(f"User with email {email} already exists")
        
        # Check if username already exists
        if await self.get_by_username(db, username=username):
            logger.warning(f"Attempt to create user with existing username: {username}")
            raise ValueError(f"User with username {username} already exists")
        
        # Create user
        return await user_repository.create_user(
            db=db,
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_superuser=is_superuser,
            gender=gender
        )
    
    async def authenticate_user(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        logger.debug(f"Authenticating user: {username}")
        user = await self.get_by_username(db, username=username)
        
        if not user:
            logger.warning(f"Authentication failed: user not found: {username}")
            return None
        
        if not user.check_password(password):
            logger.warning(f"Authentication failed: incorrect password for user: {username}")
            return None
        
        return user

# Create instance for dependency injection
user_service = UserService()
