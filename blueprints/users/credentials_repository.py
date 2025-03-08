from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from blueprints.users.models import Credentials, User


class CredentialsRepository:
    """Repository for User and Credentials models with Read/Write Separation."""

    def __init__(self, write_db_session: Session, read_db_session: Session):
        """
        Initializes the repository with separate read and write sessions.
        
        :param write_db_session: Session used for write operations
        :param read_db_session: Session used for read operations
        """
        self.write_db_session = write_db_session
        self.read_db_session = read_db_session

    def get_credentials_by_id(self, user_id: int) -> Optional[User]:
        """Fetch a user by ID (Read-Only)."""
        return self.read_db_session.query(User).filter(User.id == user_id).first()

    def create_credentials(self, **kwargs) -> int:
        """Create new credentials (Write Operation)."""
        credentials = Credentials(**kwargs)
        self.write_db_session.add(credentials)
        self.write_db_session.flush()
        return credentials.id

    def delete_credentials(self, user_id: int) -> Optional[User]:
        """Delete a user by ID (Write Operation)."""
        user = self.get_credentials_by_id(user_id)
        if user:
            self.write_db_session.delete(user)
        return user
    
    def soft_delete_credentials(self, user_id: int) -> Optional[User]:
        """Soft delete a user by ID (Write Operation)."""
        user = self.get_credentials_by_id(user_id)
        if user:
            user.deleted_at = datetime.now()
        return user

    def update_credentials(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields (Write Operation)."""
        user = self.get_credentials_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            return user
        return None
