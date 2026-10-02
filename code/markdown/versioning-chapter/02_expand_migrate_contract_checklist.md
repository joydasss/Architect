# Expand-Migrate-Contract Checklist

Illustrative review artifact, not an automated migration plan. Adapt the gates to the data store, API styles, consumer support promises, and rollback requirements in the target system.

## Worked change

An order contract replaces a single `address` value with `street`, `locality`, `region`, and `postalCode`. During migration, the canonical domain value is a structured address. The legacy field is a projection, not an independent source of truth.

## 1. Expand

- [ ] Name the old and new contract identities, accountable owners, consumers, and required old-client/new-server and new-client/old-server pairings.
- [ ] Add the new optional representation and a safe, documented absence/default rule.
- [ ] Deploy readers that accept both representations before any writer emits the new one.
- [ ] Choose exactly one canonical representation in storage. If both are persisted temporarily, define atomicity, authority, conflict resolution, and repair ownership.
- [ ] Add validation and a deterministic mapping between legacy and structured forms. Reject ambiguous or lossy conversions instead of guessing.
- [ ] Test old request/new server, new request/old server where required, old response readers, and mixed server replicas.

## 2. Migrate

- [ ] Backfill existing records from the canonical source; make the job idempotent and restartable.
- [ ] Record per-record conversion failures and provide an operator-owned repair path.
- [ ] If dual writes are unavoidable, write through one transaction or durable handoff when possible. Otherwise document the consistency window and reconciliation rule.
- [ ] Do not read whichever representation is non-null without a precedence rule. Prefer canonical new data, use legacy fallback only during the stated window, and detect disagreement.
- [ ] Run shadow reads or parity comparisons without changing customer-visible results; sample and aggregate mismatches.
- [ ] Release consumers gradually. Measure adoption by attributable cohort and record unknown/unattributed use as uncertainty.
- [ ] Keep rollback safe: old code must read data already written by the expanded system, or the rollout must provide a controlled reverse transform.

## 3. Contract

- [ ] Announce deprecation with replacement guidance, owner contact, dates, and the actual support end condition.
- [ ] Stop writing the legacy representation only after consumer and data gates pass.
- [ ] Observe a defined quiet period that covers retries, offline clients, webhook redelivery, and retained event replay.
- [ ] Remove legacy reads, schema fields, adapters, routes, and backfill code in separately reviewable changes.
- [ ] Verify that rollback no longer depends on removed state before deleting compatibility data.
- [ ] Close the inventory item with usage evidence, test results, owner sign-off, and retained decision record.

## Dual-read/write hazards to resolve explicitly

1. **Two authorities:** old and new fields diverge; no deterministic value wins.
2. **Partial writes:** one representation commits while the other fails, creating order-dependent reads.
3. **Stale fallback:** a reader prefers a legacy value that is present but older than canonical data.
4. **Non-idempotent backfill:** rerunning conversion duplicates or overwrites concurrent user edits.
5. **Rollback incompatibility:** old application code cannot read newly persisted records.
6. **Hidden consumers:** telemetry omits retries, replay, batch clients, or unregistered integrations.

The contract phase is complete only when the old representation has no supported writers or readers, no delayed delivery can require its decoder, and the owner has verified the agreed retirement evidence.