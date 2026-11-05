"""Video token explosion, short-event recall, and storage/bandwidth planning.

Standard library only. Token counts per frame and prices are ILLUSTRATIVE.
"""
import math
import random

random.seed(3)

PRICE_PER_MTOK = 3.00


def video_tokens(seconds, fps, tokens_per_frame, merge=1):
    frames = math.floor(seconds * fps)
    return frames, frames * tokens_per_frame // merge


def miss_probability(event_s, interval_s):
    """Chance a uniformly placed event of length event_s contains no sample."""
    return max(0.0, 1 - event_s / interval_s)


def simulate_miss(event_s, interval_s, trials=100_000):
    miss = 0
    for _ in range(trials):
        start = random.uniform(0, interval_s)  # offset relative to sample grid
        # samples at 0, interval, 2*interval...
        nxt = math.ceil(start / interval_s) * interval_s
        if nxt > start + event_s:
            miss += 1
    return miss / trials


if __name__ == "__main__":
    print("== Token explosion, 256 tokens per frame ==")
    for secs, fps in [(30, 30), (30, 1), (600, 1), (3600, 1), (3600, 0.2)]:
        fr, tok = video_tokens(secs, fps, 256)
        print(f"{secs:>5}s @ {fps:>4} fps -> {fr:>6} frames, {tok:>9,} tokens, "
              f"${tok * PRICE_PER_MTOK / 1e6:>7.2f}")

    print("\n== Probability a 0.5 s event is missed ==")
    for interval in [0.25, 0.5, 1, 2, 5]:
        print(f"sample every {interval:>4}s -> analytic {miss_probability(0.5, interval):.2f}, "
              f"simulated {simulate_miss(0.5, interval):.2f}")

    print("\n== Storage and bandwidth for 10,000 calls/day ==")
    calls, minutes = 10_000, 6
    pcm_mb = 16_000 * 2 * minutes * 60 / 1e6
    opus_mb = 24_000 / 8 * minutes * 60 / 1e6
    print(f"raw PCM 16k mono per call: {pcm_mb:.1f} MB; day: {pcm_mb * calls / 1000:.0f} GB")
    print(f"Opus 24 kbps per call   : {opus_mb:.2f} MB; day: {opus_mb * calls / 1000:.1f} GB; "
          f"90 days: {opus_mb * calls * 90 / 1e6:.2f} TB")
    video_mb = 2_000_000 / 8 * minutes * 60 / 1e6
    print(f"video 2 Mbps per call   : {video_mb:.0f} MB; day: {video_mb * calls / 1000:.0f} GB")
    print(f"upstream for 500 concurrent 2 Mbps streams: {500 * 2} Mbps")
