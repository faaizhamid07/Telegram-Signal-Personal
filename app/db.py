import sqlite3
from contextlib import contextmanager
from app.config import DATABASE_PATH

@contextmanager
def connect():
    db = sqlite3.connect(DATABASE_PATH, timeout=20)
    db.row_factory = sqlite3.Row
    try:
        db.execute("PRAGMA journal_mode=WAL")
        yield db
        db.commit()
    finally:
        db.close()

def init_db():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS groups (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          peer TEXT NOT NULL UNIQUE,
          title TEXT NOT NULL,
          enabled INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS keywords (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          term TEXT NOT NULL UNIQUE,
          enabled INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS matches (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          chat_id INTEGER NOT NULL,
          group_title TEXT NOT NULL,
          message_id INTEGER NOT NULL,
          text TEXT NOT NULL,
          matched_terms TEXT NOT NULL,
          link TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(chat_id, message_id)
        );
        ''')
        db.commit()

def all_rows(sql, params=()):
    with connect() as db:
        return [dict(row) for row in db.execute(sql, params).fetchall()]

def run(sql, params=()):
    with connect() as db:
        cur = db.execute(sql, params)
        return cur.lastrowid
