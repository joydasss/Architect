# Worked Example: PACELC Quadrant Classification of Five Real Systems

Companion artifact for
[07_System_Design_and_Distributed_Systems/CH06_PACELC.md](../../../07_System_Design_and_Distributed_Systems/CH06_PACELC.md),
Section 10.

For each system below, the classification is derived by answering the two
PACELC questions independently: (1) what does the system do during a
network partition (the CAP question, recapped only — full teaching in
[CAP Theorem](../../../07_System_Design_and_Distributed_Systems/CH05_CAP_Theorem.md)),
and (2) what does the system do the rest of the time, when nothing is
wrong (the Else-branch question this chapter owns)?

## 1. Amazon DynamoDB (default: eventually consistent reads)

- **Partition-branch question:** If DynamoDB's managed replication cannot
  reach the number of storage nodes it wants for a write, does it keep
  accepting writes anyway, or refuse them?
  **Answer: Availability.** DynamoDB's underlying Dynamo-style design
  (recapped from
  [DynamoDB](../../../06_Databases_and_Storage/CH17_DynamoDB.md)) uses
  sloppy quorum and hinted handoff so that a write can still be accepted
  by an available node even if the "correct" replica set is temporarily
  unreachable, favoring continued write availability over strict
  correctness during the partition window.
- **Else-branch question:** On a normal day, with no partition, does a
  default (`ConsistentRead=false`) read wait for a majority of replicas to
  agree, or does it answer from whichever replica is fastest?
  **Answer: Latency.** The default read mode is explicitly documented as
  "eventually consistent" and is optimized (and priced) for lower latency
  and higher throughput than the optional strongly-consistent read mode.
- **Classification: PA/EL.**
- **Configuration lever that produces this:** default read mode
  (`ConsistentRead: false`), managed multi-AZ replication with
  availability-favoring conflict handling.

## 2. Apache Cassandra (`LOCAL_ONE` reads and writes — a common production default)

- **Partition-branch question:** During a partition, does a Cassandra
  node configured at `LOCAL_ONE` refuse to serve requests in its own data
  center, or keep serving?
  **Answer: Availability.** `LOCAL_ONE` only requires acknowledgment from
  one local replica, so as long as at least one local replica is
  reachable, the node keeps serving reads and writes even if it cannot
  reach replicas in other data centers.
- **Else-branch question:** Under normal operation, does a `LOCAL_ONE`
  write wait for any cross-replica agreement before acknowledging, or does
  it return as soon as a single local replica accepts it?
  **Answer: Latency.** A single-replica acknowledgment is the fastest
  possible response Cassandra can give; no quorum coordination round trip
  is paid.
- **Classification: PA/EL** (same quadrant as DynamoDB, via a different
  mechanism: leaderless single-replica-ack rather than managed sloppy
  quorum — reinforcing that PA/EL is a common shape, not a single vendor's
  proprietary trick).
- **Configuration lever that produces this:** `CONSISTENCY LOCAL_ONE` (or
  `ONE`) set on both the read and write path.

## 3. Synchronously replicated PostgreSQL primary/standby pair (`synchronous_commit = remote_apply`, majority quorum)

