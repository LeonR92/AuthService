from flask import Blueprint, jsonify, redirect, request, session, url_for
from blueprints.auth.service import AuthService
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_repository import UserRepository
from blueprints.users.user_service import UserService


from core.database import get_read_db, get_write_db

auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",  
    static_folder="static" ,
    url_prefix="/auth"       
)

@auth.route("/authenticate", methods=["POST"])
def authenticate_login():
    """Authenticate user and handle MFA if enabled"""
    
    # Extract request data safely
    data = request.form
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    with get_read_db() as read_db, get_write_db() as write_db:
        cred_repo = CredentialsRepository(write_db_session=write_db,read_db_session=read_db)
        cred_service = CredentialsService(cred_repo=cred_repo)
        auth_service = AuthService(cred_service=cred_service)
        mfa_repo = MFARepository(read_db_session=read_db,write_db_session=write_db)
        mfa_service = MFAservice(mfa_repo=mfa_repo)
        user_repo = UserRepository(write_db_session=write_db,read_db_session=read_db)
        user_service = UserService(user_repo=user_repo, cred_service=cred_service , mfa_service=mfa_service)

        if not auth_service.verify_password(email, password):
            return jsonify({"error": "Authentication failed"}), 401

        mfa_enabled = mfa_service.get_mfa_details_via_email(email=email)
        user_id = user_service.get_userid_by_email(email=email)

    session["user_email"] = email
    session["user_id"] = user_id
    session["is_authenticated"] = True
    print(session.get("is_authenticated"))

    # Redirect to MFA input page if MFA is enabled
    if mfa_enabled:
        return redirect(url_for("users.mfa_input"))

    return jsonify({"message": "Authenticated successfully"}), 200



@auth.route("/verify_otp", methods=["POST"])
def verify_otp():
    """Verify OTP code for MFA authentication"""
    if not session.get("is_authenticated"):
        return redirect(url_for("users.login"))
    totp = request.form.get("code")
    user_id = session.get("user_id")  

    if not user_id:
        return jsonify({"error": "Unauthorized: No user session found"}), 401
    
    if not totp:
        return jsonify({"error": "OTP code is required"}), 400

    with get_write_db() as write_db, get_read_db() as read_db:
        mfa_repo = MFARepository(write_db_session=write_db, read_db_session=read_db)
        mfa_service = MFAservice(mfa_repo=mfa_repo)
        
        mfa_details = mfa_service.get_mfa_details_via_user_id(user_id)
        if not mfa_details:
            return jsonify({"error": "MFA not set up for this user"}), 403

        try:
            mfa_service.verify_totp(secret_key=mfa_details.totp_secret, token=totp)
            session["is_totp_authenticated"] = True
            return jsonify({"message": "OTP verified successfully"}), 200
        except ValueError:
            return jsonify({"error": "Invalid OTP code"}), 401
