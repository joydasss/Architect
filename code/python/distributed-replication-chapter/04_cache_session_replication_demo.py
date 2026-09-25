"""Replication for non-database stateful services: distributed cache + session store.

Two small simulations:
  1. Async cache replication: a write to one cache node propagates to peer
     nodes after a simulated network delay, producing a bounded stale-read
     window on the peers -- the same asynchronous-replication trade-off
     Replication (Part 06 CH07) teaches for databases, applied to a cache.
  2. Session replication vs. sticky sessions: shows why a load balancer that
     round-robins requests across app-server replicas needs the session
     itself replicated (or externalized) to avoid a "logged out" surprise
     when a request lands on a replica that never saw the login write.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CacheNode:
    name: str
    store: dict[str, str] = field(default_factory=dict)
    inbox: list[tuple[int, str, str]] = field(default_factory=list)  # (deliver_at_tick, key, value)

    def write_local(self, key: str, value: str) -> None:
        self.store[key] = value

    def receive_replicated_write(self, key: str, value: str, deliver_at_tick: int) -> None:
        self.inbox.append((deliver_at_tick, key, value))

    def apply_due_replication(self, now_tick: int) -> None:
        still_pending = []
        for deliver_at_tick, key, value in self.inbox:
            if deliver_at_tick <= now_tick:
                self.store[key] = value
            else:
                still_pending.append((deliver_at_tick, key, value))
        self.inbox = still_pending

    def read(self, key: str) -> str | None:
        return self.store.get(key)


def _simulate_async_cache_replication_stale_window() -> None:
    replication_delay_ticks = 2
    node_a = CacheNode("cache-node-a")
    node_b = CacheNode("cache-node-b")
    node_c = CacheNode("cache-node-c")
    peers = [node_b, node_c]

    clock = 0
    key, value = "product:42:price", "19.99"

    # A write lands on node A and is asynchronously fanned out to peers.
    node_a.write_local(key, value)
    for peer in peers:
        peer.receive_replicated_write(key, value, deliver_at_tick=clock + replication_delay_ticks)
    print(f"[t={clock}] wrote {key}={value} on {node_a.name}; fanned out to {[p.name for p in peers]}")

    for tick in range(1, replication_delay_ticks + 2):
        clock = tick
        for peer in peers:
            peer.apply_due_replication(clock)
        stale_reads = {p.name: p.read(key) for p in peers}
        print(f"[t={clock}] peer reads: {stale_reads}")

    assert node_b.read(key) == value and node_c.read(key) == value
    print(
        f"Stale-read window was {replication_delay_ticks} ticks: a client hitting a peer "
        f"cache node during that window would have seen a cache miss or an old price."
    )


@dataclass
class AppServerReplica:
    name: str
    sessions: dict[str, dict] = field(default_factory=dict)

    def login(self, session_id: str, user_id: str) -> None:
        self.sessions[session_id] = {"user_id": user_id}

    def replicate_session(self, session_id: str, session_data: dict) -> None:
        self.sessions[session_id] = dict(session_data)

    def handle_request(self, session_id: str) -> str:
        session = self.sessions.get(session_id)
        if session is None:
            return "401 -- no session on this replica"
        return f"200 -- welcome back, user {session['user_id']}"


def _simulate_sticky_sessions_vs_replicated_sessions() -> None:
    replica_1 = AppServerReplica("app-replica-1")
    replica_2 = AppServerReplica("app-replica-2")
    session_id = "sess-abc123"

    replica_1.login(session_id, user_id="u-9001")
    print("Without session replication (sticky-session-dependent):")
    print(f"  request -> {replica_1.name}: {replica_1.handle_request(session_id)}")
    print(f"  request -> {replica_2.name}: {replica_2.handle_request(session_id)}")

    # Fix: replicate the session write to every app-server replica synchronously
    # (or externalize it -- see Section 4.6's discussion of both options).
    session_snapshot = replica_1.sessions[session_id]
    replica_2.replicate_session(session_id, session_snapshot)
    print("With session replication applied before the next request:")
    print(f"  request -> {replica_2.name}: {replica_2.handle_request(session_id)}")


if __name__ == "__main__":
    _simulate_async_cache_replication_stale_window()
    print()
    _simulate_sticky_sessions_vs_replicated_sessions()
