"""Compensating-transaction craftsmanship: literal vs. semantic compensation,
and handling steps whose forward action is fundamentally non-reversible.

Accompanies CH13_Saga_Pattern.md Section 4.2. A compensating transaction is
not automatically "the forward action in reverse" -- three distinct
craftsmanship categories exist, and picking the wrong one silently produces
either an incorrect undo or an un-compensable saga.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CompensationKind(str, Enum):
    # The forward effect can be exactly undone in the same domain.
    LITERAL = "LITERAL"
    # The forward effect cannot be undone, but an equivalent corrective
    # action restores the *business* invariant (not the literal prior state).
    SEMANTIC = "SEMANTIC"
    # The forward effect has an irreversible real-world side effect; no
    # automated compensation exists, only manual/human escalation.
    NON_REVERSIBLE = "NON_REVERSIBLE"


@dataclass
class CompensableStep:
    name: str
    kind: CompensationKind
    forward: str
    compensation: str


CATALOG = [
    CompensableStep(
        name="reserve_inventory",
        kind=CompensationKind.LITERAL,
        forward="Decrement available_count by 1, tag with reservation_id",
        compensation="Increment available_count by 1 for the same reservation_id",
    ),
    CompensableStep(
        name="send_order_confirmation_email",
        kind=CompensationKind.SEMANTIC,
        forward="Send 'Your order is confirmed' email to the customer",
        compensation=(
            "Cannot unsend the email. Semantic compensation: send a follow-up "
            "'Your order was cancelled, here is your refund' email instead."
        ),
    ),
    CompensableStep(
        name="dispatch_courier_pickup",
        kind=CompensationKind.NON_REVERSIBLE,
        forward="Courier has already physically collected the package from the warehouse",
        compensation=(
            "No automated compensation exists once the courier has the package. "
            "Escalate to a human-operated reverse-logistics workflow "
            "(intercept-in-transit request or return-to-sender after delivery)."
        ),
    ),
]


def describe(step: CompensableStep) -> str:
    lines = [
        f"Step: {step.name}",
        f"  Kind: {step.kind.value}",
        f"  Forward action: {step.forward}",
        f"  Compensation:   {step.compensation}",
    ]
    return "\n".join(lines)


def compensate_or_escalate(step: CompensableStep, dead_letter_queue: list[CompensableStep]) -> None:
    if step.kind == CompensationKind.NON_REVERSIBLE:
        dead_letter_queue.append(step)
        print(f"  -> {step.name}: no automated compensation possible, routed to dead-letter queue")
        return
    print(f"  -> {step.name}: automated compensation executed ({step.kind.value})")


def main() -> None:
    dead_letter_queue: list[CompensableStep] = []

    for step in CATALOG:
        print(describe(step))
        print()

    print("=== Running compensation pass for a failed saga instance ===")
    for step in reversed(CATALOG):
        compensate_or_escalate(step, dead_letter_queue)

    print(f"\nDead-letter queue size after compensation pass: {len(dead_letter_queue)}")
    for step in dead_letter_queue:
        print(f"  Needs manual intervention: {step.name}")


if __name__ == "__main__":
    main()
