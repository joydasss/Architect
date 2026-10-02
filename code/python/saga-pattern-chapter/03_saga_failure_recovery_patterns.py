"""Saga failure-recovery patterns: retriable vs. non-retriable step
classification, the pivot-transaction point of no return, and dead-letter
escalation for steps that exhaust their retry budget.

Accompanies CH13_Saga_Pattern.md Section 4.3.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum


class ErrorClass(str, Enum):
    TRANSIENT = "TRANSIENT"        # network blip, timeout, 503 - retry
    PERMANENT = "PERMANENT"        # validation failure, business-rule violation - do not retry
    UNKNOWN = "UNKNOWN"            # ambiguous outcome - retry with idempotency guard


@dataclass
class SagaStepResult:
    ok: bool
    error_class: ErrorClass = ErrorClass.TRANSIENT
    message: str = ""


@dataclass
class RecoverableStep:
    name: str
    is_pivot: bool
    max_attempts: int
    simulate: "callable"
    attempts_made: int = 0


def classify_and_retry(step: RecoverableStep, dead_letter: list[str]) -> bool:
    while step.attempts_made < step.max_attempts:
        step.attempts_made += 1
        result: SagaStepResult = step.simulate(step.attempts_made)
        if result.ok:
            print(f"  [{step.name}] attempt {step.attempts_made}: succeeded")
            return True

        print(f"  [{step.name}] attempt {step.attempts_made}: failed "
              f"({result.error_class.value}) - {result.message}")

        if result.error_class == ErrorClass.PERMANENT:
            print(f"  [{step.name}] permanent error, no further retries")
            break

    if step.is_pivot:
        dead_letter.append(step.name)
        print(f"  [{step.name}] retry budget exhausted past the pivot point "
              f"- escalating to dead-letter queue for manual intervention")
    else:
        print(f"  [{step.name}] retry budget exhausted before the pivot point "
              f"- safe to compensate backward instead")
    return False


def flaky_network_call(attempt: int) -> SagaStepResult:
    if attempt < 3:
        return SagaStepResult(ok=False, error_class=ErrorClass.TRANSIENT, message="upstream timeout")
    return SagaStepResult(ok=True)


def always_permanent_failure(attempt: int) -> SagaStepResult:
    return SagaStepResult(ok=False, error_class=ErrorClass.PERMANENT, message="invalid shipping address")


def flaky_carrier_dispatch(attempt: int) -> SagaStepResult:
    # Post-pivot step: courier API is unreliable, and by this point the
    # package is already physically staged, so failure here cannot be
    # compensated -- it can only be retried or escalated.
    if attempt < 5:
        return SagaStepResult(ok=False, error_class=ErrorClass.TRANSIENT, message="carrier API 503")
    return SagaStepResult(ok=False, error_class=ErrorClass.TRANSIENT, message="carrier API 503")


def main() -> None:
    random.seed(3)
    dead_letter: list[str] = []

    print("=== Case 1: transient error, succeeds within retry budget ===")
    step1 = RecoverableStep("charge_payment", is_pivot=False, max_attempts=4, simulate=flaky_network_call)
    classify_and_retry(step1, dead_letter)

    print("\n=== Case 2: permanent error, fails fast without wasting retries ===")
    step2 = RecoverableStep("validate_shipping_address", is_pivot=False, max_attempts=4, simulate=always_permanent_failure)
    classify_and_retry(step2, dead_letter)

    print("\n=== Case 3: post-pivot step exhausts retries, escalates instead of compensating ===")
    step3 = RecoverableStep("dispatch_courier_pickup", is_pivot=True, max_attempts=3, simulate=flaky_carrier_dispatch)
    classify_and_retry(step3, dead_letter)

    print(f"\nFinal dead-letter queue: {dead_letter}")


if __name__ == "__main__":
    main()
