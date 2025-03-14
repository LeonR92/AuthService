import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from blueprints.users.user_service import UserService



@pytest.fixture
def mock_user_repo():
    return Mock()


@pytest.fixture
def mock_cred_service():
    return Mock()


@pytest.fixture
def mock_mfa_service():
    return Mock()


@pytest.fixture
def user_service(mock_user_repo, mock_cred_service, mock_mfa_service):
    return UserService(
        user_repo=mock_user_repo,
        cred_service=mock_cred_service,
        mfa_service=mock_mfa_service
    )



def test_get_user_by_id_success(user_service, mock_user_repo):

    user_id = 1
    mock_user = Mock()
    mock_user_repo.get_user_by_id.return_value = mock_user
    
    result = user_service.get_user_by_id(user_id)
    
    mock_user_repo.get_user_by_id.assert_called_once_with(user_id)
    assert result == mock_user


def test_get_user_by_id_not_found(user_service, mock_user_repo):
  
    user_id = 999
    mock_user_repo.get_user_by_id.return_value = None
    

    with pytest.raises(ValueError, match=f"User with ID {user_id} not found"):
        user_service.get_user_by_id(user_id)


def test_get_userid_by_email_success(user_service, mock_user_repo):
    email = "test@example.com"
    mock_user_repo.get_userid_by_email.return_value = (1,)
    
    result = user_service.get_userid_by_email(email)
    
    mock_user_repo.get_userid_by_email.assert_called_once_with(email=email)
    assert result == 1


def test_get_userid_by_email_not_found(user_service, mock_user_repo):
    email = "nonexistent@example.com"
    mock_user_repo.get_userid_by_email.return_value = None
    
    result = user_service.get_userid_by_email(email)
    
    mock_user_repo.get_userid_by_email.assert_called_once_with(email=email)
    assert result is None


def test_get_userid_by_email_empty_email(user_service):
    email = ""
    
    with pytest.raises(ValueError, match="Email is required"):
        user_service.get_userid_by_email(email)


def test_get_username_by_userid_success(user_service, mock_user_repo):
    user_id = 1
    mock_user_repo.get_username_by_userid.return_value = ("John", "Doe")
    
    result = user_service.get_username_by_userid(user_id)
    
    mock_user_repo.get_username_by_userid.assert_called_once_with(user_id=user_id)
    assert result == "John Doe"


def test_get_username_by_userid_no_id(user_service):
    user_id = None
    
    with pytest.raises(ValueError, match="User ID must be provided."):
        user_service.get_username_by_userid(user_id)


def test_get_username_by_userid_not_found(user_service, mock_user_repo):
    user_id = 999
    mock_user_repo.get_username_by_userid.return_value = None
    
    with pytest.raises(ValueError, match=f"User with ID {user_id} not found."):
        user_service.get_username_by_userid(user_id)


def test_get_username_by_userid_incomplete_data(user_service, mock_user_repo):
    user_id = 1
    mock_user_repo.get_username_by_userid.return_value = ("John", None)
    
    with pytest.raises(ValueError, match=f"Incomplete name data for user ID {user_id}."):
        user_service.get_username_by_userid(user_id)




def test_get_full_user_details_by_id_success(user_service, mock_user_repo):
    user_id = 1
    mock_user_details = Mock()
    mock_user_repo.get_full_user_details_by_id.return_value = mock_user_details
    
    result = user_service.get_full_user_details_by_id(user_id)
    
    # Assert
    mock_user_repo.get_full_user_details_by_id.assert_called_once_with(user_id)
    assert result == mock_user_details


def test_get_full_user_details_by_id_not_found(user_service, mock_user_repo):
    # Arrange
    user_id = 999
    mock_user_repo.get_full_user_details_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match=f"User with ID {user_id} not found"):
        user_service.get_full_user_details_by_id(user_id)


# Tests for create_user
def test_create_user_success(user_service, mock_user_repo, mock_cred_service, mock_mfa_service):
    # Arrange
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    password = "securepass"
    mfa_enabled = "false"
    country = "US"
    dob = "1990-01-01"
    
    # Email not already registered
    mock_user_repo.get_user_by_email.return_value = None
    
    # Mock service returns
    mock_cred_service.create_credentials.return_value = 10
    mock_user_repo.create_user.return_value = 1
    
    # Act
    with patch('blueprints.users.user_service.is_valid_string_value', return_value=True):
        result = user_service.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            mfa_enabled=mfa_enabled,
            country=country,
            dob=dob
        )
    
    # Assert
    mock_user_repo.get_user_by_email.assert_called_once_with(email)
    mock_cred_service.create_credentials.assert_called_once_with(email=email, password=password)
    mock_mfa_service.create_mfa_entry.assert_not_called()
    
    mock_user_repo.create_user.assert_called_once()
    assert mock_user_repo.create_user.call_args[1]['first_name'] == first_name
    assert mock_user_repo.create_user.call_args[1]['last_name'] == last_name
    assert mock_user_repo.create_user.call_args[1]['country'] == country
    assert isinstance(mock_user_repo.create_user.call_args[1]['dob'], datetime)
    assert mock_user_repo.create_user.call_args[1]['credentials_id'] == 10
    assert mock_user_repo.create_user.call_args[1]['mfa_id'] is None
    
    assert result == 1


