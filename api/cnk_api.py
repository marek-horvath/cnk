#!/usr/bin/env python3
import json
import os
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
from datetime import datetime, timezone

APP_DIR = Path(__file__).resolve().parent
SEED_FILE = APP_DIR / "seed_content.json"
DATA_DIR = Path(os.environ.get("CNK_DATA_DIR", "/var/lib/cnk-api"))
DB_PATH = Path(os.environ.get("CNK_DB_PATH", DATA_DIR / "cnk.sqlite3"))
HOST = os.environ.get("CNK_HOST", "127.0.0.1")
PORT = int(os.environ.get("CNK_PORT", "3001"))
ADMIN_PASSWORD = os.environ.get("CNK_ADMIN_PASSWORD", "change-me")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_seed():
    with SEED_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def migrate():
    seed = load_seed()
    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
              id TEXT PRIMARY KEY,
              payload TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
              id TEXT PRIMARY KEY,
              payload TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS subscribers (
              email TEXT PRIMARY KEY,
              source TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )

        version = db.execute("SELECT value FROM meta WHERE key = 'seed_version'").fetchone()
        if not version or version["value"] != "2026-07-06-5":
            db.execute("DELETE FROM settings")
            db.execute("DELETE FROM events")
            db.execute(
                "INSERT INTO settings (id, payload, updated_at) VALUES (?, ?, ?)",
                ("site", json.dumps(seed["settings"]), utc_now()),
            )
            for event in seed["events"]:
                db.execute(
                    "INSERT INTO events (id, payload, updated_at) VALUES (?, ?, ?)",
                    (event["id"], json.dumps(event), utc_now()),
                )
            db.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES ('seed_version', '2026-07-06-5')"
            )


def sorted_events(events):
    return sorted(
        events,
        key=lambda event: f"{event.get('date') or '0000-00-00'}T{event.get('time') or '00:00'}",
        reverse=True,
    )


def get_content():
    with connect() as db:
        settings_row = db.execute("SELECT payload FROM settings WHERE id = 'site'").fetchone()
        event_rows = db.execute("SELECT payload FROM events").fetchall()
    return {
        "settings": json.loads(settings_row["payload"]) if settings_row else load_seed()["settings"],
        "events": sorted_events([json.loads(row["payload"]) for row in event_rows]),
    }


def save_content(payload):
    settings = payload.get("settings")
    events = payload.get("events")
    if not isinstance(settings, dict) or not isinstance(events, list):
        raise ValueError("Invalid content payload")

    with connect() as db:
        db.execute("DELETE FROM settings")
        db.execute("DELETE FROM events")
        db.execute(
            "INSERT INTO settings (id, payload, updated_at) VALUES (?, ?, ?)",
            ("site", json.dumps({**settings, "id": "site"}), utc_now()),
        )
        for event in events:
            if not event.get("id"):
                raise ValueError("Event is missing id")
            db.execute(
                "INSERT INTO events (id, payload, updated_at) VALUES (?, ?, ?)",
                (event["id"], json.dumps(event), utc_now()),
            )


def reset_content():
    seed = load_seed()
    save_content(seed)


def list_subscribers():
    with connect() as db:
        rows = db.execute(
            "SELECT email, source, created_at FROM subscribers ORDER BY created_at DESC"
        ).fetchall()
    return [
        {"email": row["email"], "source": row["source"], "createdAt": row["created_at"]}
        for row in rows
    ]


def save_subscriber(email):
    normalized = email.strip().lower()
    if not EMAIL_RE.match(normalized):
        raise ValueError("Invalid email")
    with connect() as db:
        db.execute(
            """
            INSERT INTO subscribers (email, source, created_at)
            VALUES (?, 'homepage', ?)
            ON CONFLICT(email) DO UPDATE SET source = excluded.source
            """,
            (normalized, utc_now()),
        )
    return normalized


def delete_subscriber(email):
    with connect() as db:
        db.execute("DELETE FROM subscribers WHERE email = ?", (email.strip().lower(),))


class Handler(BaseHTTPRequestHandler):
    server_version = "cnk-api/1.0"

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Password")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def do_PUT(self):
        self.route("PUT")

    def do_DELETE(self):
        self.route("DELETE")

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def write_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def require_admin(self):
        if self.headers.get("X-Admin-Password") != ADMIN_PASSWORD:
            self.write_json(401, {"error": "Unauthorized"})
            return False
        return True

    def route(self, method):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        try:
            if method == "GET" and path == "/api/health":
                self.write_json(200, {"ok": True})
                return

            if method == "GET" and path == "/api/content":
                self.write_json(200, get_content())
                return

            if method == "PUT" and path == "/api/content":
                if not self.require_admin():
                    return
                save_content(self.read_json())
                self.write_json(200, {"ok": True})
                return

            if method == "POST" and path == "/api/reset":
                if not self.require_admin():
                    return
                reset_content()
                self.write_json(200, {"ok": True})
                return

            if method == "GET" and path == "/api/subscribers":
                if not self.require_admin():
                    return
                self.write_json(200, list_subscribers())
                return

            if method == "POST" and path == "/api/subscribers":
                email = save_subscriber(self.read_json().get("email", ""))
                self.write_json(201, {"email": email})
                return

            if method == "DELETE" and path.startswith("/api/subscribers/"):
                if not self.require_admin():
                    return
                email = unquote(path.split("/api/subscribers/", 1)[1])
                delete_subscriber(email)
                self.write_json(200, {"ok": True})
                return

            self.write_json(404, {"error": "Not found"})
        except ValueError as error:
            self.write_json(400, {"error": str(error)})
        except Exception as error:
            self.write_json(500, {"error": str(error)})

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


if __name__ == "__main__":
    migrate()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"CNK API listening on http://{HOST}:{PORT}")
    server.serve_forever()
