"""
Basic Paxos: a direct pseudocode-to-code translation of the
Prepare/Promise/Accept/Accepted phases described in Chapter 07, Section 4.2.

Demonstrates:
  1. A clean, uncontested run where a single proposer's value is chosen.
  2. The dueling-proposers livelock scenario, and the safety-critical rule
     that a proposer discovering an already-accepted value via a Promise
     response MUST adopt it instead of its own original value.

This is a pedagogical simulation, not a production Paxos implementation
(no networking, no persistence, no failure injection beyond what is
explicitly modeled).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Promise:
    granted: bool
    accepted_proposal: tuple[int, int] | None  # (proposal_number, proposer_id)
    accepted_value: str | None


class Acceptor:
    def __init__(self, acceptor_id: int) -> None:
        self.acceptor_id = acceptor_id
        self.highest_promised: tuple[int, int] | None = None
        self.accepted_proposal: tuple[int, int] | None = None
        self.accepted_value: str | None = None

    def handle_prepare(self, proposal: tuple[int, int]) -> Promise:
        if self.highest_promised is not None and proposal <= self.highest_promised:
            return Promise(granted=False, accepted_proposal=None, accepted_value=None)
        self.highest_promised = proposal
        return Promise(
            granted=True,
            accepted_proposal=self.accepted_proposal,
            accepted_value=self.accepted_value,
        )

    def handle_accept(self, proposal: tuple[int, int], value: str) -> bool:
        if self.highest_promised is not None and proposal < self.highest_promised:
            return False
        self.highest_promised = proposal
        self.accepted_proposal = proposal
        self.accepted_value = value
        return True


class Proposer:
    def __init__(self, proposer_id: int) -> None:
        self.proposer_id = proposer_id
        self._counter = 0

    def next_proposal_number(self) -> tuple[int, int]:
        self._counter += 1
        return (self._counter, self.proposer_id)

    def run_round(
        self, acceptors: list[Acceptor], desired_value: str, proposal: tuple[int, int] | None = None
    ) -> tuple[bool, str | None, tuple[int, int]]:
        """Runs one full Prepare->Accept round. Returns
        (chosen, value_that_was_chosen_or_none, proposal_number_used)."""
        proposal_number = proposal or self.next_proposal_number()
        majority = len(acceptors) // 2 + 1

        promises = [a.handle_prepare(proposal_number) for a in acceptors]
        granted = [p for p in promises if p.granted]
        print(
            f"  Proposer {self.proposer_id}: Prepare({proposal_number}) -> "
            f"{len(granted)}/{len(acceptors)} promises"
        )
        if len(granted) < majority:
            print(f"  Proposer {self.proposer_id}: failed to reach majority in Phase 1")
            return False, None, proposal_number

        already_accepted = [p for p in granted if p.accepted_value is not None]
        if already_accepted:
            highest = max(already_accepted, key=lambda p: p.accepted_proposal)
            value_to_propose = highest.accepted_value
            print(
                f"  Proposer {self.proposer_id}: a Promise revealed an already-accepted "
                f"value {value_to_propose!r} -> MUST adopt it instead of {desired_value!r}"
            )
        else:
            value_to_propose = desired_value

        accept_results = [a.handle_accept(proposal_number, value_to_propose) for a in acceptors]
        accepted_count = sum(accept_results)
        print(
            f"  Proposer {self.proposer_id}: Accept({proposal_number}, {value_to_propose!r}) -> "
            f"{accepted_count}/{len(acceptors)} accepted"
        )
        if accepted_count >= majority:
            print(f"  => Value {value_to_propose!r} is CHOSEN (majority accepted {proposal_number})")
            return True, value_to_propose, proposal_number

        print(f"  Proposer {self.proposer_id}: failed to reach majority in Phase 2")
        return False, None, proposal_number


def scenario_uncontested() -> None:
    print("--- Scenario 1: uncontested Basic Paxos round ---")
    acceptors = [Acceptor(i) for i in range(3)]
    proposer = Proposer(proposer_id=1)
    chosen, value, _ = proposer.run_round(acceptors, desired_value="X")
    assert chosen and value == "X"


def scenario_dueling_proposers() -> None:
    print("\n--- Scenario 2: dueling proposers -> livelock, then resolution ---")
    acceptors = [Acceptor(i) for i in range(3)]
    proposer_a = Proposer(proposer_id=1)
    proposer_b = Proposer(proposer_id=2)

    # Proposer A completes Phase 1 with proposal (1, 1).
    proposal_a1 = proposer_a.next_proposal_number()
    promises_a = [a.handle_prepare(proposal_a1) for a in acceptors]
    print(f"  Proposer A: Prepare({proposal_a1}) -> {sum(p.granted for p in promises_a)} promises")

    # Before A can send Accept, Proposer B runs a full round with a higher
    # proposal number, invalidating A's outstanding promises.
    chosen_b, value_b, proposal_b1 = proposer_b.run_round(acceptors, desired_value="Y")
    assert chosen_b and value_b == "Y"

    # Proposer A's stale Accept now gets rejected because acceptors already
    # promised the higher proposal number B used.
    accept_results = [a.handle_accept(proposal_a1, "X") for a in acceptors]
    print(
        f"  Proposer A: Accept({proposal_a1}, 'X') -> "
        f"{sum(accept_results)}/{len(acceptors)} accepted (rejected - stale proposal number)"
    )
    assert sum(accept_results) == 0

    # Proposer A retries with a fresh, higher proposal number. Because a
    # value has already been chosen, A's Promise responses will now reveal
    # it, forcing A to adopt "Y" instead of "X" - this is what preserves
    # Agreement across the whole cluster.
    print("  Proposer A retries with a new, higher proposal number:")
    chosen_a, value_a, _ = proposer_a.run_round(acceptors, desired_value="X")
    assert chosen_a and value_a == "Y", "Proposer A must adopt the already-chosen value"
    print("  Agreement preserved: both proposers converge on the same chosen value.")


def main() -> None:
    scenario_uncontested()
    scenario_dueling_proposers()


if __name__ == "__main__":
    main()
