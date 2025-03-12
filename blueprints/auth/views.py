from flask import Blueprint, jsonify, redirect, request, session, url_for
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.mfa_service import MFAservice
import logging


from core.database import get_read_db, get_write_db
from core.di import create_auth_service, create_mfa_service, create_user_service

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
    honeypot = request.form.get("honeypot")
    if honeypot:
            logging.warning("Honeypot triggered: Possible bot detected.")
            return "", 204
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    with get_read_db() as read_db, get_write_db() as write_db:
        user_service = create_user_service(read_db=read_db,write_db=write_db)
        auth_service = create_auth_service(read_db=read_db, write_db=write_db)
        if not auth_service.verify_password(email, password):
            return jsonify({"error": "Authentication failed"}), 401
        mfa_service = create_mfa_service(read_db=read_db,write_db=write_db)
        mfa_enabled = mfa_service.get_mfa_details_via_email(email=email)
        user_id = user_service.get_userid_by_email(email=email)

    session["user_email"] = email
    session["user_id"] = user_id
    session["is_authenticated"] = True

    # Redirect to MFA input page if MFA is enabled
    if mfa_enabled:
        return redirect(url_for("users.mfa_input"))

    return redirect(url_for('dashboard.user_dashboard'))


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
            return redirect(url_for('dashboard.user_dashboard'))
        except ValueError:
            return jsonify({"error": "Invalid OTP code"}), 401


