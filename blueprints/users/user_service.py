from datetime import datetime
from typing import Optional
from blueprints.users.user_repository import UserRepository
from core.utils import is_valid_string_value

class UserService:
    def __init__(self,user_repo:UserRepository) -> None:
        self.user_repo = user_repo
    
    def get_user_by_id(self, user_id: int):
        """Fetch a user by ID and raise an error if not found."""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user
    
    
    def create_user(self, first_name:str, last_name:str, email:str, country:Optional[str], dob:Optional[datetime]) -> int:
        """Creates a new user after validating mandatory fields."""
        if not is_valid_string_value(first_name) or not is_valid_string_value(last_name) or not is_valid_string_value(email):
            raise ValueError("First and last name cannot be empty")
        if self.user_repo.get_user_by_email(email):
            raise ValueError("Email is already registered")
        return self.user_repo.create_user(first_name,last_name,country,dob)
    
    def update_user(self,user_id:int,**kwargs):
        return self.user_repo.update(user_id,**kwargs)
    
    def delete_user(self,user_id:int):
        return self.user_repo.delete(user_id)


        


