import pytest
from unittest.mock import MagicMock
from blueprints.users.mfa_service import MFAservice
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.models import MFA


@pytest.fixture
def mock_mfa_repo():
    """Fixture to mock MFARepository."""
    return MagicMock(spec=MFARepository)

@pytest.fixture
def mfa_service(mock_mfa_repo):
    """Fixture to initialize MFAservice with a mocked repository."""
    return MFAservice(mfa_repo=mock_mfa_repo)

@pytest.fixture
def sample_mfa():
    """Fixture to provide a sample MFA object."""
    return MFA(id=1, totp_secret="sample_secret")

def test_get_mfa_details_via_user_id_valid(mfa_service, mock_mfa_repo, sample_mfa):
    """Test retrieving MFA details for a valid user."""
    mock_mfa_repo.get_mfa_details_by_user_id.return_value = sample_mfa

    result = mfa_service.get_mfa_details_via_user_id(user_id=1)

    assert result == sample_mfa

def test_get_mfa_details_via_user_id_missing_user(mfa_service):
    """Test that missing user_id raises ValueError."""
    with pytest.raises(ValueError, match="User id missing"):
        mfa_service.get_mfa_details_via_user_id(None)

def test_get_mfa_details_via_user_id_not_found(mfa_service, mock_mfa_repo):
    """Test when MFA details are not found for a user."""
    mock_mfa_repo.get_mfa_details_by_user_id.return_value = None

    with pytest.raises(Exception, match="No MFA details with the user id is found"):
        mfa_service.get_mfa_details_via_user_id(999)

def test_create_totp_secret(mfa_service):
    """Test that TOTP secret generation returns a valid string."""
    totp_secret = mfa_service.create_totp_secret()

    assert isinstance(totp_secret, str)
    assert len(totp_secret) > 0

def test_create_mfa_entry_valid(mfa_service, mock_mfa_repo, sample_mfa):
    """Test successfully creating an MFA entry for a user."""
    mock_mfa_repo.create.return_value = sample_mfa

    result = mfa_service.create_mfa_entry(user_id=1)

    assert result == sample_mfa
    mock_mfa_repo.create.assert_called_once()

def test_create_mfa_entry_missing_user(mfa_service):
    """Test that creating MFA with missing user ID raises ValueError."""
    with pytest.raises(ValueError, match="user ID cannot be missing"):
        mfa_service.create_mfa_entry(None)

def test_change_totp_secret_valid(mfa_service, mock_mfa_repo, sample_mfa):
    """Test successfully changing the TOTP secret."""
    new_secret = "new_generated_secret"
    mock_mfa_repo.update_mfa_secret.return_value = sample_mfa

    result = mfa_service.change_totp_secret(user_id=1)

    assert isinstance(result, str)
    assert result != sample_mfa.totp_secret  # Ensures a new secret is generated
    mock_mfa_repo.update_mfa_secret
