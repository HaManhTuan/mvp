from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declared_attr
from app.config.database import Base

class BaseModel(Base):
    """Base model for all database models"""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        """Generate __tablename__ automatically from class name"""
        return cls.__name__.lower() + 's'
    
    # Common columns for all models
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    @classmethod
    def from_dict(cls, data):
        """Create model instance from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__table__.columns.keys()})
    
    def __repr__(self):
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={self.id})>"
