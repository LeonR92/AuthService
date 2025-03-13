"""
User Authentication Blueprint.

This module provides routes for user authentication, registration, 
and multi-factor authentication management in the application.

Routes:
- /login: User login page
- /register: User registration page
- /users: User creation endpoint
- /show_qr_code: Display QR code for MFA setup
- /activate_mfa: Activate MFA for a user
- /logout: User logout
- /deactivate_mfa: Disable MFA for a user
- /mfa_input: OTP input page for MFA
- /forgot_password: Password reset request
- /reset_password: Password reset endpoint
- /change_password: Password change form and endpoint
"""


from flask import Blueprint, abort, redirect, render_template, request, session, url_for, jsonify
from core.di import create_credentials_service, create_mfa_service, create_user_service
from core.database import get_read_db, get_write_db


users = Blueprint(
    "users",
    __name__,
    template_folder="templates",  
    static_folder="static" ,
    url_prefix="/users"       
)


@users.route("/login")
def login():
    """Render the login page."""
    try:
        return render_template("users_login.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/register")
def register_user():
    """Render the user registration page."""
    try:
        return render_template("users_register.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/users", methods=["POST"])
def create_user():
    """Create a new user from form data.
    Redirects to login page upon successful creation.
    """
    try:
        data = request.form.to_dict()
        with get_write_db() as write_db, get_read_db() as read_db:
            user_service = create_user_service(write_db=write_db, read_db=read_db)
            user_service.create_user(**data)
            return redirect(url_for('users.login'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@users.route("/show_qr_code")
def show_qrcode():
    """Display QR code for MFA setup.
    
    Retrieves user from session and generates a QR code for
    multi-factor authentication setup.
    """
    try:
        with get_write_db() as write_db, get_read_db() as read_db:
            # retrieve user details via user_id
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"error": "User not authenticated"}), 401
                
            user_service = create_user_service(write_db=write_db, read_db=read_db)
            user = user_service.get_user_by_id(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # show name and create qrcode
            name = f"{user.last_name} {user.first_name}"
            mfa_service = create_mfa_service(write_db=write_db, read_db=read_db)
            qr_data = mfa_service.create_qrcode_totp(name=name, user_id=user_id)
            
            return render_template(
                'users_qrcode.html',
                qr_code=qr_data['qr_code_base64'],
                user_id=user_id,
                name=name
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/activate_mfa")
def activate_mfa():
    """
    Activate MFA for current user and display setup QR code.
    
    Activates multi-factor authentication for the current user
    and generates a QR code for setup.
    """
    try:
        with get_write_db() as write_db, get_read_db() as read_db:
            # retrieve user details via user_id
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"error": "User not authenticated"}), 401
                
            user_service = create_user_service(write_db=write_db, read_db=read_db)
            user = user_service.get_user_by_id(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # create qrcode
            name = f"{user.last_name} {user.first_name}"
            mfa_service = create_mfa_service(write_db=write_db, read_db=read_db)
            user_service.activate_mfa(user_id)
            qr_data = mfa_service.create_qrcode_totp(name=name, user_id=user_id)
            
            return render_template(
                'users_qrcode.html',
                qr_code=qr_data['qr_code_base64'],
                user_id=user_id,
                name=name
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/logout", methods=["POST"])
def logout():
    """
    Log user out by clearing session.
    
    Redirects to login page.
    """
    try:
        session.clear()
        return redirect(url_for("users.login"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/deactivate_mfa", methods=["POST"])
def deactivate_mfa():
    """
    Deactivate MFA for current user.
    
    Removes multi-factor authentication for the current user
    and redirects to login page.
    """
    try:
        with get_write_db() as write_db, get_read_db() as read_db:
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"error": "User not authenticated"}), 401
                
            mfa_service = create_mfa_service(write_db=write_db, read_db=read_db)
            # delete mfa details of a user via user_id
            mfa_service.deactivate_mfa(user_id=user_id)
            return redirect(url_for("users.login"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/mfa_input")
def mfa_input():
    """Render the OTP input page for MFA verification."""
    try:
        return render_template("users_otp_input.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/forgot_password")
def forgot_password():
    """Handle password reset requests (demo implementation)."""
    try:
        return "In Prod, the new randomly generated password will be sent via email"
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/reset_password", methods=["POST"])
def reset_password():
    """
    Reset user password to a randomly generated one.
    
    In production, would send new password via email.
    """
    try:
        with get_write_db() as write_db, get_read_db() as read_db:
            cred_service = create_credentials_service(write_db=write_db, read_db=read_db)
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"error": "User not authenticated"}), 401
                
            email = cred_service.get_email_by_userid(user_id)
            # Reset password using email
            new_password = cred_service.reset_password(email=email)
            session.clear()

            return f"{new_password} is your new password in the demo session. In prod, it will be sent to your email."
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users.route("/change_password", methods=["GET"])
def change_password_form():
    """Render the password change form."""
    try:
        return render_template("users_changepw.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users.route("/change_password", methods=["POST"])
def change_password():
    """
    Change user password with validation.
    
    Processes the password change form, updates the password
    and redirects to dashboard upon success.
    """
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "User not authenticated"}), 401
            
        with get_write_db() as write_db, get_read_db() as read_db:
            cred_service = create_credentials_service(write_db=write_db, read_db=read_db)
            # Password confirmation
            new_password = request.form.get("newpassword")
            confirm_new_password = request.form.get("confirmpassword")
            
            if not new_password or not confirm_new_password:
                return jsonify({"error": "Missing required password fields"}), 400
                
            # Change password
            cred_service.change_password(
                user_id=user_id,
                new_password=new_password,
                confirm_new_password=confirm_new_password
            )
            return redirect(url_for('dashboard.user_dashboard'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500