- **Partition-branch question:** If the synchronous standby becomes
  unreachable, does the primary keep accepting writes (degrading to
  effectively asynchronous or refusing new synchronous standbys), or does
  it block/refuse writes until connectivity is restored?
  **Answer: Consistency**, assuming the deployment is deliberately
  configured (per
  [Replication](../../../06_Databases_and_Storage/CH07_Replication.md)
  Section 4.8's fencing teaching) to refuse to acknowledge a write that
  cannot be confirmed durable on the required number of standbys, rather
  than silently demoting to asynchronous behavior.
- **Else-branch question:** Under normal operation, does every write wait
  for the standby's acknowledgment before the client is told it succeeded?
  **Answer: Consistency.** `synchronous_commit = remote_apply` (or
  `on`/`remote_write`, depending on the durability guarantee desired)
  explicitly blocks the client's `COMMIT` until the standby has
  acknowledged, paying a network round trip on every single write.
- **Classification: PC/EC.**
- **Configuration lever that produces this:** `synchronous_commit`
  set to a blocking mode, `synchronous_standby_names` naming the required
  standby/standbys, no automatic unfenced promotion configured.

## 4. Azure Cosmos DB — Session consistency level

- **Partition-branch question:** Does Cosmos DB's Session consistency
  level preserve its consistency guarantee through a regional failover
  event (a partition-adjacent event), or does it drop the guarantee to
  keep serving?
  **Answer: Consistency.** Microsoft's own Cosmos DB documentation states
  that Session (like Strong and Bounded Staleness) maintains its stated
  consistency guarantee even through a regional failover — the product is
  explicitly engineered to keep the promise rather than silently degrade
  it under partition-adjacent conditions.
- **Else-branch question:** Under normal, healthy operation, does a read
  wait for a majority/quorum round trip, or is it served from the nearest
  available replica with a bounded guarantee tied to the requesting
  client's own session token?
  **Answer: Latency.** Session consistency is explicitly marketed and
  priced as a low-latency option relative to Strong consistency, serving
  reads from the nearest replica while using a per-client session token
  (recapped as the sticky-routing/read-your-writes pattern in
  [CH06_PACELC.md](../../../07_System_Design_and_Distributed_Systems/CH06_PACELC.md)
  Section 7) to guarantee that *that specific client* never sees its own
  writes go backward, without paying a full cross-replica quorum cost on
  every read.
- **Classification: PC/EL.**
- **Configuration lever that produces this:** `defaultConsistencyLevel:
  Session` set at the account or request level.

## 5. Google Cloud Spanner

- **Partition-branch question:** Does Spanner preserve external
  consistency (strict serializability) across a partition/failure event,
  or does it relax it to keep serving?
  **Answer: Consistency.** Spanner's Paxos-based replica groups refuse to
  serve a write (or an externally-consistent read) that cannot be
  correctly ordered relative to all other transactions, even during a
  node or zone failure — it will fail over to a healthy Paxos group member
  rather than accept a request that could violate external consistency.
- **Else-branch question:** Under normal operation, does every
  transaction pay an unbounded, full round-trip coordination cost, or has
  the coordination cost been engineered down to a small, bounded interval?
  **Answer: Consistency, but at an engineered-down cost.** Spanner still
  fundamentally pays for cross-node agreement (it does not choose Latency
  over Consistency), but its TrueTime API bounds clock uncertainty tightly
  enough that the "commit-wait" interval a transaction must pause for is
  measured in single-digit milliseconds rather than a full unbounded
  cross-region negotiation, making a PC/EC posture viable at a latency
  budget many organizations without comparable atomic-clock/GPS
  infrastructure investment cannot replicate.
- **Classification: PC/EC** (the same quadrant as the PostgreSQL example
  above, but reached through a fundamentally more expensive and more
  latency-optimized engineering path — illustrating that a quadrant label
  alone does not tell you the *cost* of achieving it).

## Summary table

| System | Partition branch | Else branch | Quadrant |
|---|---|---|---|
| DynamoDB (default) | Availability | Latency | PA/EL |
| Cassandra (`LOCAL_ONE`) | Availability | Latency | PA/EL |
| PostgreSQL (synchronous, fenced) | Consistency | Consistency | PC/EC |
| Cosmos DB (Session) | Consistency | Latency | PC/EL |
| Google Spanner | Consistency | Consistency (engineered low-cost) | PC/EC |

The exercise's key takeaway: two systems sharing a quadrant label
(PostgreSQL and Spanner both PC/EC) can still differ enormously in the
*cost* of that classification — always ask not just "which quadrant" but
"at what engineering cost was that quadrant achieved."
