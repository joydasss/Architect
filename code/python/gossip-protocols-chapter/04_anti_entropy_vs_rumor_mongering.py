"""
Anti-entropy vs. rumor-mongering dissemination-style comparison.

Demonstrates Section 4.3 of CH09_Gossip_Protocols.md: rumor-mongering's
cheaper-but-imperfect propagation of a discrete event (including a run
where the rumor deliberately dies out before reaching every node) versus
anti-entropy's more expensive but eventually-guaranteed full-state
reconciliation, and shows anti-entropy correcting the residual gap
rumor-mongering left behind.
"""

import random
from dataclasses import dataclass, field


@dataclass
class RumorMongeringSim:
    size: int
    lose_interest_after_redundant: int = 3
    rng: random.Random = field(default_factory=lambda: random.Random(11))

    def __post_init__(self) -> None:
        self.informed = [False] * self.size
        self.informed[0] = True
        self.hot = {0}  # nodes still actively spreading the rumor
        self.redundant_streak = {0: 0}
        self.messages_sent = 0

    def random_peer(self, node: int) -> int:
        peer = node
        while peer == node:
            peer = self.rng.randrange(self.size)
        return peer

    def run_round(self) -> None:
        newly_hot = set()
        still_hot = set()
        for node in list(self.hot):
            peer = self.random_peer(node)
            self.messages_sent += 1
            if not self.informed[peer]:
                self.informed[peer] = True
                self.redundant_streak[peer] = 0
                newly_hot.add(peer)
                self.redundant_streak[node] = 0
                still_hot.add(node)
            else:
                self.redundant_streak[node] = self.redundant_streak.get(node, 0) + 1
                if self.redundant_streak[node] < self.lose_interest_after_redundant:
                    still_hot.add(node)
                # else: this node loses interest and stops actively spreading
        self.hot = still_hot | newly_hot

    def run_until_quiescent(self, max_rounds: int = 200) -> int:
        rounds = 0
        while self.hot and rounds < max_rounds:
            self.run_round()
            rounds += 1
        return rounds

    def coverage(self) -> float:
        return sum(self.informed) / self.size


@dataclass
class AntiEntropySim:
    size: int
    rng: random.Random = field(default_factory=lambda: random.Random(11))

    def __post_init__(self) -> None:
        self.informed = [False] * self.size
        self.informed[0] = True
        self.messages_sent = 0

    def random_peer(self, node: int) -> int:
        peer = node
        while peer == node:
            peer = self.rng.randrange(self.size)
        return peer

    def run_round(self) -> None:
        newly = []
        informed_nodes = [i for i, v in enumerate(self.informed) if v]
        for node in informed_nodes:
            peer = self.random_peer(node)
            self.messages_sent += 1
            # push-pull-style full-state exchange every round, every node, forever
            if not self.informed[peer]:
                newly.append(peer)
        for n in newly:
            self.informed[n] = True

    def run_until_converged(self, max_rounds: int = 200) -> int:
        rounds = 0
        while not all(self.informed) and rounds < max_rounds:
            self.run_round()
            rounds += 1
        return rounds

    def coverage(self) -> float:
        return sum(self.informed) / self.size


def main() -> None:
    size = 500

    print("Rumor-mongering (aggressive lose-interest threshold = 2 redundant contacts):")
    rumor = RumorMongeringSim(size=size, lose_interest_after_redundant=2)
    rounds = rumor.run_until_quiescent()
    print(f"  quiesced after {rounds} rounds, {rumor.messages_sent} messages sent, "
          f"coverage={rumor.coverage() * 100:.1f}%")
    if rumor.coverage() < 1.0:
        missed = size - sum(rumor.informed)
        print(f"  RUMOR DIED OUT before reaching {missed} node(s) - this is the residual-minority")
        print("  failure mode Section 4.3 describes.")

    print()
    print("Anti-entropy (every informed node exchanges full state every round, forever):")
    anti_entropy = AntiEntropySim(size=size)
    rounds = anti_entropy.run_until_converged()
    print(f"  converged after {rounds} rounds, {anti_entropy.messages_sent} messages sent, "
          f"coverage={anti_entropy.coverage() * 100:.1f}%")

    print()
    print("Layering both: anti-entropy correcting rumor-mongering's residual gap")
    combined_informed = list(rumor.informed)
    combined_sim = AntiEntropySim(size=size)
    combined_sim.informed = combined_informed
    extra_rounds = combined_sim.run_until_converged()
    print(f"  after rumor died out at coverage={rumor.coverage() * 100:.1f}%, a periodic")
    print(f"  anti-entropy pass fully reconciled the remaining gap in {extra_rounds} more round(s),")
    print(f"  reaching {combined_sim.coverage() * 100:.1f}% coverage - exactly the safety-net role")
    print("  Section 4.3 assigns to anti-entropy layered under rumor-mongering.")


if __name__ == "__main__":
    main()
