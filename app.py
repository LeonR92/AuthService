from flask import Flask
from dotenv import load_dotenv
import os
from blueprints.users.views import users
from core.init_db import init_db


# Initialize Flask app
app = Flask(__name__)
app.register_blueprint(users)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")



@app.route("/")
def get_users():
    return "hi"

# Run app
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)  

