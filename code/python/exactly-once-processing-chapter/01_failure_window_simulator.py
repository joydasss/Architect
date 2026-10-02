"""Compare duplicate attempts with atomic position-and-state processing."""

from dataclasses import dataclass


@dataclass
class Counts:
    deliveries: int = 0
    handler_invocations: int = 0
    state_transitions: int = 0
    visible_effects: int = 0


class AtomicConsumer:
    """Small model whose state and next offset commit together."""

    def __init__(self) -> None:
        self.balance = 0
        self.next_offset = 0
        self.counts = Counts()

    def deliver(self, offset: int, amount: int, fail_before_commit: bool = False) -> None:
        self.counts.deliveries += 1
        self.counts.handler_invocations += 1

        if offset < self.next_offset:
            return
        if offset != self.next_offset:
            raise ValueError(f"expected offset {self.next_offset}, got {offset}")

        next_balance = self.balance + amount
        next_offset = offset + 1
        if fail_before_commit:
            raise RuntimeError("simulated crash before atomic commit")

        self.balance = next_balance
        self.next_offset = next_offset
        self.counts.state_transitions += 1
        self.counts.visible_effects += 1


def report(label: str, consumer: AtomicConsumer) -> None:
    counts = consumer.counts
    print(
        f"{label}: balance={consumer.balance}, next_offset={consumer.next_offset}, "
        f"deliveries={counts.deliveries}, invocations={counts.handler_invocations}, "
        f"transitions={counts.state_transitions}, effects={counts.visible_effects}"
    )


def main() -> None:
    before_commit = AtomicConsumer()
    try:
        before_commit.deliver(0, 7, fail_before_commit=True)
    except RuntimeError:
        pass
    before_commit.deliver(0, 7)
    report("crash before commit then replay", before_commit)
    assert before_commit.balance == 7
    assert before_commit.counts.handler_invocations == 2
    assert before_commit.counts.state_transitions == 1

    after_commit = AtomicConsumer()
    after_commit.deliver(0, 7)
    # The source did not observe its acknowledgment, so it delivers offset 0 again.
    after_commit.deliver(0, 7)
    report("commit succeeded but acknowledgment was lost", after_commit)
    assert after_commit.balance == 7
    assert after_commit.counts.deliveries == 2
    assert after_commit.counts.handler_invocations == 2
    assert after_commit.counts.state_transitions == 1
    assert after_commit.counts.visible_effects == 1


if __name__ == "__main__":
    main()