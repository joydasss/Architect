"""Self-contained BFF fan-out demo; Python 3.10+, standard library only."""

from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads
from threading import Thread
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen


def json_response(handler: BaseHTTPRequestHandler, status: int, body: dict) -> None:
    payload = dumps(body).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


class OrdersHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        json_response(self, 200, {"orders": [{"id": "ord-42", "status": "shipped"}]})

    def log_message(self, format: str, *args: object) -> None:
        return


class ProfileHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if "fail=1" in urlsplit(self.path).query:
            json_response(self, 503, {"error": "profile service unavailable"})
            return
        json_response(self, 200, {"name": "Avery", "locale": "en-US"})

    def log_message(self, format: str, *args: object) -> None:
        return


def fetch_json(url: str, timeout: float = 0.7) -> dict:
    try:
        with urlopen(url, timeout=timeout) as response:
            return loads(response.read())
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        return {"_error": type(error).__name__}


class BffHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if urlsplit(self.path).path != "/mobile/home":
            json_response(self, 404, {"error": "not found"})
            return

        fail_profile = parse_qs(urlsplit(self.path).query).get("fail") == ["profile"]
        profile_url = "http://127.0.0.1:8002/profile"
        if fail_profile:
            profile_url += "?fail=1"

        with ThreadPoolExecutor(max_workers=2) as pool:
            orders_future = pool.submit(fetch_json, "http://127.0.0.1:8001/orders")
            profile_future = pool.submit(fetch_json, profile_url)
            orders = orders_future.result()
            profile = profile_future.result()

        body = {
            "orders": orders.get("orders", []),
            "profile": profile if "_error" not in profile else None,
            "degraded": "_error" in profile,
        }
        json_response(self, 200, body)

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(server: ThreadingHTTPServer) -> None:
    Thread(target=server.serve_forever, daemon=True).start()


def main() -> None:
    servers = [
        ThreadingHTTPServer(("127.0.0.1", 8001), OrdersHandler),
        ThreadingHTTPServer(("127.0.0.1", 8002), ProfileHandler),
        ThreadingHTTPServer(("127.0.0.1", 8080), BffHandler),
    ]
    for server in servers:
        serve(server)
    print("BFF listening at http://127.0.0.1:8080/mobile/home (Ctrl+C to stop)")
    try:
        servers[0].serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()