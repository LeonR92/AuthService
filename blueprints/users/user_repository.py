"""
User Repository Module.

This module provides data access operations for User entities,
implementing read/write separation for security and performance.

"""

from typing import List, Optional
from blueprints.users.models import Credentials, User
from sqlalchemy.orm import Session


class UserRepository:
    """
    Repository for User model with Read/Write Separation.
    
    This class provides data access methods for managing User records
    with separate database sessions for read and write operations,
    ensuring proper separation of concerns.
    """
    
    def __init__(self, read_db_session:Session ,write_db_session:Session):
        """
        Initialize the repository with separate read and write sessions.
        
        :param read_db_session: SQLAlchemy session for read operations
        :type read_db_session: Session
        :param write_db_session: SQLAlchemy session for write operations
        :type write_db_session: Session
        :return: None
        """
        self.read_db_session = read_db_session
        self.write_db_session = write_db_session

    def get_user_by_id(self, user_id: int) -> User:
        """
        Fetch a user by ID (Read-Only).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: User object if found, None otherwise
        :rtype: Optional[User]

        Usage example:
        user = self.get_user_by_id(user_id)
        """
        return self.read_db_session.query(User).filter(User.id == user_id).first()
    
    def get_userid_by_email(self,email:str) -> int:
        """
        Fetch user ID by email address (Read-Only).
        
        :param email: User's email address
        :type email: str
        :return: User ID if found, None otherwise
        :rtype: Optional[int]

        Usage example:
        user_id = self.user_repo.get_userid_by_email(email=email)
        """
        return (self.read_db_session.query(User.id)
                .join(Credentials, Credentials.id == User.credentials_id)
                .filter(Credentials.email == email)
                .first())
    
    def get_username_by_userid(self, user_id: int) -> Optional[tuple[str, str]]:
        """
        Fetch first and last name by user ID (Read-Only).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: Tuple containing (first_name, last_name) if found, None otherwise
        :rtype: Optional[Tuple[str, str]]

        Usage example:
        full_name = self.user_repo.get_username_by_userid(user_id=user_id)
        """
        return (self.read_db_session.query(User.first_name, User.last_name)
                .filter(User.id == user_id)
                .first())
    

    
    def get_full_user_details_by_id(self, user_id: int) -> User:
        """
        Fetch complete user details including credentials by ID (Read-Only).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: Tuple containing (User, Credentials) if found, None otherwise
        :rtype: Optional[Tuple[User, Credentials]]

        Usage example:
        user_details = self.user_repo.get_full_user_details_by_id(user_id)
        """
        return (self.read_db_session.query(User,Credentials)
                .join(Credentials,User.credentials_id == Credentials.id)
                .filter(User.id == user_id)
                .first())
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Fetch a user by email address (Read-Only).
        
        :param email: User's email address
        :type email: str
        :return: User object if found, None otherwise
        :rtype: Optional[User]

        Usage example:
        if self.user_repo.get_user_by_email(email)
        """
        return (self.read_db_session.query(User)
                .join(Credentials,User.credentials_id == Credentials.id)
                .filter(Credentials.email == email).first())
    
    def create_user(self,**kwargs) -> int:
        """
        Create a new user with the provided attributes (Write Operation).
        
        :param kwargs: User attributes as keyword arguments
        :type kwargs: Any
        :return: ID of the newly created user
        :rtype: int

        Usage example:
        user_id = self.user_repo.create_user(
            first_name=first_name,
            last_name=last_name,
            country=country,
            dob=dob,
            credentials_id = cred_id,
            mfa_id = mfa_id
        )
        """
        new_user = User(**kwargs)
        self.write_db_session.add(new_user)
        self.write_db_session.commit()
        self.write_db_session.refresh(new_user)
        return new_user.id

        
    def delete(self, user_id: int):
        """
        Permanently delete a user by ID (Write Operation).
        
        No soft deletion implemented due to GDPR/DSGVO compliance requirements.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: True if user was deleted, True even if user not found
        :rtype: bool

        Usage example:
        return self.user_repo.delete(user_id)
        """
        user = self.get_user_by_id(user_id)
        if user:
            self.write_db_session.delete(user)
            self.write_db_session.commit()
        return True

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update user attributes by ID (Write Operation).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :param kwargs: User attributes to update as keyword arguments
        :type kwargs: Any
        :return: Updated user object if found, None otherwise
        :rtype: Optional[User]

        Usage example:
        self.user_repo.update(user_id=user_id, mfa_id=mfa_id) 
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None  

        for key, value in kwargs.items():
            setattr(user, key, value)
            
        user = self.write_db_session.merge(user)
        self.write_db_session.commit()
        self.write_db_session.refresh(user) 
        
        return user
