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
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://redis:6379/0",
    strategy="fixed-window"
)

def create_app():
    load_dotenv()
 
    app = Flask(__name__)
    Compress(app)
    init_redis(app)

    

    limiter.init_app(app)
    app.register_blueprint(users)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)

    

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")



    limiter.limit("10 per minute")(app.view_functions["auth.authenticate_login"])


    @app.before_request
    def before_request():
        """Middleware to log requests and enforce authentication for dashboard routes."""
        
        # Log request details
        logging.info(f"Incoming request: {request.method} {request.path} - From: {request.remote_addr}")

        # Restrict access to dashboard routes for unauthenticated users
        if request.endpoint and request.endpoint.startswith('dashboard'):
            if not session.get("is_authenticated"):
                return redirect(url_for('users.login'))
            
    @app.route("/")
    def index():
        return redirect(url_for('users.login'))

    return app


    

app = create_app()

