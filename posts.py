import db

def add_post(title, rating, review_text, user_id):
    sql = """INSERT INTO posts (title, rating, review_text, user_id) VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, rating, review_text, user_id])

def get_posts():
    sql = """SELECT id, title FROM posts ORDER BY id"""
    
    return db.query(sql)

def get_post(post_id):
    sql = """SELECT posts.id, posts.title, posts.rating, posts.review_text, users.id user_id, users.username FROM posts, users WHERE posts.user_id = users.id AND posts.id = ?
    """
    return db.query(sql, [post_id])[0]

def update_post(post_id, title, rating, review_text):
    sql = """
        UPDATE posts
        SET title = ?, rating = ?, review_text = ?
        WHERE id = ?
    """
    db.execute(sql, [title, rating, review_text, post_id])
