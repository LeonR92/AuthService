import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from blueprints.users.models import Credentials
from blueprints.users.credentials_repository import CredentialsRepository  


@pytest.fixture
def mock_read_session():
    """Fixture for mocking the read database session."""
    session = Mock(spec=Session)
    return session


@pytest.fixture
def mock_write_session():
    """Fixture for mocking the write database session."""
    session = Mock(spec=Session)
    return session


@pytest.fixture
def credentials_repository(mock_write_session, mock_read_session):
    """Fixture for creating a CredentialsRepository with mock sessions."""
    return CredentialsRepository(
        write_db_session=mock_write_session,
        read_db_session=mock_read_session
    )


@pytest.fixture
def mock_credentials_list():
    """Fixture for creating a list of mock credentials."""
    return [
        Mock(spec=Credentials, id=1, email="user1@example.com", password="hashed_password1", deleted_at=None),
        Mock(spec=Credentials, id=2, email="user2@example.com", password="hashed_password2", deleted_at=None),
        Mock(spec=Credentials, id=3, email="user3@example.com", password="hashed_password3", deleted_at=datetime.now())
    ]





def test_get_credentials_by_id_existing(credentials_repository, mock_read_session, mock_credentials_list):
    """Test fetching credentials by ID when credentials exist."""
    # Arrange
    mock_query = mock_read_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_credentials_list[0]
    
    # Act
    result = credentials_repository.get_credentials_by_id(1)
    
    # Assert
    mock_read_session.query.assert_called_once_with(Credentials)
    mock_query.filter.assert_called_once()
    mock_filter.first.assert_called_once()
    assert result == mock_credentials_list[0]


def test_get_credentials_by_id_nonexistent(credentials_repository, mock_read_session):
    """Test fetching credentials by ID when credentials don't exist."""
    # Arrange
    mock_query = mock_read_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None
    
    # Act
    result = credentials_repository.get_credentials_by_id(999)
    
    # Assert
    mock_read_session.query.assert_called_once_with(Credentials)
    mock_query.filter.assert_called_once()
    mock_filter.first.assert_called_once()
    assert result is None


def test_get_credentials_by_email_existing(credentials_repository, mock_read_session, mock_credentials_list):
    """Test fetching credentials by email when credentials exist."""
    # Arrange
    mock_query = mock_read_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_credentials_list[0]
    
    # Act
    result = credentials_repository.get_credentials_by_email("user1@example.com")
    
    # Assert
    mock_read_session.query.assert_called_once_with(Credentials)
    mock_query.filter.assert_called_once()
    mock_filter.first.assert_called_once()
    assert result == mock_credentials_list[0]


def test_get_credentials_by_email_nonexistent(credentials_repository, mock_read_session):
    """Test fetching credentials by email when credentials don't exist."""
    # Arrange
    mock_query = mock_read_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None
    
    # Act
    result = credentials_repository.get_credentials_by_email("nonexistent@example.com")
    
    # Assert
    mock_read_session.query.assert_called_once_with(Credentials)
    mock_query.filter.assert_called_once()
    mock_filter.first.assert_called_once()
    assert result is None


def test_get_email_by_userid_existing(credentials_repository, mock_read_session):
    """Test fetching email by user ID when user exists."""
    # Arrange
    mock_query = mock_read_session.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_filter.first.return_value = ("user1@example.com",)
    
    # Act
    result = credentials_repository.get_email_by_userid(1)
    
    # Assert
    mock_read_session.query.assert_called_once()
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    mock_filter.first.assert_called_once()
    assert result == "user1@example.com"


def test_get_email_by_userid_nonexistent(credentials_repository, mock_read_session):
    """Test fetching email by user ID when user doesn't exist."""
    # Arrange
    mock_query = mock_read_session.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_filter.first.return_value = None
    
    # Act
    result = credentials_repository.get_email_by_userid(999)
    
    # Assert
    mock_read_session.query.assert_called_once()
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    mock_filter.first.assert_called_once()
    assert result is None


def test_create_credentials(credentials_repository, mock_write_session):
    """Test creating new credentials."""
    email = "new_user@example.com"
    password = "new_password"
    

    added_credentials = None
    
    def capture_added_credentials(cred):
        nonlocal added_credentials
        added_credentials = cred
        cred.id = 4
    
    mock_write_session.add.side_effect = capture_added_credentials
    
    result = credentials_repository.create_credentials(email, password)
    
    mock_write_session.add.assert_called_once()
    assert added_credentials is not None
    assert added_credentials.email == email
    assert added_credentials.password == password
    mock_write_session.flush.assert_called_once()
    assert result == 4


def test_delete_credentials_existing(credentials_repository, mock_write_session, mock_credentials_list):
    """Test deleting credentials when credentials exist."""
    # Arrange
    # Mock the get_credentials_by_id method to return an existing user
    with patch.object(credentials_repository, 'get_credentials_by_id', return_value=mock_credentials_list[0]):
        # Act
        result = credentials_repository.delete_credentials(1)
        
        # Assert
        credentials_repository.get_credentials_by_id.assert_called_once_with(1)
        mock_write_session.delete.assert_called_once_with(mock_credentials_list[0])
        assert result == mock_credentials_list[0]


