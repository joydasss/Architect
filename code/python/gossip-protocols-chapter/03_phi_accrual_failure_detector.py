"""
Phi Accrual failure detector, implemented from scratch.

Demonstrates Section 4.5 of CH09_Gossip_Protocols.md: maintaining a sliding
window of heartbeat inter-arrival times, estimating a normal distribution
from that window, and computing a continuously-valued suspicion level (phi)
rather than a binary alive/dead decision. Contrasts a stable, low-jitter
peer against a high-jitter, WAN-like peer under the same injected silence
gap to show why a single fixed timeout cannot be simultaneously correct
for both.
"""

import math
from collections import deque


class PhiAccrualFailureDetector:
    """Adaptive failure detector based on Hayashibara et al., 2004/2008."""

    def __init__(self, window_size: int = 100, min_std_dev_ms: float = 10.0) -> None:
        self.window_size = window_size
        self.min_std_dev_ms = min_std_dev_ms
        self.inter_arrival_times: deque[float] = deque(maxlen=window_size)
        self.last_heartbeat_ms: float | None = None

    def record_heartbeat(self, timestamp_ms: float) -> None:
        if self.last_heartbeat_ms is not None:
            gap = timestamp_ms - self.last_heartbeat_ms
            self.inter_arrival_times.append(gap)
        self.last_heartbeat_ms = timestamp_ms

    def _mean_and_std_dev(self) -> tuple[float, float]:
        if not self.inter_arrival_times:
            return 0.0, self.min_std_dev_ms
        mean = sum(self.inter_arrival_times) / len(self.inter_arrival_times)
        if len(self.inter_arrival_times) < 2:
            return mean, self.min_std_dev_ms
        variance = sum((x - mean) ** 2 for x in self.inter_arrival_times) / len(self.inter_arrival_times)
        std_dev = max(math.sqrt(variance), self.min_std_dev_ms)
        return mean, std_dev

    def _cumulative_normal_tail_probability(self, elapsed_ms: float, mean: float, std_dev: float) -> float:
        """P(inter-arrival time > elapsed_ms), i.e. the upper tail of the normal CDF."""
        z = (elapsed_ms - mean) / (std_dev * math.sqrt(2))
        # Complementary error function gives the upper-tail probability directly.
        return 0.5 * math.erfc(z)

    def phi(self, now_ms: float) -> float:
        if self.last_heartbeat_ms is None:
            return 0.0
        elapsed = now_ms - self.last_heartbeat_ms
        mean, std_dev = self._mean_and_std_dev()
        tail_probability = self._cumulative_normal_tail_probability(elapsed, mean, std_dev)
        tail_probability = max(tail_probability, 1e-15)  # avoid log(0)
        return -math.log10(tail_probability)


def simulate_peer(name: str, normal_gap_ms: float, jitter_ms: float, seed: int) -> PhiAccrualFailureDetector:
    import random

    rng = random.Random(seed)
    detector = PhiAccrualFailureDetector(window_size=50)
    t = 0.0
    for _ in range(50):
        t += max(1.0, rng.gauss(normal_gap_ms, jitter_ms))
        detector.record_heartbeat(t)
    print(f"[{name}] trained on {len(detector.inter_arrival_times)} samples, "
          f"mean~={sum(detector.inter_arrival_times) / len(detector.inter_arrival_times):.1f}ms")
    return detector, t


def main() -> None:
    print("Phi Accrual vs. fixed-timeout comparison under an injected silence gap")
    print("=" * 78)

    stable_detector, stable_t = simulate_peer("stable LAN peer", normal_gap_ms=200.0, jitter_ms=15.0, seed=1)
    wan_detector, wan_t = simulate_peer("high-jitter WAN peer", normal_gap_ms=200.0, jitter_ms=90.0, seed=2)

    fixed_timeout_ms = 600.0  # a single global constant, tuned as a compromise
    phi_threshold = 8.0

    print()
    print(f"{'elapsed(ms)':>12} {'stable phi':>12} {'WAN phi':>10} {'fixed-timeout verdict':>24}")
    for elapsed in (200, 400, 600, 800, 1000, 1400, 2000):
        stable_phi = stable_detector.phi(stable_t + elapsed)
        wan_phi = wan_detector.phi(wan_t + elapsed)
        fixed_verdict = "SUSPECT/DEAD" if elapsed >= fixed_timeout_ms else "alive"
        print(f"{elapsed:>12} {stable_phi:>12.2f} {wan_phi:>10.2f} {fixed_verdict:>24}")

    print()
    print("Observation: at elapsed=600ms the fixed timeout already flags both peers as")
    print("dead, but the WAN peer's own phi is still well below threshold because its")
    print("trained distribution has wider natural variance - avoiding a false positive")
    print("a single global constant would have produced. The stable peer's phi crosses")
    print(f"the {phi_threshold} threshold much sooner, giving faster genuine-failure detection")
    print("for a peer whose normal behavior is actually tighter.")


if __name__ == "__main__":
    main()
