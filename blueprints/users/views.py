from flask import Blueprint, render_template, request, jsonify
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.user_service import UserService
from core.database import get_read_db,get_write_db


# Initialize Blueprint
users = Blueprint(
    "users",
    __name__,
    template_folder="templates",  
    static_folder="static"        
)


@users.route("/profile")
def user_profile():
    return render_template("users_profile.html", title="User Profile")

@users.route("/users", methods=["POST"])
def create_user():
    """Create a new user."""
    data = request.json

    user_service = UserService()
    user = user_service.create_user(data)
    return jsonify({"id": user.id, "email": user.email}), 201

@users.route("/create_credentials", methods=["POST"])
def create_credentials():
    """Create a new user."""
    data = request.json

    with get_write_db() as write_db, get_read_db() as read_db:
        cred_repo = CredentialsRepository(write_db,read_db)
        cred_service = CredentialsService(cred_repo = cred_repo)
        credentials = cred_service.create_credentials(data)
    return jsonify({"id": credentials.id, "email": credentials.email}), 201

@users.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Retrieve a user by ID."""

    user_service = UserService()
    user = user_service.get_user(user_id)
    if user:
        return jsonify({"id": user.id, "email": user.email})
    return jsonify({"error": "User not found"}), 404
