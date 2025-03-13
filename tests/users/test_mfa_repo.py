import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from blueprints.users.models import MFA, Credentials, User
from blueprints.users.mfa_repository import MFARepository


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
def mfa_repository(mock_write_session, mock_read_session):
    """Fixture for creating an MFARepository with mock sessions."""
    return MFARepository(
        write_db_session=mock_write_session,
        read_db_session=mock_read_session
    )


@pytest.fixture
def mock_mfa():
    """Fixture for creating mock MFA objects."""
    mfa1 = Mock(spec=MFA)
    mfa1.id = 1
    mfa1.totp_secret = "ABCDEFGHIJKLMNOP"
    
    mfa2 = Mock(spec=MFA)
    mfa2.id = 2
    mfa2.totp_secret = "QRSTUVWXYZ123456"
    
    return [mfa1, mfa2]


@pytest.fixture
def mock_user():
    """Fixture for creating mock User objects."""
    user1 = Mock(spec=User)
    user1.id = 1
    user1.credentials_id = 1
    user1.mfa_id = 1
    
    user2 = Mock(spec=User)
    user2.id = 2
    user2.credentials_id = 2
    user2.mfa_id = 2
    
    return [user1, user2]


@pytest.fixture
def mock_credentials():
    """Fixture for creating mock Credentials objects."""
    cred1 = Mock(spec=Credentials)
    cred1.id = 1
    cred1.email = "user1@example.com"
    
    cred2 = Mock(spec=Credentials)
    cred2.id = 2
    cred2.email = "user2@example.com"
    
    return [cred1, cred2]


def test_get_mfa_details_by_user_id_existing(mfa_repository, mock_read_session, mock_mfa):
    """Test fetching MFA details by user ID when they exist."""
    user_id = 1
    
    mock_query = mock_read_session.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_filter.first.return_value = mock_mfa[0]
    
    result = mfa_repository.get_mfa_details_by_user_id(user_id)
    
    mock_read_session.query.assert_called_once_with(MFA)
    assert result == mock_mfa[0]


def test_get_mfa_details_by_user_id_nonexistent(mfa_repository, mock_read_session):
    """Test fetching MFA details by user ID when they don't exist."""
    user_id = 999
    
    mock_query = mock_read_session.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_filter.first.return_value = None
    
    result = mfa_repository.get_mfa_details_by_user_id(user_id)
    
    mock_read_session.query.assert_called_once_with(MFA)
    assert result is None



def test_get_mfa_details_via_email_existing(mfa_repository, mock_read_session, mock_user):
    """Test fetching MFA details by email when they exist."""
    email = "user1@example.com"
    
    mock_query = mock_read_session.query.return_value
    mock_join1 = mock_query.join.return_value
    mock_join2 = mock_join1.join.return_value
    mock_filter = mock_join2.filter.return_value
    mock_filter.first.return_value = mock_user[0]
    
    result = mfa_repository.get_mfa_details_via_email(email)
    
    mock_read_session.query.assert_called_once_with(User)
    assert result == mock_user[0]


def test_get_mfa_details_via_email_nonexistent(mfa_repository, mock_read_session):
    """Test fetching MFA details by email when they don't exist."""
    email = "nonexistent@example.com"
    
    mock_query = mock_read_session.query.return_value
    mock_join1 = mock_query.join.return_value
    mock_join2 = mock_join1.join.return_value
    mock_filter = mock_join2.filter.return_value
    mock_filter.first.return_value = None
    
    result = mfa_repository.get_mfa_details_via_email(email)
    
    mock_read_session.query.assert_called_once_with(User)
    assert result is None


def test_get_mfa_details_existing(mfa_repository, mock_read_session, mock_mfa):
    """Test fetching MFA details by ID when they exist."""
    mfa_id = 1
    
    mock_query = mock_read_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_mfa[0]
    
    result = mfa_repository.get_mfa_details(mfa_id)
    
    mock_read_session.query.assert_called_once_with(MFA)
    mock_query.filter.assert_called_once()
    assert result == mock_mfa[0]


def test_get_mfa_details_nonexistent(mfa_repository, mock_read_session):
    """Test fetching MFA details by ID when they don't exist."""
    mfa_id = 999
    
    mock_query = mock_read_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None
    
    result = mfa_repository.get_mfa_details(mfa_id)
    
    mock_read_session.query.assert_called_once_with(MFA)
    mock_query.filter.assert_called_once()
    assert result is None


def test_create(mfa_repository, mock_write_session):
    """Test creating a new MFA record."""
    totp_secret = "NEWTOTP123456789"
    
    mock_mfa = Mock(spec=MFA)
    mock_mfa.id = 3
    
    added_mfa = None
    
    def capture_added_mfa(mfa):
        nonlocal added_mfa
        added_mfa = mfa
        mfa.id = 3
    
    mock_write_session.add.side_effect = capture_added_mfa
    
    result = mfa_repository.create(totp_secret)
    
    mock_write_session.add.assert_called_once()
    assert added_mfa is not None
    assert hasattr(added_mfa, 'totp_secret')
    assert added_mfa.totp_secret == totp_secret
    mock_write_session.commit.assert_called_once()
    mock_write_session.flush.assert_called_once()
    assert result == 3


def test_delete_existing(mfa_repository, mock_write_session, mock_mfa):
    """Test deleting an existing MFA record."""
    mfa_id = 1
    
    with patch.object(mfa_repository, 'get_mfa_details', return_value=mock_mfa[0]) as mock_get:
        mock_write_session.merge.return_value = mock_mfa[0]
        
        mfa_repository.delete(mfa_id)
        
        mock_get.assert_called_once_with(mfa_id)
        mock_write_session.merge.assert_called_once_with(mock_mfa[0])
        mock_write_session.delete.assert_called_once_with(mock_mfa[0])
        mock_write_session.commit.assert_called_once()


def test_delete_nonexistent(mfa_repository, mock_write_session):
    """Test deleting a nonexistent MFA record."""
    mfa_id = 999
    
    with patch.object(mfa_repository, 'get_mfa_details', return_value=None) as mock_get:
        mfa_repository.delete(mfa_id)
        
        mock_get.assert_called_once_with(mfa_id)
        mock_write_session.merge.assert_not_called()
        mock_write_session.delete.assert_not_called()
        mock_write_session.commit.assert_not_called()


def test_update_mfa_secret_existing(mfa_repository, mock_write_session, mock_mfa):
    """Test updating TOTP secret for an existing MFA record."""
    user_id = 1
    new_totp_secret = "NEWTOTP123456789"
    
    with patch.object(mfa_repository, 'get_mfa_details_by_user_id', return_value=mock_mfa[0]) as mock_get:
        result = mfa_repository.update_mfa_secret(user_id, new_totp_secret)
        
        mock_get.assert_called_once_with(user_id)
        assert mock_mfa[0].totp_secret == new_totp_secret
        mock_write_session.commit.assert_called_once()
        mock_write_session.refresh.assert_called_once_with(mock_mfa[0])
        assert result == mock_mfa[0]


def test_update_mfa_secret_nonexistent(mfa_repository, mock_write_session):
    """Test updating TOTP secret for a nonexistent MFA record."""
    user_id = 999
    new_totp_secret = "NEWTOTP123456789"
    
    with patch.object(mfa_repository, 'get_mfa_details_by_user_id', return_value=None) as mock_get:
        result = mfa_repository.update_mfa_secret(user_id, new_totp_secret)
        
        mock_get.assert_called_once_with(user_id)
        mock_write_session.commit.assert_not_called()
        mock_write_session.refresh.assert_not_called()
        assert result is None