

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
    
    def get_user_details_by_mfa_id(self,email:str):
        user_details = self.mfa_repo.get_mfa_details_by_user_id(email)
        if not user_details:
            raise Exception("User details requested not found")
        return user_details
    
    def get_mfa_details_via_email(self,email:str) -> MFA:
        mfa_details = self.mfa_repo.get_mfa_details_via_email(email=email)
        if not mfa_details:
            raise ValueError("MFA is not activated for this user")
        return mfa_details

    def create_totp_secret(self) -> str:
        return pyotp.random_base32()

    def create_mfa_entry(self) -> int:
        totp_secret = self.create_totp_secret()
        mfa_id = self.mfa_repo.create(totp_secret=totp_secret)
        return mfa_id

    def change_totp_secret(self, user_id: int) -> str:
        new_totp_secret = self.create_totp_secret()
        updated_mfa = self.mfa_repo.update_mfa_secret(user_id=user_id, otp_secret=new_totp_secret)
        if not updated_mfa:
            raise ValueError(f"Failed to update MFA secret for user {user_id}")
        
        return new_totp_secret
    
    def delete_mfa(self,mfa_id=int) -> None:
        self.mfa_repo.delete(mfa_id=mfa_id)


