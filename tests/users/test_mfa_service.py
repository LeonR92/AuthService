import pytest
from unittest.mock import Mock, patch
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.models import MFA


from blueprints.users.mfa_service import MFAservice


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


def test_get_mfa_details_via_user_id_success(mfa_service, mock_mfa_repo, sample_mfa):
    mock_mfa_repo.get_mfa_details_by_user_id.return_value = sample_mfa
    user_id = 123
    
    result = mfa_service.get_mfa_details_via_user_id(user_id)
    
    mock_mfa_repo.get_mfa_details_by_user_id.assert_called_once_with(user_id)
    assert result == sample_mfa


def test_get_mfa_details_via_user_id_missing_id(mfa_service):
    user_id = None
    
    with pytest.raises(ValueError, match="User id missing"):
        mfa_service.get_mfa_details_via_user_id(user_id)


def test_get_mfa_details_via_email(mfa_service, mock_mfa_repo, sample_mfa):
    mock_mfa_repo.get_mfa_details_via_email.return_value = sample_mfa
    email = "user@example.com"
    
    result = mfa_service.get_mfa_details_via_email(email)
    
    mock_mfa_repo.get_mfa_details_via_email.assert_called_once_with(email=email)
    assert result == sample_mfa


@patch('pyotp.random_base32')
def test_create_totp_secret(mock_random_base32, mfa_service):
    expected_secret = "TESTBASE32SECRET"
    mock_random_base32.return_value = expected_secret
    
    result = mfa_service.create_totp_secret()
    
    assert result == expected_secret
    mock_random_base32.assert_called_once()


def test_create_mfa_entry(mfa_service, mock_mfa_repo):
    expected_secret = "TESTBASE32SECRET"
    expected_mfa_id = 42
    mock_mfa_repo.create.return_value = expected_mfa_id
    
    mfa_service.create_totp_secret = Mock(return_value=expected_secret)
    
    result = mfa_service.create_mfa_entry()
    
    mfa_service.create_totp_secret.assert_called_once()
    mock_mfa_repo.create.assert_called_once_with(totp_secret=expected_secret)
    assert result == expected_mfa_id


def test_change_totp_secret_success(mfa_service, mock_mfa_repo):
    user_id = 123
    new_secret = "NEWBASE32SECRET"
    mfa_service.create_totp_secret = Mock(return_value=new_secret)
    mock_mfa_repo.update_mfa_secret.return_value = True
    
    result = mfa_service.change_totp_secret(user_id)
    
    mfa_service.create_totp_secret.assert_called_once()
    mock_mfa_repo.update_mfa_secret.assert_called_once_with(user_id=user_id, otp_secret=new_secret)
    assert result == new_secret


def test_change_totp_secret_failure(mfa_service, mock_mfa_repo):
    user_id = 123
    new_secret = "NEWBASE32SECRET"
    mfa_service.create_totp_secret = Mock(return_value=new_secret)
    mock_mfa_repo.update_mfa_secret.return_value = False
    
    with pytest.raises(ValueError, match=f"Failed to update MFA secret for user {user_id}"):
        mfa_service.change_totp_secret(user_id)


def test_create_qrcode_totp_with_existing_user(mfa_service, sample_mfa):
    user_id = 123
    name = "testuser"
    secret_key = "ABCDEFGHIJKLMNOP"
    
    mfa_service.get_mfa_details_via_user_id = Mock(return_value=sample_mfa)
    
    with patch('pyotp.TOTP') as mock_totp, \
         patch('qrcode.QRCode') as mock_qrcode:
        
        mock_totp_instance = mock_totp.return_value
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp/BookStore:testuser?secret=ABCDEFGHIJKLMNOP&issuer=BookStore"
        
        mock_qrcode_instance = mock_qrcode.return_value
        mock_qr_image = Mock()
        mock_qrcode_instance.make_image.return_value = mock_qr_image
        
        with patch('io.BytesIO') as mock_bytesio, \
             patch('base64.b64encode') as mock_b64encode:
            
            mock_buffer = Mock()
            mock_bytesio.return_value = mock_buffer
            mock_b64encode.return_value = b"base64encodedstring"
            
            result = mfa_service.create_qrcode_totp(name=name, user_id=user_id)
    
    mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id)
    assert result["secret_key"] == secret_key
    assert "qr_code_base64" in result


