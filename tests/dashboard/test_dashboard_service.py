import pytest
from unittest.mock import MagicMock
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService
from blueprints.dashboard.service import DashboardService  

@pytest.fixture
def mock_user_service():
    return MagicMock(spec=UserService)

@pytest.fixture
def mock_mfa_service():
    return MagicMock(spec=MFAservice)

@pytest.fixture
def dashboard_service(mock_user_service, mock_mfa_service):
    return DashboardService(user_service=mock_user_service, mfa_service=mock_mfa_service)

def test_get_username_by_userid_success(dashboard_service, mock_user_service):
    """Test successful username retrieval."""
    user_id = 123
    expected_username = "testuser"
    
    mock_user_service.get_username_by_userid.return_value = expected_username
    
    result = dashboard_service.get_username_by_userid(user_id)
    
    assert result == expected_username
    mock_user_service.get_username_by_userid.assert_called_once_with(user_id=user_id)

def test_get_username_by_userid_not_found(dashboard_service, mock_user_service):
    """Test username retrieval for non-existent user."""
    user_id = 999
    
    mock_user_service.get_username_by_userid.return_value = None
    
    result = dashboard_service.get_username_by_userid(user_id)
    
    assert result == "Unknown user"
    mock_user_service.get_username_by_userid.assert_called_once_with(user_id=user_id)

def test_get_username_by_userid_empty_string(dashboard_service, mock_user_service):
    """Test username retrieval returning empty string."""
    user_id = 456
    
    mock_user_service.get_username_by_userid.return_value = ""
    
    result = dashboard_service.get_username_by_userid(user_id)
    
    assert result == "Unknown user"  
    mock_user_service.get_username_by_userid.assert_called_once_with(user_id=user_id)

def test_is_mfa_enabled_true(dashboard_service, mock_mfa_service):
    """Test when MFA is enabled for a user."""
    user_id = 123
    
    mock_mfa_service.get_mfa_details_via_user_id.return_value = {"secret": "ABCDEF123456", "enabled": True}
    
    result = dashboard_service.is_mfa_enabled(user_id)
    
    assert result is True
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)

def test_is_mfa_enabled_false_none(dashboard_service, mock_mfa_service):
    """Test when MFA is not enabled (None returned)."""
    user_id = 456
    
    mock_mfa_service.get_mfa_details_via_user_id.return_value = None
    
    result = dashboard_service.is_mfa_enabled(user_id)
    
    assert result is False
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)

def test_is_mfa_enabled_false_empty(dashboard_service, mock_mfa_service):
    """Test when MFA is not enabled (empty dict returned)."""
    user_id = 789
    
    mock_mfa_service.get_mfa_details_via_user_id.return_value = {}
    
    result = dashboard_service.is_mfa_enabled(user_id)
    
    assert result is False
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)

def test_is_mfa_enabled_returns_boolean(dashboard_service, mock_mfa_service):
    """Test that the method always returns a boolean regardless of input."""
    user_id = 123
    
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
        mock_mfa_service.get_mfa_details_via_user_id.return_value = mfa_return
        
        result = dashboard_service.is_mfa_enabled(user_id)
        
        assert result is expected_result
        assert isinstance(result, bool)

def test_integration_both_methods(dashboard_service, mock_user_service, mock_mfa_service):
    """Test both methods together in a single test."""
    user_id = 123
    expected_username = "testuser"
    
    mock_user_service.get_username_by_userid.return_value = expected_username
    mock_mfa_service.get_mfa_details_via_user_id.return_value = {"secret": "ABCDEF123456"}
    
    username = dashboard_service.get_username_by_userid(user_id)
    mfa_enabled = dashboard_service.is_mfa_enabled(user_id)
    
    assert username == expected_username
    assert mfa_enabled is True
    
    mock_user_service.get_username_by_userid.assert_called_once_with(user_id=user_id)
    mock_mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)

def test_service_initialization():
    """Test service initialization with default and custom parameters."""
    user_service_mock = MagicMock(spec=UserService)
    mfa_service_mock = MagicMock(spec=MFAservice)
    
    service = DashboardService(user_service=user_service_mock, mfa_service=mfa_service_mock)
    
    assert service.user_service == user_service_mock
    assert service.mfa_service == mfa_service_mock
    
    service_default_mfa = DashboardService(user_service=user_service_mock)
    
    assert service_default_mfa.user_service == user_service_mock
    assert isinstance(service_default_mfa.mfa_service, type(MFAservice))