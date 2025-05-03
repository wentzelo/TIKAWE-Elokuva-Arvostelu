from flask import Flask, abort, redirect, render_template, request, session, flash
import config
import posts
import users
from datetime import date
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

def check_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
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
    check_csrf()
    
    today = date.today().isoformat()

    title = request.form["title"].strip()
    if not title:
        flash("VIRHE: Elokuvan nimi ei voi olla tyhjä tai pelkkä välilyönti")
        return redirect("/new_post")
    if len(title) > 100:
        flash("VIRHE: Elokuvan nimi on liian pitkä (max 100 merkkiä)")
        return redirect("/new_post")

    rating = request.form["rating"]
    review_text = request.form["review_text"]
    if len(review_text) > 4200:
        flash("VIRHE: Arvostelu on liian pitkä (max 4200 merkkiä)")
        return redirect("/new_post")

    watch_date = request.form["watch_date"]
    if watch_date > today:
        flash("VIRHE: Katsomispäivä ei voi olla tulevaisuudessa.")
        return redirect("/new_post")

    user_id = session["user_id"]
    genres = request.form.getlist("genres")
    custom_genre = request.form.get("custom_genre", "").strip()

    post_id = posts.add_post(title, rating, review_text, watch_date, user_id)
    posts.update_post_genres(post_id, genres, custom_genre)

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
    check_csrf()
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
        check_csrf()
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
    check_csrf()

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
    check_csrf()
    
    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username or not password1 or not password2:
        flash("VIRHE: Kentät eivät saa olla tyhjiä")
        return redirect("/register")

    if len(password1) < 6 or not any(char.isdigit() for char in password1):
        flash("VIRHE: Salasanan tulee olla vähintään 6 merkkiä pitkä ja sisältää ainakin yksi numero")
        return redirect("/register")

    if password1 != password2:
        flash("VIRHE: Salasanat eivät ole samat")
        return redirect("/register")

    success = users.create_user(username, password1)
    if not success:
        flash("VIRHE: Tunnus on jo varattu")
        return redirect("/register")

    return render_template("register_return.html")

from flask import request, render_template, redirect, session, flash

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    if not username.strip() or not password.strip():
        flash("VIRHE: Tunnus ja salasana eivät saa olla tyhjiä")
        return redirect("/login")

    user = users.login_user(username, password)

    if user:
        session["user_id"] = user["id"]
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")

    flash("VIRHE: Väärä tunnus tai salasana")
    return redirect("/login")

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
