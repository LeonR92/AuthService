import os
import redis
from flask_session import Session
from datetime import timedelta
from urllib.parse import urlparse

session = Session()  

def init_redis(app):
    """Configure Flask session storage using Redis with 30-minute timeout"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    parsed_url = urlparse(redis_url)

    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PERMANENT"] = True  
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)  
    app.config["SESSION_USE_SIGNER"] = True  
    app.config["SESSION_KEY_PREFIX"] = "flask_session:"  
    app.config["SESSION_REDIS"] = redis.Redis(
        host=parsed_url.hostname,
        port=parsed_url.port,
        db=int(parsed_url.path.lstrip("/")),
        decode_responses=False,  
    )

    session.init_app(app)  
