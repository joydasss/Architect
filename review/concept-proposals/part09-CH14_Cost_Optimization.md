# Part 09 CH14 Cost Optimization Concept Proposals

Propose adding these ownership entries to `CORE_CONCEPTS.md` during the next concept-registry merge. They cover material the completed chapter teaches in full and that no existing row assigns. They do not change the five CH14 rows already registered (billing data model, allocation and chargeback, cost per successful workload outcome, commitment utilization risk, anomaly and budget response workflow). Performance and capacity engineering stays with Part 19, and cross-workload cost, performance, and sustainability trade-offs stay with Part 10 CH13.

| Concept | Proposed owner | Notes |
|---|---|---|
| Workload objective versus cost frontier (moves to the frontier versus moves along it) | [Cost Optimization](../../09_Cloud_Computing/CH14_Cost_Optimization.md) | Dominated design options, waste removal as a move to the frontier, objective-for-cost trades as business decisions; Part 10 CH13 and Part 22 should recap and link rather than re-teach |
| Evidence-based rightsizing of provider resources | [Cost Optimization](../../09_Cloud_Computing/CH14_Cost_Optimization.md) | Percentile thresholds and headroom, guest memory evidence from agents, lookback versus workload cycle, failover-reserve and commitment-scope checks, provider recommender behavior; load testing and headroom modeling stay with Part 19 |
| Idle and orphaned resource cleanup lifecycle | [Cost Optimization](../../09_Cloud_Computing/CH14_Cost_Optimization.md) | Owner-first notification, quarantine before delete, expiring exemptions, irreversible steps (public address release) gated by people, provider recovery windows; account and project decommissioning stays with Part 09 CH15 Landing Zones |
| Quotas as spending caps | [Cost Optimization](../../09_Cloud_Computing/CH14_Cost_Optimization.md) | Quota as burn-rate bound for sandbox and research scopes versus failure headroom for production scopes; generic quota mechanics stay with the provider chapters |
