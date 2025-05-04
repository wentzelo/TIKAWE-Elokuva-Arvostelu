import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM comments")
db.execute("DELETE FROM post_genres")
db.execute("DELETE FROM posts")
db.execute("DELETE FROM genres")
db.execute("DELETE FROM users")

user_count = 10000
post_count = 100000
genre_list = [
    "Toiminta", "Draama", "Komedia", "Sci-fi", "Kauhu", "Romantiikka",
    "Dokumentti", "Seikkailu", "Fantasia", "Animaatio"
]

genre_ids = {}
for name in genre_list:
    db.execute("INSERT INTO genres (name) VALUES (?)", [name])
    genre_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    genre_ids[name] = genre_id

for i in range(1, user_count + 1):
    username = f"user{i}"
    password_hash = "testhash"
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", [username, password_hash])

for i in range(1, post_count + 1):
    title = f"Elokuva {i}"
    rating = random.randint(1, 5)
    review_text = f"Arvostelu {i} sisältöä."
    watch_date = "2024-01-01"
    user_id = random.randint(1, user_count)
    db.execute("""INSERT INTO posts (title, rating, review_text, watch_date, user_id)
                  VALUES (?, ?, ?, ?, ?)""", [title, rating, review_text, watch_date, user_id])
    post_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    selected_genres = random.sample(list(genre_ids.values()), random.randint(1, 3))
    for genre_id in selected_genres:
        db.execute("INSERT INTO post_genres (post_id, genre_id) VALUES (?, ?)", [post_id, genre_id])

    for _ in range(random.randint(0, 5)):
        is_positive = random.randint(0, 1)
        comment = f"Kommentti arvosteluun {i}"
        db.execute("""INSERT INTO comments (post_id, is_positive, comment)
                      VALUES (?, ?, ?)""", [post_id, is_positive, comment])

db.commit()
db.close()
