from datetime import datetime
from typing import Optional
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_repository import UserRepository
from blueprints.users.crendentials_service import CredentialsService
from core.utils import is_valid_string_value

class UserService:
    def __init__(self,user_repo:UserRepository, cred_service: CredentialsService, mfa_service:MFAservice) -> None:
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
        """Fetches user ID based on email. Returns None if not found."""
        
        if not email:
            raise ValueError("Email is required")
        
        user_id = self.user_repo.get_userid_by_email(email=email)

        return user_id[0] if user_id else None 
    
    def get_username_by_userid(self, user_id: int) -> str:
        """Fetches the user's full name by user ID."""
        if not user_id:
            raise ValueError("User ID must be provided.")

        full_name = self.user_repo.get_username_by_userid(user_id=user_id)
        
        if not full_name:
            raise ValueError(f"User with ID {user_id} not found.")

        first_name, last_name = full_name
        if not first_name or not last_name:
            raise ValueError(f"Incomplete name data for user ID {user_id}.")

        return f"{first_name} {last_name}"


    def get_all_users(self):
        """Fetch a user by ID and raise an error if not found."""
        users = self.user_repo.get_all_users()
        if not users:
            raise ValueError("no user found")
        return users

    def get_full_user_details_by_id(self, user_id: int):
        """Fetch a user by ID and raise an error if not found."""
        user_details = self.user_repo.get_full_user_details_by_id(user_id)
        if not user_details:
            raise ValueError(f"User with ID {user_id} not found")
        return user_details
    
    
    def create_user(self, first_name:str, last_name:str, email:str, password:str, mfa_enabled:str,country:Optional[str], dob:Optional[datetime]) -> int:
        """Creates a new user after validating mandatory fields."""
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
        """Activates MFA for the user by creating an MFA entry if not present."""
        
        mfa_details = self.mfa_service.get_mfa_details_via_user_id(user_id=user_id)
        
        if not mfa_details or not mfa_details.id: 
            mfa_id = self.mfa_service.create_mfa_entry()  
            self.user_repo.update(user_id=user_id, mfa_id=mfa_id)  

    
    def update_user(self,user_id:int,**kwargs):
        return self.user_repo.update(user_id,**kwargs)
    
    def delete_user(self,user_id:int):
        return self.user_repo.delete(user_id)


        


