# di.py or users/__init__.py

from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.user_repository import UserRepository
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService

from core.database import get_read_db, get_write_db


def init_mfa_services():
    """Initialize and return the MFA-related services."""
    with get_write_db() as write_db, get_read_db() as read_db:
        mfa_repo = MFARepository(write_db_session=write_db, read_db_session=read_db)
        mfa_service = MFAservice(mfa_repo=mfa_repo)
        return mfa_service, mfa_repo

def init_user_services():
    """Initialize and return the user-related services."""
    with get_write_db() as write_db, get_read_db() as read_db:
        user_repo = UserRepository(write_db_session=write_db, read_db_session=read_db)
        cred_repo = CredentialsRepository(write_db=write_db, read_db=read_db)
        mfa_repo = MFARepository(write_db_session=write_db, read_db_session=read_db)

        # Services
        cred_service = CredentialsService(cred_repo=cred_repo)
        mfa_service = MFAservice(mfa_repo=mfa_repo)
        user_service = UserService(user_repo=user_repo, cred_service=cred_service, mfa_service=mfa_service)

    return user_service, cred_service, mfa_service
