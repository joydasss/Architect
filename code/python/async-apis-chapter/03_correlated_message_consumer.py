"""Request/reply correlation and retry identity over an in-memory queue."""

from __future__ import annotations

import queue
import threading
import time
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    message_id: str
    operation_id: str
    correlation_id: str
    causation_id: str | None
    value: int


@dataclass(frozen=True)
class Reply:
    message_id: str
    operation_id: str
    correlation_id: str
    causation_id: str
    state: str
    result: int


class Consumer:
    def __init__(self, requests: queue.Queue[Command | None], replies: queue.Queue[Reply]) -> None:
        self.requests = requests
        self.replies = replies
        self.completed: dict[str, Reply] = {}

    def run(self) -> None:
        while True:
            command = self.requests.get()
            if command is None:
                return
            prior = self.completed.get(command.operation_id)
            if prior is not None:
                print(f"reused recorded outcome for operationId={command.operation_id}")
                self.replies.put(prior)
                continue
            time.sleep(0.15)
            result = command.value * 2
            reply = Reply(
                message_id=str(uuid.uuid4()),
                operation_id=command.operation_id,
                correlation_id=command.correlation_id,
                causation_id=command.message_id,
                state="succeeded",
                result=result,
            )
            self.completed[command.operation_id] = reply
            self.replies.put(reply)


def wait_for_reply(replies: queue.Queue[Reply], correlation_id: str,
                   operation_id: str, timeout: float) -> Reply | None:
    deadline = time.monotonic() + timeout
    deferred: list[Reply] = []
    found: Reply | None = None
    while time.monotonic() < deadline:
        try:
            reply = replies.get(timeout=max(0.001, deadline - time.monotonic()))
        except queue.Empty:
            break
        if reply.correlation_id == correlation_id and reply.operation_id == operation_id:
            found = reply
            break
        deferred.append(reply)
    for reply in deferred:
        replies.put(reply)
    return found


def main() -> None:
    requests: queue.Queue[Command | None] = queue.Queue()
    replies: queue.Queue[Reply] = queue.Queue()
    consumer = Consumer(requests, replies)
    worker = threading.Thread(target=consumer.run, daemon=True)
    worker.start()

    operation_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())
    first = Command(str(uuid.uuid4()), operation_id, correlation_id, None, 21)
    print(f"accepted operationId={operation_id} correlationId={correlation_id}")
    requests.put(first)

    # Simulate the caller's reply wait expiring while the work continues.
    reply = wait_for_reply(replies, correlation_id, operation_id, timeout=0.02)
    if reply is None:
        print("reply not observed before timeout; outcome is unknown, not failed")

    # Retry the same logical operation. A real API contract must preserve
    # operation identity; Part 07 CH16 owns the production idempotency design.
    retry = Command(str(uuid.uuid4()), operation_id, correlation_id, first.message_id, 21)
    requests.put(retry)
    while reply is None:
        reply = wait_for_reply(replies, correlation_id, operation_id, timeout=1.0)
    print(
        f"completed operationId={reply.operation_id} result={reply.result} "
        f"correlationId={reply.correlation_id} causationId={reply.causation_id}"
    )

    requests.put(None)
    worker.join(timeout=1)
    print("messageId changes per command attempt; operationId remains stable")


if __name__ == "__main__":
    main()
