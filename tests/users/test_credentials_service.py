import pytest
from unittest.mock import Mock, patch
import bcrypt

from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.models import Credentials
from blueprints.users.crendentials_service import CredentialsService


@pytest.fixture
def mock_cred_repo():
    """Fixture for mocking the credentials repository."""
    return Mock(spec=CredentialsRepository)


@pytest.fixture
def credentials_service(mock_cred_repo):
    """Fixture for creating a CredentialsService with mock repository."""
    return CredentialsService(cred_repo=mock_cred_repo)


@pytest.fixture
def mock_credentials():
    """Fixture for creating mock credentials objects."""
    cred1 = Mock(spec=Credentials)
    cred1.id = 1
    cred1.email = "user1@example.com"
    cred1.password = "hashed_password1"
    
    cred2 = Mock(spec=Credentials)
    cred2.id = 2
    cred2.email = "user2@example.com"
    cred2.password = "hashed_password2"
    
    return [cred1, cred2]


def test_validate_and_hash_pw_valid(credentials_service):
    """Test validating and hashing a valid password."""
    # Arrange
    password = "validpassword"
    password_length = 8
    
    # Act
    hashed = credentials_service.validate_and_hash_pw(password, password_length)
    
    # Assert
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    # Verify the hash works with bcrypt verification
    assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def test_validate_and_hash_pw_empty(credentials_service):
    """Test validating an empty password."""
    # Arrange
    password = ""
    
    # Act & Assert
    with pytest.raises(ValueError, match="Password cannot be empty"):
        credentials_service.validate_and_hash_pw(password)


def test_validate_and_hash_pw_too_short(credentials_service):
    """Test validating a password that's too short."""
    # Arrange
    password = "short"
    password_length = 8
    
    # Act & Assert
    with pytest.raises(ValueError, match=f"Password cannot be shorter than {password_length}"):
        credentials_service.validate_and_hash_pw(password, password_length)


def test_get_credentials_via_email_existing(credentials_service, mock_cred_repo, mock_credentials):
    """Test getting credentials via email when they exist."""
    # Arrange
    email = "user1@example.com"
    mock_cred_repo.get_credentials_by_email.return_value = mock_credentials[0]
    
    # Act
    result = credentials_service.get_credentials_via_email(email)
    
    # Assert
    mock_cred_repo.get_credentials_by_email.assert_called_once_with(email=email)
    assert result == mock_credentials[0]


def test_get_credentials_via_email_nonexistent(credentials_service, mock_cred_repo):
    """Test getting credentials via email when they don't exist."""
    # Arrange
    email = "nonexistent@example.com"
    mock_cred_repo.get_credentials_by_email.return_value = None
    
    # Act & Assert
    with pytest.raises(Exception, match="credentials not found"):
        credentials_service.get_credentials_via_email(email)
    mock_cred_repo.get_credentials_by_email.assert_called_once_with(email=email)


def test_get_email_by_userid_existing(credentials_service, mock_cred_repo):
    """Test getting email by user ID when it exists."""
    # Arrange
    user_id = 1
    expected_email = "user1@example.com"
    mock_cred_repo.get_email_by_userid.return_value = expected_email
    
    # Act
    result = credentials_service.get_email_by_userid(user_id)
    
    # Assert
    mock_cred_repo.get_email_by_userid.assert_called_once_with(user_id=user_id)
    assert result == expected_email


def test_get_email_by_userid_nonexistent(credentials_service, mock_cred_repo):
    """Test getting email by user ID when it doesn't exist."""
    # Arrange
    user_id = 999
    mock_cred_repo.get_email_by_userid.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Email not found"):
        credentials_service.get_email_by_userid(user_id)
    mock_cred_repo.get_email_by_userid.assert_called_once_with(user_id=user_id)


def test_get_email_by_userid_empty(credentials_service, mock_cred_repo):
    """Test getting email with empty user ID."""
    # Arrange
    user_id = None
    
    # The function doesn't actually check for None values, it just passes to the repo
    # which would likely fail later, so we should mock that behavior
    mock_cred_repo.get_email_by_userid.side_effect = TypeError("NoneType object has no attribute...")
    
    # Act & Assert
    with pytest.raises(TypeError):
        credentials_service.get_email_by_userid(user_id)


