import sqlite3
from datetime import datetime

DB_NAME = "sentinel.db"

def get_connection():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn=get_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        checked_at TEXT NOT NULL,
        status_code INTEGER,
        response_ms INTEGER,
        result TEXT NOT NULL,
        error TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_check(r):
    conn=get_connection()
    conn.execute(
        """INSERT INTO checks
            (url, checked_at, status_code, response_ms, result, error)
            VALUES (?, ?, ?, ?, ?, ?)""",
        (
            r["url"],
            datetime.now().isoformat(timespec="seconds"),
            r["status_code"],
            r["response_ms"],
            r["result"],
            r["error"],
        ),
    )
    conn.commit()
    conn.close()

def get_checks(limit=20):
    conn=get_connection()
    rows=conn.execute(
        "SELECT * FROM checks ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__=="__main__":
    from checker import check_url

    init_db()
    save_check(check_url("https://httpbin.org/status/200"))
    save_check(check_url("https://httpbin.org/status/500"))
    for row in get_checks():
        print(row)
