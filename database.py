"""
AIRA MVP Database
------------------
Simple SQLite storage for users and chat messages.
Good enough for launch + friends/family testing.
(Can upgrade to PostgreSQL later without changing cloud_main.py's function calls.)
"""

import sqlite3
from datetime import datetime, timezone

DB_PATH = "aira.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT,
            name TEXT,
            created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def get_or_create_user(user_id: str, email: str, name: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (user_id, email, name, created_at) VALUES (?, ?, ?, ?)",
            (user_id, email, name, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    conn.close()


def save_message(user_id: str, role: str, content: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (user_id, role, content, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(user_id: str, limit: int = 200):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT role, content, created_at FROM messages "
        "WHERE user_id = ? ORDER BY id ASC LIMIT ?",
        (user_id, limit),
    )
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]