def test_get_id_via_email_existing(credentials_service, mock_cred_repo, mock_credentials):
    """Test getting credential ID via email when it exists."""
    # Arrange
    email = "user1@example.com"
    mock_cred_repo.get_credentials_by_email.return_value = mock_credentials[0]
    
    # Act
    result = credentials_service.get_id_via_email(email)
    
    # Assert
    mock_cred_repo.get_credentials_by_email.assert_called_once_with(email=email)
    assert result == 1  # mock_credentials[0].id


def test_get_id_via_email_nonexistent(credentials_service, mock_cred_repo):
    """Test getting credential ID via email when it doesn't exist."""
    # Arrange
    email = "nonexistent@example.com"
    mock_cred_repo.get_credentials_by_email.return_value = None
    
    # Act & Assert
    with pytest.raises(Exception, match="credentials not found"):
        credentials_service.get_id_via_email(email)
    mock_cred_repo.get_credentials_by_email.assert_called_once_with(email=email)


def test_generate_random_password(credentials_service):
    """Test generating a random password."""
    # Arrange
    length = 15
    
    # Act
    password1 = credentials_service.generate_random_password(length)
    password2 = credentials_service.generate_random_password(length)
    
    # Assert
    assert isinstance(password1, str)
    assert len(password1) == length
    assert isinstance(password2, str)
    assert len(password2) == length
    # Passwords should be different (very unlikely to be the same)
    assert password1 != password2


def test_reset_password(credentials_service, mock_cred_repo, mock_credentials):
    """Test resetting a password."""
    # Arrange
    email = "user1@example.com"
    mock_cred_repo.get_credentials_by_email.return_value = mock_credentials[0]
    
    # Patch the generate_random_password and validate_and_hash_pw methods
    with patch.object(credentials_service, 'generate_random_password', return_value='new_random_password') as mock_generate, \
         patch.object(credentials_service, 'validate_and_hash_pw', return_value='new_hashed_password') as mock_validate:
        
        # Act
        result = credentials_service.reset_password(email)
        
        # Assert
        mock_cred_repo.get_credentials_by_email.assert_called_once_with(email=email)
        mock_generate.assert_called_once()
        mock_validate.assert_called_once_with('new_random_password')
        mock_cred_repo.update_credentials.assert_called_once_with(cred_id=1, password='new_hashed_password')
        assert result == 'new_random_password'


def test_reset_password_nonexistent(credentials_service):
    """Test resetting a password for a nonexistent email."""
    # Arrange
    email = "nonexistent@example.com"
    
    # Patch the get_credentials_via_email method to raise an exception
    with patch.object(credentials_service, 'get_credentials_via_email', side_effect=ValueError(f"No credentials found for email: {email}")):
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"No credentials found for email: {email}"):
            credentials_service.reset_password(email)


def test_create_credentials_valid(credentials_service, mock_cred_repo):
    """Test creating credentials with valid data."""
    # Arrange
    email = "new_user@example.com"
    password = "valid_password"
    hashed_password = "hashed_valid_password"
    expected_cred_id = 3
    
    # Patch the validate_and_hash_pw method
    with patch.object(credentials_service, 'validate_and_hash_pw', return_value=hashed_password) as mock_validate:
        mock_cred_repo.create_credentials.return_value = expected_cred_id
        
        # Act
        result = credentials_service.create_credentials(email, password)
        
        # Assert
        mock_validate.assert_called_once_with(password)
        mock_cred_repo.create_credentials.assert_called_once_with(email=email, password=hashed_password)
        assert result == expected_cred_id


def test_create_credentials_empty_email(credentials_service):
    """Test creating credentials with an empty email."""
    # Arrange
    email = ""
    password = "valid_password"
    
    # Act & Assert
    with pytest.raises(ValueError, match="Email or Password cannot be empty"):
        credentials_service.create_credentials(email, password)


def test_create_credentials_empty_password(credentials_service):
    """Test creating credentials with an empty password."""
    # Arrange
    email = "valid@example.com"
    password = ""
    
    # Act & Assert
    with pytest.raises(ValueError, match="Email or Password cannot be empty"):
        credentials_service.create_credentials(email, password)


def test_create_credentials_error(credentials_service, mock_cred_repo):
    """Test error handling when repository fails to create credentials."""
    # Arrange
    email = "new_user@example.com"
    password = "valid_password"
    hashed_password = "hashed_valid_password"
    
    # Patch the validate_and_hash_pw method
    with patch.object(credentials_service, 'validate_and_hash_pw', return_value=hashed_password) as mock_validate:
        mock_cred_repo.create_credentials.return_value = None
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Cant create credentials"):
            credentials_service.create_credentials(email, password)
        
        mock_validate.assert_called_once_with(password)
        mock_cred_repo.create_credentials.assert_called_once_with(email=email, password=hashed_password)




