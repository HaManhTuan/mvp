from typing import TypeVar, Generic, Type, List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.logger import get_logger, get_request_id
from app.repositories.base_repository import BaseRepository
from app.models.base_model import BaseModel

# Generic types
ModelType = TypeVar("ModelType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[ModelType, RepositoryType]):
    """
    Base service class with business logic
    
    This class serves as a service layer between controllers and repositories,
    containing business logic and validation
    """
    
    def __init__(self, repository: Type[RepositoryType]):
        """
        Initialize the service with a repository
        
        Args:
            repository: The repository class to use for data access
        """
        self.repository = repository
        self.logger = get_logger("service")
      
    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """
        Get a record by id
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Record object or None if not found
        """
        self.logger.debug(f"Getting {self.repository.model.__name__} with id: {id}")
        return await self.repository.get_by_id(db, id=id)
    
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
        self.logger.debug(f"Getting list of {self.repository.model.__name__}")
        return await self.repository.get_all(
            db, skip=skip, limit=limit, filter_by=filter_by, order_by=order_by
        )
    
    async def count(self, db: AsyncSession, filter_by: Dict[str, Any] = None) -> int:
        """
        Count records with optional filtering
        
        Args:
            db: Database session
            filter_by: Dictionary of filter conditions {column_name: value}
            
        Returns:
            Count of records
        """
        return await self.repository.count(db, filter_by=filter_by)
    
    async def create(self, db: AsyncSession, *, obj_in: Union[Dict[str, Any], ModelType]) -> ModelType:
        """
        Create a new record
        
        Args:
            db: Database session
            obj_in: Input data, can be a dict or model instance
              Returns:
            Created record object
        """
        self.logger.info(f"Creating new {self.repository.model.__name__}")
        return await self.repository.create(db, obj_in=obj_in)
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        id: str,
        obj_in: Union[Dict[str, Any], ModelType]
    ) -> Optional[ModelType]:
        """
        Update a record
        
        Args:
            db: Database session
            id: Record ID
            obj_in: New data, can be a dict or model instance
            
        Returns:
            Updated record object or None if not found
        """        
        
        db_obj = await self.repository.get_by_id(db, id=id)
        if db_obj:
            self.logger.info(f"Updating {self.repository.model.__name__} with id: {id}")
            return await self.repository.update(db, db_obj=db_obj, obj_in=obj_in)
        self.logger.warning(f"{self.repository.model.__name__} with id {id} not found for update")
        return None
    
    async def delete(self, db: AsyncSession, *, id: str) -> Optional[ModelType]:
        """
        Delete a record
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Deleted record object or None if not found
        """        
        
        db_obj = await self.repository.get_by_id(db, id=id)
        if db_obj:
            self.logger.info(f"Deleting {self.repository.model.__name__} with id: {id}")
            return await self.repository.delete(db, id=id)
        self.logger.warning(f"{self.repository.model.__name__} with id {id} not found for deletion")
        return None
    
    async def soft_delete(self, db: AsyncSession, *, id: str) -> Optional[ModelType]:
        """
        Soft delete a record (mark as inactive)
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Updated record object or None if not found
        """        
        
        db_obj = await self.repository.get_by_id(db, id=id)
        if db_obj:
            self.logger.info(f"Soft-deleting {self.repository.model.__name__} with id: {id}")
            return await self.repository.soft_delete(db, id=id)
        self.logger.warning(f"{self.repository.model.__name__} with id {id} not found for soft-deletion")
        return None