def test_create_qrcode_totp_with_new_user(mfa_service):
    name = "newuser"
    secret_key = "NEWBASE32SECRET"
    
    mfa_service.create_totp_secret = Mock(return_value=secret_key)
    
    with patch('pyotp.TOTP') as mock_totp, \
         patch('qrcode.QRCode') as mock_qrcode:
        
        mock_totp_instance = mock_totp.return_value
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp/BookStore:newuser?secret=NEWBASE32SECRET&issuer=BookStore"
        
        mock_qrcode_instance = mock_qrcode.return_value
        mock_qr_image = Mock()
        mock_qrcode_instance.make_image.return_value = mock_qr_image
        
        with patch('io.BytesIO') as mock_bytesio, \
             patch('base64.b64encode') as mock_b64encode:
            
            mock_buffer = Mock()
            mock_bytesio.return_value = mock_buffer
            mock_b64encode.return_value = b"base64encodedstring"
            
            result = mfa_service.create_qrcode_totp(name=name)
    
    mfa_service.create_totp_secret.assert_called_once()
    assert result["secret_key"] == secret_key
    assert "qr_code_base64" in result


def test_create_qrcode_totp_exception_handling(mfa_service):
    user_id = 123
    name = "testuser"
    secret_key = "NEWBASE32SECRET"
    
    mfa_service.get_mfa_details_via_user_id = Mock(side_effect=Exception("MFA not found"))
    mfa_service.create_totp_secret = Mock(return_value=secret_key)
    
    with patch('pyotp.TOTP') as mock_totp, \
         patch('qrcode.QRCode') as mock_qrcode:
        
        mock_totp_instance = mock_totp.return_value
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp/BookStore:testuser?secret=NEWBASE32SECRET&issuer=BookStore"
        
        mock_qrcode_instance = mock_qrcode.return_value
        mock_qr_image = Mock()
        mock_qrcode_instance.make_image.return_value = mock_qr_image
        
        with patch('io.BytesIO') as mock_bytesio, \
             patch('base64.b64encode') as mock_b64encode:
            
            mock_buffer = Mock()
            mock_bytesio.return_value = mock_buffer
            mock_b64encode.return_value = b"base64encodedstring"
            
            result = mfa_service.create_qrcode_totp(name=name, user_id=user_id)
    
    mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id)
    mfa_service.create_totp_secret.assert_called_once()
    assert result["secret_key"] == secret_key


@patch('pyotp.TOTP')
def test_verify_totp_success(mock_totp, mfa_service):
    secret_key = "TESTBASE32SECRET"
    token = "123456"
    
    mock_totp_instance = mock_totp.return_value
    mock_totp_instance.verify.return_value = True
    
    result = mfa_service.verify_totp(secret_key, token)
    
    mock_totp.assert_called_once_with(secret_key)
    mock_totp_instance.verify.assert_called_once_with(token)
    assert result is True


@patch('pyotp.TOTP')
def test_verify_totp_failure(mock_totp, mfa_service):
    secret_key = "TESTBASE32SECRET"
    token = "123456"
    
    mock_totp_instance = mock_totp.return_value
    mock_totp_instance.verify.return_value = False
    
    result = mfa_service.verify_totp(secret_key, token)
    
    mock_totp.assert_called_once_with(secret_key)
    mock_totp_instance.verify.assert_called_once_with(token)
    assert result is False


def test_deactivate_mfa_success(mfa_service, mock_mfa_repo, sample_mfa):
    user_id = 123
    mfa_service.get_mfa_details_via_user_id = Mock(return_value=sample_mfa)
    
    mfa_service.deactivate_mfa(user_id)
    
    mfa_service.get_mfa_details_via_user_id.assert_called_once_with(user_id=user_id)
    mock_mfa_repo.delete.assert_called_once_with(mfa_id=sample_mfa.id)


def test_deactivate_mfa_not_found(mfa_service):
    user_id = 123
    mfa_service.get_mfa_details_via_user_id = Mock(return_value=None)
    
    with pytest.raises(ValueError, match="No MFA details found"):
        mfa_service.deactivate_mfa(user_id)