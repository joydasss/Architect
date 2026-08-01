"""Demonstrates content negotiation (Accept/Accept-Language/Accept-Encoding
with quality values) and transparent decompression of a negotiated response.

Referenced from 05_Networking_and_OS/CH01_HTTP.md (Section 10).
"""
import gzip
import http.client
import json


def get_negotiated_resource(host: str, path: str) -> dict:
    """Ask the server for the best available representation.

    Quality values (q=) rank preference: q=1.0 (default, omitted) is the
    most preferred; lower values are acceptable fallbacks. A q-factor of 0
    means "never send this, even if nothing else matches."
    """
    conn = http.client.HTTPSConnection(host, timeout=5)
    try:
        conn.request(
            "GET",
            path,
            headers={
                # Prefer JSON, tolerate HTML as a fallback, never plain text.
                "Accept": "application/json;q=1.0, text/html;q=0.5, text/plain;q=0",
                "Accept-Language": "en-GB, en;q=0.9, fr;q=0.3",
                "Accept-Encoding": "br, gzip;q=0.8, identity;q=0.1",
            },
        )
        response = conn.getresponse()
        raw_body = response.read()

        # The server picks one representation and must echo how it encoded
        # the body so the client knows whether/how to decompress it.
        content_encoding = response.getheader("Content-Encoding", "identity")
        if content_encoding == "gzip":
            raw_body = gzip.decompress(raw_body)
        elif content_encoding not in ("identity", ""):
            # br/deflate decoding omitted for brevity; a real client would
            # use brotli.decompress()/zlib.decompress() here.
            raise NotImplementedError(f"Unhandled Content-Encoding: {content_encoding}")

        content_type = response.getheader("Content-Type", "")
        if "application/json" not in content_type:
            raise ValueError(f"Server did not honor negotiation, got {content_type!r}")

        return json.loads(raw_body)
    finally:
        conn.close()


if __name__ == "__main__":
    print(get_negotiated_resource("api.example.com", "/articles/7"))
