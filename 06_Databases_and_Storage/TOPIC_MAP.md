# Part 06 — Databases and Storage Topic Map

This map is the coverage contract for Part 06's 22 chapters. The part first teaches database design and cross-engine mechanisms, then applies them to relational and NoSQL systems. Chapter numbering follows the overview's intended order: database design (CH01–10), relational engines (CH11–14), and NoSQL engines (CH15–22).

## Part-wide ownership boundaries

- Part 06 owns data modeling, database engine internals, query and storage behavior, database reliability mechanisms, and decisions about database selection and operation.
- Part 07 owns general distributed-systems theory: CAP/PACELC, consensus, leader election, distributed replication, transactions, partitioning, ordering, and idempotency. Part 06 explains database implementations and links to those owners rather than re-deriving general theory.
- Part 05 owns operating-system memory, I/O, filesystems, and networking; Part 09 owns cloud database products and managed-service operations; Part 19 owns general performance engineering.
- Database design chapters own general abstractions. Engine chapters explain engine-specific realization and recap generic concepts with links. Similar names do not imply identical mechanisms (for example, database partitioning versus distributed sharding).
- Distinguish logical model, physical storage, transaction semantics, query plan, and operational service guarantees. Name edition/version-specific behavior and test it on the actual engine version.

## Cross-part stakeholders and quality scenarios

- Application teams need predictable query behavior, schema evolution, transaction semantics, and recovery.
- Data/platform teams need capacity visibility, migration safety, backup/restore, replication health, and upgrade compatibility.
- Security and compliance stakeholders need access control, encryption, audit, retention, locality, and deletion evidence.
- Business owners need data correctness, service availability, acceptable recovery objectives, predictable cost, and an explicit source of truth.
- Important scenarios include a hot partition under peak traffic; a query regression after data growth; a replica lagging during failover; an engine upgrade changing plans or storage behavior; and a restore that recovers the correct point-in-time data.

## Database Design

### CH01 Normalization

**Reader outcome:** Structure relational data to reduce update anomalies while preserving constraints and meaningful dependencies.
**Coverage and evidence:** Functional dependencies, keys, first through higher normal forms, anomaly classes, decomposition, lossless join, and dependency preservation. Validate with schema constraints and representative update/query patterns.
**Boundaries:** CH02 owns deliberate denormalization; engine chapters own product-specific DDL and indexes.
**Diagram opportunities:** (1) functional dependency graph; (2) insert/update/delete anomaly; (3) decomposition to normalized relations; (4) lossless join reconstruction; (5) dependency-preservation trade-off.

### CH02 Denormalization

**Reader outcome:** Add controlled redundancy when read, scale, or availability requirements justify its consistency and storage cost.
**Coverage and evidence:** Read models, materialized views, aggregates, duplicated fields, write amplification, refresh/invalidations, CQRS recap, and stale-data tolerance. Measure read savings against update fan-out and repair cost.
**Boundaries:** Part 07 owns CQRS and event-sourcing mechanics; CH09 owns cache behavior; engine chapters own materialized-view implementation.
**Diagram opportunities:** (1) normalized write model versus denormalized read model; (2) update fan-out; (3) materialized-view refresh; (4) consistency/staleness window; (5) read-cost versus write-cost trade-off.

### CH03 Indexes

**Reader outcome:** Select and maintain indexes from query predicates, ordering, selectivity, and write-cost requirements.
**Coverage and evidence:** B-tree/B+tree, hash, composite and covering indexes, clustered/nonclustered organization, selectivity, maintenance, and plan evidence. Use representative data and explain plans.
**Boundaries:** CH04 owns optimizer plan selection; engine chapters own index implementation differences.
**Diagram opportunities:** (1) B-tree lookup path; (2) composite-index prefix ordering; (3) covering-index access versus table lookup; (4) selectivity and scan choice; (5) write amplification and index maintenance.

### CH04 Query Optimizers

**Reader outcome:** Interpret query plans and understand how statistics, transformations, and cost estimates influence database execution.
**Coverage and evidence:** Parse/rewrite/plan/execute stages, statistics, cardinality estimation, join order, nested-loop/hash/merge joins, plan caching, parameter sensitivity, and `EXPLAIN ANALYZE`. Validate estimates against runtime rows and resource use.
**Boundaries:** CH03 owns index data structures; engine chapters own optimizer specifics.
**Diagram opportunities:** (1) query processing pipeline; (2) join-order search tree; (3) cardinality-estimation error propagation; (4) join-algorithm selection; (5) estimated versus actual plan diagnostics.

