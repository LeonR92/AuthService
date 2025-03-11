from flask import Flask
from dotenv import load_dotenv
import os
from blueprints.users.views import users
from blueprints.auth.views import auth
from core.init_db import init_db
from core.init_redis import init_redis


# Initialize Flask app
app = Flask(__name__)
app.register_blueprint(users)
app.register_blueprint(auth)


load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")



@app.route("/")
def get_users():
    return "hi"

# Run app
if __name__ == "__main__":
    init_redis(app)
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)  

