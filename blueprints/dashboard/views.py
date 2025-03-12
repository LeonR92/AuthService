
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


@dashboard.route("/test")
def test_dashboard():
    return render_template("test_dashboard.html")


@dashboard.route("/welcome/")
def user_dashboard():
    user_id = session.get("user_id")
    with get_write_db() as write_db, get_read_db() as read_db:
        dashboard_service = create_dashboard_service(write_db=write_db, read_db=read_db)
        username = dashboard_service.get_username_by_userid(user_id=user_id)
        return render_template("dashboard_user.html",username=username)