"""Simplified simulation of Kafka's In-Sync Replica (ISR) set model.

Models one partition with a leader and N-1 followers. Each follower fetches
from the leader at its own pace; a follower falls out of the ISR once its
fetch lag exceeds replica.lag.time.max.ms. Demonstrates:
  - how the high watermark (highest offset acked by ALL current ISR members)
    bounds what a consumer can read,
  - how acks=all + min.insync.replicas interact to trade availability for
    durability when the ISR shrinks.
This is a teaching simulation, not a wire-protocol-accurate reimplementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Replica:
    name: str
    log_end_offset: int = 0          # highest offset this replica has appended
    last_fetch_tick: int = 0         # simulated clock of its last successful fetch


@dataclass
class PartitionReplicationState:
    replication_factor: int
    min_insync_replicas: int
    lag_time_max_ticks: int = 3
    clock: int = 0
    leader: Replica = field(default_factory=lambda: Replica("broker-1 (leader)"))
    followers: list[Replica] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.followers:
            self.followers = [Replica(f"broker-{i} (follower)") for i in range(2, self.replication_factor + 1)]

    def isr(self) -> list[Replica]:
        """A follower stays in the ISR only if it fetched recently enough."""
        in_sync = [self.leader]
        for follower in self.followers:
            lag_ticks = self.clock - follower.last_fetch_tick
            if lag_ticks <= self.lag_time_max_ticks:
                in_sync.append(follower)
        return in_sync

    def high_watermark(self) -> int:
        """Highest offset acknowledged by every replica currently in the ISR."""
        return min(r.log_end_offset for r in self.isr())

    def produce(self, acks: str) -> tuple[bool, str]:
        """Attempt to append one record under the given acks policy."""
        current_isr = self.isr()
        if acks == "all" and len(current_isr) < self.min_insync_replicas:
            return False, (
                f"NotEnoughReplicasException: ISR size {len(current_isr)} "
                f"< min.insync.replicas {self.min_insync_replicas}"
            )
        self.leader.log_end_offset += 1
        if acks == "0":
            return True, "ack returned immediately, no durability guarantee"
        if acks == "1":
            return True, "ack after leader append only; a leader crash can still lose this record"
        # acks == "all": leader waits for every current ISR member to catch up.
        for member in current_isr:
            member.log_end_offset = self.leader.log_end_offset
        return True, f"ack after all {len(current_isr)} ISR members caught up (durable)"

    def follower_fetch(self, follower_name: str) -> None:
        for follower in self.followers:
            if follower.name == follower_name:
                follower.log_end_offset = self.leader.log_end_offset
                follower.last_fetch_tick = self.clock

    def advance_clock(self, ticks: int = 1) -> None:
        self.clock += ticks


def _scenario_isr_shrinks_and_min_insync_replicas_blocks_writes() -> None:
    partition = PartitionReplicationState(replication_factor=3, min_insync_replicas=2)

    ok, detail = partition.produce(acks="all")
    print(f"[t={partition.clock}] produce(acks=all): ok={ok} -- {detail}")
    partition.follower_fetch("broker-2 (follower)")
    partition.follower_fetch("broker-3 (follower)")
    print(f"  ISR={[r.name for r in partition.isr()]} high_watermark={partition.high_watermark()}")

    # broker-3 stalls (GC pause / slow disk) and stops fetching for several ticks.
    for _ in range(partition.lag_time_max_ticks + 1):
        partition.advance_clock()
        partition.follower_fetch("broker-2 (follower)")  # broker-2 keeps up fine

    print(f"[t={partition.clock}] broker-3 stalled -> ISR={[r.name for r in partition.isr()]}")
    ok, detail = partition.produce(acks="all")
    print(f"[t={partition.clock}] produce(acks=all) with shrunk ISR: ok={ok} -- {detail}")

    # Now broker-2 also stalls: ISR drops to just the leader (size 1 < min.insync.replicas=2).
    partition.advance_clock(partition.lag_time_max_ticks + 1)
    print(f"[t={partition.clock}] both followers stalled -> ISR={[r.name for r in partition.isr()]}")
    ok, detail = partition.produce(acks="all")
    print(f"[t={partition.clock}] produce(acks=all) with ISR<min.insync.replicas: ok={ok} -- {detail}")
    assert not ok, "acks=all must refuse writes once the ISR can no longer satisfy min.insync.replicas"


if __name__ == "__main__":
    _scenario_isr_shrinks_and_min_insync_replicas_blocks_writes()
