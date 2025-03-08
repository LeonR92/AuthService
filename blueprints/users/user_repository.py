from blueprints.users.models import User
from sqlalchemy.orm import Session


class UserRepository:
    """Repository for User model."""
    
    def __init__(self, read_db_session:Session ,write_db_session:Session):
        self.read_db_session = read_db_session
        self.write_db_session = write_db_session

    def get_by_id(self, user_id: int):
        """Fetch a user by ID."""
        return self.read_db_session.query(User).filter(User.id == user_id).first()
 
    def create_user(self,**kwargs) -> int:
        new_user = User(**kwargs)
        self.write_db_session.add(new_user)
        self.write_db_session.commit()
        self.write_db_session.refresh(new_user)
        return new_user.id

        
    def delete(self, user_id: int):
        """Delete a user by ID. No soft deletion due to DSGVO"""
        user = self.get_by_id(user_id)
        if user:
            self.write_db_session.delete(user)
        return user

    def update(self, user_id: int, **kwargs) -> User | None:
        """Updates user attributes and returns the updated user."""
        user = self.get_by_id(user_id)
        if not user:
            return None  

        for key, value in kwargs.items():
            setattr(user, key, value)

        self.write_db_session.commit()
        self.write_db_session.refresh(user) 
        
        return user
