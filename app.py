import logging
from flask import Flask, redirect, request, session, url_for
from dotenv import load_dotenv
import os

from blueprints.users.views import users
from blueprints.auth.views import auth
from blueprints.dashboard.views import dashboard
from core.init_db import init_db
from core.init_redis import init_redis
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address




logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Initialize Flask app
app = Flask(__name__)
Compress(app)
init_redis(app)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://redis:6379/0",
    strategy="fixed-window"
)
limiter.init_app(app)
app.register_blueprint(users)
app.register_blueprint(auth)
app.register_blueprint(dashboard)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")



limiter.limit("10 per minute")(app.view_functions["auth.authenticate_login"])


@app.before_request
def log_request():
    """Logs every request before it reaches a route."""
    logging.info(f"Incoming request: {request.method} {request.path} - From: {request.remote_addr}")


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