### CH05 Partitioning

**Reader outcome:** Partition a single database relation or storage set to improve lifecycle, pruning, or manageability without confusing it with distributed sharding.
**Coverage and evidence:** Range/list/hash partitioning, key choice, pruning, local/global indexes, rolling-window maintenance, partition sizing, and boundary changes. Test pruning and maintenance against realistic query predicates.
**Boundaries:** CH06 owns cross-node sharding; Part 07 owns general distributed partitioning.
**Diagram opportunities:** (1) partition-key routing within one database; (2) range/list/hash layouts; (3) partition pruning from predicate; (4) rolling-window attach/detach lifecycle; (5) partitioning-versus-sharding boundary.

### CH06 Sharding

**Reader outcome:** Distribute data across database nodes when a single-node boundary is insufficient, while making routing, rebalancing, and cross-shard cost explicit.
**Coverage and evidence:** Shard-key selection, range/hash/consistent hashing, directory routing, resharding, hotspots, cross-shard queries/transactions, and tenant placement. Measure skew, data movement, query fan-out, and recovery.
**Boundaries:** Part 07 owns general partitioning and distributed-system semantics; CH05 owns single-engine table partitioning.
**Diagram opportunities:** (1) logical key to shard routing; (2) range/hash/consistent-hash placement; (3) hot-key skew; (4) shard split/rebalance; (5) cross-shard query/transaction fan-out.

### CH07 Replication

**Reader outcome:** Choose database replication topology and consistency behavior for availability, read scale, and recovery.
**Coverage and evidence:** Leader/follower, synchronous/asynchronous modes, logs/WAL, lag, quorum reads/writes, failover, fencing, split brain, and restore. Validate recovery-point and recovery-time outcomes under node/network failures.
**Boundaries:** Part 07 owns generic replication, CAP/PACELC, consensus, and failover theory; CH11–22 show engine-specific implementations.
**Diagram opportunities:** (1) leader/follower write path; (2) synchronous versus asynchronous acknowledgment; (3) replica lag and stale reads; (4) failover with fencing; (5) quorum availability under node loss.

### CH08 Transactions

**Reader outcome:** Preserve atomicity and isolation across database operations and identify which anomalies a chosen transaction model permits.
**Coverage and evidence:** ACID, transaction boundaries, isolation levels, anomalies, MVCC, locks, write-ahead logging, two-phase commit (2PC), and Saga recap. Demonstrate concurrency schedules and recovery behavior.
**Boundaries:** CH10 owns locking and deadlock mechanics; Part 07 owns distributed transactions and Saga design; engine chapters own implementation-specific semantics.
**Diagram opportunities:** (1) transaction lifecycle and commit/rollback; (2) concurrent anomaly schedule; (3) MVCC version visibility; (4) WAL recovery path; (5) local transaction versus distributed coordination boundary.

### CH09 Caching

**Reader outcome:** Choose cache placement and consistency policy that reduce repeated work without turning stale or lost cache state into data corruption.
**Coverage and evidence:** Cache-aside/read-through/write-through/write-behind, eviction, TTL, invalidation, stampedes, cache warming, distributed cache consistency, and materialized-view distinction. Measure hit ratio, staleness, and origin load.
**Boundaries:** Part 07 owns general distributed state and idempotency; engine chapters describe native caches; CH02 owns durable denormalized read models.
**Diagram opportunities:** (1) cache-aside read/write path; (2) write-through versus write-behind; (3) invalidation and stale-read race; (4) stampede collapse; (5) cache versus durable materialized view.

### CH10 Locking

**Reader outcome:** Diagnose lock contention, deadlocks, and concurrency-control choices within database transactions.
**Coverage and evidence:** Shared/exclusive and row/table locks, lock granularity, optimistic/pessimistic control, deadlock cycles, detection/victim selection, timeouts, and MVCC interaction. Use lock graphs and wait evidence.
**Boundaries:** CH08 owns transaction isolation semantics; Part 05 owns process synchronization; engine chapters own lock-manager implementations.
**Diagram opportunities:** (1) lock compatibility matrix; (2) lock escalation/granularity; (3) deadlock wait-for cycle; (4) optimistic conflict/retry; (5) MVCC reader/writer coexistence.

## Relational Engines

### CH11 PostgreSQL

