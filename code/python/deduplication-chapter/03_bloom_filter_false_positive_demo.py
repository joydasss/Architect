"""Bloom filter candidate check; exact membership remains authoritative."""
import math
import hashlib


class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float) -> None:
        self.bit_count = max(8, math.ceil(
            -expected_items * math.log(false_positive_rate) / math.log(2) ** 2
        ))
        self.hash_count = max(1, round(self.bit_count / expected_items * math.log(2)))
        self.bits = bytearray((self.bit_count + 7) // 8)

    def _positions(self, value: str) -> list[int]:
        digest = hashlib.blake2b(
            value.encode("utf-8"), digest_size=16, person=b"dedup-demo"
        ).digest()
        first = int.from_bytes(digest[:8], "big")
        second = int.from_bytes(digest[8:], "big") | 1
        return [(first + index * second) % self.bit_count
                for index in range(self.hash_count)]

    def add(self, value: str) -> None:
        for position in self._positions(value):
            self.bits[position // 8] |= 1 << (position % 8)

    def might_contain(self, value: str) -> bool:
        return all(self.bits[position // 8] & (1 << (position % 8))
                   for position in self._positions(value))


def main() -> None:
    exact: set[str] = set()
    bloom = BloomFilter(expected_items=100, false_positive_rate=0.05)
    for index in range(100):
        item = f"event-{index}"
        exact.add(item)
        bloom.add(item)
    assert all(bloom.might_contain(item) for item in exact)
    candidates = [f"other-{index}" for index in range(1000)]
    false_positives = [item for item in candidates
                       if bloom.might_contain(item) and item not in exact]
    for item in false_positives:
        assert item not in exact  # exact authority prevents dropping it
    print(f"Bloom positives among non-members: {len(false_positives)}/1000")
    print("Every positive requires exact verification before suppression.")


if __name__ == "__main__":
    main()