"""
Service Factory Module.

This module implements dependency injection pattern for the application,
providing factory functions that centralize the initialization of repositories
and services with proper dependency management.

Key Features:
- Enforces read/write separation across the application
- Centralized management of object dependencies
- Simplifies testing through easy dependency substitution
- Prevents circular dependencies between components
- Ensures consistent database session handling

Usage:
    These factory functions should be used by routes/controllers to 
    obtain properly configured service instances without needing to
    understand the complete dependency graph.

Usage Example:
    @app.route('/users')
    def users_endpoint():
        with get_write_db() as write_db, get_read_db() as read_db:
            user_service = create_user_service(write_db, read_db)
            # Use service...
"""

from blueprints.auth.service import AuthService
from blueprints.dashboard.service import DashboardService
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_repository import UserRepository
from blueprints.users.user_service import UserService

def create_user_service(write_db, read_db) -> UserService:
    """Create UserService."""
    user_repo = create_user_repository(write_db, read_db)
    cred_repo = create_credentials_repository(write_db, read_db)
    mfa_repo = create_mfa_repository(write_db, read_db)
    
    cred_service = CredentialsService(cred_repo=cred_repo)
    mfa_service = MFAservice(mfa_repo=mfa_repo)
    
    return UserService(user_repo=user_repo, cred_service=cred_service, mfa_service=mfa_service)

def create_mfa_service(write_db, read_db) -> MFAservice:
    """Create MFAservice."""
    mfa_repo = create_mfa_repository(write_db, read_db)
    return MFAservice(mfa_repo=mfa_repo)

def create_credentials_service(write_db, read_db) -> CredentialsService:
    """Create CredentialsService."""
    cred_repo = create_credentials_repository(write_db, read_db)
    return CredentialsService(cred_repo=cred_repo)

def create_auth_service(write_db, read_db) -> AuthService:
    """Create AuthService."""
    cred_repo = create_credentials_repository(write_db, read_db)
    cred_service = CredentialsService(cred_repo=cred_repo)
    return AuthService(cred_service=cred_service)

def create_dashboard_service(write_db,read_db) -> DashboardService:
    user_service = create_user_service(write_db=write_db,read_db=read_db)
    mfa_service = create_mfa_service(write_db=write_db,read_db=read_db)
    return DashboardService(user_service=user_service,mfa_service=mfa_service)

# Helper functions to init repositories
def create_user_repository(write_db, read_db) -> UserRepository:
    """Create UserRepository."""
    return UserRepository(write_db_session=write_db, read_db_session=read_db)

def create_credentials_repository(write_db, read_db) -> CredentialsRepository:
    """Create CredentialsRepository."""
    return CredentialsRepository(write_db, read_db)

def create_mfa_repository(write_db, read_db) -> MFARepository:
    """Create MFARepository."""
    return MFARepository(write_db_session=write_db, read_db_session=read_db)
