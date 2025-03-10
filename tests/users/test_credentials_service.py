import pytest
from unittest.mock import MagicMock, ANY
import bcrypt
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.models import Credentials

@pytest.fixture
def mock_cred_repo():
    """Fixture to mock CredentialsRepository."""
    return MagicMock(spec=CredentialsRepository)

@pytest.fixture
def credentials_service(mock_cred_repo):
    """Fixture to initialize CredentialsService with a mocked repository."""
    return CredentialsService(cred_repo=mock_cred_repo)

def test_validate_and_hash_pw_valid(credentials_service):
    """Test hashing a valid password."""
    password = "SecurePass123!"
    hashed_pw = credentials_service.validate_and_hash_pw(password)

    assert isinstance(hashed_pw, str)
    assert bcrypt.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8"))

@pytest.mark.parametrize("password", ["", "   ", None])
def test_validate_and_hash_pw_invalid_empty(credentials_service, password):
    """Test that empty passwords raise ValueError."""
    with pytest.raises(ValueError, match="Password cannot be empty"):
        credentials_service.validate_and_hash_pw(password)

def test_validate_and_hash_pw_too_short(credentials_service):
    """Test that short passwords raise ValueError."""
    with pytest.raises(ValueError, match="Password cannot be shorter than 8"):
        credentials_service.validate_and_hash_pw("short")

def test_create_credentials_valid(credentials_service, mock_cred_repo):
    """Test creating credentials successfully with hashing."""
    email = "test@example.com"
    password = "SecurePass123!"
    
    # Mock repository response
    mock_cred_repo.create_credentials.return_value = 1

    user_id = credentials_service.create_credentials(email, password)

    assert user_id == 1
    mock_cred_repo.create_credentials.assert_called_once_with(email=email, password=ANY)  # Fix for pytest.any

def test_create_credentials_invalid(credentials_service):
    """Test creating credentials with empty email or password raises ValueError."""
    with pytest.raises(ValueError, match="Email or Password cannot be empty"):
        credentials_service.create_credentials("", "ValidPassword")

    with pytest.raises(ValueError, match="Email or Password cannot be empty"):
        credentials_service.create_credentials("user@example.com", "")

def test_get_all_credentials(credentials_service, mock_cred_repo):
    """Test fetching all credentials from repository."""
    fake_credentials = [Credentials(id=1, email="user@example.com", password="hashed")]
    mock_cred_repo.get_all_credentials.return_value = fake_credentials

    result = credentials_service.get_all_credentials()

    assert result == fake_credentials
    mock_cred_repo.get_all_credentials.assert_called_once()

def test_get_credentials_by_email(credentials_service, mock_cred_repo):
    """Test fetching all credentials from repository."""
    fake_credentials = [Credentials(id=1, email="user@example.com", password="hashed")]
    mock_cred_repo.get_credentials_by_email.return_value = fake_credentials

    result = credentials_service.get_credentials_via_email("user@example.com")

    assert result == fake_credentials
    mock_cred_repo.get_credentials_by_email.assert_called_once()

def test_create_user_valid(credentials_service, mock_cred_repo):
    """Test creating a user with valid input."""
    user_data = {"first_name": "John", "last_name": "Doe", "email": "john@example.com"}
    mock_cred_repo.create_credentials.return_value = 1

    user_id = credentials_service.create_user(user_data)

    assert user_id == 1
    mock_cred_repo.create_credentials.assert_called_once_with(**user_data)

