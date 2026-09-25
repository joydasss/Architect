# Worked Example 2 — Twitter-like Feed: Traffic, Storage, and Bandwidth Estimation

Referenced from [CH02_Non_Functional_Requirements.md, Section 10](../../../07_System_Design_and_Distributed_Systems/CH02_Non_Functional_Requirements.md#10-complete-code-examples).

## Assumptions

- 300 million Daily Active Users (DAU).
- Each active user posts an average of 2 posts/day; average post is 280
  characters of text plus a 20% chance of an attached image averaging 200 KB.
- Each active user views their timeline an average of 10 times/day, and each
  timeline view fetches 20 posts.
- Fan-out-on-write is used for the timeline (recapped forward from the
  Distributed Systems subsection's future CQRS chapter — precomputing each
  follower's feed at write time rather than joining at read time), except
  for celebrity accounts (over 1 million followers) which fall back to
  fan-out-on-read to avoid a single post fanning out to millions of feeds
  synchronously.
- Peak-to-average multiplier: 4x (social platforms have sharper peaks than a
  utility-style API tied to a business calendar).

## Step 1 — Traffic estimation (QPS)

**Write path (post creation):**

$$
\text{Posts/day} = 300{,}000{,}000 \times 2 = 600{,}000{,}000
$$

$$
\text{Posts/sec (avg)} = \frac{600{,}000{,}000}{86{,}400} \approx 6{,}944 \text{ QPS} \qquad \text{peak} \approx 27{,}776 \text{ QPS}
$$

**Read path (timeline views):**

$$
\text{Timeline reads/day} = 300{,}000{,}000 \times 10 = 3{,}000{,}000{,}000
$$

$$
\text{Reads/sec (avg)} = \frac{3{,}000{,}000{,}000}{86{,}400} \approx 34{,}722 \text{ QPS} \qquad \text{peak} \approx 138{,}888 \text{ QPS}
$$

**Fan-out write amplification**: assume an average of 200 followers per
post (median is far lower, but a small population of high-follower accounts
skews the mean — this asymmetry is precisely why celebrity accounts get a
separate fan-out-on-read path):

$$
\text{Feed-write operations/sec (avg)} \approx 6{,}944 \times 200 \approx 1{,}388{,}800 \text{ ops/sec}
$$

**Design implication**: the raw "posts/sec" number (6,944) dramatically
understates the actual write load once fan-out is modeled — the real write
amplification (1.39 million feed-insert operations/sec) is two orders of
magnitude higher and is the number that should size the feed-fan-out
pipeline's throughput, not the naive post-count. This is the single most
common capacity-estimation mistake in a "design Twitter" interview: stopping
at the post-creation QPS and never modeling fan-out amplification.

## Step 2 — Storage estimation

**Text storage** (5-year retention):

$$
280 \text{ bytes} \times 600{,}000{,}000/\text{day} \times 365 \times 5 \approx 306.6 \text{ TB}
$$

**Image storage** (20% of posts):

$$
0.20 \times 600{,}000{,}000/\text{day} \times 365 \times 5 \times 200{,}000 \text{ bytes} \approx 43{,}800 \text{ TB} \approx 43.8 \text{ PB}
$$

**Design implication**: media dominates storage by roughly two orders of
magnitude over text — this single result is why every large-scale social
platform routes media to Blob/object storage with its own tiering and
Content Delivery Network (CDN) distribution (recapped from
[CDN](../../../05_Networking_and_OS/CH09_CDN.md)) rather than storing images
inline in the same database as post text. Text metadata belongs in a
low-latency operational store; media belongs in cheap, durable, CDN-fronted
object storage. Getting this split wrong (storing images in the primary
relational/NoSQL store) is a common anti-pattern this chapter's Section 17
calls out.

## Step 3 — Bandwidth estimation

Assume an average timeline-view response (20 posts, mostly text, occasional
thumbnail references rather than full images) is 15 KB:

$$
\text{Read bandwidth (peak)} = 138{,}888 \times 15{,}000 \text{ bytes} \approx 2.08 \text{ GB/s} \approx 16.6 \text{ Gbps}
$$

**Design implication**: 16.6 Gbps of peak read egress cannot be served from
a single instance or even a single availability zone — this number alone
justifies horizontal scaling across many stateless application-server
replicas behind a load balancer (recapped from
[Load Balancer](../../../05_Networking_and_OS/CH10_Load_Balancer.md)) and,
for the actual image bytes, offloading almost entirely to a CDN edge so the
origin fleet only ever serves cache misses.

## Summary table

| Dimension | Average | Peak (4x) | Constraint? |
|---|---|---|---|
| Post-creation QPS | 6,944 | 27,776 | No (misleadingly low alone) |
| Feed-fan-out ops/sec | 1,388,800 | ~5.5M | **Yes — write-amplification bottleneck** |
| Timeline-read QPS | 34,722 | 138,888 | **Yes — read-fleet sizing driver** |
| Text storage (5yr) | — | ~307 TB | No |
| Media storage (5yr) | — | ~43.8 PB | **Yes — dominant storage cost, drives object-storage/CDN decision** |
| Read bandwidth | — | ~16.6 Gbps | Yes — drives CDN offload decision |

The lesson this example teaches beyond Example 1: a system frequently has
**more than one** bottleneck dimension, and the fan-out multiplier is often
the hidden one that a shallow "requests per second" estimate misses
entirely.
