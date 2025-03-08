

from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService


class AuthService():
    def __init__(self,cred_service:CredentialsService, mfa_service:MFAservice) -> None:
        self.cred_service = cred_service
        self.mfa_service = mfa_service

    def check_password(self,email:str,password:str) -> bool:
        user = self.cred_service.get_credentials_via_email(email=email)
        return user
    
    def verify_mfa():
        pass

    def reset_password():
        pass

    def change_email():
        pass

    def activate_mfa():
        pass

    def deactivate_mfa():
        pass

    def resend_mfa_seed():
        pass

    def create_mfa_seed():
        pass