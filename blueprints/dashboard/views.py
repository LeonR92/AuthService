



from flask import Blueprint, render_template


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