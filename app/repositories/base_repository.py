from typing import TypeVar, Generic, Type, List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi.encoders import jsonable_encoder
from app.utils.logger import get_logger
from app.models.base_model import BaseModel

# Generic type for database models
ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    """
    Base repository class with common database operations
    
    This class provides basic CRUD operations for any model that inherits from BaseModel
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize the repository with a model
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model
        self.logger = get_logger("repository")
    
    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """
        Get a record by id
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Record object or None if not found
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filter_by: Dict[str, Any] = None,
        order_by: List[str] = None
    ) -> List[ModelType]:
        """
        Get all records with optional filtering, sorting, and pagination
        
        Args:
            db: Database session
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            filter_by: Dictionary of filter conditions {column_name: value}
            order_by: List of columns to sort by, prefix with - for descending
            
        Returns:
            List of record objects
        """
        query = select(self.model)
        
        # Apply filters if provided
        if filter_by:
            for column, value in filter_by.items():
                if hasattr(self.model, column):
                    query = query.filter(getattr(self.model, column) == value)
        
        # Apply sorting if provided
        if order_by:
            for column in order_by:
                if column.startswith("-"):
                    # Descending order
                    query = query.order_by(getattr(self.model, column[1:]).desc())
                else:
                    # Ascending order
                    query = query.order_by(getattr(self.model, column).asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count(self, db: AsyncSession, filter_by: Dict[str, Any] = None) -> int:
        """
        Count records with optional filtering
        
        Args:
            db: Database session
            filter_by: Dictionary of filter conditions {column_name: value}
            
        Returns:
            Count of records
        """
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)
        
        # Apply filters if provided
        if filter_by:
            for column, value in filter_by.items():
                if hasattr(self.model, column):
                    query = query.filter(getattr(self.model, column) == value)
        
        result = await db.execute(query)
        return result.scalar_one()
    
    async def create(self, db: AsyncSession, *, obj_in: Union[Dict[str, Any], ModelType]) -> ModelType:
        """
        Create a new record
        
        Args:
            db: Database session
            obj_in: Input data, can be a dict or model instance
            
        Returns:
            Created record object
        """
        obj_data = obj_in
        if not isinstance(obj_in, dict):
            obj_data = jsonable_encoder(obj_in)
          
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        self.logger.debug(f"Created {self.model.__name__} with id: {db_obj.id}")
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[Dict[str, Any], ModelType]
    ) -> ModelType:
        """
        Update a record
        
        Args:
            db: Database session
            db_obj: Existing database object to update
            obj_in: New data, can be a dict or model instance
            
        Returns:
            Updated record object
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in
        
        if not isinstance(obj_in, dict):
            update_data = jsonable_encoder(obj_in)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        self.logger.debug(f"Updated {self.model.__name__} with id: {db_obj.id}")
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: str) -> ModelType:
        """
        Delete a record
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Deleted record object
        """        
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalar_one_or_none()
        if obj is not None:
            await db.delete(obj)
            await db.commit()
            self.logger.debug(f"Deleted {self.model.__name__} with id: {id}")
        return obj
    
    async def soft_delete(self, db: AsyncSession, *, id: str) -> ModelType:
        """
        Soft delete a record (mark as inactive)
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Updated record object
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalar_one_or_none()
        if obj is not None:
            obj.is_active = False
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            self.logger.debug(f"Soft deleted {self.model.__name__} with id: {id}")
        return obj
