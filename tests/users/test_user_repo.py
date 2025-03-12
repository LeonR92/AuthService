import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from blueprints.users.models import User
from blueprints.users.user_repository import UserRepository


@pytest.fixture
def mock_db_sessions():
    """Fixture for mocking SQLAlchemy sessions."""
    write_session = MagicMock(spec=Session)
    read_session = MagicMock(spec=Session)
    return write_session, read_session

@pytest.fixture
def user_repo(mock_db_sessions):
    """Fixture to initialize UserRepository with mock sessions."""
    write_session, read_session = mock_db_sessions
    return UserRepository(read_db_session=read_session, write_db_session=write_session)

@pytest.fixture
def sample_user():
    """Fixture to provide a sample User object."""
    return User(id=1, first_name="John", last_name="Doe")

def test_get_user_by_id_valid(user_repo, mock_db_sessions, sample_user):
    """Test retrieving a user by ID."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_user

    result = user_repo.get_user_by_id(user_id=1)

    assert result == sample_user
    read_session.query.assert_called_once()

def test_get_user_by_id_not_found(user_repo, mock_db_sessions):
    """Test retrieving a user that does not exist."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = None

    result = user_repo.get_user_by_id(user_id=999)

    assert result is None
    read_session.query.assert_called_once()

def test_create_user(user_repo, mock_db_sessions):
    """Test creating a new user."""
    write_session, _ = mock_db_sessions
    write_session.commit = MagicMock()
    write_session.refresh = MagicMock()

    mock_user = MagicMock()
    mock_user.id = 10  # Assigning a mock ID

    write_session.add.side_effect = lambda x: setattr(x, "id", 10)

    user_id = user_repo.create_user(first_name="Jane", last_name="Doe")

    assert user_id == 10
    write_session.add.assert_called_once()
    write_session.commit.assert_called_once()
    write_session.refresh.assert_called_once()

def test_delete_existing_user(user_repo, mock_db_sessions, sample_user):
    """Test deleting an existing user."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_user

    result = user_repo.delete(user_id=sample_user.id)

    assert result is True
    write_session.delete.assert_called_once_with(sample_user)
    write_session.commit.assert_called_once()

def test_delete_non_existent_user(user_repo, mock_db_sessions):
    """Test attempting to delete a non-existent user."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = None

    result = user_repo.delete(user_id=999)

    assert result is True  # Since delete always returns True
    write_session.delete.assert_not_called()
    write_session.commit.assert_not_called()



def test_update_non_existent_user(user_repo, mock_db_sessions):
    """Test updating a non-existent user."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = None

    result = user_repo.update(user_id=999, first_name="New Name")

    assert result is None
    write_session.commit.assert_not_called()
    write_session.refresh.assert_not_called()
