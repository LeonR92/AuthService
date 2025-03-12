import pytest
from unittest.mock import MagicMock
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService
from blueprints.dashboard.service import DashboardService  # Adjust import path as needed

# Fixtures
@pytest.fixture
def mock_user_service():
    return MagicMock(spec=UserService)

@pytest.fixture
def mock_mfa_service():
    return MagicMock(spec=MFAservice)

@pytest.fixture
def dashboard_service(mock_user_service, mock_mfa_service):
    return DashboardService(user_service=mock_user_service, mfa_service=mock_mfa_service)

# Test get_username_by_userid method
def test_get_username_by_userid_success(dashboard_service, mock_user_service):
    """Test successful username retrieval."""
    user_id = 123
    expected_username = "testuser"
    
    # Configure mock to return a username
    mock_user_service.get_username_by_userid.return_value = expected_username
    
    # Test the method
    result = dashboard_service.get_username_by_userid(user_id)
    
    # Verify the result and that the mock was called correctly
    assert result == expected_username
    mock_user_service.get_username_by_userid.assert_called_once_with(user_id=user_id)

def test_get_username_by_userid_not_found(dashboard_service, mock_user_service):
    """Test username retrieval for non-existent user."""
    user_id = 999
    
    # Configure mock to return None (user not found)
    mock_user_service.get_username_by_userid.return_value = None
    
    # Test the method
    result = dashboard_service.get_username_by_userid(user_id)
    
    # Verify the result and that the mock was called correctly
    assert result == "Unknown user"
    mock_user_service.get_username_by_userid.assert_called_once_with(user_id=user_id)

def test_get_username_by_userid_empty_string(dashboard_service, mock_user_service):
    """Test username retrieval returning empty string."""
    user_id = 456
    
    # Configure mock to return an empty string
    mock_user_service.get_username_by_userid.return_value = ""
    
    # Test the method
    result = dashboard_service.get_username_by_userid(user_id)
    
    # Verify the result and that the mock was called correctly
    # Empty string is treated as falsy, so it should return "Unknown user"
    assert result == "Unknown user"  
    mock_user_service.get_username_by_userid.assert_called_once_with(user_id=user_id)

# Test is_mfa_enabled method
def test_is_mfa_enabled_true(dashboard_service, mock_mfa_service):
    """Test when MFA is enabled for a user."""
    user_id = 123
    
    # Configure mock to return MFA details (any non-empty value)
    mock_mfa_service.get_mfa_details_via_user_id.return_value = {"secret": "ABCDEF123456", "enabled": True}
    
    # Test the method
    result = dashboard_service.is_mfa_enabled(user_id)
    
    # Verify the result and that the mock was called correctly
    assert result is True
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)

def test_is_mfa_enabled_false_none(dashboard_service, mock_mfa_service):
    """Test when MFA is not enabled (None returned)."""
    user_id = 456
    
    # Configure mock to return None (no MFA details)
    mock_mfa_service.get_mfa_details_via_user_id.return_value = None
    
    # Test the method
    result = dashboard_service.is_mfa_enabled(user_id)
    
    # Verify the result and that the mock was called correctly
    assert result is False
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)

def test_is_mfa_enabled_false_empty(dashboard_service, mock_mfa_service):
    """Test when MFA is not enabled (empty dict returned)."""
    user_id = 789
    
    # Configure mock to return an empty dict
    mock_mfa_service.get_mfa_details_via_user_id.return_value = {}
    
    # Test the method
    result = dashboard_service.is_mfa_enabled(user_id)
    
    # Verify the result and that the mock was called correctly
    assert result is False
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)

def test_is_mfa_enabled_returns_boolean(dashboard_service, mock_mfa_service):
    """Test that the method always returns a boolean regardless of input."""
    user_id = 123
    
    # Test various non-boolean return values from the service
    test_cases = [
        ("String value", True),
        (42, True),
        ({}, False),
        ([], False),
        (None, False),
        (0, False),
        (False, False),
        (True, True),
    ]
    
    for mfa_return, expected_result in test_cases:
        # Configure mock
        mock_mfa_service.get_mfa_details_via_user_id.return_value = mfa_return
        
        # Test the method
        result = dashboard_service.is_mfa_enabled(user_id)
        
        # Verify the result is a boolean of the expected value
        assert result is expected_result
        assert isinstance(result, bool)

# Integration tests
def test_integration_both_methods(dashboard_service, mock_user_service, mock_mfa_service):
    """Test both methods together in a single test."""
    user_id = 123
    expected_username = "testuser"
    
    # Configure mocks
    mock_user_service.get_username_by_userid.return_value = expected_username
    mock_mfa_service.get_mfa_details_via_user_id.return_value = {"secret": "ABCDEF123456"}
    
    # Test both methods
    username = dashboard_service.get_username_by_userid(user_id)
    mfa_enabled = dashboard_service.is_mfa_enabled(user_id)
    
    # Verify results
    assert username == expected_username
    assert mfa_enabled is True
    
    # Verify mocks were called correctly
    mock_user_service.get_username_by_userid.assert_called_once_with(user_id=user_id)
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)

def test_service_initialization():
    """Test service initialization with default and custom parameters."""
    # Test with custom services
    user_service_mock = MagicMock(spec=UserService)
    mfa_service_mock = MagicMock(spec=MFAservice)
    
    service = DashboardService(user_service=user_service_mock, mfa_service=mfa_service_mock)
    
    assert service.user_service == user_service_mock
    assert service.mfa_service == mfa_service_mock
    
    # Test with only user service specified (mfa_service would use the default)
    service_default_mfa = DashboardService(user_service=user_service_mock)
    
    assert service_default_mfa.user_service == user_service_mock
    assert isinstance(service_default_mfa.mfa_service, type(MFAservice))