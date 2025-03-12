import random
import string
from typing import List, Optional
from blueprints.users.credentials_repository import CredentialsRepository
import bcrypt
from blueprints.users.models import Credentials


class CredentialsService:
    """Service layer for User operations."""

    def __init__(self, cred_repo: CredentialsRepository):
        """Initialize with a repository instance."""
        self.cred_repo = cred_repo

    def validate_and_hash_pw(self,password:str, password_length:int = 8) -> str:
        if not password or password.strip() == "":
            raise ValueError("Password cannot be empty")
        if len(password) < password_length:
            raise ValueError(f"Password cannot be shorter than {password_length}")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed_password.decode("utf-8")

    def get_credentials_via_email(self,email:str) -> Optional[Credentials]:
        credentials =  self.cred_repo.get_credentials_by_email(email=email)

        if not credentials:
            raise Exception ("credentials not found")
        return credentials
    
    def get_email_by_userid(self,user_id:int) -> Optional[str]:
        if not user_id:
            ValueError("User ID cannot be empty")
        email = self.cred_repo.get_email_by_userid(user_id=user_id)
        if not email:
            raise ValueError("Email not found")
        return email
    
    def get_id_via_email(self,email:str) -> Optional[int]:
        cred =  self.cred_repo.get_credentials_by_email(email=email)
        if not cred:
            raise Exception ("credentials not found")
        return cred.id
    
    def generate_random_password(self,length:int = 12) -> str:
        """Generate a random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        random_password = ''.join(random.choice(characters) for _ in range(length))
        return random_password
    
    def reset_password(self,email:str) -> str:
        credentials = self.get_credentials_via_email(email=email)
        if not credentials:
            raise ValueError(f"No credentials found for email: {email}")
        new_password= self.generate_random_password()
        new_hashed_password = self.validate_and_hash_pw(new_password)
        self.cred_repo.update_credentials(cred_id=credentials.id, password=new_hashed_password)
        return new_password



    def create_credentials(self, email: str, password: str) -> int:
        """Registers a new user."""
        if not email or not password:
            raise ValueError("Email or Password cannot be empty")
        hashed_password = self.validate_and_hash_pw(password)
        cred_id = self.cred_repo.create_credentials(email=email, password=hashed_password)
        if not cred_id:
            raise RuntimeError("Cant create credentials")
        return cred_id

    def get_all_credentials(self) -> List[Credentials]:
        """Fetch all credentials."""
        return self.cred_repo.get_all_credentials()

    def create_user(self, data: dict):
        """Creates a new user with basic validation."""
        if not data or not all(k in {"first_name", "last_name", "email"} for k in data):
            raise ValueError("Invalid or empty data")
        return self.cred_repo.create_credentials(**data)
    



    def change_password(self, user_id: int, new_password: str, confirm_new_password: str) -> None:
        """Changes the password for a given user, ensuring validation and secure hashing."""
        cred = self.cred_repo.get_credentials_by_id(user_id=user_id)
        if cred is None:
            raise ValueError("User not found")

        if new_password != confirm_new_password:
            raise ValueError("New passwords do not match")

        new_hashed_password = self.validate_and_hash_pw(new_password)
        self.cred_repo.update_credentials(cred_id=cred.id, password=new_hashed_password)


        
    
    def update(self, cred_id: int, password: Optional[str] = None):
        """Updates a user's credentials. TO BE REMOVED !!!!""" 
        if not cred_id:
            raise ValueError("Credential ID is required for update.")

        update_fields = {}
        if password:
            update_fields["password"] = password

        return self.cred_repo.update_credentials(cred_id, **update_fields)