def test_create_user_valid(credentials_service, mock_cred_repo):
    """Test creating a user with valid data."""
    # Arrange
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }
    expected_cred_id = 3
    mock_cred_repo.create_credentials.return_value = expected_cred_id
    
    # Act
    result = credentials_service.create_user(data)
    
    # Assert
    mock_cred_repo.create_credentials.assert_called_once_with(**data)
    assert result == expected_cred_id


def test_create_user_invalid_data(credentials_service, mock_cred_repo):
    """Test creating a user with invalid data."""
    # Arrange - Data with invalid keys
    data = {
        "first_name": "John",
        "invalid_field": "Value",
        "another_invalid": "Value"
    }
    
    # Based on the implementation, the check is actually if ALL keys are in the set,
    # not just any keys, so we need a test case that matches the actual implementation
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid or empty data"):
        credentials_service.create_user(data)


def test_create_user_empty_data(credentials_service):
    """Test creating a user with empty data."""
    # Arrange
    data = {}
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid or empty data"):
        credentials_service.create_user(data)


def test_create_user_none_data(credentials_service):
    """Test creating a user with None data."""
    # Arrange
    data = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid or empty data"):
        credentials_service.create_user(data)


def test_change_password_valid(credentials_service, mock_cred_repo, mock_credentials):
    """Test changing password with valid data."""
    # Arrange
    user_id = 1
    new_password = "new_valid_password"
    confirm_new_password = "new_valid_password"
    hashed_password = "hashed_new_valid_password"
    
    mock_cred_repo.get_credentials_by_id.return_value = mock_credentials[0]
    
    # Patch the validate_and_hash_pw method
    with patch.object(credentials_service, 'validate_and_hash_pw', return_value=hashed_password) as mock_validate:
        
        # Act
        credentials_service.change_password(user_id, new_password, confirm_new_password)
        
        # Assert
        mock_cred_repo.get_credentials_by_id.assert_called_once_with(user_id=user_id)
        mock_validate.assert_called_once_with(new_password)
        mock_cred_repo.update_credentials.assert_called_once_with(cred_id=1, password=hashed_password)


def test_change_password_user_not_found(credentials_service, mock_cred_repo):
    """Test changing password for a nonexistent user."""
    # Arrange
    user_id = 999
    new_password = "new_valid_password"
    confirm_new_password = "new_valid_password"
    
    mock_cred_repo.get_credentials_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="User not found"):
        credentials_service.change_password(user_id, new_password, confirm_new_password)
    
    mock_cred_repo.get_credentials_by_id.assert_called_once_with(user_id=user_id)


def test_change_password_mismatch(credentials_service, mock_cred_repo, mock_credentials):
    """Test changing password with mismatched passwords."""
    # Arrange
    user_id = 1
    new_password = "new_valid_password"
    confirm_new_password = "different_password"
    
    mock_cred_repo.get_credentials_by_id.return_value = mock_credentials[0]
    
    # Act & Assert
    with pytest.raises(ValueError, match="New passwords do not match"):
        credentials_service.change_password(user_id, new_password, confirm_new_password)
    
    mock_cred_repo.get_credentials_by_id.assert_called_once_with(user_id=user_id)


def test_update_valid(credentials_service, mock_cred_repo):
    """Test updating credentials with valid data."""
    # Arrange
    cred_id = 1
    password = "new_password"
    
    # Act
    credentials_service.update(cred_id, password)
    
    # Assert
    mock_cred_repo.update_credentials.assert_called_once_with(cred_id, password=password)


def test_update_no_cred_id(credentials_service):
    """Test updating credentials with no credential ID."""
    # Arrange
    cred_id = None
    password = "new_password"
    
    # Act & Assert
    with pytest.raises(ValueError, match="Credential ID is required for update."):
        credentials_service.update(cred_id, password)


def test_update_no_fields(credentials_service, mock_cred_repo):
    """Test updating credentials with no fields to update."""
    # Arrange
    cred_id = 1
    password = None
    
    # Act
    credentials_service.update(cred_id, password)
    
    # Assert
    mock_cred_repo.update_credentials.assert_called_once_with(cred_id)