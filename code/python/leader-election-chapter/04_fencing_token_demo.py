"""
Fencing token demonstration.

Shows exactly the failure mode Section 4.5 (split-brain and fencing tokens)
warns about: a leader that experiences a long stop-the-world pause (GC pause,
suspended VM, slow disk, network partition) can have its lease/session expire
at the coordination service *while it is still running*. If nothing stops it,
that "zombie" leader wakes up believing it is still in charge and can send a
write to shared storage after a new leader has already taken over -
corrupting data with two leaders active at once (split brain).

The fix: every time a node is granted leadership, the coordination service
hands it a monotonically increasing fencing token. The node must include
that token on every write to shared storage. The storage service rejects any
write whose token is lower than (or equal to, for the same token replayed)
the highest token it has already accepted. A demoted zombie leader's stale,
lower token is rejected even though its network connection to storage is
perfectly healthy - the defense lives in the storage side, not in trying to
make the zombie process stop (which is undecidable in general, see
Section 4.5's "why you can't just tell a paused process to stop" discussion).
"""

from __future__ import annotations

from dataclasses import dataclass


class FencedStorage:
    """A shared storage service that enforces fencing tokens on every write."""

    def __init__(self) -> None:
        self.highest_token_seen = 0
        self.value: str | None = None
        self.rejected_writes: list[tuple[int, str]] = []

    def write(self, fencing_token: int, value: str, writer_name: str) -> bool:
        if fencing_token <= self.highest_token_seen:
            print(f"  [storage] REJECTED write from {writer_name} "
                  f"(token={fencing_token} <= highest_seen={self.highest_token_seen})")
            self.rejected_writes.append((fencing_token, value))
            return False
        self.highest_token_seen = fencing_token
        self.value = value
        print(f"  [storage] accepted write from {writer_name} "
              f"(token={fencing_token}): value={value!r}")
        return True


@dataclass
class CoordinationService:
    """Grants leadership with a monotonically increasing fencing token."""

    _next_token: int = 100  # start above 0 so "no token yet" is distinguishable

    def grant_leadership(self, node_name: str) -> int:
        token = self._next_token
        self._next_token += 1
        print(f"[coordination] grants leadership to {node_name} with fencing "
              f"token={token}")
        return token


def main() -> None:
    coordination = CoordinationService()
    storage = FencedStorage()

    print("=== node A becomes leader, writes normally ===")
    token_a = coordination.grant_leadership("node-A")
    storage.write(token_a, "balance=100", "node-A")

    print("\n=== node A enters a long GC/stop-the-world pause here ===")
    print("(its session/lease with the coordination service now expires)")

    print("\n=== coordination service promotes node B while A is paused ===")
    token_b = coordination.grant_leadership("node-B")
    ok = storage.write(token_b, "balance=250", "node-B")
    assert ok

    print("\n=== node A wakes up, unaware it was demoted, tries to write ===")
    zombie_write_ok = storage.write(token_a, "balance=999", "node-A (zombie)")
    assert not zombie_write_ok, "the stale token must be rejected"
    assert storage.value == "balance=250", "node B's committed value must survive intact"

    print(f"\nfinal storage value: {storage.value!r}")
    print(f"rejected zombie writes: {storage.rejected_writes}")
    print("\nwithout fencing tokens, node A's write would have silently overwritten "
          "node B's, corrupting the balance with no error visible to either leader.")


if __name__ == "__main__":
    main()
