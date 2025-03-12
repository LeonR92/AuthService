import pytest
from unittest.mock import MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from blueprints.users.models import Credentials
from blueprints.users.credentials_repository import CredentialsRepository

@pytest.fixture
def mock_db_sessions():
    """Fixture for mocking SQLAlchemy sessions."""
    write_session = MagicMock(spec=Session)
    read_session = MagicMock(spec=Session)
    return write_session, read_session

@pytest.fixture
def credentials_repo(mock_db_sessions):
    """Fixture for initializing the repository with mock sessions."""
    write_session, read_session = mock_db_sessions
    return CredentialsRepository(write_db_session=write_session, read_db_session=read_session)

@pytest.fixture
def sample_credentials():
    """Fixture to provide a sample credentials object."""
    return Credentials(id=1, email="test@example.com", password="hashed_password")

def test_get_all_credentials(credentials_repo, mock_db_sessions, sample_credentials):
    """Test fetching all credentials."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.all.return_value = [sample_credentials]
    
    result = credentials_repo.get_all_credentials()
    
    assert result == [sample_credentials]
    read_session.query.assert_called_once()

def test_get_credentials_by_id(credentials_repo, mock_db_sessions, sample_credentials):
    """Test fetching credentials by ID."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_credentials
    
    result = credentials_repo.get_credentials_by_id(1)
    
    assert result == sample_credentials
    read_session.query.assert_called_once()

def test_get_credentials_by_email(credentials_repo, mock_db_sessions, sample_credentials):
    """Test fetching credentials by ID."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_credentials
    
    result = credentials_repo.get_credentials_by_email(1)
    
    assert result == sample_credentials
    read_session.query.assert_called_once()

def test_create_credentials(credentials_repo, mock_db_sessions):
    """Test creating credentials."""
    write_session, _ = mock_db_sessions
    write_session.flush = MagicMock()

    mock_credentials = MagicMock()
    mock_credentials.id = 123  

    write_session.add.side_effect = lambda x: setattr(x, "id", 123)

    credentials_id = credentials_repo.create_credentials("new@example.com", "new_password")

    assert credentials_id == 123  
    write_session.add.assert_called_once()
    write_session.flush.assert_called_once()

def test_delete_credentials(credentials_repo, mock_db_sessions, sample_credentials):
    """Test deleting credentials."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_credentials

    result = credentials_repo.delete_credentials(1)
    
    assert result == sample_credentials
    write_session.delete.assert_called_once_with(sample_credentials)

def test_delete_credentials_not_found(credentials_repo, mock_db_sessions):
    """Test deleting non-existent credentials."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = None

    result = credentials_repo.delete_credentials(999)
    
    assert result is None
    write_session.delete.assert_not_called()

def test_soft_delete_credentials(credentials_repo, mock_db_sessions, sample_credentials):
    """Test soft deleting credentials by setting deleted_at timestamp."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_credentials

    result = credentials_repo.soft_delete_credentials(1)
    
    assert result.deleted_at is not None
    assert isinstance(result.deleted_at, datetime)

def test_update_credentials(credentials_repo, mock_db_sessions, sample_credentials):
    """Test updating user credentials."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_credentials

    updated_user = credentials_repo.update_credentials(1, email="updated@example.com")
    
    assert updated_user.email == "updated@example.com"



