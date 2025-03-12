import pytest
from unittest.mock import Mock, patch
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.models import MFA


# Import the service to test
from blueprints.users.mfa_service import MFAservice


# Fixtures
@pytest.fixture
def mock_mfa_repo():
    return Mock(spec=MFARepository)


@pytest.fixture
def mfa_service(mock_mfa_repo):
    return MFAservice(mock_mfa_repo)


@pytest.fixture
def sample_mfa():
    mfa = Mock(spec=MFA)
    mfa.id = 1
    mfa.user_id = 123
    mfa.totp_secret = "ABCDEFGHIJKLMNOP"
    return mfa


# Tests for get_mfa_details_via_user_id
def test_get_mfa_details_via_user_id_success(mfa_service, mock_mfa_repo, sample_mfa):
    # Arrange
    mock_mfa_repo.get_mfa_details_by_user_id.return_value = sample_mfa
    user_id = 123
    
    # Act
    result = mfa_service.get_mfa_details_via_user_id(user_id)
    
    # Assert
    mock_mfa_repo.get_mfa_details_by_user_id.assert_called_once_with(user_id)
    assert result == sample_mfa


def test_get_mfa_details_via_user_id_missing_id(mfa_service):
    # Arrange
    user_id = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="User id missing"):
        mfa_service.get_mfa_details_via_user_id(user_id)


# Tests for get_user_details_by_mfa_id
def test_get_user_details_by_mfa_id_success(mfa_service, mock_mfa_repo, sample_mfa):
    # Arrange
    mock_mfa_repo.get_mfa_details_by_user_id.return_value = sample_mfa
    email = "user@example.com"
    
    # Act
    result = mfa_service.get_user_details_by_mfa_id(email)
    
    # Assert
    mock_mfa_repo.get_mfa_details_by_user_id.assert_called_once_with(email)
    assert result == sample_mfa


def test_get_user_details_by_mfa_id_not_found(mfa_service, mock_mfa_repo):
    # Arrange
    mock_mfa_repo.get_mfa_details_by_user_id.return_value = None
    email = "nonexistent@example.com"
    
    # Act & Assert
    with pytest.raises(Exception, match="User details requested not found"):
        mfa_service.get_user_details_by_mfa_id(email)


# Tests for get_mfa_details_via_email
def test_get_mfa_details_via_email(mfa_service, mock_mfa_repo, sample_mfa):
    # Arrange
    mock_mfa_repo.get_mfa_details_via_email.return_value = sample_mfa
    email = "user@example.com"
    
    # Act
    result = mfa_service.get_mfa_details_via_email(email)
    
    # Assert
    mock_mfa_repo.get_mfa_details_via_email.assert_called_once_with(email=email)
    assert result == sample_mfa


# Tests for create_totp_secret
@patch('pyotp.random_base32')
def test_create_totp_secret(mock_random_base32, mfa_service):
    # Arrange
    expected_secret = "TESTBASE32SECRET"
    mock_random_base32.return_value = expected_secret
    
    # Act
    result = mfa_service.create_totp_secret()
    
    # Assert
    assert result == expected_secret
    mock_random_base32.assert_called_once()


# Tests for create_mfa_entry
def test_create_mfa_entry(mfa_service, mock_mfa_repo):
    # Arrange
    expected_secret = "TESTBASE32SECRET"
    expected_mfa_id = 42
    mock_mfa_repo.create.return_value = expected_mfa_id
    
    # Mock the create_totp_secret method
    mfa_service.create_totp_secret = Mock(return_value=expected_secret)
    
    # Act
    result = mfa_service.create_mfa_entry()
    
    # Assert
    mfa_service.create_totp_secret.assert_called_once()
    mock_mfa_repo.create.assert_called_once_with(totp_secret=expected_secret)
    assert result == expected_mfa_id


# Tests for change_totp_secret
def test_change_totp_secret_success(mfa_service, mock_mfa_repo):
    # Arrange
    user_id = 123
    new_secret = "NEWBASE32SECRET"
    mfa_service.create_totp_secret = Mock(return_value=new_secret)
    mock_mfa_repo.update_mfa_secret.return_value = True
    
    # Act
    result = mfa_service.change_totp_secret(user_id)
    
    # Assert
    mfa_service.create_totp_secret.assert_called_once()
    mock_mfa_repo.update_mfa_secret.assert_called_once_with(user_id=user_id, otp_secret=new_secret)
    assert result == new_secret


def test_change_totp_secret_failure(mfa_service, mock_mfa_repo):
    # Arrange
    user_id = 123
    new_secret = "NEWBASE32SECRET"
    mfa_service.create_totp_secret = Mock(return_value=new_secret)
    mock_mfa_repo.update_mfa_secret.return_value = False
    
    # Act & Assert
    with pytest.raises(ValueError, match=f"Failed to update MFA secret for user {user_id}"):
        mfa_service.change_totp_secret(user_id)


