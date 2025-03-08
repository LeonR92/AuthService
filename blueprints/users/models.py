from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from core.database import Base
from core.models import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users" 

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(250), nullable=False, default="Unknown")
    last_name = Column(String(250), nullable=False, default="Unknown")
    dob = Column(DateTime, nullable=True, default=func.current_timestamp())
    country = Column(String(150), nullable=True)
    credentials_id = Column(Integer, ForeignKey("credentials.id"), nullable=False, unique=True)  
    # Relationships
    credentials = relationship("Credentials", back_populates="user", uselist=False)  


class Credentials(Base, TimestampMixin):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(300), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="credentials")  
