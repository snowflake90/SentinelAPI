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
    conn.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        started_at TEXT NOT NULL,
        resolved_at TEXT,
        reason TEXT
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

FAIL_THRESHOLD = 3

def update_incident(url):
    """Open or close an incident for this url, returns 'opened', 'resolved', or none."""
    conn=get_connection()
    now = datetime.now().isoformat(timespec="seconds")

    recent=conn.execute(
        "SELECT result, error FROM checks WHERE url=? ORDER BY id DESC LIMIT ?", (url, FAIL_THRESHOLD),
    ).fetchall()

    open_incident = conn.execute(
            "SELECT id FROM incidents WHERE url=? AND resolved_at IS NULL", (url,),
        ).fetchone()

    outcome = None
    all_down = len(recent) == FAIL_THRESHOLD and all(r["result"] == "down" for r in recent)
    if all_down and not open_incident:
        reason = f"{FAIL_THRESHOLD} consecutive failures ({recent[0]['error']})"
        conn.execute(
            "INSERT INTO incidents (url, started_at, reason) VALUES (?,?,?)", (url, now, reason),
        )
        outcome = "opened"
    elif recent and recent[0]["result"]!="down" and open_incident:
        conn.execute(
            "UPDATE incidents SET resolved_at =? WHERE id =?", (now, open_incident["id"]),
        )
        outcome = "resolved"

    conn.commit()
    conn.close()
    return outcome

def get_incidents():
    conn=get_connection()
    rows=conn.execute(
        "SELECT * FROM incidents ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__=="__main__":
    from checker import check_url

    init_db()
    fake_url="https://fake.test"

    def fake(result):
        return{
        "url": fake_url,
        "status_code": None, 
        "response_ms": None,
        "result": result,
        "error": "timeout" if result=="down" else None
        }

    for result in ["down", "down", "down", "healthy"]:
        save_check(fake(result))
        print(result, "->", update_incident(fake_url))

    for inc in get_incidents():
        print(inc)
