
import bcrypt
from blueprints.users.crendentials_service import CredentialsService


class AuthService():
    def __init__(self,cred_service:CredentialsService) -> None:
        self.cred_service = cred_service

    def _check_password(self, plain_password: str, hashed_password: str) -> bool:
        """Checks if the provided password matches the stored hashed password."""
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    

    def verify_password(self, email: str, password: str) -> bool:
        """Verifies a user's password against stored credentials."""
        cred = self.cred_service.get_credentials_via_email(email=email)
        # TODO add MFA flow redirection and qr_code
        # Save to session
        # Password expiry
        if not cred or not cred.password:
            raise ValueError("Invalid email or password")

        return self._check_password(password, cred.password)
    
    def reset_password(self, email: str, new_password:int) -> str:
        """Resets the password and returns the new one."""
        cred = self.cred_service.get_credentials_via_email(email)
        if not cred:
            raise Exception(f"Information not found for the email {email}")

        hashed_password = self.cred_service.validate_and_hash_pw(new_password)
        self.cred_service.update(cred.id, password=hashed_password)

        return new_password


    def verify_mfa():
        pass


    def resend_mfa_seed():
        pass

    def create_mfa_seed():
        pass