# Tests for create_qrcode_totp
def test_create_qrcode_totp_with_existing_user(mfa_service, sample_mfa):
    # Arrange
    user_id = 123
    name = "testuser"
    secret_key = "ABCDEFGHIJKLMNOP"
    
    # Mock the necessary methods and functions
    mfa_service.get_mfa_details_via_user_id = Mock(return_value=sample_mfa)
    
    with patch('pyotp.TOTP') as mock_totp, \
         patch('qrcode.QRCode') as mock_qrcode:
        
        # Configure mocks
        mock_totp_instance = mock_totp.return_value
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp/BookStore:testuser?secret=ABCDEFGHIJKLMNOP&issuer=BookStore"
        
        mock_qrcode_instance = mock_qrcode.return_value
        mock_qr_image = Mock()
        mock_qrcode_instance.make_image.return_value = mock_qr_image
        
        # Mock BytesIO and base64 encode
        with patch('io.BytesIO') as mock_bytesio, \
             patch('base64.b64encode') as mock_b64encode:
            
            mock_buffer = Mock()
            mock_bytesio.return_value = mock_buffer
            mock_b64encode.return_value = b"base64encodedstring"
            
            # Act
            result = mfa_service.create_qrcode_totp(name=name, user_id=user_id)
    
    # Assert
    mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id)
    assert result["secret_key"] == secret_key
    assert "qr_code_base64" in result


def test_create_qrcode_totp_with_new_user(mfa_service):
    # Arrange
    name = "newuser"
    secret_key = "NEWBASE32SECRET"
    
    # Mock the necessary methods and functions
    mfa_service.create_totp_secret = Mock(return_value=secret_key)
    
    with patch('pyotp.TOTP') as mock_totp, \
         patch('qrcode.QRCode') as mock_qrcode:
        
        # Configure mocks
        mock_totp_instance = mock_totp.return_value
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp/BookStore:newuser?secret=NEWBASE32SECRET&issuer=BookStore"
        
        mock_qrcode_instance = mock_qrcode.return_value
        mock_qr_image = Mock()
        mock_qrcode_instance.make_image.return_value = mock_qr_image
        
        # Mock BytesIO and base64 encode
        with patch('io.BytesIO') as mock_bytesio, \
             patch('base64.b64encode') as mock_b64encode:
            
            mock_buffer = Mock()
            mock_bytesio.return_value = mock_buffer
            mock_b64encode.return_value = b"base64encodedstring"
            
            # Act
            result = mfa_service.create_qrcode_totp(name=name)
    
    # Assert
    mfa_service.create_totp_secret.assert_called_once()
    assert result["secret_key"] == secret_key
    assert "qr_code_base64" in result


def test_create_qrcode_totp_exception_handling(mfa_service):
    # Arrange
    user_id = 123
    name = "testuser"
    secret_key = "NEWBASE32SECRET"
    
    # Mock methods to simulate an exception when getting MFA details
    mfa_service.get_mfa_details_via_user_id = Mock(side_effect=Exception("MFA not found"))
    mfa_service.create_totp_secret = Mock(return_value=secret_key)
    
    with patch('pyotp.TOTP') as mock_totp, \
         patch('qrcode.QRCode') as mock_qrcode:
        
        # Configure mocks
        mock_totp_instance = mock_totp.return_value
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp/BookStore:testuser?secret=NEWBASE32SECRET&issuer=BookStore"
        
        mock_qrcode_instance = mock_qrcode.return_value
        mock_qr_image = Mock()
        mock_qrcode_instance.make_image.return_value = mock_qr_image
        
        # Mock BytesIO and base64 encode
        with patch('io.BytesIO') as mock_bytesio, \
             patch('base64.b64encode') as mock_b64encode:
            
            mock_buffer = Mock()
            mock_bytesio.return_value = mock_buffer
            mock_b64encode.return_value = b"base64encodedstring"
            
            # Act
            result = mfa_service.create_qrcode_totp(name=name, user_id=user_id)
    
    # Assert
    mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id)
    mfa_service.create_totp_secret.assert_called_once()
    assert result["secret_key"] == secret_key


# Tests for verify_totp
@patch('pyotp.TOTP')
def test_verify_totp_success(mock_totp, mfa_service):
    # Arrange
    secret_key = "TESTBASE32SECRET"
    token = "123456"
    
    mock_totp_instance = mock_totp.return_value
    mock_totp_instance.verify.return_value = True
    
    # Act
    result = mfa_service.verify_totp(secret_key, token)
    
    # Assert
    mock_totp.assert_called_once_with(secret_key)
    mock_totp_instance.verify.assert_called_once_with(token)
    assert result is True


@patch('pyotp.TOTP')
def test_verify_totp_failure(mock_totp, mfa_service):
    # Arrange
    secret_key = "TESTBASE32SECRET"
    token = "123456"
    
    mock_totp_instance = mock_totp.return_value
    mock_totp_instance.verify.return_value = False
    
    # Act
    result = mfa_service.verify_totp(secret_key, token)
    
    # Assert
    mock_totp.assert_called_once_with(secret_key)
    mock_totp_instance.verify.assert_called_once_with(token)
    assert result is False


# Tests for deactivate_mfa
def test_deactivate_mfa_success(mfa_service, mock_mfa_repo, sample_mfa):
    # Arrange
    user_id = 123
    mfa_service.get_mfa_details_via_user_id = Mock(return_value=sample_mfa)
    
    # Act
    mfa_service.deactivate_mfa(user_id)
    
    # Assert
    mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)
    mock_mfa_repo.delete.assert_called_once_with(mfa_id=sample_mfa.id)


def test_deactivate_mfa_not_found(mfa_service):
    # Arrange
    user_id = 123
    mfa_service.get_mfa_details_via_user_id = Mock(return_value=None)
    
    # Act & Assert
    with pytest.raises(ValueError, match="No MFA details found"):
        mfa_service.deactivate_mfa(user_id)