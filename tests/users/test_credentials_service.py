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
    password = "validpassword"
    password_length = 8
    
    hashed = credentials_service.validate_and_hash_pw(password, password_length)
    
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def test_validate_and_hash_pw_empty(credentials_service):
    """Test validating an empty password."""
    password = ""
    
    with pytest.raises(ValueError, match="Password cannot be empty"):
        credentials_service.validate_and_hash_pw(password)


def test_validate_and_hash_pw_too_short(credentials_service):
    """Test validating a password that's too short."""
    password = "short"
    password_length = 8
    
    with pytest.raises(ValueError, match=f"Password cannot be shorter than {password_length}"):
        credentials_service.validate_and_hash_pw(password, password_length)


def test_get_credentials_via_email_existing(credentials_service, mock_cred_repo, mock_credentials):
    """Test getting credentials via email when they exist."""
    email = "user1@example.com"
    mock_cred_repo.get_credentials_by_email.return_value = mock_credentials[0]
    
    result = credentials_service.get_credentials_via_email(email)
    
    mock_cred_repo.get_credentials_by_email.assert_called_once_with(email=email)
    assert result == mock_credentials[0]


def test_get_credentials_via_email_nonexistent(credentials_service, mock_cred_repo):
    """Test getting credentials via email when they don't exist."""
    email = "nonexistent@example.com"
    mock_cred_repo.get_credentials_by_email.return_value = None
    
    with pytest.raises(Exception, match="credentials not found"):
        credentials_service.get_credentials_via_email(email)
    mock_cred_repo.get_credentials_by_email.assert_called_once_with(email=email)


def test_get_email_by_userid_existing(credentials_service, mock_cred_repo):
    """Test getting email by user ID when it exists."""
    user_id = 1
    expected_email = "user1@example.com"
    mock_cred_repo.get_email_by_userid.return_value = expected_email
    
    result = credentials_service.get_email_by_userid(user_id)
    
    mock_cred_repo.get_email_by_userid.assert_called_once_with(user_id=user_id)
    assert result == expected_email


def test_get_email_by_userid_nonexistent(credentials_service, mock_cred_repo):
    """Test getting email by user ID when it doesn't exist."""
    user_id = 999
    mock_cred_repo.get_email_by_userid.return_value = None
    
    with pytest.raises(ValueError, match="Email not found"):
        credentials_service.get_email_by_userid(user_id)
    mock_cred_repo.get_email_by_userid.assert_called_once_with(user_id=user_id)


def test_get_email_by_userid_empty(credentials_service, mock_cred_repo):
    """Test getting email with empty user ID."""
    user_id = None
    
    mock_cred_repo.get_email_by_userid.side_effect = TypeError("NoneType object has no attribute...")
    
    with pytest.raises(TypeError):
        credentials_service.get_email_by_userid(user_id)




def test_generate_random_password(credentials_service):
    """Test generating a random password."""
    length = 15
    
    password1 = credentials_service.generate_random_password(length)
    password2 = credentials_service.generate_random_password(length)
    
    assert isinstance(password1, str)
    assert len(password1) == length
    assert isinstance(password2, str)
    assert len(password2) == length
    assert password1 != password2


def test_reset_password(credentials_service, mock_cred_repo, mock_credentials):
    """Test resetting a password."""
    email = "user1@example.com"
    mock_cred_repo.get_credentials_by_email.return_value = mock_credentials[0]
    
    with patch.object(credentials_service, 'generate_random_password', return_value='new_random_password') as mock_generate, \
         patch.object(credentials_service, 'validate_and_hash_pw', return_value='new_hashed_password') as mock_validate:
        
        result = credentials_service.reset_password(email)
        
        mock_cred_repo.get_credentials_by_email.assert_called_once_with(email=email)
        mock_generate.assert_called_once()
        mock_validate.assert_called_once_with('new_random_password')
        mock_cred_repo.update_credentials.assert_called_once_with(cred_id=1, password='new_hashed_password')
        assert result == 'new_random_password'


