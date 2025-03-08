

import secrets
import bcrypt
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.mfa_service import MFAservice



class AuthService():
    def __init__(self,cred_service:CredentialsService, mfa_service:MFAservice) -> None:
        self.cred_service = cred_service
        self.mfa_service = mfa_service

    def check_password(self,email:str,password:str) -> bool:
        cred = self.cred_service.get_credentials_via_email(email=email)
        if not cred:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), cred.password.encode("utf-8"))
    
    def reset_password(self, email: str) -> str:
        """Resets the password and returns the new one."""
        cred = self.cred_service.get_credentials_via_email(email)
        if not cred:
            raise Exception(f"Information not found for the email {email}")

        new_password = self.generate_temp_password()
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        self.cred_service.update(cred.id, password=hashed_password)

        return new_password  # Send this to the user securely

    @staticmethod
    def generate_temp_password(length: int = 12) -> str:
        """Generates a random temporary password."""
        return secrets.token_urlsafe(length)

    def verify_mfa():
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