import db

def add_post(title, rating, review_text, watch_date, user_id):
    sql = """
        INSERT INTO posts (title, rating, review_text, watch_date, user_id)
        VALUES (?, ?, ?, ?, ?)
    """
    db.execute(sql, [title, rating, review_text, watch_date, user_id])
    return db.last_insert_id()

def get_post_count():
    sql = "SELECT COUNT(*) FROM posts"
    return db.query(sql)[0][0]

def get_posts(page, page_size):
    limit = page_size
    offset = page_size * (page - 1)
    sql = """
        SELECT posts.id, posts.title, posts.user_id, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.id DESC
        LIMIT ? OFFSET ?
    """
    return db.query(sql, [limit, offset])

def get_post(post_id):
    sql = """
        SELECT posts.id, posts.title, posts.rating, posts.review_text, posts.watch_date,
        users.id AS user_id, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.id = ?
    """
    result = db.query(sql, [post_id])
    if not result:
        return None
    return dict(result[0])

def get_post_genres(post_id):
    sql = """
    SELECT genres.name
    FROM genres
    JOIN post_genres ON genres.id = post_genres.genre_id
    WHERE post_genres.post_id = ?
    """
    return db.query(sql, [post_id])

def update_post(post_id, title, rating, review_text, watch_date):
    sql = """
        UPDATE posts
        SET title = ?, rating = ?, review_text = ?, watch_date = ?
        WHERE id = ?
    """
    db.execute(sql, [title, rating, review_text, watch_date, post_id])

def delete_post(post_id):

    db.execute("DELETE FROM comments WHERE post_id = ?", [post_id])

    db.execute("DELETE FROM post_genres WHERE post_id = ?", [post_id])

    db.execute("DELETE FROM posts WHERE id = ?", [post_id])

def find_posts(query):
    sql = """
    SELECT id, title 
    FROM posts 
    WHERE review_text LIKE ? OR title LIKE ? 
    ORDER BY id DESC
    """
    return db.query(sql, ["%" + query + "%", "%" + query + "%"])

#Genre code

def get_or_create_genre(name):
    sql = "SELECT id FROM genres WHERE name = ?"
    result = db.query(sql, [name])
    if result:
        return result[0]["id"]

    sql = "INSERT INTO genres (name) VALUES (?)"
    db.execute(sql, [name])
    return db.last_insert_id()

def add_post_genre(post_id, genre_id):
    sql = "INSERT INTO post_genres (post_id, genre_id) VALUES (?, ?)"
    db.execute(sql, [post_id, genre_id])

def update_post_genres(post_id, selected_genres, custom_genre=None):

    db.execute("DELETE FROM post_genres WHERE post_id = ?", [post_id])

    genre_set = set(selected_genres)

    if custom_genre:
        for genre in custom_genre.split(","):
            genre = genre.strip()
            if genre:
                genre_set.add(genre)

    for genre in genre_set:
        genre_id = get_or_create_genre(genre)
        add_post_genre(post_id, genre_id)

#Comment code

def add_comment(post_id, is_positive, comment):
    sql = "INSERT INTO comments (post_id, is_positive, comment) VALUES (?, ?, ?)"
    db.execute(sql, [post_id, is_positive, comment])

def get_comments(post_id):
    sql = """
    SELECT is_positive, comment, created_at
    FROM comments
    WHERE post_id = ?
    ORDER BY created_at DESC
    """
    return db.query(sql, [post_id])
