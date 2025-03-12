import pytest
from unittest.mock import MagicMock

from core.di import (
    create_user_service,
    create_mfa_service,
    create_credentials_service,
    create_auth_service,
    create_dashboard_service,
    create_user_repository,
    create_credentials_repository,
    create_mfa_repository
)
from blueprints.users.user_service import UserService
from blueprints.users.mfa_service import MFAservice
from blueprints.users.crendentials_service import CredentialsService
from blueprints.auth.service import AuthService
from blueprints.dashboard.service import DashboardService
from blueprints.users.user_repository import UserRepository
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.mfa_repository import MFARepository


@pytest.fixture
def mock_db():
    """Mock database connections."""
    write_db = MagicMock()
    read_db = MagicMock()
    return write_db, read_db


def test_create_user_repository(mock_db):
    """Test creating a user repository."""
    write_db, read_db = mock_db
    
    user_repo = create_user_repository(write_db, read_db)
    
    assert isinstance(user_repo, UserRepository)
    assert user_repo.write_db_session == write_db
    assert user_repo.read_db_session == read_db


def test_create_credentials_repository(mock_db):
    """Test creating a credentials repository."""
    write_db, read_db = mock_db
    
    cred_repo = create_credentials_repository(write_db, read_db)
    
    assert isinstance(cred_repo, CredentialsRepository)
    # Check that the db sessions were passed correctly
    # Note: This assumes CredentialsRepository uses these attribute names
    # Adjust if your actual implementation uses different attribute names
    assert cred_repo.write_db_session == write_db
    assert cred_repo.read_db_session == read_db


def test_create_mfa_repository(mock_db):
    """Test creating an MFA repository."""
    write_db, read_db = mock_db
    
    mfa_repo = create_mfa_repository(write_db, read_db)
    
    assert isinstance(mfa_repo, MFARepository)
    assert mfa_repo.write_db_session == write_db
    assert mfa_repo.read_db_session == read_db


def test_create_credentials_service(mock_db):
    """Test creating a credentials service."""
    write_db, read_db = mock_db
    
    # Create service
    cred_service = create_credentials_service(write_db, read_db)
    
    # Assertions
    assert isinstance(cred_service, CredentialsService)
    assert isinstance(cred_service.cred_repo, CredentialsRepository)
    
    # Verify repository has correct db sessions
    assert cred_service.cred_repo.write_db_session == write_db
    assert cred_service.cred_repo.read_db_session == read_db


def test_create_mfa_service(mock_db):
    """Test creating an MFA service."""
    write_db, read_db = mock_db
    
    # Create service
    mfa_service = create_mfa_service(write_db, read_db)
    
    # Assertions
    assert isinstance(mfa_service, MFAservice)
    assert isinstance(mfa_service.mfa_repo, MFARepository)
    
    # Verify repository has correct db sessions
    assert mfa_service.mfa_repo.write_db_session == write_db
    assert mfa_service.mfa_repo.read_db_session == read_db


def test_create_user_service(mock_db):
    """Test creating a user service with all dependencies."""
    write_db, read_db = mock_db
    
    # Create service
    user_service = create_user_service(write_db, read_db)
    
    # Assertions
    assert isinstance(user_service, UserService)
    
    # Verify repositories
    assert isinstance(user_service.user_repo, UserRepository)
    assert user_service.user_repo.write_db_session == write_db
    assert user_service.user_repo.read_db_session == read_db
    
    # Verify dependent services
    assert isinstance(user_service.cred_service, CredentialsService)
    assert isinstance(user_service.mfa_service, MFAservice)
    
    # Verify nested repositories in the dependent services
    assert isinstance(user_service.cred_service.cred_repo, CredentialsRepository)
    assert isinstance(user_service.mfa_service.mfa_repo, MFARepository)


def test_create_auth_service(mock_db):
    """Test creating an auth service."""
    write_db, read_db = mock_db
    
    # Create service
    auth_service = create_auth_service(write_db, read_db)
    
    # Assertions
    assert isinstance(auth_service, AuthService)
    assert isinstance(auth_service.cred_service, CredentialsService)
    assert isinstance(auth_service.cred_service.cred_repo, CredentialsRepository)
    
    # Verify repository has correct db sessions
    assert auth_service.cred_service.cred_repo.write_db_session == write_db
    assert auth_service.cred_service.cred_repo.read_db_session == read_db


def test_create_dashboard_service(mock_db):
    """Test creating a dashboard service with all dependencies."""
    write_db, read_db = mock_db
    
    # Create service
    dashboard_service = create_dashboard_service(write_db, read_db)
    
    # Assertions
    assert isinstance(dashboard_service, DashboardService)
    
    # Verify dependent services
    assert isinstance(dashboard_service.user_service, UserService)
    assert isinstance(dashboard_service.mfa_service, MFAservice)
    
    # Verify user_service properties
    assert isinstance(dashboard_service.user_service.user_repo, UserRepository)
    assert isinstance(dashboard_service.user_service.cred_service, CredentialsService)
    assert isinstance(dashboard_service.user_service.mfa_service, MFAservice)
    
    # Verify mfa_service properties
    assert isinstance(dashboard_service.mfa_service.mfa_repo, MFARepository)
    
    # Verify DB sessions are correctly passed through the chain
    assert dashboard_service.user_service.user_repo.write_db_session == write_db
    assert dashboard_service.user_service.user_repo.read_db_session == read_db
    assert dashboard_service.mfa_service.mfa_repo.write_db_session == write_db
    assert dashboard_service.mfa_service.mfa_repo.read_db_session == read_db


def test_service_factory_integration():
    """Test that all factories work together correctly."""
    # Setup mock DB
    write_db = MagicMock()
    read_db = MagicMock()
    
    # Create all services
    user_service = create_user_service(write_db, read_db)
    mfa_service = create_mfa_service(write_db, read_db)
    cred_service = create_credentials_service(write_db, read_db)
    auth_service = create_auth_service(write_db, read_db)
    dashboard_service = create_dashboard_service(write_db, read_db)
    
    # Verify all services are created correctly
    assert isinstance(user_service, UserService)
    assert isinstance(mfa_service, MFAservice)
    assert isinstance(cred_service, CredentialsService)
    assert isinstance(auth_service, AuthService)
    assert isinstance(dashboard_service, DashboardService)
    
    # Verify dependency chain for dashboard service
    assert isinstance(dashboard_service.user_service, UserService)
    assert isinstance(dashboard_service.mfa_service, MFAservice)