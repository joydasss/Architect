"""CH22 Time Series Databases — Example 2: from-scratch delta-of-delta
timestamp encoding and XOR-based value compression (Facebook's Gorilla
paper, 2015).

This is a teaching implementation, not a production codec: it favors
readability over bit-packing efficiency (it stores each encoded field as a
Python int with an explicit bit-width comment rather than writing to a real
bitstream), but it reproduces the exact algorithmic decisions Gorilla makes
so the compression-ratio numbers it prints are representative of the real
technique described in the chapter's Sections 4.5-4.6.

Run: python 02_delta_of_delta_gorilla_encoder.py
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Part A: delta-of-delta timestamp encoding (Section 4.5)
# ---------------------------------------------------------------------------
#
# Naive storage: each timestamp as a raw 8-byte (64-bit) integer.
# Delta encoding: store the first timestamp raw, then each subsequent value
# as (t[i] - t[i-1]) — this alone is already smaller because most series are
# sampled on a near-fixed interval, so deltas are small numbers.
# Delta-of-delta goes one step further: since the delta itself is usually
# IDENTICAL scrape-to-scrape (a 15-second-interval Prometheus target
# produces a stream of deltas that are almost always exactly 15 seconds),
# encoding the *change in delta* collapses the overwhelmingly common case
# down to a single stored value: zero.


@dataclass
class DeltaOfDeltaEncoder:
    """Encodes a strictly increasing timestamp series as delta-of-delta."""

    timestamps: list[int]

    def encode(self) -> list[tuple[int, int]]:
        """Returns a list of (value, bit_width) pairs mimicking Gorilla's
        variable-length bucketing, so the demo can report a realistic bit
        cost instead of a fixed 64 bits per point."""
        if not self.timestamps:
            return []

        encoded: list[tuple[int, int]] = []
        # First timestamp is stored raw (64 bits) — there is no prior point
        # to delta against yet.
        encoded.append((self.timestamps[0], 64))

        if len(self.timestamps) == 1:
            return encoded

        # Second timestamp is stored as a plain delta (Gorilla uses 14 bits
        # for the second point's delta) — there is no prior *delta* yet
        # either, so delta-of-delta cannot start until the third point.
        prev_delta = self.timestamps[1] - self.timestamps[0]
        encoded.append((prev_delta, 14))

        for i in range(2, len(self.timestamps)):
            delta = self.timestamps[i] - self.timestamps[i - 1]
            dod = delta - prev_delta  # the delta-of-delta value
            encoded.append((dod, _dod_bit_width(dod)))
            prev_delta = delta

        return encoded

    def decode(self, encoded: list[tuple[int, int]]) -> list[int]:
        """Reconstructs the original timestamps from encoded (value, width)
        pairs — proves the encoding is lossless."""
        if not encoded:
            return []
        timestamps = [encoded[0][0]]
        if len(encoded) == 1:
            return timestamps
        prev_delta = encoded[1][0]
        timestamps.append(timestamps[0] + prev_delta)
        for value, _width in encoded[2:]:
            delta = prev_delta + value
            timestamps.append(timestamps[-1] + delta)
            prev_delta = delta
        return timestamps


def _dod_bit_width(dod: int) -> int:
    """Gorilla's variable-length bucketing for delta-of-delta values: a
    control bit (or few) selects one of several fixed ranges, and a value
    of exactly zero (the overwhelmingly common case for a fixed-interval
    scrape) costs a single bit."""
    if dod == 0:
        return 1
    if -63 <= dod <= 64:
        return 1 + 7          # 1 control bit + 7-bit signed range
    if -255 <= dod <= 256:
        return 1 + 1 + 9      # 2 control bits + 9-bit signed range
    if -2047 <= dod <= 2048:
        return 1 + 1 + 1 + 12  # 3 control bits + 12-bit signed range
    return 1 + 1 + 1 + 1 + 32  # 4 control bits + 32-bit signed range (rare)


# ---------------------------------------------------------------------------
# Part B: XOR-based value compression (Section 4.6, the Gorilla paper)
# ---------------------------------------------------------------------------
#
# Gorilla's insight for floating-point *values* (as opposed to timestamps)
# is different: consecutive samples of most real-world metrics (CPU usage,
# temperature, request latency) tend to be numerically close, and their
# IEEE-754 bit patterns share a long common prefix and suffix of zero bits
# once XORed together. So instead of delta-of-delta arithmetic, Gorilla
# stores the XOR of each value against the previous value, then encodes how
# many leading/trailing zero bits that XOR result has, storing only the
# meaningful middle bits explicitly.


@dataclass
class XorValueEncoder:
    """Encodes a series of floats using Gorilla's XOR scheme."""

    values: list[float]
    encoded_bits: list[int] = field(default_factory=list, init=False)

    def encode(self) -> list[int]:
        if not self.values:
            return []
        bits_used: list[int] = [64]  # first value stored raw (64-bit IEEE-754)
        prev_bits = _float_to_bits(self.values[0])
        prev_leading = 64
        prev_trailing = 64

        for value in self.values[1:]:
            cur_bits = _float_to_bits(value)
            xor = prev_bits ^ cur_bits

            if xor == 0:
                # Identical to the previous value: costs a single control
                # bit ("0" meaning no change) — extremely common for a
                # metric that is flat between scrapes.
                bits_used.append(1)
            else:
                leading = _leading_zero_bits(xor)
                trailing = _trailing_zero_bits(xor)
                meaningful = 64 - leading - trailing
                if leading >= prev_leading and trailing >= prev_trailing:
                    # Reuse the previous block's leading/trailing-zero
                    # window: only the meaningful bits need to be stored,
                    # plus a control bit signaling "reuse window."
                    bits_used.append(1 + meaningful)
                else:
                    # New window: pay a one-time 5+6-bit header to describe
                    # the new leading/trailing-zero counts, then the
                    # meaningful bits themselves.
                    bits_used.append(1 + 5 + 6 + meaningful)
                    prev_leading, prev_trailing = leading, trailing

            prev_bits = cur_bits

        self.encoded_bits = bits_used
        return bits_used


