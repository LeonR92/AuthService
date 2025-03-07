from typing import Any, Dict, Optional
from blueprints.users.models import Credentials, User


class UserRepository:
    """Repository for User model."""
    
    def __init__(self, db_session):
        self.db_session = db_session

    def get_by_id(self, user_id: int):
        """Fetch a user by ID."""
        return self.db_session.query(User).filter(User.id == user_id).first()
    
 
    def create_user(crendential_id:int):
        pass

        
    def delete(self, user_id: int):
        """Delete a user by ID."""
        user = self.get_by_id(user_id)
        if user:
            self.db_session.delete(user)
        return user

    def update(self, user_id: int, **kwargs):
        user = self.get_by_id(user_id)
        if user:
            # Update attributes one by one
            for key, value in kwargs.items():
                setattr(user, key, value)
            # No need to call db_session.add() - the object is already tracked
            return user
        return None