from flask import Blueprint, request

auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",  
    static_folder="static" ,
    url_prefix="/auth"       
)

@auth.route("/create_user", method = ["POST"])
def create_user():
    data = request.form
    return data