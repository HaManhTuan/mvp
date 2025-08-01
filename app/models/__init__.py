"""
Import all models here to ensure they are registered with SQLAlchemy metadata.
This is used by Alembic for auto-generating migrations.
"""

# Import all models
from app.models.base_model import BaseModel
from app.models.user import User

# Add any other models imports here
# from app.models.product import Product
# from app.models.order import Order

__all__ = ["BaseModel", "User"]