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
        if mfa_enabled == "true":
            mfa_id = self.mfa_service.create_mfa_entry()
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


    
    def update_user(self,user_id:int,**kwargs):
        return self.user_repo.update(user_id,**kwargs)
    
    def delete_user(self,user_id:int):
        return self.user_repo.delete(user_id)


        


