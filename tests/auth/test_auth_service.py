import pytest
import bcrypt
from unittest.mock import MagicMock
from blueprints.users.crendentials_service import CredentialsService
from blueprints.auth.service import AuthService  

# Fixtures
@pytest.fixture
def mock_cred_service():
    return MagicMock(spec=CredentialsService)

@pytest.fixture
def auth_service(mock_cred_service):
    return AuthService(mock_cred_service)

# Test check_password method
def test_check_password_success(auth_service):
    """Test successful password verification."""
    # Generate a real hashed password for testing
    password = "correct_password"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    # Test the method
    result = auth_service.check_password(password, hashed)
    
    assert result is True

def test_check_password_failure(auth_service):
    """Test failed password verification."""
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    result = auth_service.check_password(wrong_password, hashed)
    
    assert result is False

# Test verify_password method
def test_verify_password_success(auth_service, mock_cred_service):
    """Test successful password verification with credentials service."""
    email = "user@example.com"
    password = "valid_password"
    
    # Set up the mock to return credentials with the correct password
    mock_creds = MagicMock()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    mock_creds.password = hashed_password
    mock_cred_service.get_credentials_via_email.return_value = mock_creds
    
    # Test the method
    result = auth_service.verify_password(email, password)
    
    assert result is True
    mock_cred_service.get_credentials_via_email.assert_called_once_with(email=email)

def test_verify_password_failure(auth_service, mock_cred_service):
    """Test failed password verification with credentials service."""
    email = "user@example.com"
    password = "wrong_password"
    correct_password = "correct_password"
    
    # Set up the mock to return credentials with a different password
    mock_creds = MagicMock()
    hashed_password = bcrypt.hashpw(correct_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    mock_creds.password = hashed_password
    mock_cred_service.get_credentials_via_email.return_value = mock_creds
    
    # Test the method
    result = auth_service.verify_password(email, password)
    
    assert result is False
    mock_cred_service.get_credentials_via_email.assert_called_once_with(email=email)

def test_verify_password_invalid_email(auth_service, mock_cred_service):
    """Test password verification with invalid email."""
    email = "nonexistent@example.com"
    password = "any_password"
    
    # Set up the mock to return None (no credentials found)
    mock_cred_service.get_credentials_via_email.return_value = None
    
    # Test that the method raises the expected exception
    with pytest.raises(ValueError, match="Invalid email or password"):
        auth_service.verify_password(email, password)
    
    mock_cred_service.get_credentials_via_email.assert_called_once_with(email=email)

def test_verify_password_null_password(auth_service, mock_cred_service):
    """Test password verification with null stored password."""
    email = "user@example.com"
    password = "any_password"
    
    # Set up the mock to return credentials with a null password
    mock_creds = MagicMock()
    mock_creds.password = None
    mock_cred_service.get_credentials_via_email.return_value = mock_creds
    
    # Test that the method raises the expected exception
    with pytest.raises(ValueError, match="Invalid email or password"):
        auth_service.verify_password(email, password)
    
    mock_cred_service.get_credentials_via_email.assert_called_once_with(email=email)




