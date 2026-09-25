"""Leader/follower WAL log-shipping simulator (CH07_Replication.md Sections 4.2-4.4, 10).

Models a leader appending Write-Ahead Log (WAL) records and shipping them to
followers over a simulated, delayed network, under async/sync/semi-sync
modes, so the durability-vs-latency trade-off (Section 4.3) can be measured
with actual numbers instead of only argued in prose.
"""
from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from enum import Enum


class ReplicationMode(Enum):
    ASYNC = "async"        # leader never waits on a follower
    SEMI_SYNC = "semi_sync"  # leader waits for at least one follower to RECEIVE the record
    SYNC = "sync"           # leader waits for at least one follower to APPLY the record


@dataclass
class WalRecord:
    lsn: int
    payload: str


@dataclass
class Follower:
    name: str
    network_delay_ms: tuple[float, float]  # (min, max) simulated one-way latency
    apply_delay_ms: tuple[float, float]
    received_lsn: int = 0
    applied_lsn: int = 0

    def receive_and_apply(self, record: WalRecord, rng: random.Random) -> tuple[float, float]:
        transfer_ms = rng.uniform(*self.network_delay_ms)
        self.received_lsn = record.lsn
        apply_ms = rng.uniform(*self.apply_delay_ms)
        self.applied_lsn = record.lsn
        return transfer_ms, apply_ms


@dataclass
class Leader:
    followers: list[Follower]
    mode: ReplicationMode
    wal: list[WalRecord] = field(default_factory=list)
    next_lsn: int = 1
    rng: random.Random = field(default_factory=random.Random)

    def commit_write(self, payload: str) -> dict:
        """Returns commit latency and, for async mode, the data-loss-window size."""
        record = WalRecord(lsn=self.next_lsn, payload=payload)
        self.wal.append(record)
        self.next_lsn += 1

        leader_local_write_ms = self.rng.uniform(0.2, 0.6)  # local fsync-equivalent cost
        commit_latency_ms = leader_local_write_ms

        if self.mode is ReplicationMode.ASYNC:
            # Client is told "committed" before any follower has seen the record.
            for follower in self.followers:
                follower.receive_and_apply(record, self.rng)
            unshipped = sum(1 for f in self.followers if f.applied_lsn < record.lsn)
            return {"commit_latency_ms": commit_latency_ms, "unacked_followers_at_commit": len(self.followers)}

        # sync / semi_sync: wait for at least one follower before acknowledging.
        best_transfer, best_apply = None, None
        for follower in self.followers:
            transfer_ms, apply_ms = follower.receive_and_apply(record, self.rng)
            wait_ms = transfer_ms if self.mode is ReplicationMode.SEMI_SYNC else transfer_ms + apply_ms
            if best_transfer is None or wait_ms < best_transfer:
                best_transfer = wait_ms
        commit_latency_ms += best_transfer or 0.0
        return {"commit_latency_ms": commit_latency_ms, "unacked_followers_at_commit": 0}


def run_scenario(mode: ReplicationMode, num_writes: int = 200, seed: int = 42) -> dict:
    rng = random.Random(seed)
    followers = [
        Follower("replica-a", network_delay_ms=(2, 15), apply_delay_ms=(1, 5)),
        Follower("replica-b", network_delay_ms=(20, 120), apply_delay_ms=(1, 8)),  # cross-region
    ]
    leader = Leader(followers=followers, mode=mode, rng=rng)

    latencies = []
    max_unacked_at_a_commit = 0
    for i in range(num_writes):
        result = leader.commit_write(payload=f"write-{i}")
        latencies.append(result["commit_latency_ms"])
        max_unacked_at_a_commit = max(max_unacked_at_a_commit, result["unacked_followers_at_commit"])

    return {
        "mode": mode.value,
        "p50_commit_ms": round(statistics.median(latencies), 3),
        "p99_commit_ms": round(statistics.quantiles(latencies, n=100)[98], 3),
        "max_followers_unacked_if_leader_died_mid_run": max_unacked_at_a_commit,
    }


if __name__ == "__main__":
    for mode in ReplicationMode:
        print(run_scenario(mode))