def _float_to_bits(value: float) -> int:
    return struct.unpack(">Q", struct.pack(">d", value))[0]


def _leading_zero_bits(value: int, width: int = 64) -> int:
    if value == 0:
        return width
    return width - value.bit_length()


def _trailing_zero_bits(value: int, width: int = 64) -> int:
    if value == 0:
        return width
    count = 0
    while value & 1 == 0:
        value >>= 1
        count += 1
    return count


def demo() -> None:
    # A realistic 15-second-interval scrape series with one hiccup (a late
    # scrape at index 6) to show delta-of-delta handling a non-uniform gap.
    base = 1_726_000_000
    timestamps = [base + i * 15 for i in range(10)]
    timestamps[6] += 3  # simulate one late/jittery scrape

    dod = DeltaOfDeltaEncoder(timestamps)
    encoded_ts = dod.encode()
    decoded_ts = dod.decode(encoded_ts)
    assert decoded_ts == timestamps, "delta-of-delta round-trip must be lossless"

    naive_ts_bits = 64 * len(timestamps)
    dod_ts_bits = sum(width for _value, width in encoded_ts)
    print("=== Delta-of-delta timestamp compression ===")
    print(f"Points:                 {len(timestamps)}")
    print(f"Naive (64-bit each):    {naive_ts_bits} bits")
    print(f"Delta-of-delta encoded: {dod_ts_bits} bits")
    print(f"Compression ratio:      {naive_ts_bits / dod_ts_bits:.2f}x\n")

    # A CPU-usage-like series: mostly small fluctuations around a set point.
    values = [42.5, 42.6, 42.6, 42.4, 42.6, 55.1, 55.1, 55.0, 55.2, 42.7]
    xor_encoder = XorValueEncoder(values)
    encoded_values = xor_encoder.encode()

    naive_value_bits = 64 * len(values)
    xor_value_bits = sum(encoded_values)
    print("=== XOR-based value compression (Gorilla) ===")
    print(f"Points:                 {len(values)}")
    print(f"Naive (64-bit each):    {naive_value_bits} bits")
    print(f"XOR encoded:            {xor_value_bits} bits")
    print(f"Compression ratio:      {naive_value_bits / xor_value_bits:.2f}x")


if __name__ == "__main__":
    demo()
