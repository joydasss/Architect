"""
Ring (Chang-Roberts) algorithm simulation.

Nodes are arranged in a logical unidirectional ring. A node that notices the
leader is unreachable sends an ELECTION message, carrying its own ID,
clockwise to its immediate successor. Each node that relays an ELECTION
message compares the carried candidate ID to its own:

- if the carried ID is greater than its own, it forwards the message
  unchanged (someone with a better claim is still in the running);
- if the carried ID is less than its own, it replaces the carried ID with
  its own before forwarding (it out-ranks the current candidate);
- if the carried ID equals its own, its own ID has traveled all the way
  around the ring - it is therefore the highest ID present and declares
  itself leader, then circulates one COORDINATOR message so every node
  learns the result.

Mirrors the sequence diagram in CH08_Leader_Election.md Section 4.3.
"""

from __future__ import annotations


class RingCluster:
    def __init__(self, node_ids_in_ring_order: list[int]) -> None:
        self.ring = list(node_ids_in_ring_order)
        self.alive = {nid: True for nid in self.ring}
        self.leader_id: int | None = None
        self.hops = 0

    def crash(self, node_id: int) -> None:
        self.alive[node_id] = False
        if self.leader_id == node_id:
            self.leader_id = None

    def _successor(self, node_id: int) -> int:
        idx = self.ring.index(node_id)
        n = len(self.ring)
        nxt = (idx + 1) % n
        while not self.alive[self.ring[nxt]]:
            nxt = (nxt + 1) % n
        return self.ring[nxt]

    def start_election(self, initiator_id: int) -> int:
        print(f"node {initiator_id} notices leader is unreachable, starts an election")
        current = initiator_id
        candidate = initiator_id

        while True:
            nxt = self._successor(current)
            self.hops += 1
            print(f"  node {current} -> node {nxt}: ELECTION(candidate={candidate})")

            if nxt == candidate:
                # The candidate's own ID has arrived back at the candidate.
                winner = candidate
                break
            if candidate < nxt:
                print(f"  node {nxt} out-ranks candidate {candidate}, "
                      f"replaces it with its own ID {nxt}")
                candidate = nxt
            current = nxt

        self.leader_id = winner
        print(f"node {winner} sees its own ID has circled the ring: it is the leader")
        self._circulate_coordinator(winner)
        return winner

    def _circulate_coordinator(self, winner_id: int) -> None:
        current = winner_id
        for _ in range(len(self.ring)):
            nxt = self._successor(current)
            self.hops += 1
            print(f"  node {current} -> node {nxt}: COORDINATOR(leader={winner_id})")
            current = nxt
            if current == winner_id:
                break


def main() -> None:
    cluster = RingCluster(node_ids_in_ring_order=[10, 30, 20, 50, 40])
    print("=== ring topology (logical order): 10 -> 30 -> 20 -> 50 -> 40 -> 10 ===")
    winner = cluster.start_election(initiator_id=10)
    assert winner == 50, "highest ID in the ring must win"
    print(f"leader is node {winner}, total hops used: {cluster.hops}\n")

    print("=== leader (node 50) crashes; node 20 notices first ===")
    cluster.crash(50)
    cluster.hops = 0
    winner = cluster.start_election(initiator_id=20)
    assert winner == 40, "next-highest surviving ID must win"
    print(f"leader is node {winner}, total hops used in this round: {cluster.hops}")


if __name__ == "__main__":
    main()
