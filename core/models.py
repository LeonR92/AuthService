from sqlalchemy import Column, DateTime, func

class TimestampMixin:
    """Mixin to add timestamp fields to models."""
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
