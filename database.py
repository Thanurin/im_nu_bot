import sqlite3
import os
from datetime import datetime


DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "users.db")


def get_connection():
    os.makedirs(DB_FOLDER, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        user_id INTEGER PRIMARY KEY,

        username TEXT,

        first_name TEXT,

        is_premium INTEGER DEFAULT 0,

        scan_count INTEGER DEFAULT 0,

        joined_at TEXT,

        last_scan TEXT

    )
    """)


    conn.commit()
    conn.close()



def user_exists(user_id):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        "SELECT 1 FROM users WHERE user_id = ?",
        (user_id,)
    )


    result = cursor.fetchone()


    conn.close()


    return result is not None



def add_user(user):

    if user_exists(user.id):
        return


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO users
    (
        user_id,
        username,
        first_name,
        joined_at
    )

    VALUES (?, ?, ?, ?)

    """,

    (
        user.id,
        user.username,
        user.first_name,
        datetime.utcnow().isoformat()
    ))


    conn.commit()
    conn.close()



def increase_scan_count(user_id):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    UPDATE users

    SET

    scan_count = scan_count + 1,

    last_scan = ?

    WHERE user_id = ?

    """,

    (
        datetime.utcnow().isoformat(),
        user_id
    ))


    conn.commit()
    conn.close()



def total_users():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )


    total = cursor.fetchone()[0]


    conn.close()


    return total