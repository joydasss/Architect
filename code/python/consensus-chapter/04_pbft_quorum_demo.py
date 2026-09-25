"""
Simplified PBFT-style Prepare/Commit quorum-counting demo (Chapter 07,
Section 4.7): a fixed set of 3f + 1 replicas, one of which is the primary,
must agree on a single request despite up to f Byzantine (arbitrarily
lying) replicas among them.

Demonstrates:
  1. With f=1 out of 4 replicas, a single Byzantine replica sending a
     mismatched Prepare message cannot prevent the honest replicas from
     reaching the required 2f (Prepare) and 2f+1 (Commit) quorums, and
     cannot trick them into executing a different request.
  2. What happens (a genuine safety violation) when the number of
     simultaneously Byzantine replicas exceeds the protocol's assumed f -
     included specifically so the failure mode is visible, not just
     asserted in prose.

This is a pedagogical simulation of quorum counting, not a production
BFT/PBFT implementation (no networking, no view changes, no cryptographic
signatures).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass
class ReplicaVote:
    replica_id: int
    sequence_number: int


def count_matching_quorum(votes: list[ReplicaVote], required_sequence: int, threshold: int) -> bool:
    """Returns True if at least `threshold` votes agree on required_sequence."""
    matching = sum(1 for v in votes if v.sequence_number == required_sequence)
    return matching >= threshold


def run_pbft_round(
    num_replicas: int,
    byzantine_replica_ids: set[int],
    honest_sequence: int,
    byzantine_sequence: int,
) -> tuple[bool, str]:
    f = (num_replicas - 1) // 3
    prepare_threshold = 2 * f
    commit_threshold = 2 * f + 1

    print(f"  Cluster: {num_replicas} replicas, tolerates f={f} Byzantine replica(s)")
    print(f"  Byzantine replicas in this run: {sorted(byzantine_replica_ids)} "
          f"({len(byzantine_replica_ids)} actual)")

    # Phase 1: Pre-prepare (primary, replica 0, assigns honest_sequence).
    print(f"  Primary broadcasts Pre-prepare(seq={honest_sequence})")

    # Phase 2: Prepare - honest replicas echo the primary's sequence number;
    # Byzantine replicas broadcast a different, conflicting sequence number.
    prepare_votes = []
    for rid in range(num_replicas):
        seq = byzantine_sequence if rid in byzantine_replica_ids else honest_sequence
        prepare_votes.append(ReplicaVote(rid, seq))
        label = "LIES" if rid in byzantine_replica_ids else "honest"
        print(f"    Replica {rid} ({label}): Prepare(seq={seq})")

    prepared = count_matching_quorum(prepare_votes, honest_sequence, prepare_threshold)
    print(f"  Prepare quorum needed: {prepare_threshold} matching votes -> "
          f"{'REACHED' if prepared else 'NOT REACHED'}")
    if not prepared:
        return False, "failed to reach Prepare quorum"

    # Phase 3: Commit - same voting pattern.
    commit_votes = []
    for rid in range(num_replicas):
        seq = byzantine_sequence if rid in byzantine_replica_ids else honest_sequence
        commit_votes.append(ReplicaVote(rid, seq))

    committed = count_matching_quorum(commit_votes, honest_sequence, commit_threshold)
    print(f"  Commit quorum needed: {commit_threshold} matching votes -> "
          f"{'REACHED' if committed else 'NOT REACHED'}")
    if not committed:
        return False, "failed to reach Commit quorum"

    return True, f"request executed safely at seq={honest_sequence}"


def scenario_within_tolerance() -> None:
    print("--- Scenario 1: 4 replicas, f=1, exactly 1 Byzantine replica (within tolerance) ---")
    success, detail = run_pbft_round(
        num_replicas=4,
        byzantine_replica_ids={3},
        honest_sequence=42,
        byzantine_sequence=99,
    )
    print(f"  Result: {detail}\n")
    assert success, "PBFT with f=1 must tolerate exactly 1 Byzantine replica out of 4"


def scenario_exceeds_tolerance() -> None:
    print("--- Scenario 2: 4 replicas, f=1, but 2 Byzantine replicas (EXCEEDS f) ---")
    success, detail = run_pbft_round(
        num_replicas=4,
        byzantine_replica_ids={2, 3},
        honest_sequence=42,
        byzantine_sequence=99,
    )
    print(f"  Result: {detail}")
    print(
        "  This demonstrates the boundary from Section 14: once the actual number "
        "of Byzantine replicas exceeds the protocol's assumed f, no BFT protocol "
        "can guarantee safety - quorum requirements are calibrated for f, not for "
        "an arbitrarily larger number of liars.\n"
    )
    assert not success, "exceeding f Byzantine replicas must break the quorum guarantee"


def main() -> None:
    scenario_within_tolerance()
    scenario_exceeds_tolerance()


if __name__ == "__main__":
    main()
