from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
from core.database import Base
from core.models import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(250), nullable=False, default="Unknown")
    last_name = Column(String(250), nullable=False, default="Unknown")
    dob = Column(DateTime, nullable=True, default=func.current_timestamp())
    country = Column(String(150), nullable=True)
    credentials_id = Column(Integer, ForeignKey("credentials.id"), nullable=False)

    # Relationships
    credentials = relationship("Credentials", back_populates="users")

    # Constraints
    __table_args__ = (
        CheckConstraint("dob <= GETDATE()", name="CHK_User_DOB_NotFuture"),  
    )


class Credentials(Base, TimestampMixin):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(300), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    last_login = Column(DateTime, nullable=True)

class SSO(Base, TimestampMixin):
    pass