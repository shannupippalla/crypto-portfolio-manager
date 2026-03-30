"""
database_manager.py — SQLite persistence for CryptoPortfolio Manager.

The API key column has been removed from the settings table.
The API key is now managed exclusively via the .env file (see api_key() in app.py).
"""

import sqlite3
import os
import hashlib

# SQLite database lives in a data/ folder alongside this file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "crypto.db")


def _conn() -> sqlite3.Connection:
    """Open a connection to the SQLite database, creating the directory if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    return conn


def init_db() -> None:
    """Create all tables if they don't already exist."""
    conn = _conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            email    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS holdings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            coin_id        TEXT NOT NULL,
            coin_name      TEXT NOT NULL,
            quantity       REAL NOT NULL,
            purchase_price REAL NOT NULL,
            added_at       TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS price_history (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id  TEXT NOT NULL,
            price    REAL NOT NULL,
            recorded TEXT DEFAULT (datetime('now'))
        );

        -- Note: API key column removed — key now lives in .env only
        CREATE TABLE IF NOT EXISTS settings (
            user_id        INTEGER PRIMARY KEY,
            risk_threshold REAL DEFAULT 10.0,
            alert_email    TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _hash(password: str) -> str:
    """Return a SHA-256 hash of a password string."""
    return hashlib.sha256(password.encode()).hexdigest()


# ── Users ──────────────────────────────────────────────────────────────────────

def register_user(email: str, password: str) -> tuple:
    """
    Insert a new user. Returns (True, success_message) or (False, error_message).
    Email is stored in lower-case to prevent duplicate registrations.
    """
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email.strip().lower(), _hash(password)),
        )
        conn.commit()
        return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()


def login_user(email: str, password: str) -> dict | None:
    """
    Look up a user by email + password hash.
    Returns the user row as a dict, or None if credentials are wrong.
    """
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email.strip().lower(), _hash(password)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Holdings ───────────────────────────────────────────────────────────────────

def add_holding(user_id: int, coin_id: str, coin_name: str,
                quantity: float, purchase_price: float) -> None:
    """Insert a new holding record for a user."""
    conn = _conn()
    conn.execute(
        "INSERT INTO holdings (user_id, coin_id, coin_name, quantity, purchase_price) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, coin_id.lower(), coin_name, quantity, purchase_price),
    )
    conn.commit()
    conn.close()


def get_holdings(user_id: int) -> list[dict]:
    """Return all holdings for a user, most recently added first."""
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM holdings WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_holding(holding_id: int) -> None:
    """Remove a single holding by its primary key."""
    conn = _conn()
    conn.execute("DELETE FROM holdings WHERE id = ?", (holding_id,))
    conn.commit()
    conn.close()


# ── Price history ──────────────────────────────────────────────────────────────

def save_price(coin_id: str, price: float) -> None:
    """Append a price snapshot to the history table."""
    conn = _conn()
    conn.execute(
        "INSERT INTO price_history (coin_id, price) VALUES (?, ?)",
        (coin_id, price),
    )
    conn.commit()
    conn.close()


# ── Settings ───────────────────────────────────────────────────────────────────

def get_settings(user_id: int) -> dict:
    """
    Return the settings row for a user.
    Falls back to safe defaults if no row exists yet.
    Note: API key is NOT stored here — it lives in .env.
    """
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM settings WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else {
        "user_id": user_id,
        "risk_threshold": 10.0,
        "alert_email": "",
    }


def save_settings(user_id: int, risk_threshold: float, alert_email: str) -> None:
    """
    Upsert the settings row for a user.
    Only stores risk_threshold and alert_email — no API key.
    """
    conn = _conn()
    conn.execute(
        """
        INSERT INTO settings (user_id, risk_threshold, alert_email)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            risk_threshold = excluded.risk_threshold,
            alert_email    = excluded.alert_email
        """,
        (user_id, risk_threshold, alert_email),
    )
    conn.commit()
    conn.close()