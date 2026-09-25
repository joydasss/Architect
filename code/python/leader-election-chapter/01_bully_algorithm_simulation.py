"""
Bully algorithm simulation.

Simulates a small cluster of nodes, each with a distinct numeric ID. When a
node notices the current leader is unreachable, it starts an election by
sending ELECTION messages to every higher-ID node. Any higher node that is
alive responds with an OK and starts its own election; if a node gets no OK
back, it declares itself leader and broadcasts COORDINATOR to everyone.

This is an in-process message-passing simulation (no real sockets/threads) so
the message flow is deterministic and easy to read in the printed trace. It
intentionally mirrors the sequence diagram in CH08_Leader_Election.md Section
4.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Node:
    node_id: int
    alive: bool = True
    is_leader: bool = False


class BullyCluster:
    """A synchronous, single-process model of the Bully algorithm."""

    def __init__(self, node_ids: list[int]) -> None:
        self.nodes: dict[int, Node] = {nid: Node(nid) for nid in node_ids}
        self.leader_id: int | None = None
        self.messages_sent = 0

    def crash(self, node_id: int) -> None:
        self.nodes[node_id].alive = False
        if self.leader_id == node_id:
            print(f"[cluster] leader node {node_id} has crashed")
            self.leader_id = None
        for node in self.nodes.values():
            node.is_leader = False

    def _higher_alive_nodes(self, node_id: int) -> list[int]:
        return sorted(
            nid
            for nid, node in self.nodes.items()
            if nid > node_id and node.alive
        )

    def start_election(self, initiator_id: int, _depth: int = 0) -> int:
        """Recursively runs the Bully protocol starting at initiator_id.

        Returns the node_id that ends up declaring itself leader as a result
        of this initiator's election attempt.
        """
        indent = "  " * _depth
        print(f"{indent}node {initiator_id} starts an election")
        higher = self._higher_alive_nodes(initiator_id)

        if not higher:
            # No higher node is alive -> this node wins immediately.
            return self._declare_leader(initiator_id, indent)

        got_ok = False
        for candidate_id in higher:
            self.messages_sent += 1
            print(f"{indent}  node {initiator_id} -> node {candidate_id}: ELECTION")
            if self.nodes[candidate_id].alive:
                got_ok = True
                self.messages_sent += 1
                print(f"{indent}  node {candidate_id} -> node {initiator_id}: OK")
                # The higher node takes over the election and runs its own.
                return self.start_election(candidate_id, _depth + 1)

        if not got_ok:
            return self._declare_leader(initiator_id, indent)
        raise AssertionError("unreachable")

    def _declare_leader(self, winner_id: int, indent: str) -> int:
        self.leader_id = winner_id
        for node in self.nodes.values():
            node.is_leader = node.node_id == winner_id
        print(f"{indent}node {winner_id} declares itself leader")
        for nid, node in self.nodes.items():
            if nid != winner_id and node.alive:
                self.messages_sent += 1
                print(f"{indent}  node {winner_id} -> node {nid}: COORDINATOR")
        return winner_id


def main() -> None:
    cluster = BullyCluster(node_ids=[1, 2, 3, 4, 5])
    print("=== initial election, all nodes alive ===")
    winner = cluster.start_election(initiator_id=1)
    assert winner == 5, "highest surviving node ID must win"
    print(f"leader is node {winner}\n")

    print("=== leader (node 5) crashes; node 3 notices first ===")
    cluster.crash(5)
    winner = cluster.start_election(initiator_id=3)
    assert winner == 4, "next-highest surviving node ID must win"
    print(f"leader is node {winner}")
    print(f"total messages exchanged across both elections: {cluster.messages_sent}")


if __name__ == "__main__":
    main()
