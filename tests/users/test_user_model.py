import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from blueprints.users.models import User, Credentials, MFA


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(engine):
    """Create a new database session for testing."""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_user_creation(db_session):
    """Test creating a user with valid data."""
    credentials = Credentials(email="test@example.com", password="hashed_password")
    db_session.add(credentials)
    db_session.flush()
    
    user = User(
        first_name="John",
        last_name="Doe",
        dob=datetime(1990, 1, 1),
        country="US",
        credentials_id=credentials.id
    )
    db_session.add(user)
    db_session.commit()
    
    retrieved_user = db_session.query(User).filter_by(id=user.id).first()
    
    assert retrieved_user is not None
    assert retrieved_user.first_name == "John"
    assert retrieved_user.last_name == "Doe"
    assert retrieved_user.dob == datetime(1990, 1, 1)
    assert retrieved_user.country == "US"
    assert retrieved_user.credentials_id == credentials.id
    assert retrieved_user.mfa_id is None
    
    assert retrieved_user.created_at is not None


def test_user_with_mfa(db_session):
    """Test creating a user with MFA enabled."""
    credentials = Credentials(email="mfa@example.com", password="hashed_password")
    db_session.add(credentials)
    
    mfa = MFA(totp_secret="some_secret_key")
    db_session.add(mfa)
    db_session.flush()
    
    user = User(
        first_name="Jane",
        last_name="Smith",
        credentials_id=credentials.id,
        mfa_id=mfa.id
    )
    db_session.add(user)
    db_session.commit()
    
    retrieved_user = db_session.query(User).filter_by(id=user.id).first()
    assert retrieved_user.mfa_id == mfa.id
    
    assert retrieved_user.mfa.totp_secret == "some_secret_key"
    assert retrieved_user.credentials.email == "mfa@example.com"


def test_user_without_credentials(db_session):
    """Test that creating a user without credentials fails."""
    user = User(
        first_name="No",
        last_name="Credentials"
    )
    db_session.add(user)
    
    with pytest.raises(Exception) as excinfo:
        db_session.commit()
    
    assert "NOT NULL constraint" in str(excinfo.value)
    
    db_session.rollback()


def test_user_defaults(db_session):
    """Test that default values are applied correctly."""
    credentials = Credentials(email="defaults@example.com", password="password")
    db_session.add(credentials)
    db_session.flush()
    
    user = User(credentials_id=credentials.id)
    db_session.add(user)
    db_session.commit()
    
    retrieved_user = db_session.query(User).filter_by(id=user.id).first()
    assert retrieved_user.first_name == "Unknown"
    assert retrieved_user.last_name == "Unknown"
    assert retrieved_user.dob is None
    assert retrieved_user.country is None


def test_user_credential_relationship(db_session):
    """Test the relationship between User and Credentials."""
    credentials = Credentials(email="relation@example.com", password="password")
    db_session.add(credentials)
    db_session.flush()
    
    user = User(
        first_name="Relation",
        last_name="Test",
        credentials_id=credentials.id
    )
    db_session.add(user)
    db_session.commit()
    
    retrieved_user = db_session.query(User).filter_by(id=user.id).first()
    assert retrieved_user.credentials.email == "relation@example.com"
    
    retrieved_credentials = db_session.query(Credentials).filter_by(id=credentials.id).first()
    assert retrieved_credentials.user.first_name == "Relation"


def test_user_delete_orphans_cascade(db_session):
    """Test that when a user is deleted, associated MFA record is deleted."""
    credentials = Credentials(email="orphans@example.com", password="password")
    mfa = MFA(totp_secret="orphan_secret")
    db_session.add_all([credentials, mfa])
    db_session.flush()
    
    user = User(
        first_name="Orphan",
        last_name="Test",
        credentials_id=credentials.id,
        mfa_id=mfa.id
    )
    db_session.add(user)
    db_session.commit()
    

    mfa_id = mfa.id
    
    db_session.delete(user)
    db_session.commit()
    
    assert db_session.query(MFA).filter_by(id=mfa_id).first() is None


def test_credentials_creation(db_session):
    """Test creating credentials with valid data."""
    credentials = Credentials(
        email="credentials@example.com",
        password="hashed_password",
        last_login=datetime.now()
    )
    db_session.add(credentials)
    db_session.commit()
    
    retrieved_credentials = db_session.query(Credentials).filter_by(id=credentials.id).first()
    assert retrieved_credentials is not None
    assert retrieved_credentials.email == "credentials@example.com"
    assert retrieved_credentials.password == "hashed_password"
    assert retrieved_credentials.last_login is not None
    assert retrieved_credentials.created_at is not None


def test_credentials_unique_email(db_session):
    """Test that duplicate emails are rejected."""
    credentials1 = Credentials(email="unique@example.com", password="password1")
    db_session.add(credentials1)
    db_session.commit()
    
    credentials2 = Credentials(email="unique@example.com", password="password2")
    db_session.add(credentials2)
    
    with pytest.raises(Exception) as excinfo:
        db_session.commit()
    
    assert "UNIQUE constraint" in str(excinfo.value) or "unique" in str(excinfo.value).lower()
    
    db_session.rollback()


def test_mfa_creation(db_session):
    """Test creating an MFA record."""
    mfa = MFA(totp_secret="mfa_secret_key")
    db_session.add(mfa)
    db_session.commit()
    
    retrieved_mfa = db_session.query(MFA).filter_by(id=mfa.id).first()
    assert retrieved_mfa is not None
    assert retrieved_mfa.totp_secret == "mfa_secret_key"
    assert retrieved_mfa.created_at is not None


def test_mfa_null_secret(db_session):
    """Test that totp_secret can be null."""
    mfa = MFA() 
    db_session.add(mfa)
    db_session.commit()
    
    retrieved_mfa = db_session.query(MFA).filter_by(id=mfa.id).first()
    assert retrieved_mfa is not None
    assert retrieved_mfa.totp_secret is None


def test_timestamp_creation(db_session):
    """Test that created_at timestamp is populated."""
    credentials = Credentials(email="timestamps@example.com", password="password")
    db_session.add(credentials)
    db_session.commit()
    
    assert credentials.created_at is not None
    
    mfa = MFA()
    user = User(
        first_name="Time", 
        last_name="Stamp",
        credentials_id=credentials.id
    )
    
    db_session.add_all([mfa, user])
    db_session.commit()
    
    assert user.created_at is not None
    assert mfa.created_at is not None