"""Minimal HTTP client demonstrating method, headers, and status-code handling.

Referenced from 05_Networking_and_OS/CH01_HTTP.md (Section 10).
"""
import http.client
import json


def get_product(host: str, path: str) -> dict:
    conn = http.client.HTTPSConnection(host, timeout=5)
    try:
        conn.request("GET", path, headers={"Accept": "application/json"})
        response = conn.getresponse()
        body = response.read()

        if response.status == 200:
            return json.loads(body)
        if response.status == 304:
            # Caller already has a fresh copy — nothing to update.
            return {}
        if 400 <= response.status < 500:
            raise ValueError(f"Client error {response.status}: {body!r}")
        if response.status >= 500:
            raise RuntimeError(f"Server error {response.status}: {body!r}")
        raise RuntimeError(f"Unexpected status {response.status}")
    finally:
        conn.close()


def put_product(host: str, path: str, payload: dict) -> int:
    """PUT is idempotent: safe to retry this call with the same payload."""
    conn = http.client.HTTPSConnection(host, timeout=5)
    try:
        body = json.dumps(payload)
        conn.request(
            "PUT",
            path,
            body=body,
            headers={"Content-Type": "application/json"},
        )
        return conn.getresponse().status
    finally:
        conn.close()


if __name__ == "__main__":
    print(get_product("example.com", "/product/42"))
