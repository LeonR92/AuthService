import os
import redis
from flask_session import Session
from urllib.parse import urlparse

session = Session()  

def init_redis(app):
    """Configure Flask session storage using Redis"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    parsed_url = urlparse(redis_url)

    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_KEY_PREFIX"] = "session:"
    app.config["SESSION_REDIS"] = redis.Redis(
        host=parsed_url.hostname,
        port=parsed_url.port,
        db=int(parsed_url.path.lstrip("/")),
        decode_responses=False,  
    )

    # Use JSON serialization explicitly
    app.config["SESSION_SERIALIZATION_FORMAT"] = "json"

    session.init_app(app)  