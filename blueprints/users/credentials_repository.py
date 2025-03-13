"""
Credentials and User Repository Module.

This module provides a data access layer with read/write separation
for secure and efficient database operations on user authentication data.

"""


from datetime import datetime
from typing import Any, Optional
from sqlalchemy.orm import Session
from blueprints.users.models import Credentials, User


class CredentialsRepository:
    """
    Repository for User and Credentials models with Read/Write Separation.
    
    This class implements the repository pattern with separate database sessions
    for read and write operations, improving security and performance through
    proper separation of concerns.
    """

    def __init__(self, write_db_session: Session, read_db_session: Session):
        """
        Initialize the repository with separate read and write sessions.
        
        :param write_db_session: SQLAlchemy session for write operations
        :type write_db_session: Session
        :param read_db_session: SQLAlchemy session for read operations
        :type read_db_session: Session
        :return: None
        """
        self.write_db_session = write_db_session
        self.read_db_session = read_db_session
    


    def get_credentials_by_id(self, user_id: int) -> Optional[Credentials]:
        """
        Fetch credentials by user ID (Read-Only).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: Credentials object if found, None otherwise
        :rtype: Optional[Credentials]

        Usage example:
        user = self.get_credentials_by_id(user_id)
        """
        return self.read_db_session.query(Credentials).filter(Credentials.id == user_id).first()
    
    def get_credentials_by_email(self,email:str) -> Optional[Credentials]:
        """
        Fetch credentials by email address (Read-Only).
        
        :param email: User's email address
        :type email: str
        :return: Credentials object if found, None otherwise
        :rtype: Optional[Credentials]

        Usage example:
        credentials =  self.cred_repo.get_credentials_by_email(email=email)
        """
        return self.read_db_session.query(Credentials).filter(Credentials.email == email).first()
    
    def get_email_by_userid(self, user_id: int) -> Optional[str]:
        """
        Fetch the email address of a user by user ID (Read-Only).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: User's email address if found, None otherwise
        :rtype: Optional[str]

        Usage example:
        email = self.cred_repo.get_email_by_userid(user_id=user_id)
        """
        result = (
            self.read_db_session.query(Credentials.email)
            .join(User, User.credentials_id == Credentials.id)
            .filter(User.id == user_id)
            .first()
        )
        
        return result[0] if result else None

    def create_credentials(self, email:str, password:str) -> int:
        """
        Create new credentials (Write Operation).
        
        :param email: User's email address
        :type email: str
        :param password: User's password (should be pre-hashed)
        :type password: str
        :return: ID of the newly created credentials
        :rtype: int

        Usage example:
        cred_id = self.cred_repo.create_credentials(email=email, password=hashed_password)
        """
        credentials = Credentials(email = email, password = password)
        self.write_db_session.add(credentials)
        self.write_db_session.flush()
        return credentials.id

    def delete_credentials(self, user_id: int) -> Optional[User]:
        """
        Permanently delete credentials by ID (Write Operation).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: Deleted credentials object if found, None otherwise
        :rtype: Optional[Credentials]
        """
        user = self.get_credentials_by_id(user_id)
        if user:
            self.write_db_session.delete(user)
        return user
    
    def soft_delete_credentials(self, user_id: int) -> Optional[User]:
        """
        Soft delete credentials by ID by setting deletion timestamp (Write Operation).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: Updated credentials object if found, None otherwise
        :rtype: Optional[Credentials]
        """
        user = self.get_credentials_by_id(user_id)
        if user:
            user.deleted_at = datetime.now()
        return user

    def update_credentials(self, cred_id: int, **kwargs:Any)-> Optional[Credentials]:
        """
        Update credentials fields by ID (Write Operation).
        
        :param cred_id: Unique identifier of the credentials record
        :type cred_id: int
        :param kwargs: Arbitrary keyword arguments representing fields to update
        :type kwargs: Any
        :return: Updated credentials object if found, None otherwise
        :rtype: Optional[Credentials]

        Usage example:
        self.cred_repo.update_credentials(cred_id=credentials.id, password=new_hashed_password)
        """
        cred = self.read_db_session.query(Credentials).filter_by(id=cred_id).first()
        
        if not cred:
            return None

        cred = self.write_db_session.merge(cred)

        for key, value in kwargs.items():
            setattr(cred, key, value)

        self.write_db_session.commit()
        self.write_db_session.refresh(cred)

        return cred
