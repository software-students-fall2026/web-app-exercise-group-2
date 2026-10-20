import os

from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from flask import Flask, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

csrf = CSRFProtect(app)

# Connect to MongoDB
client = MongoClient(
    os.environ["MONGO_URI"],
    serverSelectionTimeoutMS=5000
)

db = client[os.environ["MONGO_DB"]]
users = db["users"]

users.create_index("email", unique=True)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Check the information before saving
        if not name or not email or not password or not confirm_password:
            error = "Please fill in all fields."
        elif len(password) < 8:
            error = "Your password must have at least 8 characters."
        elif password != confirm_password:
            error = "Your passwords do not match."
        else:
            try:
                validate_email(email, check_deliverability=False)
            except EmailNotValidError:
                error = "Please enter a valid email address."

        if error is None:
            new_user = {
                "name": name,
                "email": email,
                "password_hash": generate_password_hash(password)
            }

            try:
                users.insert_one(new_user)
                return redirect(url_for("login", registered="yes"))
            except DuplicateKeyError:
                error = "An account with this email already exists."

    return render_template("signup.html", error=error)