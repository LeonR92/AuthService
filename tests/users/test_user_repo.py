import pytest
from unittest.mock import Mock, create_autospec
from sqlalchemy.orm import Session

from blueprints.users.models import User, Credentials
from blueprints.users.user_repository import UserRepository


@pytest.fixture
def mock_read_session():
    session = create_autospec(Session)
    return session


@pytest.fixture
def mock_write_session():
    session = create_autospec(Session)
    return session


@pytest.fixture
def user_repository(mock_read_session, mock_write_session):
    return UserRepository(read_db_session=mock_read_session, write_db_session=mock_write_session)


@pytest.fixture
def sample_user():
    user = Mock(spec=User)
    user.id = 1
    user.first_name = "John"
    user.last_name = "Doe"
    user.credentials_id = 10
    return user


@pytest.fixture
def sample_credentials():
    credentials = Mock(spec=Credentials)
    credentials.id = 10
    credentials.email = "john.doe@example.com"
    return credentials


def test_get_user_by_id(user_repository, mock_read_session, sample_user):
    user_id = 1
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = sample_user
    mock_query.filter.return_value = mock_filter
    mock_read_session.query.return_value = mock_query
    
    result = user_repository.get_user_by_id(user_id)
    
    mock_read_session.query.assert_called_once_with(User)
    mock_query.filter.assert_called_once()
    assert result == sample_user


def test_get_user_by_id_not_found(user_repository, mock_read_session):
    user_id = 999
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_read_session.query.return_value = mock_query
    
    result = user_repository.get_user_by_id(user_id)
    
    mock_read_session.query.assert_called_once_with(User)
    mock_query.filter.assert_called_once()
    assert result is None


def test_get_userid_by_email(user_repository, mock_read_session, sample_user):
    email = "john.doe@example.com"
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = (1,)  
    mock_join.filter.return_value = mock_filter
    mock_query.join.return_value = mock_join
    mock_read_session.query.return_value = mock_query
    
    result = user_repository.get_userid_by_email(email)
    
    mock_read_session.query.assert_called_once_with(User.id)
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    assert result == (1,)


def test_get_username_by_userid(user_repository, mock_read_session):
    user_id = 1
    expected_result = ("John", "Doe")
    
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = expected_result
    mock_query.filter.return_value = mock_filter
    mock_read_session.query.return_value = mock_query
    
    result = user_repository.get_username_by_userid(user_id)
    
    mock_read_session.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == expected_result


def test_get_username_by_userid_not_found(user_repository, mock_read_session):
    user_id = 999
    
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_read_session.query.return_value = mock_query
    
    result = user_repository.get_username_by_userid(user_id)
    
    mock_read_session.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result is None




def test_get_full_user_details_by_id(user_repository, mock_read_session, sample_user, sample_credentials):
    user_id = 1
    expected_result = (sample_user, sample_credentials)
    
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = expected_result
    mock_join.filter.return_value = mock_filter
    mock_query.join.return_value = mock_join
    mock_read_session.query.return_value = mock_query
    
    result = user_repository.get_full_user_details_by_id(user_id)
    
    mock_read_session.query.assert_called_once()
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    assert result == expected_result


def test_get_user_by_email(user_repository, mock_read_session, sample_user):
    email = "john.doe@example.com"
    
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = sample_user
    mock_join.filter.return_value = mock_filter
    mock_query.join.return_value = mock_join
    mock_read_session.query.return_value = mock_query
    
    result = user_repository.get_user_by_email(email)
    
    mock_read_session.query.assert_called_once_with(User)
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    assert result == sample_user


def test_get_user_by_email_not_found(user_repository, mock_read_session):
    email = "nonexistent@example.com"
    
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_join.filter.return_value = mock_filter
    mock_query.join.return_value = mock_join
    mock_read_session.query.return_value = mock_query
    
    result = user_repository.get_user_by_email(email)
    
    mock_read_session.query.assert_called_once_with(User)
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    assert result is None


def test_create_user(user_repository, mock_write_session):
    user_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "credentials_id": 20
    }
    
    
    original_add = mock_write_session.add
    added_user = None
    
    def side_effect_add(user):
        nonlocal added_user
        added_user = user
        return original_add(user)
    
    mock_write_session.add = Mock(side_effect=side_effect_add)
    
    mock_write_session.refresh = Mock(side_effect=lambda user: setattr(user, 'id', 2))
    
    result = user_repository.create_user(**user_data)
    
    assert mock_write_session.add.called
    assert mock_write_session.commit.called
    assert mock_write_session.refresh.called
    
    assert added_user is not None
    for key, value in user_data.items():
        assert getattr(added_user, key) == value
    
    assert result == 2


def test_delete_user_exists(user_repository, mock_write_session, sample_user):
    user_id = 1
    user_repository.get_user_by_id = Mock(return_value=sample_user)
    
    result = user_repository.delete(user_id)
    
    user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_write_session.delete.assert_called_once_with(sample_user)
    mock_write_session.commit.assert_called_once()
    assert result is True


def test_delete_user_not_exists(user_repository, mock_write_session):
    user_id = 999
    user_repository.get_user_by_id = Mock(return_value=None)
    
    result = user_repository.delete(user_id)
    
    user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_write_session.delete.assert_not_called()
    mock_write_session.commit.assert_not_called()
    assert result is True


def test_update_user_exists(user_repository, mock_write_session, sample_user):
    user_id = 1
    update_data = {
        "first_name": "Jane",
        "last_name": "Doe"
    }
    
    updated_user = Mock(spec=User)
    updated_user.id = user_id
    updated_user.first_name = "Jane"
    updated_user.last_name = "Doe"
    
    user_repository.get_user_by_id = Mock(return_value=sample_user)
    mock_write_session.merge.return_value = updated_user
    
    result = user_repository.update(user_id, **update_data)
    
    user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_write_session.merge.assert_called_once_with(sample_user)
    mock_write_session.commit.assert_called_once()
    mock_write_session.refresh.assert_called_once_with(updated_user)
    assert result == updated_user


def test_update_user_not_exists(user_repository, mock_write_session):
    user_id = 999
    update_data = {
        "first_name": "Jane",
        "last_name": "Doe"
    }
    
    user_repository.get_user_by_id = Mock(return_value=None)
    
    result = user_repository.update(user_id, **update_data)
    
    user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_write_session.merge.assert_not_called()
    mock_write_session.commit.assert_not_called()
    mock_write_session.refresh.assert_not_called()
    assert result is None