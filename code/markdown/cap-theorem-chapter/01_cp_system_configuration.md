# Example 1 — CP System Configuration (etcd and MongoDB)

Referenced from [CH05_CAP_Theorem.md, Section 10](../../../07_System_Design_and_Distributed_Systems/CH05_CAP_Theorem.md#10-complete-code-examples).

Both configurations below bias explicitly toward Consistency over
Availability: each requires a majority quorum before a write is considered
durable, and each defines a clear, bounded refusal behavior for the
minority side of a partition rather than leaving that case undefined.

## etcd — 5-node cluster, Raft majority quorum

```yaml
# etcd.conf.yml — one node's configuration in a 5-node cluster
name: etcd-node-3
initial-cluster: >
  etcd-node-1=https://10.0.1.11:2380,
  etcd-node-2=https://10.0.1.12:2380,
  etcd-node-3=https://10.0.1.13:2380,
  etcd-node-4=https://10.0.1.14:2380,
  etcd-node-5=https://10.0.1.15:2380
initial-cluster-state: new
election-timeout: 1000       # milliseconds before a follower starts a new election
heartbeat-interval: 100      # milliseconds between leader heartbeats
# No "quorum size" setting exists because it is not configurable -
# etcd's Raft implementation always requires ceil((N+1)/2) nodes,
# i.e. 3 of 5 here, before any write is committed.
```

**What happens during a partition.** If the network splits this 5-node
cluster into a 3-node group and a 2-node group, the 3-node group can still
elect a leader and commit writes (3 out of 5 is a majority). The 2-node
group cannot elect a leader that can commit anything — `etcdctl put`
issued against a node in the 2-node group blocks until `election-timeout`
is exceeded, then returns an explicit error:

```
$ etcdctl put mykey myvalue
{"level":"warn","msg":"context deadline exceeded"}
Error: etcdserver: request timed out
```

This is the mechanical, code-level realization of Section 4.2's proof:
the minority side is not silently serving stale data — it is refusing to
answer, by design, because it structurally cannot confirm a quorum.

## MongoDB — replica set with majority write/read concern

```javascript
// Application write path, explicitly requesting majority acknowledgment
db.orders.insertOne(
  { orderId: "ORD-88213", amount: 4999, currency: "USD" },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
);

// Application read path, explicitly requesting a majority-committed read
db.orders.find(
  { orderId: "ORD-88213" }
).readConcern("majority");
```

```javascript
// rs.conf() excerpt for a 5-member replica set
{
  "_id": "ordersReplSet",
  "members": [
    { "_id": 0, "host": "mongo-1:27017", "priority": 2 },
    { "_id": 1, "host": "mongo-2:27017", "priority": 1 },
    { "_id": 2, "host": "mongo-3:27017", "priority": 1 },
    { "_id": 3, "host": "mongo-4:27017", "priority": 1 },
    { "_id": 4, "host": "mongo-5:27017", "priority": 1 }
  ],
  "settings": { "electionTimeoutMillis": 10000 }
}
```

**What happens during a partition.** With `writeConcern: { w: "majority" }`,
an `insertOne` call issued against a primary stranded in a minority
partition (unable to reach 3 of 5 members, including itself) blocks for up
to `wtimeout` (5000 ms above) and then returns a
`WriteConcernError` — the write is *not* silently accepted locally and
later discarded; the driver surfaces the failure to the calling
application immediately, which is what lets the application implement its
own retry-or-surface-to-user policy (Section 9, step 2) rather than
guessing whether the write actually succeeded.
