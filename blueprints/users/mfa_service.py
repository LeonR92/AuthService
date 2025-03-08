

from blueprints.users.mfa_repository import MFARepository
from blueprints.users.models import MFA
import pyotp


class MFAservice:
    def __init__(self,mfa_repo:MFARepository) -> None:
        self.mfa_repo = mfa_repo
    
    def get_mfa_details_via_user_id(self,user_id:int)->MFA:
        if not user_id:
            raise ValueError("User id missing")
        mfa_details = self.mfa_repo.get_mfa_details_by_user_id(user_id)
        if not mfa_details:
            raise Exception("No MFA details with the user id is found")
        return mfa_details
    
    def create_totp_secret(self) -> str:
        return pyotp.random_base32()

    def create_mfa_entry(self, user_id:int) -> MFA:
        if not user_id:
            raise ValueError("user ID cannot be missing")
        totp_secret = self.create_totp_secret()
        return self.mfa_repo.create(totp_secret=totp_secret)

    def change_totp_secret(self, user_id: int) -> str:
        new_totp_secret = self.create_totp_secret()
        updated_mfa = self.mfa_repo.update_mfa_secret(user_id=user_id, otp_secret=new_totp_secret)
        if not updated_mfa:
            raise ValueError(f"Failed to update MFA secret for user {user_id}")
        
        return new_totp_secret
