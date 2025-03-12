from flask import Flask, redirect, request, session, url_for
from dotenv import load_dotenv
import os
from blueprints.users.views import users
from blueprints.auth.views import auth
from blueprints.dashboard.views import dashboard
from core.init_db import init_db
from core.init_redis import init_redis
from flask_compress import Compress



# Initialize Flask app
app = Flask(__name__)
Compress(app)
init_redis(app)
app.register_blueprint(users)
app.register_blueprint(auth)
app.register_blueprint(dashboard)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

@app.before_request
def require_login():
    """Function to block access to the dashboard blueprint for unauthenticated users."""
    # Check if the request is for a route under the dashboard blueprint
    if request.endpoint and request.endpoint.startswith('dashboard'):
        if not session.get("is_authenticated"):
            return redirect(url_for('users.login'))





@app.route("/")
def get_users():
    return "hi"

# Run app
if __name__ == "__main__":

    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)  

