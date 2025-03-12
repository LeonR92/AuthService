import pytest
from unittest.mock import Mock, create_autospec
from sqlalchemy.orm import Session

from blueprints.users.models import User, Credentials
from blueprints.users.user_repository import UserRepository


# Fixtures
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


# Tests for get_user_by_id
def test_get_user_by_id(user_repository, mock_read_session, sample_user):
    # Arrange
    user_id = 1
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = sample_user
    mock_query.filter.return_value = mock_filter
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_user_by_id(user_id)
    
    # Assert
    mock_read_session.query.assert_called_once_with(User)
    mock_query.filter.assert_called_once()
    assert result == sample_user


def test_get_user_by_id_not_found(user_repository, mock_read_session):
    # Arrange
    user_id = 999
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_user_by_id(user_id)
    
    # Assert
    mock_read_session.query.assert_called_once_with(User)
    mock_query.filter.assert_called_once()
    assert result is None


# Tests for get_userid_by_email
def test_get_userid_by_email(user_repository, mock_read_session, sample_user):
    # Arrange
    email = "john.doe@example.com"
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = (1,)  # Return a tuple with user ID
    mock_join.filter.return_value = mock_filter
    mock_query.join.return_value = mock_join
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_userid_by_email(email)
    
    # Assert
    mock_read_session.query.assert_called_once_with(User.id)
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    assert result == (1,)


# Tests for get_username_by_userid
def test_get_username_by_userid(user_repository, mock_read_session):
    # Arrange
    user_id = 1
    expected_result = ("John", "Doe")
    
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = expected_result
    mock_query.filter.return_value = mock_filter
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_username_by_userid(user_id)
    
    # Assert
    mock_read_session.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == expected_result


def test_get_username_by_userid_not_found(user_repository, mock_read_session):
    # Arrange
    user_id = 999
    
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_username_by_userid(user_id)
    
    # Assert
    mock_read_session.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result is None


# Tests for get_all_users
def test_get_all_users(user_repository, mock_read_session, sample_user):
    # Arrange
    mock_query = Mock()
    mock_query.all.return_value = [sample_user]
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_all_users()
    
    # Assert
    mock_read_session.query.assert_called_once_with(User)
    mock_query.all.assert_called_once()
    assert len(result) == 1
    assert result[0] == sample_user


# Tests for get_full_user_details_by_id
def test_get_full_user_details_by_id(user_repository, mock_read_session, sample_user, sample_credentials):
    # Arrange
    user_id = 1
    expected_result = (sample_user, sample_credentials)
    
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = expected_result
    mock_join.filter.return_value = mock_filter
    mock_query.join.return_value = mock_join
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_full_user_details_by_id(user_id)
    
    # Assert
    mock_read_session.query.assert_called_once()
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    assert result == expected_result


# Tests for get_user_by_email
def test_get_user_by_email(user_repository, mock_read_session, sample_user):
    # Arrange
    email = "john.doe@example.com"
    
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = sample_user
    mock_join.filter.return_value = mock_filter
    mock_query.join.return_value = mock_join
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_user_by_email(email)
    
    # Assert
    mock_read_session.query.assert_called_once_with(User)
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    assert result == sample_user


def test_get_user_by_email_not_found(user_repository, mock_read_session):
    # Arrange
    email = "nonexistent@example.com"
    
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_join.filter.return_value = mock_filter
    mock_query.join.return_value = mock_join
    mock_read_session.query.return_value = mock_query
    
    # Act
    result = user_repository.get_user_by_email(email)
    
    # Assert
    mock_read_session.query.assert_called_once_with(User)
    mock_query.join.assert_called_once()
    mock_join.filter.assert_called_once()
    assert result is None


# Tests for create_user
def test_create_user(user_repository, mock_write_session):
    # Arrange
    user_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "credentials_id": 20
    }
    
    # We need to capture the user that gets created
    # instead of trying to mock the User constructor
    
    # Act
    # Use the spy pattern to capture what gets added to the session
    original_add = mock_write_session.add
    added_user = None
    
    def side_effect_add(user):
        nonlocal added_user
        added_user = user
        return original_add(user)
    
    mock_write_session.add = Mock(side_effect=side_effect_add)
    
    # Set up the id for the mock user that will be returned
    mock_write_session.refresh = Mock(side_effect=lambda user: setattr(user, 'id', 2))
    
    # Call the method
    result = user_repository.create_user(**user_data)
    
    # Assert
    assert mock_write_session.add.called
    assert mock_write_session.commit.called
    assert mock_write_session.refresh.called
    
    # Check that the user was created with the correct attributes
    assert added_user is not None
    for key, value in user_data.items():
        assert getattr(added_user, key) == value
    
    assert result == 2


# Tests for delete
def test_delete_user_exists(user_repository, mock_write_session, sample_user):
    # Arrange
    user_id = 1
    user_repository.get_user_by_id = Mock(return_value=sample_user)
    
    # Act
    result = user_repository.delete(user_id)
    
    # Assert
    user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_write_session.delete.assert_called_once_with(sample_user)
    mock_write_session.commit.assert_called_once()
    assert result is True


def test_delete_user_not_exists(user_repository, mock_write_session):
    # Arrange
    user_id = 999
    user_repository.get_user_by_id = Mock(return_value=None)
    
    # Act
    result = user_repository.delete(user_id)
    
    # Assert
    user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_write_session.delete.assert_not_called()
    mock_write_session.commit.assert_not_called()
    assert result is True


# Tests for update
def test_update_user_exists(user_repository, mock_write_session, sample_user):
    # Arrange
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
    
    # Act
    result = user_repository.update(user_id, **update_data)
    
    # Assert
    user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_write_session.merge.assert_called_once_with(sample_user)
    mock_write_session.commit.assert_called_once()
    mock_write_session.refresh.assert_called_once_with(updated_user)
    assert result == updated_user


def test_update_user_not_exists(user_repository, mock_write_session):
    # Arrange
    user_id = 999
    update_data = {
        "first_name": "Jane",
        "last_name": "Doe"
    }
    
    user_repository.get_user_by_id = Mock(return_value=None)
    
    # Act
    result = user_repository.update(user_id, **update_data)
    
    # Assert
    user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_write_session.merge.assert_not_called()
    mock_write_session.commit.assert_not_called()
    mock_write_session.refresh.assert_not_called()
    assert result is None