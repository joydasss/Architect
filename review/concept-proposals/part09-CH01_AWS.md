# Concept Proposals — AWS (CH01, Part 09 Cloud Computing)

New cross-cutting concepts introduced by the in-depth rewrite of
[Amazon Web Services Operating Model](../../09_Cloud_Computing/CH01_AWS.md).
Suggested ownership = this chapter for all entries below. Existing CH01 rows in
`CORE_CONCEPTS.md` (global infrastructure scope, accounts and Organizations,
control/data plane and scope, shared responsibility, service-family selection)
remain as they are; these rows add concepts the rewrite now teaches in depth.

| Concept | Scope note |
|---|---|
| Static stability (pre-provisioned capacity and data-plane-only recovery) | Survive a dependency or AZ impairment without control-plane actions; n/(n−1) capacity sizing; global-service control planes (IAM, Route 53, CloudFront, Organizations) kept off the recovery path. Section 6. Compute (CH04) and Part 10 resilience chapters should recap and link. |
| AWS Resource Control Policies (RCPs) and the organization data perimeter | Resource-side permission ceiling complementing SCPs; supported-service subset, management-account and service-linked-role exceptions, staged rollout. Section 5.4. IAM (CH09) owns the full evaluation algorithm and should recap. |
| Provider service quotas and token-bucket API throttling | Resource quotas versus rate limits versus fixed limits; account-and-Region scope; applied versus default values; burst/refill token buckets including resource rate limiting (EC2 `RunInstances`); quota-versus-capacity distinction during scale-out. Section 13. Generic limiter design remains with Part 08 Rate Limiting. |
| Cloud data-transfer path pricing (inter-AZ, NAT processing, endpoints, public IPv4) | How the route a byte takes determines its cost; gateway endpoints versus NAT; zone-aware routing trade-off. Section 14. Cost Optimization (CH14) owns billing data and optimization tooling and should recap. |
