"""
Raft log replication simulator (in-process, discrete-event).

Builds on 01_raft_leader_election_simulator.py's concept of an elected
Leader to simulate:
  - AppendEntries-based log replication to Followers.
  - Majority-based commit-index advancement.
  - The current-term-only commit restriction (Chapter 07, Section 4.5):
    a Leader only directly commits entries from its OWN current term by
    counting replicas; older-term entries become committed only as a
    byproduct of a later current-term entry being committed on top of them.
  - Recovery of a Follower whose log has diverged, via the Leader
    backtracking nextIndex until it finds a matching prevLogIndex/Term
    (the Log Matching Property).

This is a pedagogical simulation, not a production Raft implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LogEntry:
    term: int
    command: str


@dataclass
class RaftNode:
    node_id: int
    log: list[LogEntry] = field(default_factory=list)
    commit_index: int = -1  # index of the highest committed entry (-1 = none)

    def last_log_index(self) -> int:
        return len(self.log) - 1

    def last_log_term(self) -> int:
        return self.log[-1].term if self.log else 0


class RaftReplicationCluster:
    def __init__(self, leader_id: int, follower_ids: list[int], current_term: int) -> None:
        self.current_term = current_term
        self.leader = RaftNode(leader_id)
        self.followers = {fid: RaftNode(fid) for fid in follower_ids}
        self.majority = len(follower_ids) + 1
        self.majority = self.majority // 2 + 1
        # nextIndex[follower_id] = index of the next log entry to send to that follower
        self.next_index: dict[int, int] = {fid: 0 for fid in follower_ids}

    def append_entries(self, follower: RaftNode, prev_index: int, prev_term: int, entry: LogEntry | None) -> bool:
        """Simulates the AppendEntries RPC handler on a Follower. Returns
        True (success) only if the Follower's log matches at prev_index."""
        if prev_index >= 0:
            if prev_index >= len(follower.log):
                return False
            if follower.log[prev_index].term != prev_term:
                return False
        if entry is not None:
            follower.log = follower.log[: prev_index + 1]
            follower.log.append(entry)
        return True

    def replicate(self, command: str) -> int:
        """Leader appends a new entry for its current term and replicates it
        to all Followers, backtracking nextIndex for anyone that rejects."""
        entry = LogEntry(term=self.current_term, command=command)
        self.leader.log.append(entry)
        new_index = self.leader.last_log_index()
        print(f"  Leader appends entry {new_index} (term {entry.term}): {command!r}")

        ack_count = 1  # leader implicitly acks its own entry
        for fid, follower in self.followers.items():
            next_idx = self.next_index[fid]
            while True:
                prev_index = next_idx - 1
                prev_term = self.leader.log[prev_index].term if prev_index >= 0 else 0
                entry_to_send = self.leader.log[next_idx] if next_idx <= new_index else None
                success = self.append_entries(follower, prev_index, prev_term, entry_to_send)
                if success:
                    print(f"    Follower {fid}: AppendEntries(prevIndex={prev_index}) -> success")
                    self.next_index[fid] = new_index + 1
                    ack_count += 1
                    break
                print(f"    Follower {fid}: AppendEntries(prevIndex={prev_index}) -> REJECTED, backtracking")
                next_idx -= 1

        self.next_index_update_check()
        return self._maybe_commit(new_index, ack_count)

    def next_index_update_check(self) -> None:
        # No-op placeholder retained for readability of the replication flow;
        # nextIndex bookkeeping happens inline in replicate().
        return

    def _maybe_commit(self, index: int, ack_count: int) -> int:
        entry_term = self.leader.log[index].term
        if ack_count < self.majority:
            print(f"  Entry {index}: only {ack_count}/{self.majority_size()} acks - NOT committed yet")
            return self.leader.commit_index

        if entry_term != self.current_term:
            print(
                f"  Entry {index} is replicated to a majority but is from an OLDER term "
                f"({entry_term} != current term {self.current_term}) - "
                "NOT directly committed (current-term-only commit rule)"
            )
            return self.leader.commit_index

        self.leader.commit_index = index
        print(f"  Entry {index} (term {entry_term}): majority acked in CURRENT term -> COMMITTED")
        for follower in self.followers.values():
            follower.commit_index = index
        return index

    def majority_size(self) -> int:
        return self.majority


def scenario_clean_replication() -> None:
    print("--- Scenario 1: clean replication to a healthy majority ---")
    cluster = RaftReplicationCluster(leader_id=1, follower_ids=[2, 3, 4, 5], current_term=5)
    committed_index = cluster.replicate("SET x=1")
    assert committed_index == 0
    print(f"  Final commit index: {cluster.leader.commit_index}\n")


def scenario_old_term_entry_not_directly_committed() -> None:
    print("--- Scenario 2: current-term-only commit restriction ---")
    cluster = RaftReplicationCluster(leader_id=1, follower_ids=[2, 3], current_term=3)
    # Simulate an entry from an OLDER term already present only on the leader
    # and one follower (a majority of 3), left over from a prior leader crash.
    cluster.leader.log.append(LogEntry(term=2, command="SET y=OLD"))
    follower_2 = cluster.followers[2]
    follower_2.log.append(LogEntry(term=2, command="SET y=OLD"))
    cluster.next_index[2] = 1
    cluster.next_index[3] = 0
    ack_count = 2  # leader + follower 2 already have it, majority of 3
    result = cluster._maybe_commit(index=0, ack_count=ack_count)
    assert result == -1, "an old-term entry must not be directly committed by counting alone"

    print("  Leader now replicates a NEW entry in its current term:")
    committed_index = cluster.replicate("SET z=NEW")
    assert committed_index == 1
    print(
        "  Entry 0 (the old-term entry) is now transitively committed as a "
        "byproduct of entry 1's commit, per the Log Matching Property."
    )
    cluster.leader.commit_index = max(cluster.leader.commit_index, 0)


def main() -> None:
    scenario_clean_replication()
    scenario_old_term_entry_not_directly_committed()


if __name__ == "__main__":
    main()
