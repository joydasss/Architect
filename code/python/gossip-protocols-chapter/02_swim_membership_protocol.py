"""
SWIM (Scalable Weakly-consistent Infection-style Process group Membership)
protocol simulator.

Demonstrates Section 4.4 of CH09_Gossip_Protocols.md: direct probing,
indirect probing via helper peers, the SUSPECT intermediate state, and
refutation, including a scenario where a single congested network path
would produce a false positive under naive direct-only probing but is
correctly resolved by indirect probing.
"""

import random
from dataclasses import dataclass, field
from enum import Enum


class Status(Enum):
    ALIVE = "ALIVE"
    SUSPECT = "SUSPECT"
    CONFIRMED_DEAD = "CONFIRMED_DEAD"


@dataclass
class Link:
    """A directed network path between two nodes; may be congested/down."""
    reachable: bool = True


@dataclass
class SwimCluster:
    node_count: int
    indirect_helpers: int = 3
    rng: random.Random = field(default_factory=lambda: random.Random(7))

    def __post_init__(self) -> None:
        self.status = {i: Status.ALIVE for i in range(self.node_count)}
        # links[(a, b)] = whether a direct PING from a can reach b
        self.links: dict[tuple[int, int], Link] = {}
        for a in range(self.node_count):
            for b in range(self.node_count):
                if a != b:
                    self.links[(a, b)] = Link(reachable=True)

    def set_link(self, a: int, b: int, reachable: bool) -> None:
        self.links[(a, b)].reachable = reachable

    def direct_ping(self, prober: int, target: int) -> bool:
        return self.links[(prober, target)].reachable

    def indirect_ping(self, prober: int, target: int) -> bool:
        """Ask k random helper peers to probe target on prober's behalf."""
        candidates = [n for n in range(self.node_count) if n not in (prober, target)]
        helpers = self.rng.sample(candidates, min(self.indirect_helpers, len(candidates)))
        for helper in helpers:
            if self.links[(helper, target)].reachable:
                print(f"    indirect probe via node {helper} -> node {target}: ACK (target reachable)")
                return True
            print(f"    indirect probe via node {helper} -> node {target}: no ACK")
        return False

    def probe_cycle(self, prober: int, target: int) -> None:
        print(f"Node {prober} probing node {target} (direct)...")
        if self.direct_ping(prober, target):
            print(f"  direct ACK received - node {target} confirmed ALIVE")
            self.status[target] = Status.ALIVE
            return

        print(f"  no direct ACK from node {target}; falling back to indirect probing")
        if self.indirect_ping(prober, target):
            print(f"  indirect ACK received - node {target} is ALIVE (path {prober}->{target} was congested)")
            self.status[target] = Status.ALIVE
            return

        print(f"  no direct or indirect ACK - marking node {target} as SUSPECT")
        self.status[target] = Status.SUSPECT

    def attempt_refutation(self, target: int, refuting_prober: int) -> bool:
        """A different node tries to directly reach the SUSPECT node."""
        if self.direct_ping(refuting_prober, target):
            print(f"  refutation: node {refuting_prober} got a direct ACK from node {target} - status reverts to ALIVE")
            self.status[target] = Status.ALIVE
            return True
        return False

    def confirm_dead(self, target: int) -> None:
        if self.status[target] is Status.SUSPECT:
            print(f"  no refutation arrived before timeout - node {target} is CONFIRMED_DEAD")
            self.status[target] = Status.CONFIRMED_DEAD


def scenario_congested_path_not_dead() -> None:
    print("=" * 70)
    print("Scenario 1: congested direct path, target actually alive")
    print("=" * 70)
    cluster = SwimCluster(node_count=6)
    # Node 0's direct path to node 3 is congested, but node 3 is otherwise fine.
    cluster.set_link(0, 3, reachable=False)
    cluster.probe_cycle(prober=0, target=3)
    final = cluster.status[3]
    print(f"Final status of node 3: {final.value}")
    assert final is Status.ALIVE, "indirect probing should have prevented a false SUSPECT"
    print("PASS: indirect probing correctly avoided a false positive.\n")


def scenario_genuine_failure() -> None:
    print("=" * 70)
    print("Scenario 2: node genuinely unreachable on every path")
    print("=" * 70)
    cluster = SwimCluster(node_count=6)
    target = 5
    for other in range(6):
        if other != target:
            cluster.set_link(other, target, reachable=False)
    cluster.probe_cycle(prober=0, target=target)
    print(f"Status after probe cycle: {cluster.status[target].value}")

    print("Attempting refutation from two other nodes before confirm-timeout...")
    refuted = False
    for candidate in (1, 2):
        if cluster.attempt_refutation(target, candidate):
            refuted = True
            break
    if not refuted:
        cluster.confirm_dead(target)

    final = cluster.status[target]
    print(f"Final status of node {target}: {final.value}")
    assert final is Status.CONFIRMED_DEAD, "a genuinely unreachable node should be confirmed dead"
    print("PASS: genuine failure correctly progressed SUSPECT -> CONFIRMED_DEAD.\n")


def main() -> None:
    scenario_congested_path_not_dead()
    scenario_genuine_failure()


if __name__ == "__main__":
    main()
