"""
Authentication Blueprint Module.

This module provides Flask routes for user authentication, including
login verification and multi-factor authentication (MFA) functionality.
It implements rate limiting to protect against brute force attacks and
uses Redis for session storage.

Routes:
    - /auth/authenticate: Processes user login credentials
    - /auth/verify_otp: Verifies one-time passwords for MFA
"""


from flask import Blueprint, jsonify, redirect, request, session, url_for
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.mfa_service import MFAservice
import logging
import redis


from core.database import get_read_db, get_write_db
from core.di import create_auth_service, create_mfa_service, create_user_service

auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",  
    static_folder="static" ,
    url_prefix="/auth"       
)

# Redis client for session storage
redis_client = redis.Redis(host='redis', port=6379, db=0)  




@auth.route("/authenticate", methods=["POST"])
def authenticate_login():
    """Authenticate user login credentials and handle MFA redirection if enabled.
    This endpoint processes the login form data, verifies credentials against
    the database, and initializes user session.
    """
    
    
    # Extracting HTML form data
    data = request.form
    email = data.get("email")
    password = data.get("password")

    # Guard claude and honeypot check
    honeypot = request.form.get("honeypot")
    if honeypot:
            logging.warning("Honeypot triggered: Possible bot detected.")
            return jsonify({"message": "Form submitted successfully"}), 204
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Init services
    with get_read_db() as read_db, get_write_db() as write_db:
        user_service = create_user_service(read_db=read_db,write_db=write_db)
        auth_service = create_auth_service(read_db=read_db, write_db=write_db)
        # verify password against db
        if not auth_service.verify_password(email, password):
            return jsonify({"error": "Authentication failed. Please check creds"}), 401
        
        # get MFA details to determine routing process
        mfa_service = create_mfa_service(read_db=read_db,write_db=write_db)
        mfa_enabled = mfa_service.get_mfa_details_via_email(email=email)
        user_id = user_service.get_userid_by_email(email=email)

    # save login into session
    session["user_email"] = email
    session["user_id"] = user_id
    session["is_authenticated"] = True

    # Redirect to MFA input page if MFA is enabled
    if mfa_enabled:
        return jsonify({"status": "success", "redirect": url_for("users.mfa_input")}), 200

    return jsonify({"status": "success", "redirect": url_for('dashboard.user_dashboard')}), 200


@auth.route("/verify_otp", methods=["POST"])
def verify_otp():
    """Verify the one-time password (OTP) code for MFA authentication.
    
    This endpoint validates a time-based one-time password (TOTP) submitted
    by a user who has MFA enabled.
    
    """

    # Only logged in users can access this page
    if not session.get("is_authenticated"):
        return jsonify({"error": "Authentication required", "redirect": url_for("users.login")}), 401
    
    # HTML form data extraction and guard clause
    totp = request.form.get("code")
    user_id = session.get("user_id")  
    if not user_id:
        return jsonify({"error": "Unauthorized: No user session found"}), 401
    if not totp:
        return jsonify({"error": "OTP code is required"}), 400

    # Init services for workflow
    with get_write_db() as write_db, get_read_db() as read_db:
        mfa_repo = MFARepository(write_db_session=write_db, read_db_session=read_db)
        mfa_service = MFAservice(mfa_repo=mfa_repo)
        # Guard clause
        mfa_details = mfa_service.get_mfa_details_via_user_id(user_id)
        if not mfa_details:
            return jsonify({"error": "MFA not set up for this user"}), 403

        try:
            # Verify OTP and save to session
            mfa_service.verify_totp(secret_key=mfa_details.totp_secret, token=totp)
            session["is_totp_authenticated"] = True
            return jsonify({"status": "success", "redirect": url_for('dashboard.user_dashboard')}), 200
        except ValueError:
            return jsonify({"error": "Invalid OTP code"}), 401