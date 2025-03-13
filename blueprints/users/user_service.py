"""
User Service Module.

This module provides business logic for user management operations,
coordinating between repositories and related services for a complete
user management solution.

"""

from datetime import datetime
from typing import Optional
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_repository import UserRepository
from blueprints.users.crendentials_service import CredentialsService
from core.utils import is_valid_string_value

class UserService:
    """
    Service layer for User management operations.
    
    This class implements business logic for user operations, coordinating
    between the user repository, credentials service, and MFA service to provide
    comprehensive user management functionality.
    """
    def __init__(self,user_repo:UserRepository, cred_service: CredentialsService, mfa_service:MFAservice) -> None:
        """
        Initialize with repository and service dependencies.
        
        :param user_repo: Repository providing user data access operations
        :type user_repo: UserRepository
        :param cred_service: Service for credential operations
        :type cred_service: CredentialsService
        :param mfa_service: Service for MFA operations
        :type mfa_service: MFAService
        :return: None
        """
        self.user_repo = user_repo
        self.cred_service = cred_service
        self.mfa_service = mfa_service
    
    def get_user_by_id(self, user_id: int):
        """Fetch a user by ID and raise an error if not found."""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user
    
    def get_userid_by_email(self, email: str) -> Optional[int]:
        """
        Fetch a user by ID with error handling.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: User object
        :rtype: User
        :raises ValueError: If user not found

        Usage example:
        user_id = user_service.get_userid_by_email(email=email)
        """
        
        if not email:
            raise ValueError("Email is required")
        
        user_id = self.user_repo.get_userid_by_email(email=email)

        return user_id[0] if user_id else None 
    
    def get_username_by_userid(self, user_id: int) -> str:
        """
        Fetch user ID based on email address.
        
        :param email: User's email address
        :type email: str
        :return: User ID if found, None otherwise
        :rtype: Optional[int]
        :raises ValueError: If email is empty

        Usage example:
        username = self.user_service.get_username_by_userid(user_id=user_id)
        """
        if not user_id:
            raise ValueError("User ID must be provided.")

        full_name = self.user_repo.get_username_by_userid(user_id=user_id)
        
        if not full_name:
            raise ValueError(f"User with ID {user_id} not found.")

        first_name, last_name = full_name
        if not first_name or not last_name:
            raise ValueError(f"Incomplete name data for user ID {user_id}.")

        return f"{first_name} {last_name}"




    def get_full_user_details_by_id(self, user_id: int):
        """
        Fetch complete user details including credentials by ID.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: Tuple containing user and credentials objects
        :rtype: Tuple[User, Credentials]
        :raises ValueError: If user not found
        """
        user_details = self.user_repo.get_full_user_details_by_id(user_id)
        if not user_details:
            raise ValueError(f"User with ID {user_id} not found")
        return user_details
    
    
    def create_user(self, first_name:str, last_name:str, email:str, password:str, mfa_enabled:str,country:Optional[str], dob:Optional[datetime]) -> int:
        """
        Create a new user with complete validation.
        
        :param first_name: User's first name
        :type first_name: str
        :param last_name: User's last name
        :type last_name: str
        :param email: User's email address
        :type email: str
        :param password: User's plain text password (will be hashed)
        :type password: str
        :param mfa_enabled: String indicating whether MFA should be enabled ("true"/"false")
        :type mfa_enabled: str
        :param country: Optional country code
        :type country: Optional[str]
        :param dob: Optional date of birth in YYYY-MM-DD format
        :type dob: Optional[str]
        :return: ID of the newly created user
        :rtype: int
        :raises ValueError: If required fields are empty or invalid
        :raises RuntimeError: If user creation fails

        Usage example:
        user_service.create_user(**data)
        """
        if not is_valid_string_value(first_name) or not is_valid_string_value(last_name) or not is_valid_string_value(email):
            raise ValueError("First and last name cannot be empty")
        if self.user_repo.get_user_by_email(email):
            raise ValueError("Email is already registered")
        
        dob = None if not dob or dob.strip() == "" else datetime.strptime(dob, "%Y-%m-%d")
        cred_id = self.cred_service.create_credentials(email = email,password=password)
        mfa_enabled = mfa_enabled.lower() == "true"
        mfa_id = self.mfa_service.create_mfa_entry() if mfa_enabled else None
        user_id = self.user_repo.create_user(
            first_name=first_name,
            last_name=last_name,
            country=country,
            dob=dob,
            credentials_id = cred_id,
            mfa_id = mfa_id
        )
        if not user_id:
            raise RuntimeError("Error creating user")
        return user_id

    def activate_mfa(self, user_id: int) -> None:
        """
        Activate Multi-Factor Authentication for a user.
        
        Creates a new MFA entry if not already present and associates it with the user.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: None

        Usage example:
        user_service.activate_mfa(user_id)
        """
        
        mfa_details = self.mfa_service.get_mfa_details_via_user_id(user_id=user_id)
        
        if not mfa_details or not mfa_details.id: 
            mfa_id = self.mfa_service.create_mfa_entry()  
            self.user_repo.update(user_id=user_id, mfa_id=mfa_id)  
