"""Minimal REST orders API demonstrating status codes, Location header, and ETag concurrency.

Referenced from 08_API_Architecture/CH01_REST.md (Section 10).
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re

orders = {42: {"id": 42, "status": "pending", "version": 1}}


class OrdersHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        match = re.match(r"^/orders/(\d+)$", self.path)
        if not match:
            return self._send(404, {"error": "not found"})
        order_id = int(match.group(1))
        order = orders.get(order_id)
        if not order:
            return self._send(404, {"error": "not found"})

        etag = f'"{order_id}-v{order["version"]}"'
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304)
            self.end_headers()
            return
        self._send(200, order, extra_headers={"ETag": etag})

    def do_POST(self):
        if self.path != "/orders":
            return self._send(404, {"error": "not found"})
        new_id = max(orders.keys(), default=0) + 1
        orders[new_id] = {"id": new_id, "status": "pending", "version": 1}
        self._send(201, orders[new_id], extra_headers={"Location": f"/orders/{new_id}"})

    def do_PUT(self):
        match = re.match(r"^/orders/(\d+)$", self.path)
        if not match:
            return self._send(404, {"error": "not found"})
        order_id = int(match.group(1))
        order = orders.get(order_id)
        if not order:
            return self._send(404, {"error": "not found"})

        expected_etag = f'"{order_id}-v{order["version"]}"'
        if self.headers.get("If-Match") != expected_etag:
            # Optimistic concurrency: reject stale writes instead of overwriting.
            return self._send(409, {"error": "version conflict"})

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        order["status"] = body["status"]
        order["version"] += 1
        self._send(200, order)

    def _send(self, status, payload, extra_headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())


if __name__ == "__main__":
    HTTPServer(("localhost", 8081), OrdersHandler).serve_forever()
