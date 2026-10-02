"""Demonstrate bounded keyset pagination with a tamper-evident cursor."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass


SECRET = b"example-secret-change-before-production"


@dataclass(frozen=True)
class Order:
    created_at: str
    order_id: int


def encode_cursor(order: Order) -> str:
    payload = json.dumps(
        {"created_at": order.created_at, "order_id": order.order_id},
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    signature = hmac.new(SECRET, payload, hashlib.sha256).digest()
    token = payload + b"." + base64.urlsafe_b64encode(signature)
    return base64.urlsafe_b64encode(token).decode().rstrip("=")


def decode_cursor(cursor: str) -> Order:
    padded = cursor + "=" * (-len(cursor) % 4)
    token = base64.urlsafe_b64decode(padded.encode())
    payload, signature_token = token.rsplit(b".", 1)
    signature_token += b"=" * (-len(signature_token) % 4)
    signature = base64.urlsafe_b64decode(signature_token)
    expected = hmac.new(SECRET, payload, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("invalid cursor signature")
    decoded = json.loads(payload)
    return Order(decoded["created_at"], int(decoded["order_id"]))


def page_orders(orders: list[Order], limit: int, cursor: str | None = None) -> tuple[list[Order], str | None]:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    ordered = sorted(orders, key=lambda order: (order.created_at, order.order_id))
    if cursor is not None:
        after = decode_cursor(cursor)
        ordered = [
            order
            for order in ordered
            if (order.created_at, order.order_id) > (after.created_at, after.order_id)
        ]

    selected = ordered[:limit]
    next_cursor = encode_cursor(selected[-1]) if len(ordered) > limit else None
    return selected, next_cursor


def main() -> None:
    orders = [
        Order("2026-10-01T10:00:00Z", 4),
        Order("2026-10-01T10:00:00Z", 7),
        Order("2026-10-01T10:01:00Z", 8),
        Order("2026-10-01T10:02:00Z", 9),
    ]

    first_page, cursor = page_orders(orders, limit=2)
    second_page, next_cursor = page_orders(orders, limit=2, cursor=cursor)
    print("page 1:", [(o.created_at, o.order_id) for o in first_page])
    print("page 2:", [(o.created_at, o.order_id) for o in second_page])
    print("has next page:", next_cursor is not None)

    assert [o.order_id for o in first_page + second_page] == [4, 7, 8, 9]
    assert next_cursor is None

    tampered = cursor[:-1] + ("A" if cursor[-1] != "A" else "B")
    try:
        decode_cursor(tampered)
    except ValueError:
        print("tampered cursor rejected")
    else:
        raise AssertionError("tampered cursor must be rejected")


if __name__ == "__main__":
    main()