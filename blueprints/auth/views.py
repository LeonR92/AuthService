from flask import Blueprint, jsonify, redirect, request, session, url_for
from blueprints.auth.service import AuthService
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.mfa_service import MFAservice


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

    with get_read_db() as read_db:
        cred_repo = CredentialsRepository(read_db_session=read_db)
        auth_service = AuthService(cred_repo=cred_repo)
        
        mfa_repo = MFARepository(read_db_session=read_db)
        mfa_service = MFAservice(mfa_repo=mfa_repo)

        if not auth_service.verify_password(email, password):
            return jsonify({"error": "Authentication failed"}), 401

        mfa_enabled = mfa_service.get_mfa_details_via_email(email=email)

    session["user_email"] = email
    session["is_authenticated"] = True

    # Redirect to MFA input page if MFA is enabled
    if mfa_enabled:
        return redirect(url_for("user.mfa_input"))

    return jsonify({"message": "Authenticated successfully"}), 200
