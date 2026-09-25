# Worked Example: Replication and Consistency-Level Configuration Worksheet

Companion artifact for
[07_System_Design_and_Distributed_Systems/CH06_PACELC.md](../../../07_System_Design_and_Distributed_Systems/CH06_PACELC.md),
Section 10. Use this worksheet to translate a target PACELC quadrant
(Section 4.3 of the chapter) into the concrete configuration values that
realize it on four real products, following Section 4.4's knob-mapping
methodology.

## Step 1 — Classify the workload

Answer these two questions for the data entity being configured:

1. **If the network partitions, should this data keep accepting
   writes/reads (Availability), or refuse them until connectivity is
   restored (Consistency)?**
2. **On a normal day with no partition, is it acceptable for a read to be
   milliseconds-to-seconds stale in exchange for lower latency (Latency),
   or must every read reflect the most recent acknowledged write
   (Consistency)?**

Record the answer as a target quadrant, e.g. `PC/EC` for a payments ledger,
`PA/EL` for a social-feed "like count."

## Step 2 — PostgreSQL / MySQL (streaming replication)

| Target quadrant | `synchronous_commit` (or equivalent) | Standby/quorum config | Failover fencing |
|---|---|---|---|
| PA/EL | `off` or `local` (async replication) | No synchronous standby required | Not applicable — replicas can lag freely |
| PC/EC | `remote_apply` (strongest) or `on`/`remote_write` | `synchronous_standby_names` naming required standby/standbys | Mandatory: STONITH/fencing token on any automated failover, per [Replication](../../../06_Databases_and_Storage/CH07_Replication.md) Section 4.8 |
| PA/EC (usually accidental — flag for review) | `remote_apply`/`on` | Synchronous standby configured | Automatic promotion **without** fencing — this is the accidental drift pattern [CH06_PACELC.md](../../../07_System_Design_and_Distributed_Systems/CH06_PACELC.md) Section 15 warns about; do not configure this deliberately |
| PC/EL | Not directly expressible in vanilla streaming replication without an application-level read-your-writes token; typically requires routing reads through a session-token/sticky-routing layer on top of async replicas | `synchronous_standby_names` unset, but read layer enforces a minimum-applied-LSN check per client session | Mandatory fencing on the write path |

## Step 3 — Apache Cassandra (per-query consistency level)

| Target quadrant | Write consistency level | Read consistency level | `W + R > N` check (N=3 example) |
|---|---|---|---|
| PA/EL | `ONE` or `LOCAL_ONE` | `ONE` or `LOCAL_ONE` | `W=1, R=1`, `1+1=2 <= 3` — **no** read-after-write guarantee, by design |
| PC/EC | `QUORUM` or `EACH_QUORUM` (multi-DC) | `QUORUM` | `W=2, R=2`, `2+2=4 > 3` — guarantee holds |
| PC/EL | `QUORUM` write, `ONE`/`LOCAL_ONE` read | `W=2, R=1`, `2+1=3`, not `>N` — this is a deliberate, *documented* relaxation for read latency, not a mistake, provided the workload's staleness tolerance has been explicitly reviewed | — |

> Always re-run the `W + R > N` check whenever either value changes — this
> is the single most common configuration mistake described in
> [CH06_PACELC.md](../../../07_System_Design_and_Distributed_Systems/CH06_PACELC.md)
> Section 4.4 and Section 15.

## Step 4 — Amazon DynamoDB

| Target quadrant | Write path | `ConsistentRead` flag | Notes |
|---|---|---|---|
| PA/EL | Standard `PutItem`/managed replication | `false` (default) | Lowest cost, lowest latency, eventual-consistency window typically well under 1 second |
| PC/EC-adjacent | `TransactWriteItems` for atomicity where needed | `true` | DynamoDB's strongly-consistent reads are same-region only; this does not achieve Spanner-style global external consistency, only single-region strong consistency — document this limitation explicitly if the workload is multi-region |

## Step 5 — MongoDB (replica set)

| Target quadrant | `writeConcern` | `readPreference` / `readConcern` |
|---|---|---|
| PA/EL-adjacent | `w:1` | `readPreference: nearest`, `readConcern: local` |
| PC/EC | `w:"majority"` | `readPreference: primary`, `readConcern: majority` (or `linearizable` for the strictest guarantee) |
| PC/EL | `w:"majority"` (durability preserved) | `readPreference: secondaryPreferred`, `readConcern: local` (reads may lag the majority-committed point) |

## Step 6 — Document the decision

For each entity/table configured, record in the accompanying Architecture
Decision Record (ADR template recapped, fully owned by
[Architecture Thinking](../../../01_Architecture_Mindset/CH03_Architecture_Thinking.md)
Section 10):

- The target PACELC quadrant and the business reason for it.
- The exact configuration values from the tables above.
- The verification performed (quorum-arithmetic check, measured staleness
  window, measured P99 latency).
- The monitoring signal that will detect if the configuration silently
  drifts from its intended guarantee (Section 14 of the chapter).
