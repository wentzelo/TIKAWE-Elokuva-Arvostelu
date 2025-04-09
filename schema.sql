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
    user_id INTEGER REFERENCES users
);
