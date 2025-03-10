from datetime import datetime
from typing import Optional
from blueprints.users.user_repository import UserRepository
from blueprints.users.crendentials_service import CredentialsService
from core.utils import is_valid_string_value

class UserService:
    def __init__(self,user_repo:UserRepository, cred_service: CredentialsService) -> None:
        self.user_repo = user_repo
        self.cred_service = cred_service
    
    def get_user_by_id(self, user_id: int):
        """Fetch a user by ID and raise an error if not found."""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user
    
    
    def create_user(self, first_name:str, last_name:str, email:str, password:str, mfa_enabled:str,country:Optional[str], dob:Optional[datetime]) -> int:
        """Creates a new user after validating mandatory fields."""
        if not is_valid_string_value(first_name) or not is_valid_string_value(last_name) or not is_valid_string_value(email):
            raise ValueError("First and last name cannot be empty")
        if self.user_repo.get_user_by_email(email):
            raise ValueError("Email is already registered")
        if mfa_enabled == "true":
            pass
        dob = None if not dob or dob.strip() == "" else datetime.strptime(dob, "%Y-%m-%d")
        cred_id = self.cred_service.create_credentials(email = email,password=password)
        return self.user_repo.create_user(
            first_name=first_name,
            last_name=last_name,
            country=country,
            dob=dob,
            credentials_id = cred_id
        )
    
    def update_user(self,user_id:int,**kwargs):
        return self.user_repo.update(user_id,**kwargs)
    
    def delete_user(self,user_id:int):
        return self.user_repo.delete(user_id)


        


