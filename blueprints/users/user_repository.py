from typing import List, Optional
from blueprints.users.models import Credentials, User
from sqlalchemy.orm import Session


class UserRepository:
    """Repository for User model."""
    
    def __init__(self, read_db_session:Session ,write_db_session:Session):
        self.read_db_session = read_db_session
        self.write_db_session = write_db_session

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user by ID."""
        return self.read_db_session.query(User).filter(User.id == user_id).first()
    
    def get_userid_by_email(self,email:str) -> int:
        return (self.read_db_session.query(User.id)
                .join(Credentials, Credentials.id == User.credentials_id)
                .filter(Credentials.email == email)
                .first())
    
    def get_all_users(self) -> List[User]:
        """Fetch all users."""
        return self.read_db_session.query(User).all()
    
    def get_full_user_details_by_id(self, user_id: int) -> User:
        """Fetch a user by ID."""
        return (self.read_db_session.query(User,Credentials)
                .join(Credentials,User.credentials_id == Credentials.id)
                .filter(User.id == user_id)
                .first())
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email."""
        return (self.read_db_session.query(User)
                .join(Credentials,User.credentials_id == Credentials.id)
                .filter(Credentials.email == email).first())
    
    def create_user(self,**kwargs) -> int:
        new_user = User(**kwargs)
        self.write_db_session.add(new_user)
        self.write_db_session.commit()
        self.write_db_session.refresh(new_user)
        return new_user.id

        
    def delete(self, user_id: int):
        """Delete a user by ID. No soft deletion due to DSGVO"""
        user = self.get_user_by_id(user_id)
        if user:
            self.write_db_session.delete(user)
            self.write_db_session.commit()
        return True

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Updates user attributes and returns the updated user."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None  

        for key, value in kwargs.items():
            setattr(user, key, value)

        self.write_db_session.commit()
        self.write_db_session.refresh(user) 
        
        return user
