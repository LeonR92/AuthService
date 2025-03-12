import pytest
import bcrypt
from unittest.mock import MagicMock, patch
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

# Test reset_password method
def test_reset_password_success(auth_service, mock_cred_service):
    """Test successful password reset."""
    email = "user@example.com"
    new_password = 12345  # Note: this is an int as per the function signature
    user_id = "user123"
    hashed_new_password = "hashed_new_password"
    
    # Set up the mocks
    mock_creds = MagicMock()
    mock_creds.id = user_id
    mock_cred_service.get_credentials_via_email.return_value = mock_creds
    mock_cred_service.validate_and_hash_pw.return_value = hashed_new_password
    
    # Test the method
    result = auth_service.reset_password(email, new_password)
    
    assert result == new_password
    mock_cred_service.get_credentials_via_email.assert_called_once_with(email)
    mock_cred_service.validate_and_hash_pw.assert_called_once_with(new_password)
    mock_cred_service.update.assert_called_once_with(user_id, password=hashed_new_password)

def test_reset_password_invalid_email(auth_service, mock_cred_service):
    """Test password reset with invalid email."""
    email = "nonexistent@example.com"
    new_password = 12345
    
    # Set up the mock to return None (no credentials found)
    mock_cred_service.get_credentials_via_email.return_value = None
    
    # Test that the method raises the expected exception
    with pytest.raises(Exception, match=f"Information not found for the email {email}"):
        auth_service.reset_password(email, new_password)
    
    mock_cred_service.get_credentials_via_email.assert_called_once_with(email)
    mock_cred_service.validate_and_hash_pw.assert_not_called()
    mock_cred_service.update.assert_not_called()

# Optional: Test handling of exceptions from credential service
def test_reset_password_validation_error(auth_service, mock_cred_service):
    """Test password reset with validation error."""
    email = "user@example.com"
    new_password = 12345
    user_id = "user123"
    
    # Set up the mocks
    mock_creds = MagicMock()
    mock_creds.id = user_id
    mock_cred_service.get_credentials_via_email.return_value = mock_creds
    mock_cred_service.validate_and_hash_pw.side_effect = ValueError("Password does not meet requirements")
    
    # Test that the method propagates the exception
    with pytest.raises(ValueError, match="Password does not meet requirements"):
        auth_service.reset_password(email, new_password)
    
    mock_cred_service.get_credentials_via_email.assert_called_once_with(email)
    mock_cred_service.validate_and_hash_pw.assert_called_once_with(new_password)
    mock_cred_service.update.assert_not_called()

def test_integration_verify_and_reset_password(auth_service, mock_cred_service):
    """Integration test for verifying and then resetting a password."""
    email = "user@example.com"
    old_password = "old_password"
    new_password = 54321
    user_id = "user123"
    
    # Set up for verify_password
    mock_creds = MagicMock()
    mock_creds.id = user_id
    hashed_old_password = bcrypt.hashpw(old_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    mock_creds.password = hashed_old_password
    mock_cred_service.get_credentials_via_email.return_value = mock_creds
    
    # Set up for reset_password
    hashed_new_password = "hashed_new_password"
    mock_cred_service.validate_and_hash_pw.return_value = hashed_new_password
    
    # First verify the old password
    verify_result = auth_service.verify_password(email, old_password)
    assert verify_result is True
    
    # Then reset to a new password
    reset_result = auth_service.reset_password(email, new_password)
    assert reset_result == new_password
    
    # Check that the appropriate methods were called
    assert mock_cred_service.get_credentials_via_email.call_count == 2
    mock_cred_service.validate_and_hash_pw.assert_called_once_with(new_password)
    mock_cred_service.update.assert_called_once_with(user_id, password=hashed_new_password)