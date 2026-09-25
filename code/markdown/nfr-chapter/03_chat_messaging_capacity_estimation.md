# Worked Example 3 — Real-Time Chat/Messaging: Traffic, Storage, and Bandwidth Estimation

Referenced from [CH02_Non_Functional_Requirements.md, Section 10](../../../07_System_Design_and_Distributed_Systems/CH02_Non_Functional_Requirements.md#10-complete-code-examples).

## Assumptions

- 50 million DAU, each holding an average of 3 concurrent open WebSocket
  connections (recapped from
  [WebSockets](../../../05_Networking_and_OS/CH17_WebSockets.md), phone +
  desktop + tablet sessions being a common real pattern) held open for an
  average session length of 30 minutes across the day.
- Each user sends an average of 40 messages/day; average message payload is
  100 bytes of text plus a per-message protocol/metadata overhead of 50
  bytes = 150 bytes.
- Each sent message is delivered to an average of 2 recipients (1:1 chat plus
  a modest share of small-group chats).
- Delivery must be **at-least-once** with client-side deduplication (recapped
  forward from the Distributed Systems subsection's future Idempotency and
  Deduplication chapters), not exactly-once at the transport layer, which
  is the pragmatic default for most chat systems rather than paying the
  latency cost of a stricter guarantee.
- Peak-to-average multiplier: 2.5x (messaging traffic follows daily human
  activity rhythms more smoothly than a viral social feed).

## Step 1 — Concurrent connection estimation (a chat-specific capacity axis)

Unlike the previous two examples, the first capacity question for a
real-time system is not QPS but **concurrent open connections**, since each
open WebSocket holds server-side memory and a file descriptor (recapped
from
[Sockets](../../../05_Networking_and_OS/CH16_Sockets.md)) for its entire
duration, independent of whether it is actively sending messages:

$$
\text{Concurrent connections (avg)} = 50{,}000{,}000 \times 3 \times \frac{30}{1440} \approx 3{,}125{,}000
$$

$$
\text{Concurrent connections (peak)} \approx 3{,}125{,}000 \times 2.5 \approx 7{,}812{,}500
$$

**Design implication**: 7.8 million concurrent connections cannot be held on
one machine — a single Linux host with careful `ulimit`/ephemeral-port
tuning (recapped from
[TCP/IP](../../../05_Networking_and_OS/CH03_TCPIP.md)) tops out in the
low millions of connections at best, and production budgets are usually far
more conservative than the theoretical ceiling. This single number is what
forces a **connection-gateway tier** — many stateful gateway nodes, each
holding a shard of total connections, decoupled from stateless message-
routing/storage services behind them — as an architectural pattern, not an
implementation detail.

## Step 2 — Traffic estimation (messages/sec)

$$
\text{Messages/day} = 50{,}000{,}000 \times 40 = 2{,}000{,}000{,}000
$$

$$
\text{Sent messages/sec (avg)} = \frac{2{,}000{,}000{,}000}{86{,}400} \approx 23{,}148 \text{ msg/sec} \qquad \text{peak} \approx 57{,}870 \text{ msg/sec}
$$

**Delivery fan-out** (average 2 recipients/message):

$$
\text{Delivery events/sec (peak)} \approx 57{,}870 \times 2 \approx 115{,}740 \text{ deliveries/sec}
$$

**Design implication**: the send-side QPS (57,870) and the delivery-side
throughput (115,740) diverge by roughly 2x here — a much gentler fan-out
than the social-feed example, because chat fan-out is bounded by
conversation-participant count (small), not follower count (potentially
huge). This contrast between Example 2 and Example 3 is itself the point:
**the fan-out multiplier is domain-specific**, and an architect must derive
it from the product's actual social graph shape rather than assuming one
system's amplification factor applies to another.

## Step 3 — Storage estimation

$$
\text{Total messages over 5 years} = 2{,}000{,}000{,}000 \times 365 \times 5 = 3.65 \times 10^{12} \text{ messages}
$$

$$
\text{Raw storage} = 3.65 \times 10^{12} \times 150 \text{ bytes} \approx 547.5 \text{ TB}
$$

Applying replication factor 3 and a 25% index/overhead factor:

$$
\text{Provisioned storage} \approx 547.5 \text{ TB} \times 3 \times 1.25 \approx 2{,}053 \text{ TB} \approx 2.05 \text{ PB}
$$

**Design implication**: at 2+ PB, this dataset is squarely in
horizontally-partitioned territory (recapped from
[Partitioning](../../../06_Databases_and_Storage/CH05_Partitioning.md) and
[Sharding](../../../06_Databases_and_Storage/CH06_Sharding.md)) — the
natural partition key is conversation ID, since nearly all reads/writes are
scoped to a single conversation's message history, giving good locality
without cross-shard fan-out on the hot read/write path.

## Step 4 — Bandwidth estimation

Two very different bandwidth costs exist in a chat system: the message
payload bytes themselves, and the **connection-keepalive overhead** of
millions of idle-but-open WebSockets:

$$
\text{Message bandwidth (peak)} = 115{,}740 \times 150 \text{ bytes} \approx 17.4 \text{ MB/s} \approx 139 \text{ Mbps}
$$

Assuming a lightweight ping/pong keepalive frame of 20 bytes every 30
seconds per connection:

$$
\text{Keepalive bandwidth} = \frac{7{,}812{,}500 \times 20 \text{ bytes}}{30 \text{ sec}} \approx 5.2 \text{ MB/s} \approx 42 \text{ Mbps}
$$

**Design implication**: keepalive overhead (42 Mbps) is almost a third of
actual message bandwidth (139 Mbps) purely from holding connections open —
a detail a naive "just count message bytes" estimate misses, and a concrete
reason connection-gateway capacity planning must budget for idle-connection
cost, not only active-traffic cost.

## Summary table

| Dimension | Average | Peak | Constraint? |
|---|---|---|---|
| Concurrent connections | 3,125,000 | 7,812,500 | **Yes — forces gateway-tier sharding** |
| Send QPS | 23,148 | 57,870 | No |
| Delivery throughput | — | 115,740/sec | Moderate |
| Storage (5yr, replicated) | — | ~2.05 PB | **Yes — forces conversation-ID partitioning** |
| Message bandwidth | — | ~139 Mbps | No |
| Keepalive bandwidth | — | ~42 Mbps | Non-trivial, budget explicitly |

This example's distinct lesson versus Examples 1 and 2: for a persistent-
connection system, **concurrent connection count is its own first-class
capacity dimension**, separate from and not derivable purely from QPS.
