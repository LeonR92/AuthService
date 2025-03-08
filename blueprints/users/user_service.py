from core.database import get_read_db,get_write_db
from blueprints.users.user_repository import UserRepository

class UserService:
    """Service layer for User operations."""

    def register_user(self, email: str, name: str):
        """Registers a new user."""
        with get_write_db() as db:  
            user_repo = UserRepository(db)
            return user_repo.create(email=email, name=name)

    def get_user(self, user_id: int):
        """Fetch a user by ID."""
        with get_read_db() as db:
            user_repo = UserRepository(db)
            return user_repo.get_by_id(user_id)

    def create_user(self):
        with get_write_db() as db:
            user_repo = UserRepository(db)
        # form validator
        # create credentials
        # create user
        pass

    def authentication():
        # auth service
        pass

    def reset_password():
        pass