CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);


CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    review TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    user_id INTEGER REFERENCES user
);
