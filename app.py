"""Main application file for the Elokuva-arvostelu web app."""

from flask import Flask
from flask import abort, redirect, render_template, request, session
import config
import posts
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def check_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_posts = posts.get_posts()
    return render_template("index.html", posts=all_posts)

@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = posts.get_post(post_id)
    genres = posts.get_post_genres(post_id)
    if not post:
        abort(404)

    good_count, bad_count = posts.get_comment_counts(post_id)
    comments = posts.get_comments(post_id)

    return render_template("show_post.html",
                                            post=post,
                                            genres=genres,
                                            good_count=good_count,
                                            bad_count=bad_count,
                                            comments=comments)

@app.route("/new_post")
def new_post():
    check_login()
    return render_template("new_post.html")

@app.route("/create_post", methods=["POST"])
def create_post():
    check_login()

    title = request.form["title"]
    if len(title) > 100:
        abort(403)
    rating = request.form["rating"]
    review_text = request.form["review_text"]
    if len(review_text) > 4200:
        abort(403)

    user_id = session["user_id"]
    watch_date = request.form["watch_date"]
    genres = request.form.getlist("genres")
    custom_genre = request.form.get("custom_genre", "").strip()

    post_id = posts.add_post(title, rating, review_text, watch_date, user_id)

    if custom_genre:
        genres.append(custom_genre)

    for genre in genres:
        genre_id = posts.get_or_create_genre(genre)
        posts.add_post_genre(post_id, genre_id)

    return redirect("/")

@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    check_login()

    post = posts.get_post(post_id)
    genres = posts.get_post_genres(post_id)

    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit_post.html", post=post, genres=genres)

    # POST
    title = request.form["title"]
    if len(title) > 100:
        abort(403)

    rating = request.form["rating"]
    review_text = request.form["review_text"]
    if len(review_text) > 4200:
        abort(403)

    watch_date = request.form["watch_date"]
    selected_genres = request.form.getlist("genres")
    custom_genre = request.form.get("custom_genre", "").strip()

    posts.update_post(post_id, title, rating, review_text, watch_date)

    #replace old genres
    posts.update_post_genres(post_id, selected_genres, custom_genre)

    return redirect(f"/post/{post_id}")

@app.route("/remove_post/<int:post_id>", methods=["GET", "POST"])
def remove_post(post_id):
    check_login()

    post = posts.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_post.html", post=post)

    if request.method == "POST" and "continue" in request.form:
        posts.delete_post(post_id)
    return redirect("/")

@app.route("/search_post")
def search_post():
    query = request.args.get("query")
    results = posts.find_posts(query) if query else []
    return render_template("search_post.html", query=query, results=results)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_posts = users.get_user_posts(user_id)
    return render_template("show_user.html", user=user, posts=user_posts)

@app.route("/comment/<int:post_id>", methods=["POST"])
def give_comment(post_id):
    reaction = request.form.get("reaction")
    text = request.form.get("comment", "").strip()

    if reaction not in ("good", "bad"):
        abort(400)

    is_positive = 1 if reaction == "good" else 0
    posts.add_comment(post_id, is_positive, text)

    return redirect(f"/post/{post_id}")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username.strip() or not password1.strip() or not password2.strip():
        return "VIRHE: kentät eivät saa olla tyhjiä" 

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

    return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
