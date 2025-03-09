
import bcrypt
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService



class AuthService():
    def __init__(self,cred_service:CredentialsService, mfa_service:MFAservice, user_service:UserService) -> None:
        self.cred_service = cred_service
        self.mfa_service = mfa_service
        self.user_service = user_service

    def verify_password(self,email:str,password:str) -> bool:
        cred = self.cred_service.get_credentials_via_email(email=email)
        if not cred:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), cred.password.encode("utf-8"))
    
    def reset_password(self, email: str, new_password:int) -> str:
        """Resets the password and returns the new one."""
        cred = self.cred_service.get_credentials_via_email(email)
        if not cred:
            raise Exception(f"Information not found for the email {email}")

        hashed_password = self.cred_service.validate_and_hash_pw(new_password)
        self.cred_service.update(cred.id, password=hashed_password)

        return new_password

    def activate_mfa(self, email:str):
        user = self.cred_service.get_credentials_via_email(email=email)
        if not user:
            raise Exception(f"No user found with the email:{email}")
        mfa_id = self.mfa_service.create_mfa_entry()
        if not mfa_id:
            raise RuntimeError("Error creating MFA entry")
        user.mfa_id = mfa_id
        self.user_service.update_user(user)
    
    def deactivate_mfa(self, email: str) -> None:
        """Deactivates MFA for a user by removing their MFA record."""
        user = self.cred_service.get_credentials_via_email(email=email)
        if not user:
            raise ValueError(f"No user found with the email {email}")

        mfa_info = self.mfa_service.get_mfa_details_via_user_id(user.id)
        if not mfa_info:
            raise ValueError(f"No MFA record found for user {email}")

        self.mfa_service.delete_mfa(mfa_info)



    

    def verify_mfa():
        pass




    def resend_mfa_seed():
        pass

    def create_mfa_seed():
        pass