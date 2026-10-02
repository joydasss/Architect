"""Signed webhook delivery with retries and a dead-letter outcome; stdlib only."""

from __future__ import annotations

import hashlib
import hmac
import json
import random
import time
from dataclasses import dataclass
from typing import Callable

SECRET = b"local-demo-secret-change-me"


def signature(secret: bytes, timestamp: int, body: bytes) -> str:
    signed = str(timestamp).encode("ascii") + b"." + body
    digest = hmac.new(secret, signed, hashlib.sha256).hexdigest()
    return f"v1={digest}"


def verify(secret: bytes, timestamp_header: str, signature_header: str, body: bytes,
           *, now: int, tolerance_seconds: int = 300) -> bool:
    try:
        timestamp = int(timestamp_header)
    except ValueError:
        return False
    if abs(now - timestamp) > tolerance_seconds:
        return False
    expected = signature(secret, timestamp, body)
    return hmac.compare_digest(expected, signature_header)


@dataclass
class DeliveryResult:
    event_id: str
    state: str
    attempts: int
    last_status: int | None


def send_with_retry(event: dict[str, object], secret: bytes,
                    receiver: Callable[[dict[str, str], bytes], int], *,
                    max_attempts: int = 4, base_delay: float = 0.05,
                    max_delay: float = 0.5) -> DeliveryResult:
    body = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
    event_id = str(event["eventId"])
    rng = random.Random(event_id)
    last_status: int | None = None
    for attempt in range(1, max_attempts + 1):
        timestamp = int(time.time())
        headers = {
            "X-Event-Id": event_id,
            "X-Webhook-Timestamp": str(timestamp),
            "X-Webhook-Signature": signature(secret, timestamp, body),
        }
        last_status = receiver(headers, body)
        print(f"attempt={attempt} eventId={event_id} status={last_status}")
        if 200 <= last_status < 300:
            return DeliveryResult(event_id, "acknowledged", attempt, last_status)
        if 400 <= last_status < 500 and last_status != 429:
            return DeliveryResult(event_id, "quarantined", attempt, last_status)
        if attempt < max_attempts:
            ceiling = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay = rng.uniform(ceiling * 0.5, ceiling)
            print(f"retrying after {delay:.3f}s (capped exponential backoff with jitter)")
            time.sleep(delay)
    return DeliveryResult(event_id, "dead_letter", max_attempts, last_status)


class DemoReceiver:
    def __init__(self, failures_before_success: int) -> None:
        self.failures_before_success = failures_before_success
        self.calls = 0
        self.received_event_ids: set[str] = set()

    def __call__(self, headers: dict[str, str], body: bytes) -> int:
        self.calls += 1
        if not verify(SECRET, headers["X-Webhook-Timestamp"],
                      headers["X-Webhook-Signature"], body, now=int(time.time())):
            return 401
        event = json.loads(body)
        if headers["X-Event-Id"] != event["eventId"]:
            return 400
        # This set is only a demonstration of stable event identity at the
        # receiver boundary; general deduplication is owned by Part 07 CH19.
        if event["eventId"] in self.received_event_ids:
            return 204
        if self.calls <= self.failures_before_success:
            return 503
        self.received_event_ids.add(event["eventId"])
        print(f"receiver durably accepted {event['eventId']}")
        return 204


def main() -> None:
    event = {
        "eventId": "evt-transfer-42",
        "type": "transfer.settled",
        "schemaVersion": 1,
        "operationId": "op-transfer-42",
        "data": {"transferId": "tr-42", "amountMinor": 12500},
    }
    print("Transient outage, then success:")
    delivered = send_with_retry(event, SECRET, DemoReceiver(failures_before_success=2))
    print(f"result={delivered}\n")

    print("Persistent outage, then dead-letter outcome:")
    stuck = {**event, "eventId": "evt-transfer-43", "operationId": "op-transfer-43"}
    dead_letter = send_with_retry(
        stuck, SECRET, DemoReceiver(failures_before_success=99), max_attempts=3
    )
    print(f"deadLetterRecord={dead_letter}")

    body = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
    tampered = body.replace(b"12500", b"1")
    now = int(time.time())
    print("tamperedBodyAccepted=", verify(
        SECRET, str(now), signature(SECRET, now, body), tampered, now=now
    ))


if __name__ == "__main__":
    main()
