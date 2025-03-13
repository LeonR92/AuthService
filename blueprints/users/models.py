"""
User Authentication Models.

This module defines the database models for user authentication including
User profiles, Credentials, and Multi-Factor Authentication data.

The models use SQLAlchemy ORM and include relationship definitions
to ensure proper cascading behavior for data integrity.

"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from core.models import TimestampMixin


class User(Base, TimestampMixin):
    """
    User model representing profile information.
    
    This model stores user profile data and maintains relationships
    with authentication data (credentials and MFA). It inherits timestamp
    functionality for auditing purposes.

    Attributes:
        id (int): Primary key and unique identifier
        first_name (str): User's first name, required
        last_name (str): User's last name, required
        dob (datetime): Date of birth, optional
        country (str): User's country code, optional
        credentials_id (int): Foreign key to credentials table
        mfa_id (int): Foreign key to MFA table, nullable for optional MFA
        credentials (Credentials): One-to-one relationship with credentials
        mfa (MFA): One-to-one relationship with MFA configuration
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(250), nullable=False, default="Unknown")
    last_name = Column(String(250), nullable=False, default="Unknown")
    dob = Column(DateTime, nullable=True)
    country = Column(String(150), nullable=True)

    # Foreign Keys
    credentials_id = Column(Integer, ForeignKey("credentials.id", ondelete="CASCADE"), nullable=False, unique=True)
    mfa_id = Column(Integer, ForeignKey("mfa.id", ondelete="SET NULL"), nullable=True, unique=True)

    # Relationships
    credentials = relationship("Credentials", back_populates="user", uselist=False, cascade="all, delete")
    mfa = relationship("MFA", back_populates="user", uselist=False, cascade="all, delete")



class Credentials(Base, TimestampMixin):
    """
    Credentials model for authentication data.
    
    Stores user authentication information including email and password.
    The password is stored as a hash, never in plain text. Includes
    timestamp tracking for security audit purposes.
    
    Attributes:
        id (int): Primary key and unique identifier
        email (str): User's email address, unique and indexed
        password (str): Hashed password
        last_login (datetime): Timestamp of last successful login
        user (User): One-to-one relationship with user profile
    """
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(320), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)  
    last_login = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="credentials", uselist=False)


class MFA(Base, TimestampMixin):
    """
    Multi-Factor Authentication model.
    
    Stores information needed for Multi-Factor Authentication,
    primarily the TOTP (Time-based One-Time Password) secret used
    for generating verification codes.
    
    Attributes:
        id (int): Primary key and unique identifier
        totp_secret (str): Secret key used for TOTP generation
        user (User): One-to-one relationship with user profile
    """
    __tablename__ = "mfa"

    id = Column(Integer, primary_key=True, autoincrement=True)
    totp_secret = Column(String(100), nullable=True) 

    # Relationship
    user = relationship("User", back_populates="mfa", uselist=False)

