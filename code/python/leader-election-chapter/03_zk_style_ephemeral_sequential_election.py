"""
ZooKeeper-style ephemeral sequential znode election simulator.

Models the well-known Apache ZooKeeper election recipe without requiring a
live ZooKeeper ensemble:

1. Every candidate creates an ephemeral, sequential child znode under a
   shared election path (e.g. "/election/guid-0000000042").
2. A candidate lists the children, sorts them by their sequence suffix, and
   checks whether its own znode has the lowest sequence number.
   - If yes, it IS the leader.
   - If no, it sets a watch on the znode with the next-lowest sequence number
     (its immediate predecessor) - NOT on every other znode. Watching only
     the predecessor avoids the "herd effect," where every follower would
     otherwise be woken up and re-check on every single leader change.
3. Because the znode is ephemeral, a session timeout (crash, GC pause, or
   network partition long enough to expire the session) causes ZooKeeper
   itself to delete that node, which fires exactly one watch: the
   predecessor's. That candidate re-checks the (now shorter) children list
   and either becomes leader or watches its own new predecessor.

This module simulates the ensemble's child list and watch delivery in
memory; it does not implement ZooKeeper's Zab replication protocol itself
(that mechanism is recapped, not re-taught, in CH08_Leader_Election.md
Section 4.4 - Zab/consensus internals are out of scope for this simulator).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FakeZkEnsemble:
    """A minimal in-memory stand-in for the ZooKeeper election subtree."""

    _next_seq: int = 1
    _children: dict[str, int] = field(default_factory=dict)  # node_name -> seq
    _watch_callbacks: dict[str, list] = field(default_factory=dict)

    def create_ephemeral_sequential(self, prefix: str) -> str:
        seq = self._next_seq
        self._next_seq += 1
        node_name = f"{prefix}-{seq:010d}"
        self._children[node_name] = seq
        return node_name

    def get_sorted_children(self) -> list[str]:
        return sorted(self._children, key=lambda name: self._children[name])

    def watch_predecessor(self, node_name: str, callback) -> str | None:
        children = self.get_sorted_children()
        idx = children.index(node_name)
        if idx == 0:
            return None
        predecessor = children[idx - 1]
        self._watch_callbacks.setdefault(predecessor, []).append(callback)
        return predecessor

    def session_expire(self, node_name: str) -> None:
        """Simulates a crash/GC-pause long enough to expire the ephemeral node."""
        print(f"  [ensemble] session for {node_name} expires; node deleted")
        del self._children[node_name]
        callbacks = self._watch_callbacks.pop(node_name, [])
        for cb in callbacks:
            cb()


class Candidate:
    def __init__(self, name: str, ensemble: FakeZkEnsemble) -> None:
        self.name = name
        self.ensemble = ensemble
        self.node_name: str | None = None
        self.is_leader = False

    def join_election(self) -> None:
        self.node_name = self.ensemble.create_ephemeral_sequential(
            f"/election/{self.name}"
        )
        print(f"{self.name} creates ephemeral sequential znode {self.node_name}")
        self._check_or_watch()

    def _check_or_watch(self) -> None:
        children = self.ensemble.get_sorted_children()
        if children[0] == self.node_name:
            self.is_leader = True
            print(f"{self.name} sees its znode {self.node_name} is lowest-sequence "
                  f"-> becomes leader")
            return
        predecessor = self.ensemble.watch_predecessor(
            self.node_name, self._on_predecessor_deleted
        )
        print(f"{self.name} is not lowest-sequence; watches predecessor "
              f"{predecessor}")

    def _on_predecessor_deleted(self) -> None:
        print(f"{self.name} received a watch notification: predecessor is gone")
        self._check_or_watch()


def main() -> None:
    ensemble = FakeZkEnsemble()
    candidates = [Candidate(name, ensemble) for name in ("app-1", "app-2", "app-3", "app-4")]

    print("=== all 4 candidates join the election in order ===")
    for c in candidates:
        c.join_election()

    leader = next(c for c in candidates if c.is_leader)
    assert leader.name == "app-1", "the first-created ephemeral znode wins the initial election"
    print(f"current leader: {leader.name}\n")

    print("=== leader crashes; ZooKeeper expires its ephemeral znode ===")
    leader.is_leader = False  # the crashed process itself no longer holds leadership
    ensemble.session_expire(leader.node_name)  # type: ignore[arg-type]
    new_leader = next(c for c in candidates if c.is_leader)
    assert new_leader.name == "app-2", (
        "only app-2 was watching app-1's node (its direct predecessor); "
        "it is promoted without app-3/app-4 being woken up at all"
    )
    print(f"new leader: {new_leader.name}")
    print("note: app-3 and app-4 received ZERO notifications for this failover - "
          "each candidate only ever watches its own immediate predecessor")


if __name__ == "__main__":
    main()
