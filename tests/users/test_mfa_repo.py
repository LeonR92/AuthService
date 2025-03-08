import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from blueprints.users.models import MFA, User
from blueprints.users.mfa_repository import MFARepository

@pytest.fixture
def mock_db_sessions():
    """Fixture for mocking SQLAlchemy sessions."""
    write_session = MagicMock(spec=Session)
    read_session = MagicMock(spec=Session)
    return write_session, read_session

@pytest.fixture
def mfa_repo(mock_db_sessions):
    """Fixture to initialize MFARepository with mock sessions."""
    write_session, read_session = mock_db_sessions
    return MFARepository(write_db_session=write_session, read_db_session=read_session)

@pytest.fixture
def sample_mfa():
    """Fixture to provide a sample MFA object."""
    return MFA(id=1, totp_secret="sample_secret")

@pytest.fixture
def sample_user(sample_mfa):
    """Fixture to provide a sample User object linked to MFA."""
    return User(id=1, mfa_id=sample_mfa.id)

def test_get_mfa_details_by_user_id(mfa_repo, mock_db_sessions, sample_mfa, sample_user):
    """Test retrieving MFA details by user ID."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.join.return_value.filter.return_value.first.return_value = sample_mfa

    result = mfa_repo.get_mfa_details_by_user_id(user_id=sample_user.id)

    assert result == sample_mfa
    read_session.query.assert_called_once()

def test_get_mfa_details(mfa_repo, mock_db_sessions, sample_mfa):
    """Test retrieving MFA details by MFA ID."""
    _, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_mfa

    result = mfa_repo.get_mfa_details(mfa_id=sample_mfa.id)

    assert result == sample_mfa
    read_session.query.assert_called_once()

def test_create(mfa_repo, mock_db_sessions):
    """Test creating a new MFA record."""
    write_session, _ = mock_db_sessions
    write_session.commit = MagicMock()
    write_session.flush = MagicMock()

    mock_mfa = MagicMock()
    mock_mfa.id = 10  

    write_session.add.side_effect = lambda x: setattr(x, "id", 10)

    mfa_id = mfa_repo.create(totp_secret="new_secret")

    assert mfa_id == 10
    write_session.add.assert_called_once()
    write_session.commit.assert_called_once()
    write_session.flush.assert_called_once()

def test_delete_existing_mfa(mfa_repo, mock_db_sessions, sample_mfa):
    """Test deleting an existing MFA record."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = sample_mfa

    mfa_repo.delete(mfa_id=sample_mfa.id)

    write_session.delete.assert_called_once_with(sample_mfa)
    write_session.commit.assert_called_once()

def test_delete_non_existent_mfa(mfa_repo, mock_db_sessions):
    """Test attempting to delete a non-existent MFA record."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.filter.return_value.first.return_value = None

    mfa_repo.delete(mfa_id=999)

    write_session.delete.assert_not_called()
    write_session.commit.assert_not_called()

def test_update_mfa_secret_existing(mfa_repo, mock_db_sessions, sample_mfa, sample_user):
    """Test updating the OTP secret for an existing MFA entry."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.join.return_value.filter.return_value.first.return_value = sample_mfa

    updated_mfa = mfa_repo.update_mfa_secret(user_id=sample_user.id, totp_secret="new_secret")

    assert updated_mfa.totp_secret == "new_secret"
    write_session.commit.assert_called_once()
    write_session.refresh.assert_called_once_with(sample_mfa)

def test_update_mfa_secret_non_existent(mfa_repo, mock_db_sessions, sample_user):
    """Test updating the OTP secret for a user without MFA."""
    write_session, read_session = mock_db_sessions
    read_session.query.return_value.join.return_value.filter.return_value.first.return_value = None

    result = mfa_repo.update_mfa_secret(user_id=sample_user.id, totp_secret="new_secret")

    assert result is None
    write_session.commit.assert_not_called()
    write_session.refresh.assert_not_called()
