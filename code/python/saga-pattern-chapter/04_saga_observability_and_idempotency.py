"""Saga observability (distributed tracing across saga steps) and the
saga-idempotency interplay (recap; full idempotency-key mechanics owned by
the sibling Idempotency chapter, this same batch).

Accompanies CH13_Saga_Pattern.md Sections 4.4 and 4.5.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class Span:
    trace_id: str
    span_name: str
    start_time: float
    end_time: float | None = None
    status: str = "OK"

    def duration_ms(self) -> float:
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000


class SagaTracer:
    """A minimal in-process stand-in for a distributed tracer (e.g. an
    OpenTelemetry SDK exporting to Jaeger/Tempo). Every saga step becomes
    one child span under a single trace_id shared across the whole saga."""

    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id
        self.spans: list[Span] = []

    def start_span(self, name: str) -> Span:
        span = Span(trace_id=self.trace_id, span_name=name, start_time=time.perf_counter())
        self.spans.append(span)
        return span

    def end_span(self, span: Span, status: str = "OK") -> None:
        span.end_time = time.perf_counter()
        span.status = status

    def report(self) -> None:
        print(f"Trace {self.trace_id}:")
        for span in self.spans:
            print(f"  span={span.span_name!r} status={span.status} duration_ms={span.duration_ms():.3f}")


class IdempotencyStore:
    """Recap of the Idempotency chapter's core mechanism: an idempotency
    key maps to a previously observed result, so a retried step call
    returns the cached outcome instead of re-executing a side effect."""

    def __init__(self) -> None:
        self._seen: dict[str, str] = {}

    def already_applied(self, idempotency_key: str) -> bool:
        return idempotency_key in self._seen

    def record(self, idempotency_key: str, outcome: str) -> None:
        self._seen[idempotency_key] = outcome

    def result_for(self, idempotency_key: str) -> str:
        return self._seen[idempotency_key]


def charge_payment_step(tracer: SagaTracer, idempotency_store: IdempotencyStore, saga_id: str, attempt: int) -> None:
    span = tracer.start_span("charge_payment")
    # The idempotency key is derived from the saga instance and step name,
    # not from the attempt number -- every retry of this same logical step
    # must reuse the same key so the payment provider only charges once.
    idempotency_key = f"{saga_id}:charge_payment"

    if idempotency_store.already_applied(idempotency_key):
        outcome = idempotency_store.result_for(idempotency_key)
        print(f"  attempt {attempt}: idempotency key already seen, "
              f"returning cached outcome '{outcome}' without re-charging")
        tracer.end_span(span, status="OK (deduplicated)")
        return

    outcome = "charged"
    idempotency_store.record(idempotency_key, outcome)
    print(f"  attempt {attempt}: executed charge_payment, recorded outcome '{outcome}'")
    tracer.end_span(span, status="OK")


def main() -> None:
    saga_id = str(uuid.uuid4())
    tracer = SagaTracer(trace_id=saga_id)
    idempotency_store = IdempotencyStore()

    print("=== Simulating a saga step that gets retried after a timeout ===")
    reserve_span = tracer.start_span("reserve_inventory")
    time.sleep(0.001)
    tracer.end_span(reserve_span)

    # The orchestrator times out waiting for a response and retries the
    # same step; without idempotency, this would double-charge the card.
    charge_payment_step(tracer, idempotency_store, saga_id, attempt=1)
    charge_payment_step(tracer, idempotency_store, saga_id, attempt=2)

    ship_span = tracer.start_span("ship_order")
    time.sleep(0.001)
    tracer.end_span(ship_span)

    print()
    tracer.report()


if __name__ == "__main__":
    main()