def test_create_user_with_mfa_enabled(user_service, mock_user_repo, mock_cred_service, mock_mfa_service):
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    password = "securepass"
    mfa_enabled = "True"  
    country = "US"
    dob = "1990-01-01"
    
    mock_user_repo.get_user_by_email.return_value = None
    
    mock_cred_service.create_credentials.return_value = 10
    mock_mfa_service.create_mfa_entry.return_value = 20
    mock_user_repo.create_user.return_value = 1
    
    # Act
    with patch('blueprints.users.user_service.is_valid_string_value', return_value=True):
        result = user_service.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            mfa_enabled=mfa_enabled,
            country=country,
            dob=dob
        )
    
    # Assert
    mock_mfa_service.create_mfa_entry.assert_called_once()
    mock_user_repo.create_user.assert_called_once()
    assert mock_user_repo.create_user.call_args[1]['mfa_id'] == 20
    assert result == 1


def test_create_user_email_already_registered(user_service, mock_user_repo):
    # Arrange
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    password = "securepass"
    mfa_enabled = "false"
    country = "US"
    dob = "1990-01-01"
    
    # Email already registered
    mock_user_repo.get_user_by_email.return_value = Mock()
    
    # Act & Assert
    with patch('blueprints.users.user_service.is_valid_string_value', return_value=True):
        with pytest.raises(ValueError, match="Email is already registered"):
            user_service.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                mfa_enabled=mfa_enabled,
                country=country,
                dob=dob
            )


def test_create_user_invalid_name(user_service):
    # Arrange
    first_name = ""  
    last_name = "Doe"
    email = "john.doe@example.com"
    password = "securepass"
    mfa_enabled = "false"
    country = "US"
    dob = "1990-01-01"
    
    # Act & Assert
    with patch('blueprints.users.user_service.is_valid_string_value', side_effect=[False, True, True]):
        with pytest.raises(ValueError, match="First and last name cannot be empty"):
            user_service.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                mfa_enabled=mfa_enabled,
                country=country,
                dob=dob
            )


def test_create_user_empty_dob(user_service, mock_user_repo, mock_cred_service):
    # Arrange
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    password = "securepass"
    mfa_enabled = "false"
    country = "US"
    dob = "" 
    
    mock_user_repo.get_user_by_email.return_value = None
    
    mock_cred_service.create_credentials.return_value = 10
    mock_user_repo.create_user.return_value = 1
    
    with patch('blueprints.users.user_service.is_valid_string_value', return_value=True):
        result = user_service.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            mfa_enabled=mfa_enabled,
            country=country,
            dob=dob
        )
    
    mock_user_repo.create_user.assert_called_once()
    assert mock_user_repo.create_user.call_args[1]['dob'] is None
    assert result == 1


def test_create_user_error_creating(user_service, mock_user_repo, mock_cred_service):
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    password = "securepass"
    mfa_enabled = "false"
    country = "US"
    dob = "1990-01-01"
    
    mock_user_repo.get_user_by_email.return_value = None
    
    mock_cred_service.create_credentials.return_value = 10
    mock_user_repo.create_user.return_value = None  
    
    with patch('blueprints.users.user_service.is_valid_string_value', return_value=True):
        with pytest.raises(RuntimeError, match="Error creating user"):
            user_service.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                mfa_enabled=mfa_enabled,
                country=country,
                dob=dob
            )


# Tests for activate_mfa
def test_activate_mfa_no_existing_mfa(user_service, mock_user_repo, mock_mfa_service):
    user_id = 1
    mock_mfa_service.get_mfa_details_via_user_id.return_value = None
    mock_mfa_service.create_mfa_entry.return_value = 20
    
    user_service.activate_mfa(user_id)
    
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)
    mock_mfa_service.create_mfa_entry.assert_called_once()
    mock_user_repo.update.assert_called_once_with(user_id=user_id, mfa_id=20)


def test_activate_mfa_existing_mfa_without_id(user_service, mock_user_repo, mock_mfa_service):
    user_id = 1
    mock_mfa = Mock()
    mock_mfa.id = None
    mock_mfa_service.get_mfa_details_via_user_id.return_value = mock_mfa
    mock_mfa_service.create_mfa_entry.return_value = 20
    
    user_service.activate_mfa(user_id)
    
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)
    mock_mfa_service.create_mfa_entry.assert_called_once()
    mock_user_repo.update.assert_called_once_with(user_id=user_id, mfa_id=20)


def test_activate_mfa_existing_mfa_with_id(user_service, mock_user_repo, mock_mfa_service):
    user_id = 1
    mock_mfa = Mock()
    mock_mfa.id = 20
    mock_mfa_service.get_mfa_details_via_user_id.return_value = mock_mfa
    
    user_service.activate_mfa(user_id)
    
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)
    mock_mfa_service.create_mfa_entry.assert_not_called()
    mock_user_repo.update.assert_not_called()

