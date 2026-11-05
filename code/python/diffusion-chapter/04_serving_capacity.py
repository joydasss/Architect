"""Serving capacity arithmetic for an image-generation feature (standard library only).

All inputs are illustrative assumptions, stated in the constants below. Replace them with
measurements from your own hardware, model, and traffic.

Run: python 04_serving_capacity.py
"""

import math

# --- assumptions (illustrative) -------------------------------------------------
STEPS = 25
CFG_FACTOR = 2            # conditional + unconditional pass per step
CALL_MS_BATCH1 = 45.0     # denoiser call, batch 1
CALL_MS_BATCH4 = 120.0    # denoiser call, batch 4 (sub-linear)
CALL_MS_BATCH8 = 220.0    # denoiser call, batch 8
TEXT_ENC_MS = 20.0        # text encoder per prompt
VAE_DECODE_MS = 60.0      # per image
SAFETY_MS = 25.0          # output classifier per image
GPU_HOURLY_USD = 2.50     # assumed on-demand price per GPU-hour
PEAK_RPS = 6.0            # assumed peak requests per second
TARGET_UTIL = 0.6         # keep queues stable


def per_image_seconds(call_ms, batch):
    denoise = STEPS * CFG_FACTOR * call_ms / 1000.0 / batch
    fixed = (TEXT_ENC_MS + VAE_DECODE_MS + SAFETY_MS) / 1000.0
    return denoise + fixed


def main():
    print("Per-image GPU time (amortised over the batch)")
    results = {}
    for batch, call_ms in ((1, CALL_MS_BATCH1), (4, CALL_MS_BATCH4), (8, CALL_MS_BATCH8)):
        s = per_image_seconds(call_ms, batch)
        batch_latency = STEPS * CFG_FACTOR * call_ms / 1000.0 + batch * (VAE_DECODE_MS + SAFETY_MS) / 1000.0 + TEXT_ENC_MS / 1000.0
        results[batch] = (s, batch_latency)
        print(f"batch {batch}: {s:.3f} s/image of GPU time, {1/s:.2f} images/s/GPU, "
              f"request latency about {batch_latency:.2f} s once the batch runs")

    print("\nGPUs needed at peak", PEAK_RPS, "requests/s, target utilisation", TARGET_UTIL)
    for batch in (1, 4, 8):
        s, _ = results[batch]
        gpus = PEAK_RPS * s / TARGET_UTIL
        print(f"batch {batch}: {gpus:.2f} -> {math.ceil(gpus)} GPUs")

    print("\nCost per 1000 images at GPU price", GPU_HOURLY_USD, "USD/hour, 100% busy")
    for batch in (1, 4, 8):
        s, _ = results[batch]
        print(f"batch {batch}: {1000 * s / 3600 * GPU_HOURLY_USD:.3f} USD")

    s4, _ = results[4]
    print("\nAt 60% utilisation batch 4 costs", f"{1000 * s4 / 3600 * GPU_HOURLY_USD / TARGET_UTIL:.3f}", "USD per 1000 images")

    # Little's law: concurrent in-flight requests = arrival rate x time in system
    lat = results[4][1] + 0.5  # add 0.5 s queue wait for batch formation
    print(f"Little's law: in flight = {PEAK_RPS} x {lat:.2f} = {PEAK_RPS * lat:.1f} requests")

    # Text embedding cache: encoder cost saved
    hit = 0.35
    saved = hit * TEXT_ENC_MS
    print(f"\nText embedding cache hit rate {hit:.0%}: saves {saved:.1f} ms of encoder time per request on average")

    # Memory: weights in fp16
    for name, params in (("U-Net 0.86B", 0.86e9), ("DiT 2B", 2.0e9), ("DiT 8B", 8.0e9)):
        print(f"{name}: fp16 weights {params * 2 / 2**30:.2f} GiB")


if __name__ == "__main__":
    main()
