# Concept proposals: Part 09 CH09 IAM

Proposed additions to `CORE_CONCEPTS.md` from the in-depth rewrite of
[Cloud Identity and Access Management](../../09_Cloud_Computing/CH09_IAM.md).
The five existing CH09 rows (policy composition, control-plane versus
data-plane authorization, workload identity federation and managed
identities, guardrails versus grants, cross-account/subscription/project
trust) remain as they are. The rows below are taught in full in the chapter
and are not currently in the registry. In the registry the owner cell would be
`[IAM](09_Cloud_Computing/CH09_IAM.md)`.

| Concept | Proposed owner | Scope note |
|---|---|---|
| Cloud confused-deputy defenses: external IDs for third-party role assumption and source-resource conditions (`aws:SourceArn`, `aws:SourceAccount`, `aws:SourceOrgID`) for service principals | IAM (Part 09 CH09), section 10.3 | Cloud-authorization forms of the confused deputy. The protocol form (bare OAuth access token as identity proof) stays with Part 05 OIDC; Azure Lighthouse and Google Cloud service-agent grants are covered as provider analogues |
| Identity-attach permission as privilege equivalence (`iam:PassRole`, Managed Identity Operator assign action, `iam.serviceAccounts.actAs`) | IAM (Part 09 CH09), section 9.3 | Holding the right to attach an identity to compute equals holding that identity's permissions; scoping and detection. Azure's "anyone who runs code on the resource" rule stays as a CH02 sub-note |
| Credential revocation window analysis (residual lifetime of derived sessions and tokens after revocation) | IAM (Part 09 CH09), sections 13.1 to 13.4 | Exposure = detection + action + propagation + longest derived credential not covered; per-provider handles (`aws:TokenIssueTime` deny, Entra session revocation and CAE, service-account disable). Secret-value rotation stays with Secrets Management (CH13); token-lifetime protocol theory stays with Part 05 OAuth |
| OIDC subject-claim pinning for CI/CD workload federation, including immutable-ID subjects | IAM (Part 09 CH09), sections 9.4 and 9.5 | What each pin proves (repository, branch, environment, reusable workflow) and its weakness. Could be folded into the existing CH09 row "Workload identity federation and managed cloud identities" if the merge step prefers |

Merge note: Kubernetes Pod identity mechanics remain with
[Kubernetes](../../09_Cloud_Computing/CH08_Kubernetes.md) section 5.3, and
instance metadata protections with the CH04 proposal; CH09 recaps both.
