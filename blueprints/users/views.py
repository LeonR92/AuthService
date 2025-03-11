from flask import Blueprint, abort, redirect, render_template, request, jsonify, session, url_for
from blueprints.users import init_user_services


users = Blueprint(
    "users",
    __name__,
    template_folder="templates",  
    static_folder="static" ,
    url_prefix="/users"       
)


@users.route("/login")
def login():
    return render_template("users_login.html")

@users.route("/register")
def register_user():
    return render_template("users_register.html")

@users.route("/users", methods=["POST"])
def create_user():
    """Create a new user."""
    data = request.form.to_dict()
    user_service = init_user_services()
    user_service.create_user(**data)
    return redirect(url_for('users.login'))



@users.route("/get_users")
def get_user():
    user_service = init_user_services()
    users = user_service.get_all_users()
    return jsonify([{k: v for k, v in user.__dict__.items() if not k.startswith("_")} for user in users])

@users.route("/show_qr_code/<int:user_id>")
def show_qrcode(user_id: int):
    """Display QR code for MFA setup for both new and existing users"""
    user_service = init_user_services()
    user = user_service.get_user_by_id(user_id)
    if not user:
        abort(404)
        
    name = f"{user.last_name} {user.first_name}"
    
    qr_data = mfa_service.create_qrcode_totp(name=name, user_id=user_id)
    
    return render_template(
        'users_qrcode.html',
        qr_code=qr_data['qr_code_base64'],
        user_id=user_id,
        name=name
    )


@users.route("/mfa_input")
def mfa_input():
    user_id = session.get("user_id") 
    return render_template("users_otp_input.html", user_id = user_id)
