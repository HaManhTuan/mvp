from app.repositories.base_repository import BaseRepository
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

class UserRepository(BaseRepository[User]):
    """Repository for User model"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, username: str, email: str, password: str, full_name: str = None, is_superuser: bool = False) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_superuser=is_superuser
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

# Create instance for dependency injection
user_repository = UserRepository()
