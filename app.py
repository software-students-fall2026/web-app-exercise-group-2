"""Flask routes for the campus lost and found feed."""

import os
import re
import secrets

from bson import ObjectId
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
    MONGO_URI=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
    MONGO_DBNAME=os.getenv("MONGO_DBNAME", "lost_and_found"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
)

mongo_client = MongoClient(app.config["MONGO_URI"])


def posts_collection():
    """Return the configured collection; tests may inject an isolated collection."""
    configured_collection = app.config.get("POSTS_COLLECTION")
    if configured_collection is not None:
        return configured_collection
    return mongo_client[app.config["MONGO_DBNAME"]].posts


def csrf_token():
    token = session.get("csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


app.jinja_env.globals["csrf_token"] = csrf_token


def require_valid_csrf():
    submitted = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not secrets.compare_digest(submitted, expected):
        abort(400, description="The form expired or was invalid. Please try again.")


def post_id_from_url(post_id):
    if not re.fullmatch(r"[0-9a-fA-F]{24}", post_id):
        abort(400, description="Invalid post ID.")
    return ObjectId(post_id)


def owned_post(post_id):
    owner_id = session.get("owner_id")
    if owner_id is None:
        abort(404)
    post = posts_collection().find_one(
        {"_id": post_id_from_url(post_id), "owner_id": owner_id}
    )
    if post is None:
        # Same response for missing, ownerless, and another user's posts.
        abort(404)
    return post


def validated_post_fields():
    fields = {
        name: request.form.get(name, "").strip()
        for name in ("title", "description", "last_seen")
    }
    missing = [name.replace("_", " ") for name, value in fields.items() if not value]
    if missing:
        return None, "Please provide " + ", ".join(missing) + "."
    return fields, None


@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/home")
def home():
    posts = list(posts_collection().find().sort("_id", -1))
    for post in posts:
        post["id"] = str(post["_id"])
    return render_template("home.html", posts=posts, owner_id=session.get("owner_id"))


@app.route("/add_post", methods=["GET"])
def add_post():
    return render_template("add_post.html", post={})


@app.route("/save", methods=["POST"])
def create_post():
    require_valid_csrf()
    fields, error = validated_post_fields()
    if error:
        return render_template("add_post.html", post=request.form, error=error), 400

    owner_id = session.get("owner_id")
    if owner_id is None:
        owner_id = secrets.token_urlsafe(32)
        session["owner_id"] = owner_id
    posts_collection().insert_one({**fields, "owner_id": owner_id})
    flash("Your post was added.", "success")
    return redirect(url_for("home"))


@app.route("/posts/<post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    post_id_from_url(post_id)
    post = owned_post(post_id)
    if request.method == "POST":
        require_valid_csrf()
        fields, error = validated_post_fields()
        if error:
            return render_template(
                "edit-post.html", post={**post, **request.form, "id": post_id}, error=error
            ), 400
        posts_collection().update_one(
            {"_id": post["_id"], "owner_id": session["owner_id"]}, {"$set": fields}
        )
        flash("Your changes were saved.", "success")
        return redirect(url_for("home"))
    post["id"] = post_id
    return render_template("edit-post.html", post=post)


@app.route("/posts/<post_id>/delete", methods=["GET", "POST"])
def delete_post(post_id):
    post_id_from_url(post_id)
    post = owned_post(post_id)
    if request.method == "POST":
        require_valid_csrf()
        posts_collection().delete_one(
            {"_id": post["_id"], "owner_id": session["owner_id"]}
        )
        flash("Your post was deleted.", "success")
        return redirect(url_for("home"))
    return render_template("delete-post.html", post=post, post_id=post_id)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