def test_reset_password_nonexistent(credentials_service):
    """Test resetting a password for a nonexistent email."""
    email = "nonexistent@example.com"
    
    with patch.object(credentials_service, 'get_credentials_via_email', side_effect=ValueError(f"No credentials found for email: {email}")):
        
        with pytest.raises(ValueError, match=f"No credentials found for email: {email}"):
            credentials_service.reset_password(email)


def test_create_credentials_valid(credentials_service, mock_cred_repo):
    """Test creating credentials with valid data."""
    email = "new_user@example.com"
    password = "valid_password"
    hashed_password = "hashed_valid_password"
    expected_cred_id = 3
    
    with patch.object(credentials_service, 'validate_and_hash_pw', return_value=hashed_password) as mock_validate:
        mock_cred_repo.create_credentials.return_value = expected_cred_id
        
        result = credentials_service.create_credentials(email, password)
        
        mock_validate.assert_called_once_with(password)
        mock_cred_repo.create_credentials.assert_called_once_with(email=email, password=hashed_password)
        assert result == expected_cred_id


def test_create_credentials_empty_email(credentials_service):
    """Test creating credentials with an empty email."""
    email = ""
    password = "valid_password"
    
    with pytest.raises(ValueError, match="Email or Password cannot be empty"):
        credentials_service.create_credentials(email, password)


def test_create_credentials_empty_password(credentials_service):
    """Test creating credentials with an empty password."""
    email = "valid@example.com"
    password = ""
    
    with pytest.raises(ValueError, match="Email or Password cannot be empty"):
        credentials_service.create_credentials(email, password)


def test_create_credentials_error(credentials_service, mock_cred_repo):
    """Test error handling when repository fails to create credentials."""
    email = "new_user@example.com"
    password = "valid_password"
    hashed_password = "hashed_valid_password"
    
    with patch.object(credentials_service, 'validate_and_hash_pw', return_value=hashed_password) as mock_validate:
        mock_cred_repo.create_credentials.return_value = None
        
        with pytest.raises(RuntimeError, match="Cant create credentials"):
            credentials_service.create_credentials(email, password)
        
        mock_validate.assert_called_once_with(password)
        mock_cred_repo.create_credentials.assert_called_once_with(email=email, password=hashed_password)






def test_change_password_valid(credentials_service, mock_cred_repo, mock_credentials):
    """Test changing password with valid data."""
    user_id = 1
    new_password = "new_valid_password"
    confirm_new_password = "new_valid_password"
    hashed_password = "hashed_new_valid_password"
    
    mock_cred_repo.get_credentials_by_id.return_value = mock_credentials[0]
    
    with patch.object(credentials_service, 'validate_and_hash_pw', return_value=hashed_password) as mock_validate:
        
        credentials_service.change_password(user_id, new_password, confirm_new_password)
        
        mock_cred_repo.get_credentials_by_id.assert_called_once_with(user_id=user_id)
        mock_validate.assert_called_once_with(new_password)
        mock_cred_repo.update_credentials.assert_called_once_with(cred_id=1, password=hashed_password)


def test_change_password_user_not_found(credentials_service, mock_cred_repo):
    """Test changing password for a nonexistent user."""
    user_id = 999
    new_password = "new_valid_password"
    confirm_new_password = "new_valid_password"
    
    mock_cred_repo.get_credentials_by_id.return_value = None
    
    with pytest.raises(ValueError, match="User not found"):
        credentials_service.change_password(user_id, new_password, confirm_new_password)
    
    mock_cred_repo.get_credentials_by_id.assert_called_once_with(user_id=user_id)


def test_change_password_mismatch(credentials_service, mock_cred_repo, mock_credentials):
    """Test changing password with mismatched passwords."""
    user_id = 1
    new_password = "new_valid_password"
    confirm_new_password = "different_password"
    
    mock_cred_repo.get_credentials_by_id.return_value = mock_credentials[0]
    
    with pytest.raises(ValueError, match="New passwords do not match"):
        credentials_service.change_password(user_id, new_password, confirm_new_password)
    
    mock_cred_repo.get_credentials_by_id.assert_called_once_with(user_id=user_id)




