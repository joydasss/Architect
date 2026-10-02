"""Minimal SQLite-backed operation-resource API; Python 3.10+, stdlib only."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

DB_PATH = Path(os.environ.get("ASYNC_API_DB", Path(__file__).with_name("operations.sqlite3")))
MAX_BODY_BYTES = 16_384
WAKE_WORKER = threading.Event()


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            """CREATE TABLE IF NOT EXISTS operations (
                operation_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                result_json TEXT,
                error_code TEXT,
                progress INTEGER NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )"""
        )
        # This demo's work is a repeatable transformation; real effects need
        # an explicit recovery and idempotency boundary.
        connection.execute(
            "UPDATE operations SET status='queued', updated_at=? WHERE status='running'",
            (time.time(),),
        )


def worker() -> None:
    while True:
        with connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT operation_id, payload_json FROM operations "
                "WHERE status='queued' ORDER BY created_at LIMIT 1"
            ).fetchone()
            if row is not None:
                connection.execute(
                    "UPDATE operations SET status='running', progress=10, updated_at=? "
                    "WHERE operation_id=? AND status='queued'",
                    (time.time(), row["operation_id"]),
                )
            connection.commit()

        if row is None:
            WAKE_WORKER.wait(timeout=1)
            WAKE_WORKER.clear()
            continue

        operation_id = row["operation_id"]
        payload = json.loads(row["payload_json"])
        time.sleep(min(float(payload.get("durationSeconds", 0.2)), 2.0))
        result = {"document": payload["document"], "summary": payload["document"].upper()}
        with connect() as connection:
            connection.execute(
                "UPDATE operations SET status='succeeded', progress=100, result_json=?, updated_at=? "
                "WHERE operation_id=? AND status='running'",
                (json.dumps(result), time.time(), operation_id),
            )


class Handler(BaseHTTPRequestHandler):
    server_version = "AsyncOperationDemo/1.0"

    def send_json(self, status: int, body: dict[str, object]) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/operations":
            self.send_json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_BODY_BYTES:
                self.send_json(413, {"error": "invalid_or_oversized_body"})
                return
            payload = json.loads(self.rfile.read(length))
            document = payload.get("document")
            duration = payload.get("durationSeconds", 0.2)
            if not isinstance(document, str) or not document.strip():
                self.send_json(400, {"error": "document_required"})
                return
            if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 0 <= duration <= 2:
                self.send_json(400, {"error": "durationSeconds_must_be_between_0_and_2"})
                return
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"error": "invalid_json"})
            return

        operation_id = str(uuid.uuid4())
        now = time.time()
        with connect() as connection:
            connection.execute(
                "INSERT INTO operations VALUES (?, 'queued', ?, NULL, NULL, 0, ?, ?)",
                (operation_id, json.dumps({"document": document, "durationSeconds": duration}), now, now),
            )
        WAKE_WORKER.set()
        status_url = f"http://{self.headers.get('Host', '127.0.0.1:8080')}/operations/{operation_id}"
        self.send_response(202)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Location", status_url)
        self.send_header("Retry-After", "1")
        body = json.dumps({"operationId": operation_id, "statusUrl": status_url, "status": "queued"}).encode()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        prefix = "/operations/"
        if not path.startswith(prefix) or "/" in path[len(prefix):]:
            self.send_json(404, {"error": "not_found"})
            return
        operation_id = path[len(prefix):]
        with connect() as connection:
            row = connection.execute(
                "SELECT operation_id, status, progress, result_json, error_code, created_at, updated_at "
                "FROM operations WHERE operation_id=?",
                (operation_id,),
            ).fetchone()
        if row is None:
            self.send_json(404, {"error": "operation_not_found"})
            return
        body: dict[str, object] = {
            "operationId": row["operation_id"],
            "status": row["status"],
            "progress": row["progress"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }
        if row["result_json"]:
            body["result"] = json.loads(row["result_json"])
        if row["error_code"]:
            body["errorCode"] = row["error_code"]
        self.send_json(200, body)

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"{self.log_date_time_string()} {self.address_string()} {format_string % args}")


def main() -> None:
    initialize()
    threading.Thread(target=worker, daemon=True, name="operation-worker").start()
    server = ThreadingHTTPServer(("127.0.0.1", 8080), Handler)
    print(f"Listening on http://127.0.0.1:8080; SQLite database: {DB_PATH}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
