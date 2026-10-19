import os
import pymongo
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, abort, url_for, make_response
from bson.objectid import ObjectId
import datetime

load_dotenv()

connection = pymongo.MongoClient(os.getenv("MONGO_URI"))

db = connection[os.getenv("MONGO_DBNAME")]

app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/add_post")
def add_post():
    return render_template("add_post.html")

@app.route("/save", methods=['POST'])
def post():
    title = request.form["title"]
    description = request.form["description"]
    last_seen = request.form["last_seen"]

    db.posts.insert_one({
        "title": title,
        "description": description,
        "last_seen": last_seen
    })

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)