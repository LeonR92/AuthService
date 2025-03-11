

from blueprints.users.mfa_repository import MFARepository
from blueprints.users.models import MFA
import pyotp
import qrcode
import io
import base64


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
    
    
    def create_qrcode_totp(self, name: str, user_id: int = None) -> dict:
        if user_id:
            try:
                mfa_details = self.get_mfa_details_via_user_id(user_id)
                secret_key = mfa_details.totp_secret
            except Exception:
                # No existing MFA for this user, create a new secret
                secret_key = self.create_totp_secret()
        else:
            secret_key = self.create_totp_secret()
        
        totp = pyotp.TOTP(secret_key)
        provisioning_uri = totp.provisioning_uri(
            name=name,
            issuer_name="BookStore"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Convert to base64 image
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered)
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {
            "qr_code_base64": qr_code_base64,
            "secret_key": secret_key
        }

    
    def verify_totp(self, secret_key: str, token: str) -> bool:
        """
        Verify a TOTP token provided by the user.
        
        Args:
            secret_key: The user's secret key
            token: The TOTP token provided by the user
            
        Returns:
            bool: True if the token is valid, False otherwise
        """
        totp = pyotp.TOTP(secret_key)
        return totp.verify(token)
    
    def delete_mfa(self,mfa_id:int) -> None:
        self.mfa_repo.delete(mfa_id=mfa_id)


