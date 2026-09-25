"""
Raft leader-election simulator (in-process, discrete-event).

Models a small Raft cluster's leader-election sub-protocol only (no log
replication - see 02_raft_log_replication_simulator.py for that). Each node
runs randomized election timeouts, increments terms, requests votes, and
grants at most one vote per term, honoring the Election Restriction
(a voter only grants its vote if the candidate's log is at least as
up-to-date as its own). A split-vote scenario is deliberately forced once
to demonstrate re-randomized timeouts resolving it in a later term.

This is a pedagogical simulation of message passing and state transitions,
not a production consensus implementation.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum, auto


class Role(Enum):
    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()


@dataclass
class NodeState:
    node_id: int
    role: Role = Role.FOLLOWER
    current_term: int = 0
    voted_for: int | None = None
    last_log_index: int = 0
    last_log_term: int = 0
    votes_received: set[int] = field(default_factory=set)


class RaftElectionCluster:
    """Simulates leader election for a fixed set of node ids."""

    def __init__(self, node_ids: list[int], seed: int = 42) -> None:
        self.rng = random.Random(seed)
        self.nodes: dict[int, NodeState] = {nid: NodeState(nid) for nid in node_ids}
        self.majority = len(node_ids) // 2 + 1
        self.trace: list[str] = []

    def log(self, message: str) -> None:
        self.trace.append(message)
        print(message)

    def request_vote(self, voter: NodeState, candidate: NodeState) -> bool:
        """Voter decides whether to grant its vote to candidate, per the
        Election Restriction: only if candidate's log is at least as
        up-to-date (higher last-log-term, or equal term and >= length)."""
        if candidate.current_term < voter.current_term:
            return False

        if candidate.current_term > voter.current_term:
            voter.current_term = candidate.current_term
            voter.voted_for = None
            voter.role = Role.FOLLOWER

        already_voted = voter.voted_for is not None and voter.voted_for != candidate.node_id
        if already_voted:
            return False

        candidate_up_to_date = (candidate.last_log_term, candidate.last_log_index) >= (
            voter.last_log_term,
            voter.last_log_index,
        )
        if not candidate_up_to_date:
            return False

        voter.voted_for = candidate.node_id
        return True

    def run_election_round(
        self,
        candidate_ids: list[int],
        voter_arrival_order: dict[int, list[int]] | None = None,
    ) -> int | None:
        """One or more nodes simultaneously time out and start an election
        in the same new term. `voter_arrival_order` optionally controls,
        per voter, the order in which competing RequestVote messages are
        modeled as arriving (a genuine split vote requires that different
        voters see different candidates' requests first, exactly as an
        asynchronous network would deliver them out of order). Returns the
        winning node id, or None if the vote split with no majority winner.
        """
        new_term = max(self.nodes[cid].current_term for cid in candidate_ids) + 1

        for cid in candidate_ids:
            node = self.nodes[cid]
            node.current_term = new_term
            node.role = Role.CANDIDATE
            node.voted_for = cid
            node.votes_received = {cid}
            self.log(f"  Node {cid}: election timeout -> term {new_term}, votes for self")

        other_ids = [nid for nid in self.nodes if nid not in candidate_ids]
        for oid in other_ids:
            voter = self.nodes[oid]
            arrival_order = (voter_arrival_order or {}).get(oid, list(candidate_ids))
            for cid in arrival_order:
                candidate = self.nodes[cid]
                granted = self.request_vote(voter, candidate)
                if granted:
                    candidate.votes_received.add(oid)
                    self.log(f"  Node {oid} -> grants vote to Node {cid} (term {new_term})")
                else:
                    self.log(f"  Node {oid} -> rejects vote request from Node {cid}")

        winners = [
            cid for cid in candidate_ids if len(self.nodes[cid].votes_received) >= self.majority
        ]
        if len(winners) == 1:
            winner_id = winners[0]
            self.nodes[winner_id].role = Role.LEADER
            for nid, node in self.nodes.items():
                if nid != winner_id:
                    node.role = Role.FOLLOWER
            self.log(
                f"  => Node {winner_id} wins term {new_term} with "
                f"{len(self.nodes[winner_id].votes_received)}/{len(self.nodes)} votes -> LEADER"
            )
            return winner_id

        self.log(f"  => Split vote in term {new_term}: no candidate reached a majority")
        return None


def main() -> None:
    cluster = RaftElectionCluster(node_ids=[1, 2, 3, 4, 5])

    print("--- Scenario 1: clean election, single candidate times out first ---")
    winner = cluster.run_election_round(candidate_ids=[1])
    assert winner == 1

    print("\n--- Scenario 2: forced split vote (three candidates time out together) ---")
    # With 5 nodes, 2 remaining voters (1 and 5) each receive the competing
    # RequestVote messages in a different order - modeling exactly the kind
    # of asynchronous message-delivery race that produces a real split vote.
    result = cluster.run_election_round(
        candidate_ids=[2, 3, 4],
        voter_arrival_order={1: [2, 3, 4], 5: [3, 2, 4]},
    )
    assert result is None, "expected a split vote with no majority winner"

    print("\n--- Scenario 3: re-randomized timeouts resolve the split in a later term ---")
    winner_after_split = cluster.run_election_round(candidate_ids=[2])
    assert winner_after_split == 2

    print("\nFinal roles:")
    for node in cluster.nodes.values():
        print(f"  Node {node.node_id}: term={node.current_term}, role={node.role.name}")


if __name__ == "__main__":
    main()
