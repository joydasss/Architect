# Worked Example: Migrating a Session-Token Store from PA/EL to PC/EC

Companion artifact for
[07_System_Design_and_Distributed_Systems/CH06_PACELC.md](../../../07_System_Design_and_Distributed_Systems/CH06_PACELC.md),
Section 10, expanding the session-token scenario introduced in the
chapter's Section 4.4.

## Background

A three-node Cassandra cluster (`N=3`) originally hosted only a
product-catalog workload, configured at `CONSISTENCY LOCAL_ONE` for both
reads and writes — a PA/EL posture appropriate for catalog content, where a
few hundred milliseconds of staleness on a price update is commercially
invisible. A new team added a `session_tokens` table to the *same physical
cluster*, initially copying the catalog team's `LOCAL_ONE`/`LOCAL_ONE`
configuration because "that's what worked before." Session tokens record
whether an API credential is currently valid or has been revoked.

## Why the initial configuration was wrong

A revoked token read as still-valid, even briefly, is a security defect
(recapped from the chapter's Section 13), not a cosmetic staleness issue.
Under `LOCAL_ONE`/`LOCAL_ONE`, a read is answered by a single replica with
no quorum overlap guarantee against the write — per the worksheet in
[02_replication_config_decision_worksheet.md](02_replication_config_decision_worksheet.md),
`W=1, R=1` gives `W+R=2`, which does **not** exceed `N=3`, so a read is not
mathematically guaranteed to see the most recent acknowledged write. A
revocation written to one replica can be invisible to a read served by a
different replica that has not yet received the revoke, for as long as
Cassandra's normal (sub-second, but non-zero) inter-replica propagation
takes.

## Step-by-step migration

### 1. Classify the target quadrant

Session-token validity must never be read stale. Partition-branch
question: if the cluster partitions, should token validation keep serving
(risking a stale "valid" answer) or refuse to answer (risking an outage)?
The team decides refusing to answer under partition is the safer failure
mode for a security-relevant check — favoring Consistency on both axes.
**Target quadrant: PC/EC.**

### 2. Configuration diff

```diff
- CREATE TABLE IF NOT EXISTS auth.session_tokens (
-     token_id text PRIMARY KEY,
-     account_id text,
-     revoked boolean,
-     issued_at timestamp
- );
- -- Application code:
- session = QUERY "SELECT revoked FROM auth.session_tokens WHERE token_id=?"
-     CONSISTENCY LOCAL_ONE;
- writeRevocation = UPDATE "auth.session_tokens SET revoked=true WHERE token_id=?"
-     CONSISTENCY LOCAL_ONE;

+ -- Schema unchanged; only the per-query consistency level changes.
+ session = QUERY "SELECT revoked FROM auth.session_tokens WHERE token_id=?"
+     CONSISTENCY QUORUM;
+ writeRevocation = UPDATE "auth.session_tokens SET revoked=true WHERE token_id=?"
+     CONSISTENCY QUORUM;
```

No schema change is required — the migration is entirely a per-query
consistency-level change, demonstrating the chapter's Section 4.4 point
that PACELC posture is frequently a configuration decision layered on
shared infrastructure, not a re-architecture.

### 3. Verify the quorum-overlap arithmetic

`N=3`, new `W=2` (`QUORUM` write), new `R=2` (`QUORUM` read):
`W + R = 4 > N = 3` — the overlap condition now holds. Every read quorum
is now mathematically guaranteed to intersect every write quorum on at
least one replica, so a read cannot miss the most recent acknowledged
revocation.

### 4. Measure the trade-off actually paid

| Metric | Before (`LOCAL_ONE`/`LOCAL_ONE`) | After (`QUORUM`/`QUORUM`) |
|---|---|---|
| P50 write latency | ~0.8 ms | ~1.6 ms |
| P99 write latency | ~3 ms | ~7 ms |
| P50 read latency | ~0.6 ms | ~1.4 ms |
| Read-after-write guarantee | None (best-effort) | Guaranteed (`W+R>N`) |
| Failure mode under partition | Keeps serving, risk of stale "valid" read | Refuses to answer on minority side (`QUORUM` requires 2 of 3 reachable) |

The measured latency cost — roughly 1-4 ms of additional coordination time
per operation, entirely within the same data center — is negligible against
the security requirement it purchases, confirming this was the correct
trade-off for this specific data class, even though the exact same physical
cluster continues to serve the catalog table at `LOCAL_ONE`/`LOCAL_ONE`
alongside it.

### 5. Confirm isolation from the catalog workload

Because the consistency level is set per query rather than per cluster,
the catalog table's `LOCAL_ONE` configuration is verified (via the
cross-table consistency-policy isolation test described in the chapter's
Section 16) to be completely unaffected by the session-token table's
change — both PACELC postures coexist on one physical deployment.

## Outcome

The session-token workload moved from an unintentional, unreviewed PA/EL
posture to a deliberately chosen and verified PC/EC posture, at a small,
measured, and acceptable latency cost, without any schema change, without
migrating to different infrastructure, and without affecting the
co-located catalog workload's own, separately appropriate PA/EL
configuration.
