from sqlalchemy import Column, String, Boolean, Date, Integer, Enum
from app.models.base_model import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class User(BaseModel):
    """User model for authentication"""
    
    # User information
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=False, default=GenderEnum.other)
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    token_balance = Column(Integer, default=0, nullable=False)
    profile_picture = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    def __init__(self, username, email, password, full_name=None, is_superuser=False, gender=None, token_balance=0):
        """Initialize a new user"""
        self.username = username
        self.email = email
        self.full_name = full_name
        self.gender = gender
        self.token_balance = token_balance
        self.set_password(password)
        self.is_superuser = is_superuser
    
    def set_password(self, password):
        """Set password hash"""
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against stored hash"""
        return check_password_hash(self.hashed_password, password)
    
    def __repr__(self):
        """String representation"""
        return f"<User(id={self.id}, username={self.username})>"
