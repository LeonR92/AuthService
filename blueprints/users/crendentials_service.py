from typing import List
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
        if len(password) <= password_length:
            raise ValueError(f"Password cannot be shorther than {password_length}")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed_password.decode("utf-8")
                        

    def create_credentials(self, email: str, password: str) -> None:
        """Registers a new user."""
        if not email or not password:
            raise ValueError("Email or Password cannot be empty")
        hashed_password = self.validate_and_hash_pw(password)

        return self.cred_repo.create_credentials(email=email, password=hashed_password)

    def get_all_credentials(self) -> List[Credentials]:
        """Fetch all credentials."""
        return self.cred_repo.get_all_credentials()

    def create_user(self, data: dict):
        """Creates a new user with basic validation."""
        if not data or not all(k in {"first_name", "last_name", "email"} for k in data):
            raise ValueError("Invalid or empty data")
        return self.cred_repo.create_credentials(**data)
