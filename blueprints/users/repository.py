from BookStore.blueprints.users.models import User


class UserRepository:
    """Repository for User model."""
    
    def __init__(self, db_session):
        self.db_session = db_session

    def get_by_id(self, user_id: int):
        """Fetch a user by ID."""
        return self.db_session.query(User).filter(User.id == user_id).first()

    def get_all(self):
        """Fetch all users."""
        return self.db_session.query(User).all()

    def create(self, **kwargs):
        """Create a new user."""
        user = User(**kwargs)
        self.db_session.add(user)
        return user  # `get_db()` will commit automatically

    def delete(self, user_id: int):
        """Delete a user by ID."""
        user = self.get_by_id(user_id)
        if user:
            self.db_session.delete(user)
        return user