**Reader outcome:** Operate PostgreSQL through its MVCC, vacuum, WAL, extensions, indexing, and connection model.
**Coverage and evidence:** Heap tuples and visibility, vacuum/bloat, WAL and replication, extensions, GIN/GiST/BRIN and partial indexes, JSONB, partitioning, connection pooling, and planner behavior. Diagnose with system catalogs, `EXPLAIN`, and runtime statistics.
**Boundaries:** Recap CH03–10 generic design and mechanisms; Part 09 owns managed PostgreSQL products.
**Diagram opportunities:** (1) MVCC tuple visibility; (2) vacuum and bloat lifecycle; (3) WAL replication; (4) index-family access paths; (5) backend process versus pooled connection architecture.

### CH12 MySQL

**Reader outcome:** Choose and operate MySQL storage engines, indexing, replication, and concurrency behavior for application workloads.
**Coverage and evidence:** InnoDB clustered storage, buffer pool, redo/undo, next-key/gap locks, binlog formats, GTIDs, replication and Group Replication, query cache history, and failover. Validate lock waits, replication state, and execution plans.
**Boundaries:** Recap generic transactions, replication, indexes, and caching; Part 09 owns managed MySQL products.
**Diagram opportunities:** (1) clustered primary-key organization; (2) redo/undo and commit; (3) next-key lock interval; (4) binlog replication topology; (5) buffer pool and page eviction.

### CH13 Oracle

**Reader outcome:** Explain Oracle instance/database architecture, memory and process model, consistency, and high-availability options.
**Coverage and evidence:** System Global Area/Program Global Area (SGA/PGA), background processes, tablespaces/datafiles, undo and System Change Number (SCN) consistency, PL/SQL, Cost-Based Optimizer, Real Application Clusters (RAC), and Data Guard. Verify with views and execution plans.
**Boundaries:** Recap generic optimizer, transaction, replication, and indexing concepts; Part 09 owns managed Oracle products.
**Diagram opportunities:** (1) instance SGA/PGA/background-process topology; (2) tablespace/datafile mapping; (3) undo/SCN consistent read; (4) RAC instances and shared storage; (5) Data Guard primary/standby transition.

### CH14 SQL Server

**Reader outcome:** Assess SQL Server storage, transaction log, availability groups, memory-optimized tables, Query Store, and columnstore features.
**Coverage and evidence:** Transaction log/checkpoints, Accelerated Database Recovery, clustered storage, Always On Availability Groups, In-Memory OLTP, Query Store, columnstore, and T-SQL. Evaluate edition/version limits and workload evidence.
**Boundaries:** Recap generic ACID, indexes, replication, and optimizer concepts; Part 09 owns managed SQL Server products.
**Diagram opportunities:** (1) transaction log/checkpoint/recovery; (2) availability-group replica and listener path; (3) memory-optimized versus disk table path; (4) Query Store plan regression loop; (5) rowstore versus columnstore execution.

## NoSQL Engines

### CH15 MongoDB

**Reader outcome:** Model document data and operate MongoDB replication, sharding, indexing, and consistency from application query patterns.
**Coverage and evidence:** BSON/documents, schema validation, aggregation pipeline, replica sets/oplog/elections, sharding, WiredTiger, transactions, write/read concerns, and indexes. Test query plans, chunk balance, and failover.
**Boundaries:** Recap generic sharding/replication/transactions/indexes; Part 09 owns managed MongoDB products.
**Diagram opportunities:** (1) document model and embedded/reference choice; (2) replica-set election; (3) shard-key-to-chunk routing; (4) aggregation pipeline; (5) WiredTiger MVCC/locking path.

### CH16 Redis

**Reader outcome:** Choose Redis data structures and deployment modes for low-latency state while accounting for persistence, eviction, replication, and failover.
**Coverage and evidence:** Event-loop execution, structures/complexity, RDB/AOF, Cluster hash slots, Sentinel, pub/sub, maxmemory and eviction, persistence risk, and client retry behavior. Measure latency, hot keys, memory, and replica state.
**Boundaries:** Recap caching, replication, sharding, and transactions; CH09 owns generic cache patterns.
**Diagram opportunities:** (1) command/event-loop execution; (2) data structure operation complexity; (3) RDB versus AOF recovery; (4) Cluster hash-slot routing; (5) Sentinel/Cluster failover and stale-client path.

### CH17 DynamoDB

