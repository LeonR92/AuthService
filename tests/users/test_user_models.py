import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from blueprints.users.models import User, Credentials, MFA
from datetime import datetime

# Create an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=True)

# Use a separate session factory for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db_session():
    """Fixture to set up and tear down a fresh database for each test."""
    Base.metadata.create_all(bind=engine)  # Create schema
    session = TestingSessionLocal()
    yield session  # Provide the session to the test
    session.rollback()  # Rollback any changes after test
    session.close()
    Base.metadata.drop_all(bind=engine)  # Clean up schema after test

@pytest.fixture
def create_user(test_db_session):
    """Helper fixture to create a User."""
    credentials = Credentials(email="test@example.com", password="hashed_password")
    test_db_session.add(credentials)
    test_db_session.commit()

    user = User(
        first_name="John",
        last_name="Doe",
        dob=datetime(1990, 1, 1),
        country="USA",
        credentials_id=credentials.id
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

def test_create_user(test_db_session):
    """Test creating a user with valid data."""
    credentials = Credentials(email="user@example.com", password="securepassword")
    test_db_session.add(credentials)
    test_db_session.commit()

    user = User(
        first_name="Alice",
        last_name="Smith",
        dob=datetime(1985, 5, 20),
        country="Germany",
        credentials_id=credentials.id
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)

    assert user.id is not None
    assert user.first_name == "Alice"
    assert user.last_name == "Smith"
    assert user.credentials.email == "user@example.com"

def test_create_user_without_credentials(test_db_session):
    """Test that creating a user without credentials_id raises an IntegrityError."""
    with pytest.raises(Exception):  # Expect SQLAlchemy integrity error
        user = User(first_name="Bob", last_name="Brown", dob=None, country="France")
        test_db_session.add(user)
        test_db_session.commit()

def test_user_relationships(test_db_session, create_user):
    """Test that User has a valid relationship with Credentials."""
    user = create_user
    assert user.credentials is not None
    assert user.credentials.email == "test@example.com"

def test_mfa_linked_to_user(test_db_session, create_user):
    """Test creating MFA and linking it to a User."""
    mfa = MFA(totp_secret="S3CRET-TOTP", user=create_user)
    test_db_session.add(mfa)
    test_db_session.commit()
    test_db_session.refresh(mfa)

    assert mfa.id is not None
    assert mfa.totp_secret == "S3CRET-TOTP"
    assert mfa.user.id == create_user.id

def test_delete_user_cascades_credentials(test_db_session, create_user):
    """Test deleting a User cascades deletion of Credentials."""
    user_id = create_user.id
    credentials_id = create_user.credentials.id

    test_db_session.delete(create_user)
    test_db_session.commit()

    deleted_user = test_db_session.query(User).filter_by(id=user_id).first()
    deleted_credentials = test_db_session.query(Credentials).filter_by(id=credentials_id).first()

    assert deleted_user is None  # User should be deleted
    assert deleted_credentials is None  # Credentials should be deleted due to CASCADE

def test_delete_user_retains_mfa(test_db_session, create_user):
    """Test deleting a User retains MFA (due to SET NULL on delete)."""
    mfa = MFA(totp_secret="TOTP-KEY", user=create_user)
    test_db_session.add(mfa)
    test_db_session.commit()
    test_db_session.refresh(mfa)

    user_id = create_user.id
    test_db_session.delete(create_user)
    test_db_session.commit()

    deleted_user = test_db_session.query(User).filter_by(id=user_id).first()
    retained_mfa = test_db_session.query(MFA).filter_by(id=mfa.id).first()

    assert deleted_user is None
    assert retained_mfa is None

