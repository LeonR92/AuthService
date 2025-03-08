from blueprints.users.credentials_repository import CredentialsRepository

class CredentialsService:
    """Service layer for User operations."""

    def __init__(self, cred_repo: CredentialsRepository):
        """Initialize with a repository instance."""
        self.cred_repo = cred_repo

    def register_user(self, email: str, name: str):
        """Registers a new user."""
        return self.cred_repo.create_credentials(email=email, name=name)

    def get_user(self, user_id: int):
        """Fetch a user by ID."""
        return self.cred_repo.get_by_id(user_id)

    def create_user(self, data: dict):
        """Creates a new user with basic validation."""
        if not data or not all(k in {"first_name", "last_name", "email"} for k in data):
            raise ValueError("Invalid or empty data")
        return self.cred_repo.create_credentials(**data)