**Reader outcome:** Design DynamoDB access patterns and capacity using partition keys, sort keys, secondary indexes, consistency, and streams.
**Coverage and evidence:** Single-table design, partition distribution, capacity modes, adaptive capacity, GSI/LSI, conditional writes, transactions, Streams, and Global Tables. Monitor throttling and hot partitions.
**Boundaries:** Recap generic sharding, replication, transactions, and indexing; Part 09 owns the managed service's cloud/IAM/pricing mechanics.
**Diagram opportunities:** (1) partition/sort-key item collection; (2) partition-key hash distribution; (3) GSI write/read propagation; (4) conditional transaction; (5) Streams/Global Tables replication path.

### CH18 Cassandra

**Reader outcome:** Choose Cassandra data models and consistency settings around query-first access, replicas, partitions, and repair.
**Coverage and evidence:** CQL query-first modeling, token ring/vnodes, replication factor, tunable consistency, gossip and failure detection, hinted handoff, anti-entropy repair, LSM storage, and Lightweight Transactions/Paxos. Measure repair, compaction, tombstones, and consistency availability.
**Boundaries:** Part 07 owns quorum/replication/CAP/PACELC theory; CH06 owns generic sharding and CH03 owns index fundamentals.
**Diagram opportunities:** (1) token ring/vnode ownership; (2) coordinator and replica quorum; (3) gossip membership and failure detector; (4) write path through commit log/memtable/SSTable; (5) repair and hinted-handoff recovery.

### CH19 Neo4j

**Reader outcome:** Model and query connected data using a property graph while understanding traversal, storage, clustering, and graph analytics boundaries.
**Coverage and evidence:** Nodes/relationships/properties, Cypher patterns, index-free adjacency, storage records, query plans, Graph Data Science algorithms, causal clustering, and Raft. Compare graph traversal with relational joins on representative workloads.
**Boundaries:** Recap indexes, optimizer, replication, transactions, and sharding; Part 07 owns general consensus and leader election.
**Diagram opportunities:** (1) property graph and relationship traversal; (2) index-free adjacency path; (3) Cypher matching execution; (4) graph projection/algorithm workflow; (5) causal cluster roles and Raft election.

### CH20 ElasticSearch

**Reader outcome:** Design search/index workloads with analyzers, mappings, inverted indexes, shards, replicas, and near-real-time visibility.
**Coverage and evidence:** Tokenization/analyzers, inverted index, BM25, Lucene segments, mappings, Query DSL/aggregations, shard/replica cluster, refresh/translog, and acknowledged-write failure risks. Inspect query profiles and segment/cluster state.
**Boundaries:** Recap general indexing, sharding, replication, transactions, and caching; treat ElasticSearch as a search system, not automatically the authoritative database.
**Diagram opportunities:** (1) text analysis to inverted index; (2) BM25 scoring and candidate ranking; (3) shard/replica placement; (4) segment merge and refresh visibility; (5) query and aggregation execution.

### CH21 Vector Databases

**Reader outcome:** Evaluate vector indexing and retrieval for embedding workloads while balancing recall, latency, memory, and filtering needs.
**Coverage and evidence:** Embeddings and similarity, exact versus approximate nearest-neighbor search, HNSW, IVF/product quantization, filtering/hybrid search, index build/update, and retrieval-augmented generation boundary. Measure recall/latency and drift across embedding versions.
**Boundaries:** Part 14 owns model and embedding generation; CH03 owns traditional index structures; Part 07 owns distributed replication/sharding theory.
**Diagram opportunities:** (1) embedding/vector similarity space; (2) exact versus approximate search; (3) HNSW graph traversal; (4) IVF partition and quantization path; (5) retrieval and reranking pipeline.

### CH22 Time Series Databases

**Reader outcome:** Select time-series storage and query strategies for ingestion, retention, downsampling, and high-cardinality telemetry.
**Coverage and evidence:** Time-series data model, time-partitioned chunks, write-optimized ingestion, retention/downsampling, delta-of-delta/Gorilla compression, label cardinality, Prometheus pull model, and query/rollup behavior. Measure ingest rate, series count, retention, and query cost.
**Boundaries:** Part 14 owns observability concepts and SLOs; CH05 owns general partitioning; Part 09 owns managed time-series services.
**Diagram opportunities:** (1) sample/series/label data model; (2) ingestion to time-partitioned chunks; (3) retention and downsampling lifecycle; (4) delta-of-delta/XOR compression; (5) cardinality growth and storage cost.
