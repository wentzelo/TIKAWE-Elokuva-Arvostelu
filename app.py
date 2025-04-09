import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session 
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import posts
import users

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_posts = posts.get_posts()
    return render_template("index.html", posts=all_posts)

@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = posts.get_post(post_id)
    return render_template("show_post.html", post=post)

@app.route("/new_post")
def new_post():
    return render_template("new_post.html")

@app.route("/create_post", methods=["POST"])
def create_post():
    title = request.form["title"]
    rating = request.form["rating"]
    review_text = request.form["review_text"]
    user_id = session["user_id"]

    posts.add_post(title, rating, review_text, user_id)

    return redirect("/") #Moves to the main page after creating the post

@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = posts.get_post(post_id)

    if request.method == "GET":
        return render_template("edit_post.html", post=post)

    if request.method == "POST":
        title = request.form["title"]
        rating = request.form["rating"]
        review_text = request.form["review_text"]

        posts.update_post(post_id, title, rating, review_text)

        return redirect(f"/post/{post_id}")
    
@app.route("/remove_post/<int:post_id>", methods=["GET", "POST"])
def remove_post(post_id):
    post = posts.get_post(post_id)

    if request.method == "GET":
        return render_template("remove_post.html", post=post)

    if request.method == "POST":
        if "continue" in request.form:
            posts.delete_post(post_id)
        return redirect("/")
    
@app.route("/search_post")
def search_post():
    query = request.args.get("query")
    results = posts.find_posts(query) if query else []
    return render_template("search_post.html", query=query, results=results)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"

    success = users.create_user(username, password1)
    if not success:
        return "VIRHE: tunnus on jo varattu"

    return render_template("register_return.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = users.login_user(username, password)

    if user:
        session["user_id"] = user["id"]
        session["username"] = username
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
