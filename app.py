from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os



# Initialize Flask app
app = Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")



@app.route("/")
def get_users():
    return "hi"

# Run app
if __name__ == "__main__":
    app.run(debug=True)
