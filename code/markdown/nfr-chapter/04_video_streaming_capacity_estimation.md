# Worked Example 4 — Video Streaming Platform: Traffic, Storage, and Bandwidth Estimation

Referenced from [CH02_Non_Functional_Requirements.md, Section 10](../../../07_System_Design_and_Distributed_Systems/CH02_Non_Functional_Requirements.md#10-complete-code-examples).

## Assumptions

- 20 million DAU; each watches an average of 40 minutes/day of video.
- Adaptive bitrate streaming (recapped forward, this is a delivery-protocol
  detail owned by a future dedicated streaming/media-delivery treatment, not
  this chapter) serves an average effective bitrate of 3 Mbps per stream
  once mid-tier and high-tier device mixes are blended.
- 500,000 new hours of video are uploaded per day across all creators; each
  uploaded minute is transcoded into 5 renditions (240p/480p/720p/1080p/4K)
  averaging a combined 40 MB/minute of stored output across all renditions.
- Over 95% of playback bandwidth is served from CDN edge caches, not the
  origin (recapped from [CDN](../../../05_Networking_and_OS/CH09_CDN.md));
  this example estimates total delivered bandwidth regardless of which tier
  serves it, since that total is what the CDN contract/cost model is sized
  against.
- Peak-to-average multiplier: 2x (evening-hours viewing concentration is
  real but smoother than a spiky social-feed pattern).

## Step 1 — Bandwidth estimation (the dominant dimension for streaming)

$$
\text{Total watch-minutes/day} = 20{,}000{,}000 \times 40 = 800{,}000{,}000 \text{ minutes}
$$

$$
\text{Concurrent average streams} = \frac{800{,}000{,}000 \text{ min}}{1440 \text{ min/day}} \approx 555{,}556
$$

$$
\text{Concurrent peak streams} \approx 555{,}556 \times 2 \approx 1{,}111{,}112
$$

$$
\text{Peak delivered bandwidth} = 1{,}111{,}112 \times 3 \text{ Mbps} \approx 3{,}333{,}336 \text{ Mbps} \approx 3.33 \text{ Tbps}
$$

**Design implication**: 3.33 Tbps of sustained peak egress is the headline
number that makes video streaming fundamentally a **bandwidth-bound**
problem rather than a compute- or storage-bound one — no single data center,
and typically no single CDN provider's full capacity in a region, should be
assumed sufficient without a multi-CDN or multi-provider strategy. This is
precisely why the CDN percentage assumption above (95%+ served at the edge)
is not an optimization but a load-bearing architectural requirement: at this
scale, serving even 10% of this traffic from origin would require
provisioning hundreds of Gbps of origin egress capacity that would sit
mostly idle outside peak hours.

## Step 2 — Storage estimation

$$
\text{Stored bytes/day (all renditions)} = 500{,}000 \text{ hours} \times 60 \text{ min/hr} \times 40 \text{ MB/min} = 1.2 \times 10^9 \text{ MB} = 1.2 \text{ PB/day}
$$

$$
\text{Storage growth over 5 years} \approx 1.2 \text{ PB/day} \times 365 \times 5 \approx 2{,}190 \text{ PB} \approx 2.19 \text{ EB}
$$

**Design implication**: exabyte-scale storage growth makes storage-tiering
policy (recapped from
[Partitioning's storage-tiering pattern](../../../06_Databases_and_Storage/CH05_Partitioning.md#partition-maintenancerolling-window-pattern-local-vs-global-indexes-composite-sub-partitioning-storage-tiering))
a first-order design decision, not an afterthought: most uploaded content
receives the overwhelming majority of its lifetime views within the first
days/weeks after upload, so moving cold, rarely-viewed renditions (older
long-tail content, lower-demand resolutions) to cheaper archival-class
object storage tiers is what keeps the effective cost curve from growing
linearly with the raw exabyte total.

## Step 3 — Traffic estimation (control-plane QPS, distinct from the data-plane bandwidth above)

Video streaming's request-per-second load is dominated not by the video
bytes themselves (those flow over persistent CDN-edge connections, not
discrete request/response cycles) but by metadata/control-plane calls:
starting a playback session, fetching the manifest (list of available
renditions), and periodic playback-heartbeat/analytics pings.

$$
\text{Playback-session starts/sec (peak)} \approx \frac{1{,}111{,}112 \text{ concurrent streams}}{40 \text{ min avg session} \times 60 \text{ sec/min}} \times 60 \approx 27{,}778 \text{ starts/sec}
$$

Assuming 1 heartbeat ping every 10 seconds per active stream:

$$
\text{Heartbeat QPS (peak)} = \frac{1{,}111{,}112}{10} \approx 111{,}111 \text{ QPS}
$$

**Design implication**: the control-plane load (heartbeats at ~111K QPS) is
actually the larger *request-count* number, even though it is trivial in
*bytes* compared to the video data plane — a reminder that "capacity" is not
one number but several independent axes (bandwidth, storage, and request
rate) that can each become the binding constraint for a different part of
the same system.

## Summary table

| Dimension | Average | Peak | Constraint? |
|---|---|---|---|
| Concurrent streams | 555,556 | 1,111,112 | Input to bandwidth calc |
| Delivered bandwidth | — | ~3.33 Tbps | **Yes — dominant; forces multi-CDN strategy** |
| Storage growth (5yr, all renditions) | — | ~2.19 EB | **Yes — forces storage-tiering policy** |
| Playback-session starts | — | ~27,778/sec | Moderate |
| Heartbeat/analytics QPS | — | ~111,111/sec | Yes for the control-plane fleet specifically |

This example's distinct lesson versus Examples 1-3: **bandwidth**, not
storage or request count, is the primary capacity axis for a media-delivery
system, and a competent estimate must separate the low-QPS/high-bandwidth
data plane from the high-QPS/low-bandwidth control plane, since each drives
a different part of the architecture's sizing.
