"""
Gossip round simulator: push, pull, and push-pull dissemination.

Demonstrates Section 4.1 (exponential/logarithmic convergence) and Section 4.2
(push vs. pull vs. push-pull) of CH09_Gossip_Protocols.md by simulating
discrete gossip rounds across a configurable number of nodes and measuring
how many rounds each variant needs to reach full cluster convergence from a
single originating node.
"""

import random
from dataclasses import dataclass, field
from enum import Enum


class Variant(Enum):
    PUSH = "push"
    PULL = "pull"
    PUSH_PULL = "push_pull"


@dataclass
class GossipCluster:
    size: int
    fanout: int = 1
    rng: random.Random = field(default_factory=lambda: random.Random(42))

    def __post_init__(self) -> None:
        self.informed = [False] * self.size
        self.informed[0] = True  # node 0 originates the new information

    def random_peer(self, node: int) -> int:
        peer = node
        while peer == node:
            peer = self.rng.randrange(self.size)
        return peer

    def run_round(self, variant: Variant) -> int:
        """Runs one gossip round; returns the number of newly informed nodes."""
        newly_informed = []
        if variant is Variant.PUSH:
            # Only already-informed nodes initiate contact (they push outward).
            active_nodes = [i for i, v in enumerate(self.informed) if v]
        else:
            # PULL and PUSH_PULL: every node (informed or not) initiates contact,
            # since an uninformed node must itself reach out to discover new state.
            active_nodes = list(range(self.size))

        for node in active_nodes:
            for _ in range(self.fanout):
                peer = self.random_peer(node)
                if variant is Variant.PUSH:
                    if not self.informed[peer]:
                        newly_informed.append(peer)
                elif variant is Variant.PULL:
                    # A node pulls from a random peer; if that peer is informed
                    # and this node is not, this node becomes informed.
                    if self.informed[peer] and not self.informed[node]:
                        newly_informed.append(node)
                else:  # PUSH_PULL
                    if not self.informed[peer]:
                        newly_informed.append(peer)
                    if self.informed[peer] and not self.informed[node]:
                        newly_informed.append(node)
        for n in newly_informed:
            self.informed[n] = True
        return len(set(newly_informed))

    def converged(self) -> bool:
        return all(self.informed)


def simulate(size: int, variant: Variant, fanout: int = 1, max_rounds: int = 200) -> int:
    cluster = GossipCluster(size=size, fanout=fanout)
    rounds = 0
    while not cluster.converged() and rounds < max_rounds:
        cluster.run_round(variant)
        rounds += 1
    return rounds


def main() -> None:
    import math

    print("Gossip convergence-round comparison (push / pull / push-pull)")
    print("=" * 70)
    for size in (10, 100, 1000, 10000):
        theoretical_log2 = math.log2(size)
        row = [f"n={size:>6}", f"log2(n)~={theoretical_log2:5.1f}"]
        for variant in (Variant.PUSH, Variant.PULL, Variant.PUSH_PULL):
            rounds = simulate(size, variant)
            row.append(f"{variant.value:>10}={rounds:>4} rounds")
        print("  ".join(row))

    print()
    print("Round-by-round trace for a 32-node cluster (push-pull):")
    cluster = GossipCluster(size=32, fanout=1)
    round_no = 0
    while not cluster.converged():
        newly = cluster.run_round(Variant.PUSH_PULL)
        round_no += 1
        informed_count = sum(cluster.informed)
        print(f"  round {round_no}: +{newly} newly informed -> {informed_count}/32 total")


if __name__ == "__main__":
    main()
