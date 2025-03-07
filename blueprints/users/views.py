from flask import Blueprint, render_template, request, jsonify
from blueprints.users.service import UserService

# Initialize Blueprint
users_bp = Blueprint(
    "users",
    __name__,
    template_folder="templates",  
    static_folder="static"        
)


@users_bp.route("/profile")
def user_profile():
    return render_template("users_profile.html", title="User Profile")

@users_bp.route("/users", methods=["POST"])
def create_user():
    """Create a new user."""
    data = request.json

    user_service = UserService()
    user = user_service.register_user(email=data["email"], name=data["name"])
    return jsonify({"id": user.id, "email": user.email}), 201

@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Retrieve a user by ID."""

    user_service = UserService()
    user = user_service.get_user(user_id)
    if user:
        return jsonify({"id": user.id, "email": user.email})
    return jsonify({"error": "User not found"}), 404
