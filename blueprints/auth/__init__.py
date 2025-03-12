from blueprints.auth.service import AuthService
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.crendentials_service import CredentialsService
from core.database import get_read_db, get_write_db

def init_auth_services():
    """Initialize and return the authentication-related services."""
    with get_write_db() as write_db, get_read_db() as read_db:
        cred_repo = CredentialsRepository(write_db=write_db, read_db=read_db)
        cred_service = CredentialsService(cred_repo=cred_repo)
        auth_service = AuthService(cred_service=cred_service)
        return auth_service, cred_service
