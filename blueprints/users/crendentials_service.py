"""
Credentials Service Module.

This module provides a service layer for user authentication operations,
implementing business logic and validation on top of the data access layer.

"""

import random
import string
from blueprints.users.credentials_repository import CredentialsRepository
import bcrypt
from blueprints.users.models import Credentials


class CredentialsService:
    """
    Service layer for User authentication operations.
    
    This class implements business logic, validation, and security operations
    for user credentials, acting as an intermediary between controllers and
    the data access layer to enforce domain rules.
    """

    def __init__(self, cred_repo: CredentialsRepository):
        """
        Initialize with a repository instance.
        
        :param cred_repo: Repository providing data access operations
        :type cred_repo: CredentialsRepository
        :return: None
        """
        self.cred_repo = cred_repo

    def validate_and_hash_pw(self,password:str, password_length:int = 8) -> str:
        """
        Validate password requirements and hash it securely.
        
        :param password: Plain text password to validate and hash
        :type password: str
        :param password_length: Minimum required password length
        :type password_length: int
        :return: Securely hashed password string
        :rtype: str
        :raises ValueError: If password is empty or too short

        Usage example:
        new_hashed_password = self.validate_and_hash_pw(new_password)
        """
        if not password or password.strip() == "":
            raise ValueError("Password cannot be empty")
        if len(password) < password_length:
            raise ValueError(f"Password cannot be shorter than {password_length}")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed_password.decode("utf-8")

    def get_credentials_via_email(self,email:str) -> Credentials:
        """
        Retrieve credentials using email address.
        
        :param email: User's email address
        :type email: str
        :return: Credentials object
        :rtype: Credentials
        :raises Exception: If credentials not found

        Usage example:
        credentials = self.get_credentials_via_email(email=email)
        """
        credentials =  self.cred_repo.get_credentials_by_email(email=email)

        if not credentials:
            raise Exception ("credentials not found")
        return credentials
    
    def get_email_by_userid(self,user_id:int) -> str:
        """
        Retrieve email address using user ID.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: User's email address
        :rtype: str
        :raises ValueError: If user ID is empty or email not found

        Usage example:
        email = cred_service.get_email_by_userid(user_id)
        """
        if not user_id:
            ValueError("User ID cannot be empty")
        email = self.cred_repo.get_email_by_userid(user_id=user_id)
        if not email:
            raise ValueError("Email not found")
        return email
    

    
    def generate_random_password(self,length:int = 12) -> str:
        """
        Generate a secure random password.
        
        :param length: Length of the generated password
        :type length: int
        :return: Randomly generated password
        :rtype: str

        Usage example:
        new_password= self.generate_random_password()
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        random_password = ''.join(random.choice(characters) for _ in range(length))
        return random_password
    
    def reset_password(self,email:str) -> str:
        """
        Reset a user's password to a new random password.
        
        :param email: User's email address
        :type email: str
        :return: New plain text password (should be transmitted securely)
        :rtype: str
        :raises ValueError: If no credentials found for the email

        Usage example:
        new_password = cred_service.reset_password(email=email)
        """
        credentials = self.get_credentials_via_email(email=email)
        if not credentials:
            raise ValueError(f"No credentials found for email: {email}")
        new_password= self.generate_random_password()
        new_hashed_password = self.validate_and_hash_pw(new_password)
        self.cred_repo.update_credentials(cred_id=credentials.id, password=new_hashed_password)
        return new_password



    def create_credentials(self, email: str, password: str) -> int:
        """
        Register new user credentials after validation.
        
        :param email: User's email address
        :type email: str
        :param password: User's plain text password
        :type password: str
        :return: ID of the newly created credentials
        :rtype: int
        :raises ValueError: If email or password is empty
        :raises RuntimeError: If credential creation fails

        Usage example:
        cred_id = self.cred_service.create_credentials(email = email,password=password)
        """
        if not email or not password:
            raise ValueError("Email or Password cannot be empty")
        hashed_password = self.validate_and_hash_pw(password)
        cred_id = self.cred_repo.create_credentials(email=email, password=hashed_password)
        if not cred_id:
            raise RuntimeError("Cant create credentials")
        return cred_id


    def change_password(self, user_id: int, new_password: str, confirm_new_password: str) -> None:
        """
        Change password for a given user with validation.
        
        :param user_id: Unique identifier of the user
        :type user_id: int
        :param new_password: New plain text password
        :type new_password: str
        :param confirm_new_password: Confirmation of new password
        :type confirm_new_password: str
        :return: None
        :raises ValueError: If user not found or passwords don't match

        Usage example:
        cred_service.change_password(user_id=user_id,new_password=new_password,confirm_new_password=confirm_new_password)
        """

        cred = self.cred_repo.get_credentials_by_id(user_id=user_id)
        if cred is None:
            raise ValueError("User not found")

        if new_password != confirm_new_password:
            raise ValueError("New passwords do not match")

        new_hashed_password = self.validate_and_hash_pw(new_password)
        self.cred_repo.update_credentials(cred_id=cred.id, password=new_hashed_password)
