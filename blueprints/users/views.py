from flask import Blueprint, abort, redirect, render_template, request, jsonify, url_for
from blueprints.users.credentials_repository import CredentialsRepository
from blueprints.users.crendentials_service import CredentialsService
from blueprints.users.mfa_repository import MFARepository
from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_repository import UserRepository
from blueprints.users.user_service import UserService
from core.database import get_read_db,get_write_db


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
    with get_write_db() as write_db, get_read_db() as read_db:
        user_repo = UserRepository(write_db_session=write_db,read_db_session=read_db)
        cred_repo = CredentialsRepository(write_db, read_db)
        cred_service = CredentialsService(cred_repo=cred_repo)
        mfa_repo = MFARepository(write_db_session=write_db, read_db_session=read_db)
        mfa_service = MFAservice(mfa_repo=mfa_repo)
        user_service = UserService(user_repo=user_repo,cred_service=cred_service, mfa_service=mfa_service)
        user_id = user_service.create_user(**data)
    return redirect(url_for('users.login'))



@users.route("/get_users")
def get_user():
     with get_write_db() as write_db, get_read_db() as read_db:
        user_repo = UserRepository(write_db_session=write_db,read_db_session=read_db)
        cred_repo = CredentialsRepository(write_db, read_db)
        cred_service = CredentialsService(cred_repo=cred_repo)
        mfa_repo = MFARepository(write_db_session=write_db, read_db_session=read_db)
        mfa_service = MFAservice(mfa_repo=mfa_repo)
        user_service = UserService(user_repo=user_repo,cred_service=cred_service, mfa_service=mfa_service)
        users = user_service.get_all_users()
        return jsonify([{k: v for k, v in user.__dict__.items() if not k.startswith("_")} for user in users])

@users.route("/show_qr_code/<int:user_id>")
def show_qrcode(user_id:int):
    with get_write_db() as write_db, get_read_db() as read_db:
        user_repo = UserRepository(write_db_session=write_db,read_db_session=read_db)
        user_service = UserService(user_repo=user_repo)
        mfa_repo = MFARepository(write_db_session=write_db,read_db_session=read_db)
        mfa_service = MFAservice(mfa_repo=mfa_repo)
        
        user = user_service.get_user_by_id(user_id)
        if not user:
            abort(404)  
        
        email = user.email
        
        # Check if user already has MFA
        try:
            # Try to get existing MFA details
            mfa_details = mfa_service.get_mfa_details_via_user_id(user_id)
            has_existing_mfa = True
        except Exception:
            has_existing_mfa = False
        
        # Generate QR code
        qr_data = mfa_service.create_qrcode_totp(email=email, user_id=user_id if has_existing_mfa else None)
    

    # Render the template with the QR code
    return render_template(
        'users/mfa_setup.html',
        qr_code=qr_data['qr_code_base64'],
        user_id=user_id,
        email=email,
        is_new_setup=not has_existing_mfa
    )
        



@users.route("/mfa_input")
def mfa_input():
    return render_template("users_otp_input.html")
