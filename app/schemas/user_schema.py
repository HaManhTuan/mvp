from typing import Optional
from pydantic import EmailStr, Field, field_validator
from datetime import datetime
from app.schemas.base_schema import BaseSchema
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class UserBase(BaseSchema):
    """Base schema for user data"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    gender: Optional[GenderEnum] = GenderEnum.other
    token_balance: int = 0
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    
    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseSchema):
    """Schema for user update"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    created_at: datetime
    updated_at: datetime

class UserInDB(UserBase):
    """Schema for user in database"""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
