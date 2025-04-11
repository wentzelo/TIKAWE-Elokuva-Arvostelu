"""Handles user-related database operations: registration, login, and profile data."""

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import db

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    try:
        db.execute(sql, [username, password_hash])
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user = result[0]
    return user if check_password_hash(user["password_hash"], password) else None


def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_user_posts(user_id):
    sql = """
    SELECT id, title
    FROM posts 
    WHERE user_id = ?
    ORDER BY id DESC
    """
    return db.query(sql, [user_id])
