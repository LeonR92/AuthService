

from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService


class AuthService():
    def __init__(self,user_service:UserService, mfa_service:MFAservice) -> None:
        pass
    def check_password():
        pass
    
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