import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path("data") / "diplotrack.db"

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        tier TEXT DEFAULT 'free',
        role TEXT DEFAULT 'student',
        usage_this_month INTEGER DEFAULT 0,
        credits INTEGER DEFAULT 0,
        last_active_month TEXT,
        security_question TEXT,
        security_answer TEXT,
        created_at TEXT,
        badges TEXT DEFAULT '[]'
    );

    CREATE TABLE IF NOT EXISTS simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp TEXT
    );

    CREATE TABLE IF NOT EXISTS credit_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        pack_name TEXT,
        credits_added INTEGER,
        timestamp TEXT
    );

    CREATE TABLE IF NOT EXISTS usage_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        action TEXT,
        timestamp TEXT
    );

    CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        data TEXT
    );
    """)
    # Varsayılan senaryo yoksa ekle (örnek)
    cur = conn.execute("SELECT COUNT(*) FROM scenarios")
    if cur.fetchone()[0] == 0:
        sample = [
            ("Ukrayna Krizi 2023", "Rusya-Ukrayna savaşında arabuluculuk", '{"issue":"Güvenlik","countries":["RUS","UKR"],"steps":3}'),
            ("İklim Zirvesi", "Küresel emisyon hedefleri", '{"issue":"İklim","countries":["USA","CHN","DEU"],"steps":3}')
        ]
        conn.executemany("INSERT INTO scenarios (title,description,data) VALUES (?,?,?)", sample)
    conn.commit()
    conn.close()

def load_users():
    # Kullanıcı sözlüğü döndür (username: {..})
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return {row["username"]: dict(row) for row in rows}

def save_user(username, data):
    conn = get_conn()
    # data dict olarak gelir, INSERT OR REPLACE
    keys = list(data.keys())
    vals = [data[k] for k in keys]
    placeholders = ",".join(["?" for _ in keys])
    cols = ",".join(keys)
    conn.execute(f"INSERT OR REPLACE INTO users ({cols}) VALUES ({placeholders})", vals)
    conn.commit()
    conn.close()

def update_user(username, updates):
    conn = get_conn()
    sets = [f"{k}=?" for k in updates]
    vals = list(updates.values()) + [username]
    conn.execute(f"UPDATE users SET {','.join(sets)} WHERE username=?", vals)
    conn.commit()
    conn.close()

def get_user(username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_simulation(username, data_json_str, timestamp):
    conn = get_conn()
    conn.execute("INSERT INTO simulations (username,data,timestamp) VALUES (?,?,?)", (username, data_json_str, timestamp))
    conn.commit()
    conn.close()

def get_simulations(username):
    conn = get_conn()
    rows = conn.execute("SELECT data, timestamp FROM simulations WHERE username=? ORDER BY timestamp DESC", (username,)).fetchall()
    conn.close()
    return [{"data": row["data"], "timestamp": row["timestamp"]} for row in rows]

def get_all_simulations():
    conn = get_conn()
    rows = conn.execute("SELECT username, data, timestamp FROM simulations ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [{"username": row["username"], "data": row["data"], "timestamp": row["timestamp"]} for row in rows]

def add_credit_purchase(username, pack, credits_added):
    conn = get_conn()
    conn.execute("INSERT INTO credit_purchases (username,pack_name,credits_added,timestamp) VALUES (?,?,?,?)",
                 (username, pack, credits_added, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def log_action(username, action):
    conn = get_conn()
    conn.execute("INSERT INTO usage_log (username,action,timestamp) VALUES (?,?,?)",
                 (username, action, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_usage_stats(username):
    conn = get_conn()
    rows = conn.execute("SELECT action, COUNT(*) as cnt FROM usage_log WHERE username=? GROUP BY action", (username,)).fetchall()
    conn.close()
    return {row["action"]: row["cnt"] for row in rows}

def get_students(teacher_username):
    # Basitlik: öğretmen tüm student'ları görsün (gerçekte sınıf ilişkisi kurulabilir)
    conn = get_conn()
    rows = conn.execute("SELECT username FROM users WHERE role='student'").fetchall()
    conn.close()
    return [row["username"] for row in rows]

# Veritabanını başlat
init_db()
