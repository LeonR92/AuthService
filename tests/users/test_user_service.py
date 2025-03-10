import pytest
from unittest.mock import MagicMock
from datetime import datetime
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService
from blueprints.users.user_repository import UserRepository
from blueprints.users.models import User
from blueprints.users.crendentials_service import CredentialsService


@pytest.fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)

@pytest.fixture
def mock_cred_service():
    return MagicMock(spec=CredentialsService)

@pytest.fixture
def mock_mfa_service():
    return MagicMock(spec=MFAservice)

@pytest.fixture
def user_service(mock_user_repo):
    return UserService(user_repo=mock_user_repo, cred_service=mock_cred_service, mfa_service=mock_mfa_service )

@pytest.fixture
def sample_user():
    return User(id=1, first_name="John", last_name="Doe", country="Germany", dob=datetime(1990, 5, 15))

def test_get_user_by_id_valid(user_service, mock_user_repo, sample_user):
    mock_user_repo.get_user_by_id.return_value = sample_user

    result = user_service.get_user_by_id(user_id=1)

    assert result == sample_user
    mock_user_repo.get_user_by_id.assert_called_once_with(1)

def test_get_user_by_id_not_found(user_service, mock_user_repo):
    mock_user_repo.get_user_by_id.return_value = None

    with pytest.raises(ValueError, match="User with ID 999 not found"):
        user_service.get_user_by_id(user_id=999)


@pytest.mark.parametrize("first_name, last_name", [
    ("", "Doe"),
    ("Jane", ""),
    (" ", "Doe"),
    ("Jane", " "),
])
def test_create_user_invalid_names(user_service, first_name, last_name):
    with pytest.raises(ValueError):
        user_service.create_user("Jane", "Doe", "USA", datetime(1995, 7, 20),'true','Germany','')

def test_update_user_valid(user_service, mock_user_repo, sample_user):
    updated_sample_user = User(id=1, first_name="UpdatedName", last_name="Doe", country="Germany", dob=datetime(1990, 5, 15))
    mock_user_repo.update.return_value = updated_sample_user

    updated_user = user_service.update_user(user_id=1, first_name="UpdatedName")

    assert updated_user.first_name == "UpdatedName"
    mock_user_repo.update.assert_called_once_with(1, first_name="UpdatedName")

def test_delete_user_valid(user_service, mock_user_repo):
    mock_user_repo.delete.return_value = True

    result = user_service.delete_user(user_id=1)

    assert result is True
    mock_user_repo.delete.assert_called_once_with(1)
