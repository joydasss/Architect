# Worked Example 1 — URL Shortener: Traffic, Storage, and Bandwidth Estimation

Referenced from [CH02_Non_Functional_Requirements.md, Section 10](../../../07_System_Design_and_Distributed_Systems/CH02_Non_Functional_Requirements.md#10-complete-code-examples).

## Assumptions (stated explicitly, as an interview would require)

- 500 million new short links created per month.
- Read:write ratio of 100:1 (short links are looked up far more often than
  created — every read is a redirect).
- Each stored record: short code (7 bytes), long URL (average 100 bytes),
  metadata (creator ID, timestamp, click counter — approximately 43 bytes) =
  **150 bytes/record**.
- Data must be retained for 5 years before any archival/expiry policy.
- Traffic is not uniform across the day: peak traffic runs at **3x** the
  daily average (a common architect's rule of thumb absent real telemetry).

## Step 1 — Traffic estimation (QPS)

$$
\text{Writes/sec (avg)} = \frac{500{,}000{,}000}{30 \times 24 \times 3600} \approx 193 \text{ writes/sec}
$$

$$
\text{Reads/sec (avg)} = 193 \times 100 = 19{,}300 \text{ reads/sec}
$$

Applying the peak-to-average multiplier (3x):

$$
\text{Writes/sec (peak)} \approx 579 \text{ QPS} \qquad \text{Reads/sec (peak)} \approx 57{,}900 \text{ QPS}
$$

**Design implication**: the read path dominates by two orders of magnitude —
this is a read-heavy system, so the design should prioritize a cache in front
of the datastore (recapped from
[Caching](../../../06_Databases_and_Storage/CH09_Caching.md)) and a
read-optimized index on the short code, not write-path optimization. The 3x
peak multiplier is the number that actually sizes the fleet — provisioning
for the *average* would mean the system falls over during every traffic
spike, which is precisely the gap between average-case napkin math and a
usable capacity plan.

## Step 2 — Storage estimation

$$
\text{Total records over 5 years} = 500{,}000{,}000 \times 12 \times 5 = 30{,}000{,}000{,}000 \text{ records}
$$

$$
\text{Raw storage} = 30 \times 10^9 \times 150 \text{ bytes} = 4.5 \times 10^{12} \text{ bytes} = 4.5 \text{ TB}
$$

Applying a replication factor of 3 (for durability and read scaling, recapped
from
[Replication](../../../06_Databases_and_Storage/CH07_Replication.md)) and a
conservative 30% index/overhead factor:

$$
\text{Provisioned storage} \approx 4.5 \text{ TB} \times 3 \times 1.3 \approx 17.6 \text{ TB}
$$

**Design implication**: 17.6 TB fits comfortably on a handful of modern SSD-
backed nodes — this system is not storage-bound. The interesting capacity
question is not "how much disk" but "how much of the working set (the most
recently/frequently accessed short codes) fits in a cache tier," since that
determines cache-hit ratio and therefore the real read latency the majority
of users experience.

## Step 3 — Bandwidth estimation

Assume an average HTTP redirect response is 500 bytes (headers plus a small
body) and an average creation request/response pair is 1 KB.

$$
\text{Read bandwidth (peak)} = 57{,}900 \times 500 \text{ bytes} \approx 28.95 \text{ MB/s} \approx 232 \text{ Mbps}
$$

$$
\text{Write bandwidth (peak)} = 579 \times 1000 \text{ bytes} \approx 0.58 \text{ MB/s} \approx 4.6 \text{ Mbps}
$$

**Design implication**: total peak egress of roughly 237 Mbps is trivial for
a single modern network interface, let alone a load-balanced fleet — network
bandwidth is not the constraint for this system. The binding constraint,
worked out above, is read QPS against the datastore/cache tier, which drives
the number of application-server and cache instances needed, not the raw
byte count.

## Summary table

| Dimension | Average | Peak (3x) | Constraint? |
|---|---|---|---|
| Write QPS | 193 | 579 | No |
| Read QPS | 19,300 | 57,900 | **Yes — dominant scaling driver** |
| Storage (5yr, replicated) | — | 17.6 TB | No |
| Bandwidth | — | ~237 Mbps | No |

This is the pattern a back-of-the-envelope estimate should produce: not just
numbers, but an identified **bottleneck dimension** that tells the architect
where to spend design effort (see
[CH02_Non_Functional_Requirements.md, Section 4.9](../../../07_System_Design_and_Distributed_Systems/CH02_Non_Functional_Requirements.md#49-back-of-the-envelope-capacity-estimation)).
