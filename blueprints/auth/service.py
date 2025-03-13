"""Authentication service module for managing user authentication operations.

This module provides the AuthService class for handling password verification,
checking, and resetting functionality with secure hashing via bcrypt.
"""
import bcrypt
from blueprints.users.crendentials_service import CredentialsService


class AuthService:
    """Service for handling user authentication operations.
    
    Manages the verification and manipulation of user credentials including
    password checking and resetting with secure bcrypt hashing.
    """

    def __init__(self, cred_service: CredentialsService) -> None:
        """Authentication service initialization.
        
        :param cred_service: Service for retrieving and updating user credentials
        :type cred_service: CredentialsService
        """
        self.cred_service = cred_service

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify if a plaintext password matches its hashed version.
        
        :param plain_password: Plaintext password to check
        :type plain_password: str
        :param hashed_password: Bcrypt-hashed password for comparison
        :type hashed_password: str
        :return: True if passwords match, False otherwise
        :rtype: bool

        Usage Example:
        return self.check_password(password, cred.password)
        """
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    
    def verify_password(self, email: str, password: str) -> bool:
        """Authenticate a user by email and password.
        
        :param email: User's email address
        :type email: str
        :param password: User's plaintext password
        :type password: str
        :return: True if authentication succeeds
        :rtype: bool
        :raises ValueError: If email not found or password doesn't match

        Usage example:
        if not auth_service.verify_password(email, password):
            do_things()
        """
        cred = self.cred_service.get_credentials_via_email(email=email)
        if not cred or not cred.password:
            raise ValueError("Invalid email or password")

        return self.check_password(password, cred.password)
    
