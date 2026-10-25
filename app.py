import os
import pymongo
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from bson.objectid import ObjectId
import flask_login
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError

load_dotenv()

connection = pymongo.MongoClient(os.getenv("MONGO_URI"))

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

db = connection[os.getenv("MONGO_DBNAME")]

users = db.users
users.create_index("email", unique = True)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    try:
        data = users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None

    user = User()
    user.id = str(data["_id"])
    user.name = data["name"]
    user.email = data["email"]
    return user

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if not name or not email or not password:
            return render_template("signup.html", error="missing fields")

        if len(password) < 8:
            return render_template("signup.html", error="password is too short")

        if password != confirm:
            return render_template("signup.html", error="passwords do not match")

        try:
            db.users.insert_one({
                "name": name,
                "email": email,
                "password_hash": generate_password_hash(password)
            })

            return redirect(url_for("login"))
        
        except DuplicateKeyError:
            return render_template("signup.html", error="user already exists")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        data = db.users.find_one({"email": email})

        if data and check_password_hash(data["password_hash"], password):
            user = User()
            user.id = str(data["_id"])
            user.name = data["name"]
            user.email = data["email"]

            flask_login.login_user(user)
            return redirect(url_for("home"))

        return render_template("login.html", error="incorrect email or password")

    return render_template("login.html")
        
@app.route("/home")
def home():
    post = db.posts.find().sort("_id", -1)
    return render_template("home.html", posts=post)

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("login"))

@app.route("/add_post")
@flask_login.login_required
def add_post():
    return render_template("add_post.html")

@app.route("/save", methods=['POST'])
@flask_login.login_required
def post():
    title = request.form["title"]
    description = request.form["description"]
    last_seen = request.form["last_seen"]

    db.posts.insert_one({
        "title": title,
        "description": description,
        "last_seen": last_seen,
        "user_id": str(flask_login.current_user.id)
    })

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)