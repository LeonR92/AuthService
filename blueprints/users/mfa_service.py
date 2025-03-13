"""
Multi-Factor Authentication Service Module.

This module provides business logic for managing Multi-Factor Authentication (MFA)
operations, including TOTP secret generation, QR code creation, and token validation.

"""

from blueprints.users.mfa_repository import MFARepository
from blueprints.users.models import MFA
import pyotp
import qrcode
import io
import base64


class MFAservice:
    """
    Service layer for Multi-Factor Authentication operations.
    
    This class implements business logic for MFA functionality including
    TOTP (Time-based One-Time Password) generation, verification, 
    QR code creation, and management of MFA records.
    """

    def __init__(self,mfa_repo:MFARepository) -> None:
        """
        Initialize with an MFA repository instance.
        
        :param mfa_repo: Repository providing MFA data access operations
        :type mfa_repo: MFARepository
        :return: None
        """
        self.mfa_repo = mfa_repo
    
    def get_mfa_details_via_user_id(self,user_id:int)->MFA:
        """
        Retrieve MFA details for a specific user by ID.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: MFA details for the user
        :rtype: MFA
        :raises ValueError: If user ID is missing

        Usage example:
        mfa_details = self.get_mfa_details_via_user_id(user_id)
        """
        if not user_id:
            raise ValueError("User id missing")
        mfa_details = self.mfa_repo.get_mfa_details_by_user_id(user_id)

        return mfa_details
    
    
    def get_mfa_details_via_email(self,email:str) -> MFA:
        """
        Retrieve user details using email address.
        
        :param email: User's email address
        :type email: str
        :return: User details with MFA information
        :rtype: User
        :raises Exception: If user details not found

        Usage example:
        mfa_enabled = mfa_service.get_mfa_details_via_email(email=email)
        """
        mfa_details = self.mfa_repo.get_mfa_details_via_email(email=email)
        return mfa_details

    def create_totp_secret(self) -> str:
        """
        Generate a new random TOTP secret key.
        
        :return: Base32 encoded secret key for TOTP
        :rtype: str

        Usage example:
        totp_secret = self.create_totp_secret()
        """
        return pyotp.random_base32()

    def create_mfa_entry(self) -> int:
        """
        Create a new MFA entry with a random TOTP secret.
        
        :return: ID of the newly created MFA record
        :rtype: int
        
        Usage example:
        mfa_id = self.mfa_service.create_mfa_entry()
        """
        totp_secret = self.create_totp_secret()
        mfa_id = self.mfa_repo.create(totp_secret=totp_secret)
        return mfa_id

    def change_totp_secret(self, user_id: int) -> str:
        """
        Change the TOTP secret for a user's MFA entry.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: New TOTP secret key
        :rtype: str
        :raises ValueError: If failed to update MFA secret
        """
        new_totp_secret = self.create_totp_secret()
        updated_mfa = self.mfa_repo.update_mfa_secret(user_id=user_id, otp_secret=new_totp_secret)
        if not updated_mfa:
            raise ValueError(f"Failed to update MFA secret for user {user_id}")
        
        return new_totp_secret
    
    
    def create_qrcode_totp(self, name: str, user_id: int = None) -> dict:
        """
        Generate a QR code for TOTP setup and corresponding secret key.
        
        :param name: User identifier (typically email) for TOTP setup
        :type name: str
        :param user_id: Optional user ID to fetch existing MFA details
        :type user_id: Optional[int]
        :return: Dictionary containing QR code as base64 and secret key
        :rtype: Dict[str, str]

        Usage example:
        qr_data = mfa_service.create_qrcode_totp(name=name, user_id=user_id)
        """
        if user_id:
            try:
                mfa_details = self.get_mfa_details_via_user_id(user_id)
                secret_key = mfa_details.totp_secret
            except Exception:
                # if no MFA for this user, create a new secret
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
        
        :param secret_key: The user's TOTP secret key
        :type secret_key: str
        :param token: The TOTP token provided by the user
        :type token: str
        :return: True if the token is valid, False otherwise
        :rtype: bool

        Usage example:
        mfa_service.verify_totp(secret_key=mfa_details.totp_secret, token=totp)
        """
        totp = pyotp.TOTP(secret_key)
        return totp.verify(token)
    
    def deactivate_mfa(self,user_id:int) -> None:
        """
        Deactivate MFA for a specific user.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: None
        :raises ValueError: If no MFA details found for the user

        Usage example:
        mfa_service.deactivate_mfa(user_id=user_id)
        """
        mfa_details = self.get_mfa_details_via_user_id(user_id=user_id)
        if not mfa_details:
            raise ValueError("No MFA details found")
        self.mfa_repo.delete(mfa_id=mfa_details.id)


