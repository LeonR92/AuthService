from flask import Blueprint, jsonify, request, session
from blueprints.auth.service import AuthService
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.crendentials_service import CredentialsService

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
    with get_write_db() as write_db, get_read_db() as read_db:
        cred_repo = CredentialsRepository(write_db_session=write_db, read_db_session=read_db)
        cred_service = CredentialsService(cred_repo=cred_repo)
        auth_service = AuthService(cred_service=cred_service)

        data = request.form
        email = data["email"]
        password = data["password"]
        try:
            if auth_service.verify_password(email, password):
                session["user_email"] = email
                session["is_authenticated"] = True
                return jsonify({"message": "Authenticated successfully"}), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
        except ValueError:
            return "Failed"
