CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    review_text TEXT,
    rating INTEGER,
    watch_date TEXT,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE genres (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE post_genres (
    post_id INTEGER REFERENCES posts(id),
    genre_id INTEGER REFERENCES genres(id),
    PRIMARY KEY (post_id, genre_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    is_positive INTEGER,
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_id ON posts(id DESC);
CREATE INDEX idx_posts_user_id ON posts(user_id);