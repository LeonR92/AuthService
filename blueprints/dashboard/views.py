"""Dashboard routes for user portal.
"""
from flask import Blueprint, render_template, session
from core.database import get_read_db, get_write_db
from core.di import create_dashboard_service


dashboard = Blueprint(
    "dashboard",
    __name__,
    template_folder="templates",  
    static_folder="static" ,
    url_prefix="/dashboard"       
)



@dashboard.route("/welcome/")
def user_dashboard():
    """User's main dashboard page.
    
    :return: Rendered dashboard with username and MFA status
    :rtype: str
    """
    user_id = session.get("user_id")
    with get_write_db() as write_db, get_read_db() as read_db:
        dashboard_service = create_dashboard_service(write_db=write_db, read_db=read_db)
        # If MFA is enabled then show "deactivate MFA in dashboard else activate MFA"
        mfa_enabled = dashboard_service.is_mfa_enabled(user_id=user_id)
        # for greeting prupose
        username = dashboard_service.get_username_by_userid(user_id=user_id)
        return render_template("dashboard_user.html",username=username,mfa_enabled = mfa_enabled)