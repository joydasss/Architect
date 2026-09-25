"""
03_lightweight_transaction_cas_demo.py

Self-contained in-memory simulation of Cassandra's Lightweight Transactions
(LWT) -- the Paxos-based compare-and-set mechanism behind
`INSERT ... IF NOT EXISTS` and `UPDATE ... IF <condition>`. Runs two
concurrent "coordinators" competing for the same row with plain `threading`
(no live cluster or driver dependency) to show why only one wins and the
other observes the row was already claimed, exactly like a real LWT's
`[applied]` column. See CH18_Cassandra.md Section 4.7.

Run with: python 03_lightweight_transaction_cas_demo.py
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class PaxosRow:
    """One row plus the Paxos state Cassandra tracks alongside it: the
    highest ballot (proposal number) any coordinator has been promised,
    and the currently accepted (but not yet committed) value, if any."""

    lock: threading.Lock = field(default_factory=threading.Lock)
    committed_value: object | None = None
    promised_ballot: int = 0
    accepted_ballot: int = 0
    accepted_value: object | None = None


def paxos_cas(
    row: PaxosRow, coordinator_name: str, ballot: int, proposed_value: object
) -> tuple[bool, object | None]:
    """Run one round of the four-phase Paxos-based CAS Cassandra performs
    for a lightweight transaction: Prepare/Promise, then Propose/Accept,
    then a Commit phase (simplified here into a single critical section --
    real Cassandra's phases are separate network round trips across the
    replica set, which is exactly why LWTs cost 4x the round trips of a
    normal write and must be reserved for genuine compare-and-set needs,
    not routine writes -- Section 4.7's decision-implications point).

    Returns (applied, current_value) mirroring the real CQL response shape:
    a `[applied]` boolean plus the row's current value either way.
    """
    with row.lock:
        # Phase 1: Prepare -- this ballot must be strictly higher than any
        # ballot already promised, or the round is rejected outright.
        if ballot <= row.promised_ballot:
            return False, row.committed_value
        row.promised_ballot = ballot

        # Phase 2: Propose -- the condition (IF NOT EXISTS, here modeled as
        # "committed_value is still None") is evaluated against the
        # CURRENT committed state, not a client-cached copy -- this is what
        # makes it safe under concurrent competing writers.
        if row.committed_value is not None:
            # Someone already committed a value; this CAS is rejected and
            # the caller learns the current value, exactly like a real
            # LWT's `[applied]=false` response row.
            return False, row.committed_value

        row.accepted_ballot = ballot
        row.accepted_value = proposed_value

        # Phase 3: Commit -- simplified to an immediate commit since this
        # single-process simulation has no partial-replica-failure case to
        # reconcile; real Cassandra additionally persists the committed
        # value in a way survivable across coordinator failure mid-round.
        row.committed_value = proposed_value
        return True, proposed_value


def concurrent_claim_attempt(
    row: PaxosRow, coordinator_name: str, ballot: int, proposed_value: object, results: dict
) -> None:
    # A tiny random-ish delay (deterministic here via ballot) simulates
    # network jitter between competing coordinators' Paxos rounds.
    time.sleep(0.01 * (ballot % 3))
    applied, current_value = paxos_cas(row, coordinator_name, ballot, proposed_value)
    results[coordinator_name] = (applied, current_value)


def demo_username_claim_race() -> None:
    """Classic LWT use case: claiming a unique username. Two application
    instances race to INSERT the same username `IF NOT EXISTS` -- exactly
    one may win, and the loser must be told the row already exists rather
    than silently overwriting it (which a normal, non-conditional INSERT
    would do, last-write-wins, with no such guarantee)."""
    print("=== Two coordinators racing to claim username 'octocat' ===")
    row = PaxosRow()
    results: dict[str, tuple[bool, object | None]] = {}

    threads = [
        threading.Thread(
            target=concurrent_claim_attempt,
            args=(row, "app-instance-A", 101, "user_id=alice-uuid", results),
        ),
        threading.Thread(
            target=concurrent_claim_attempt,
            args=(row, "app-instance-B", 102, "user_id=bob-uuid", results),
        ),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for name, (applied, current_value) in results.items():
        outcome = "WON (row created)" if applied else f"LOST (row already = {current_value!r})"
        print(f"{name}: [applied]={applied} -> {outcome}")

    winners = [name for name, (applied, _) in results.items() if applied]
    assert len(winners) == 1, "exactly one coordinator must win a CAS race"
    print(f"\nExactly one winner, as Paxos guarantees: {winners[0]}")


def demo_conditional_update_stale_ballot_retry() -> None:
    """UPDATE ... IF status = 'PENDING': a lower/stale ballot is rejected
    outright by Phase 1 (Prepare), forcing the caller to retry with a new,
    higher ballot -- this is the concrete mechanism behind the client-
    visible retry behavior LWTs require under contention (Section 4.7's
    failure-mode note on Paxos contention/livelock under high write
    concurrency to the same partition)."""
    print("\n=== Stale ballot rejected, forcing a retry with a fresh ballot ===")
    row = PaxosRow()
    paxos_cas(row, "worker-1", ballot=50, proposed_value="status=PROCESSING")
    applied, current = paxos_cas(row, "worker-2", ballot=10, proposed_value="status=FAILED")
    print(f"worker-2 stale ballot(10) after promised(50): applied={applied}, current={current!r}")
    assert not applied
    # A correct client library increments and retries with ballot > promised_ballot.
    applied, current = paxos_cas(row, "worker-2", ballot=51, proposed_value="status=FAILED")
    print(f"worker-2 retried with ballot(51): applied={applied} -> but row already committed to {current!r}")


if __name__ == "__main__":
    demo_username_claim_race()
    demo_conditional_update_stale_ballot_retry()
