"""
Multi-Factor Authentication Repository Module.

This module provides data access operations for MFA functionality,
implementing read/write separation for secure authentication operations.

"""

from typing import Optional
from sqlalchemy.orm import Session

from blueprints.users.models import MFA, Credentials, User

class MFARepository():
    """
    Repository for Multi-Factor Authentication operations with Read/Write Separation.
    
    This class provides data access methods for managing Multi-Factor Authentication (MFA)
    records with proper separation between read and write database operations
    for enhanced security and performance.
    """

    def __init__(self,write_db_session:Session, read_db_session:Session) -> None:
        """
        Initialize the repository with separate read and write sessions.
        
        :param write_db_session: SQLAlchemy session for write operations
        :type write_db_session: Session
        :param read_db_session: SQLAlchemy session for read operations
        :type read_db_session: Session
        :return: None
        self.write_db_session = write_db_session
        self.read_db_session = read_db_session
        """
        self.write_db_session = write_db_session
        self.read_db_session = read_db_session


    def get_mfa_details_by_user_id(self, user_id:int) -> Optional[MFA]:
        """
        Fetch MFA details by user ID (Read-Only).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: MFA object if found, None otherwise
        :rtype: Optional[MFA]
        Usage example:
        mfa = self.get_mfa_details_by_user_id(user_id)
        """
        return self.read_db_session.query(MFA).join(User,User.mfa_id == MFA.id).filter(User.id == user_id).first()
    

    
    def get_mfa_details_via_email(self, email: str):
        """
        Fetch user details by email with MFA association (Read-Only).
        
        :param email: User's email address
        :type email: str
        :return: User object if found, None otherwise
        :rtype: Optional[User]

        Usage example:
        mfa_details = self.mfa_repo.get_mfa_details_via_email(email=email)
        """
        return (
            self.read_db_session.query(User) 
            .join(Credentials, User.credentials_id == Credentials.id)
            .join(MFA, User.mfa_id == MFA.id)
            .filter(Credentials.email == email)
            .first()
        )
    def get_mfa_details(self, mfa_id:int) -> Optional[MFA]:
        """
        Fetch MFA details by MFA ID (Read-Only).
        
        :param mfa_id: Unique identifier of the MFA record
        :type mfa_id: int
        :return: MFA object if found, None otherwise
        :rtype: Optional[MFA]

        Usage example:
        mfa = self.get_mfa_details(mfa_id)
        """
        return self.read_db_session.query(MFA).filter(MFA.id == mfa_id).first()
    
    def create(self,totp_secret:str) -> int:
        """
        Create new MFA record with TOTP secret (Write Operation).
        
        :param totp_secret: Time-based One-Time Password secret key
        :type totp_secret: str
        :return: ID of the newly created MFA record
        :rtype: int

        Usage example:
        mfa_id = self.mfa_repo.create(totp_secret=totp_secret)
        """
        mfa = MFA(totp_secret = totp_secret)
        self.write_db_session.add(mfa)
        self.write_db_session.commit()
        self.write_db_session.flush()
        return mfa.id
    
    def delete(self,mfa_id:int)->None:
        """
        Delete MFA record by ID (Write Operation).
        
        :param mfa_id: Unique identifier of the MFA record
        :type mfa_id: int
        :return: None

        Usage example:
        self.mfa_repo.delete(mfa_id=mfa_details.id)
        """
        mfa = self.get_mfa_details(mfa_id)
        if mfa:
            mfa = self.write_db_session.merge(mfa)
            self.write_db_session.delete(mfa)
            self.write_db_session.commit()
    
    def update_mfa_secret(self, user_id: int, totp_secret: str) -> Optional[MFA]:
        """
        Update the TOTP secret for a user's MFA record (Write Operation).
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :param totp_secret: New Time-based One-Time Password secret key
        :type totp_secret: str
        :return: Updated MFA object if found, None otherwise
        :rtype: Optional[MFA]

        Usage example:
        updated_mfa = self.mfa_repo.update_mfa_secret(user_id=user_id, otp_secret=new_totp_secret)
        """
        mfa = self.get_mfa_details_by_user_id(user_id)
        if not mfa:
            return None

        mfa.totp_secret = totp_secret
        self.write_db_session.commit()
        self.write_db_session.refresh(mfa)
        
        return mfa