def test_delete_credentials_nonexistent(credentials_repository, mock_write_session):
    """Test deleting credentials when credentials don't exist."""
    # Arrange
    # Mock the get_credentials_by_id method to return None
    with patch.object(credentials_repository, 'get_credentials_by_id', return_value=None):
        # Act
        result = credentials_repository.delete_credentials(999)
        
        # Assert
        credentials_repository.get_credentials_by_id.assert_called_once_with(999)
        mock_write_session.delete.assert_not_called()
        assert result is None


def test_soft_delete_credentials_existing(credentials_repository, mock_credentials_list):
    """Test soft deleting credentials when credentials exist."""
    # Arrange
    # Mock the get_credentials_by_id method to return an existing user
    mock_user = mock_credentials_list[0]
    mock_user.deleted_at = None
    
    with patch.object(credentials_repository, 'get_credentials_by_id', return_value=mock_user):
        # Act
        result = credentials_repository.soft_delete_credentials(1)
        
        # Assert
        credentials_repository.get_credentials_by_id.assert_called_once_with(1)
        assert result == mock_user
        assert result.deleted_at is not None


def test_soft_delete_credentials_nonexistent(credentials_repository):
    """Test soft deleting credentials when credentials don't exist."""
    # Arrange
    # Mock the get_credentials_by_id method to return None
    with patch.object(credentials_repository, 'get_credentials_by_id', return_value=None):
        # Act
        result = credentials_repository.soft_delete_credentials(999)
        
        # Assert
        credentials_repository.get_credentials_by_id.assert_called_once_with(999)
        assert result is None


def test_update_credentials_existing(credentials_repository, mock_read_session, mock_write_session, mock_credentials_list):
    """Test updating credentials when credentials exist."""
    # Arrange
    mock_cred = mock_credentials_list[0]
    cred_id = 1
    new_email = "updated@example.com"
    
    # Mock query chain for read session
    mock_read_query = mock_read_session.query.return_value
    mock_read_filter = mock_read_query.filter_by.return_value
    mock_read_filter.first.return_value = mock_cred
    
    # Mock merge operation
    mock_write_session.merge.return_value = mock_cred
    
    # Act
    result = credentials_repository.update_credentials(cred_id, email=new_email)
    
    # Assert
    mock_read_session.query.assert_called_once_with(Credentials)
    mock_read_query.filter_by.assert_called_once_with(id=cred_id)
    mock_read_filter.first.assert_called_once()
    
    mock_write_session.merge.assert_called_once_with(mock_cred)
    # Check that setattr was used to update the email
    assert mock_cred.email == new_email
    
    mock_write_session.commit.assert_called_once()
    mock_write_session.refresh.assert_called_once_with(mock_cred)
    assert result == mock_cred


def test_update_credentials_nonexistent(credentials_repository, mock_read_session, mock_write_session):
    """Test updating credentials when credentials don't exist."""
    # Arrange
    cred_id = 999
    new_email = "updated@example.com"
    
    # Mock query chain for read session to return None
    mock_read_query = mock_read_session.query.return_value
    mock_read_filter = mock_read_query.filter_by.return_value
    mock_read_filter.first.return_value = None
    
    # Act
    result = credentials_repository.update_credentials(cred_id, email=new_email)
    
    # Assert
    mock_read_session.query.assert_called_once_with(Credentials)
    mock_read_query.filter_by.assert_called_once_with(id=cred_id)
    mock_read_filter.first.assert_called_once()
    
    mock_write_session.merge.assert_not_called()
    mock_write_session.commit.assert_not_called()
    mock_write_session.refresh.assert_not_called()
    assert result is None


def test_update_credentials_multiple_fields(credentials_repository, mock_read_session, mock_write_session, mock_credentials_list):
    """Test updating multiple fields of credentials."""
    # Arrange
    mock_cred = mock_credentials_list[0]
    cred_id = 1
    new_email = "updated@example.com"
    new_password = "new_password"
    
    # Mock query chain for read session
    mock_read_query = mock_read_session.query.return_value
    mock_read_filter = mock_read_query.filter_by.return_value
    mock_read_filter.first.return_value = mock_cred
    
    # Mock merge operation
    mock_write_session.merge.return_value = mock_cred
    
    # Act
    result = credentials_repository.update_credentials(cred_id, email=new_email, password=new_password)
    
    # Assert
    mock_read_session.query.assert_called_once_with(Credentials)
    mock_read_query.filter_by.assert_called_once_with(id=cred_id)
    mock_read_filter.first.assert_called_once()
    
    mock_write_session.merge.assert_called_once_with(mock_cred)
    # Check that setattr was used to update both fields
    assert mock_cred.email == new_email
    assert mock_cred.password == new_password
    
    mock_write_session.commit.assert_called_once()
    mock_write_session.refresh.assert_called_once_with(mock_cred)
    assert result == mock_cred