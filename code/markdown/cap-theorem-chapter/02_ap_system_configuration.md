# Example 2 — AP System Configuration (Cassandra and DynamoDB)

Referenced from [CH05_CAP_Theorem.md, Section 10](../../../07_System_Design_and_Distributed_Systems/CH05_CAP_Theorem.md#10-complete-code-examples).

Both configurations below bias explicitly toward Availability over
Consistency by default, while exposing a tunable dial so a caller can
request stronger consistency on specific operations that need it.

## Cassandra — tunable per-query consistency level

```sql
-- Availability-favoring write: succeeds as soon as ANY one replica
-- (including via hinted handoff to a non-owning node) acknowledges.
CONSISTENCY ONE;
INSERT INTO events.click_stream (user_id, event_id, ts, payload)
VALUES (8213, uuid(), toTimestamp(now()), '{"page":"/product/42"}');

-- Same table, a different query path that needs a stronger read:
-- QUORUM requires ceil((RF/2)+1) replicas to agree, trading latency
-- for a much lower chance of reading a stale/conflicting value.
CONSISTENCY QUORUM;
SELECT * FROM events.click_stream WHERE user_id = 8213;
```

```yaml
# cassandra.yaml (relevant excerpt) — hinted handoff kept enabled,
# which is precisely the mechanism that lets a write succeed even
# when the data's actual owning replica is unreachable during a partition.
hinted_handoff_enabled: true
max_hint_window_in_ms: 10800000   # 3 hours - hints older than this are dropped
```

**What happens during a partition.** With `CONSISTENCY ONE`, a write to a
node that cannot reach the key's normal owning replicas is still accepted
by any reachable node, which stores a "hint" to replay to the correct
owner once it becomes reachable again — the write never blocks on the
partition; it simply defers full replication until later (Section 5's
anti-entropy / hinted-handoff mechanism).

## DynamoDB — eventually-consistent reads by default, strong reads on demand

```python
import boto3

table = boto3.resource("dynamodb").Table("Orders")

# Default: eventually-consistent read - lower latency, may reflect a
# slightly stale value if a very recent write hasn't fully propagated.
response = table.get_item(Key={"orderId": "ORD-88213"})

# Explicit opt-in: strongly-consistent read - higher latency and cost,
# guaranteed to reflect the most recently acknowledged write.
response_strong = table.get_item(
    Key={"orderId": "ORD-88213"},
    ConsistentRead=True,
)
```

**What happens during a partition.** DynamoDB's default `get_item` call
(no `ConsistentRead` flag) keeps succeeding by reading from whichever
replica currently answers first, which is Section 4.4's AP posture in a
single API parameter; the `ConsistentRead=True` variant will instead fail
or slow down if the request cannot reach enough replicas to confirm the
latest value, giving callers a per-request dial between the two Section
4.4 postures rather than a single, fixed, table-wide choice.
