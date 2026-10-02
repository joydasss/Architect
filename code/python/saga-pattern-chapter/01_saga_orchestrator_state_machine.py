"""Production-grade Saga orchestrator: explicit state machine, durable
state store, timeout handling, and exponential-backoff retry policy.

Accompanies CH13_Saga_Pattern.md Section 4.1 (production orchestrator
design). Demonstrates: (1) a happy-path saga, (2) a saga that fails and
compensates in reverse order, and (3) crash-recovery by reloading the saga's
state from the durable store and resuming instead of restarting from step 0.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class SagaState(str, Enum):
    RUNNING = "RUNNING"
    COMPENSATING = "COMPENSATING"
    COMPLETED = "COMPLETED"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"


class StepStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.01
    max_delay_seconds: float = 0.2

    def delay_for_attempt(self, attempt: int) -> float:
        return min(self.max_delay_seconds, self.base_delay_seconds * (2 ** (attempt - 1)))


@dataclass
class SagaStep:
    name: str
    action: Callable[[dict], None]
    compensation: Optional[Callable[[dict], None]] = None
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_seconds: float = 1.0
    # A pivot step is the point of no return: once it commits, the saga
    # must retry forward instead of compensating backward (Section 4.3).
    is_pivot: bool = False


@dataclass
class SagaRecord:
    saga_id: str
    state: SagaState
    current_step_index: int
    step_status: dict


class SagaStateStore:
    """Simulates a durable state store (a database row per saga instance)."""

    def __init__(self) -> None:
        self._records: dict[str, SagaRecord] = {}

    def save(self, record: SagaRecord) -> None:
        self._records[record.saga_id] = record

    def load(self, saga_id: str) -> Optional[SagaRecord]:
        return self._records.get(saga_id)


class SagaOrchestrator:
    def __init__(self, saga_id: str, steps: list[SagaStep], store: SagaStateStore) -> None:
        self.saga_id = saga_id
        self.steps = steps
        self.store = store

    def _record(self) -> SagaRecord:
        record = self.store.load(self.saga_id)
        if record is None:
            record = SagaRecord(
                saga_id=self.saga_id,
                state=SagaState.RUNNING,
                current_step_index=0,
                step_status={step.name: StepStatus.PENDING for step in self.steps},
            )
            self.store.save(record)
        return record

    def _run_with_retry(self, step: SagaStep, context: dict) -> bool:
        deadline = time.monotonic() + step.timeout_seconds
        for attempt in range(1, step.retry_policy.max_attempts + 1):
            if time.monotonic() > deadline:
                print(f"    [{step.name}] timed out before attempt {attempt}")
                return False
            try:
                step.action(context)
                return True
            except Exception as exc:  # noqa: BLE001 - demo boundary, log and retry
                print(f"    [{step.name}] attempt {attempt} failed: {exc}")
                if attempt < step.retry_policy.max_attempts:
                    time.sleep(step.retry_policy.delay_for_attempt(attempt))
        return False

    def run(self, context: dict) -> SagaState:
        record = self._record()
        print(f"Saga {self.saga_id}: resuming at step index {record.current_step_index}")

        for index in range(record.current_step_index, len(self.steps)):
            step = self.steps[index]
            record.current_step_index = index
            self.store.save(record)

            print(f"  Executing step '{step.name}' (pivot={step.is_pivot})")
            succeeded = self._run_with_retry(step, context)

            if succeeded:
                record.step_status[step.name] = StepStatus.COMPLETED
                self.store.save(record)
                continue

            record.step_status[step.name] = StepStatus.FAILED
            if step.is_pivot:
                # Past the point of no return: forward-only recovery, no compensation.
                record.state = SagaState.FAILED
                self.store.save(record)
                print(f"Saga {self.saga_id}: pivot step failed, escalating (no compensation)")
                return record.state

            record.state = SagaState.COMPENSATING
            self.store.save(record)
            self._compensate(record, index, context)
            return record.state

        record.state = SagaState.COMPLETED
        self.store.save(record)
        print(f"Saga {self.saga_id}: completed successfully")
        return record.state

    def _compensate(self, record: SagaRecord, failed_index: int, context: dict) -> None:
        for index in range(failed_index - 1, -1, -1):
            step = self.steps[index]
            if record.step_status[step.name] != StepStatus.COMPLETED:
                continue
            if step.compensation is None:
                continue
            print(f"  Compensating step '{step.name}'")
            step.compensation(context)
            record.step_status[step.name] = StepStatus.COMPENSATED
            self.store.save(record)
        record.state = SagaState.COMPENSATED
        self.store.save(record)
        print(f"Saga {self.saga_id}: compensated back to a consistent state")


def reserve_inventory(ctx: dict) -> None:
    ctx["inventory_reserved"] = True


def release_inventory(ctx: dict) -> None:
    ctx["inventory_reserved"] = False


def charge_payment(ctx: dict) -> None:
    if ctx.get("force_payment_failure"):
        raise RuntimeError("card declined")
    ctx["payment_charged"] = True


def refund_payment(ctx: dict) -> None:
    ctx["payment_charged"] = False


def ship_order(ctx: dict) -> None:
    ctx["order_shipped"] = True


def build_steps() -> list[SagaStep]:
    return [
        SagaStep("reserve_inventory", reserve_inventory, release_inventory),
        SagaStep("charge_payment", charge_payment, refund_payment, retry_policy=RetryPolicy(max_attempts=2)),
        SagaStep("ship_order", ship_order, is_pivot=True),
    ]


def main() -> None:
    random.seed(7)

    print("=== Scenario 1: happy path ===")
    store = SagaStateStore()
    orchestrator = SagaOrchestrator("order-1", build_steps(), store)
    orchestrator.run({})

    print("\n=== Scenario 2: payment fails, compensates inventory reservation ===")
    store2 = SagaStateStore()
    orchestrator2 = SagaOrchestrator("order-2", build_steps(), store2)
    orchestrator2.run({"force_payment_failure": True})

    print("\n=== Scenario 3: crash after step 1, resume from durable state ===")
    store3 = SagaStateStore()
    record = SagaRecord(
        saga_id="order-3",
        state=SagaState.RUNNING,
        current_step_index=1,
        step_status={"reserve_inventory": StepStatus.COMPLETED, "charge_payment": StepStatus.PENDING, "ship_order": StepStatus.PENDING},
    )
    store3.save(record)
    orchestrator3 = SagaOrchestrator("order-3", build_steps(), store3)
    orchestrator3.run({})


if __name__ == "__main__":
    main()
