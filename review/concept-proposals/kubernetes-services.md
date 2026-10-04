# Kubernetes Services Concept Proposals

Source: `12_Kubernetes/CH04_Services.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Kubernetes Service as a stable virtual endpoint over changing Pod membership | CH04 Services | Owns Service selector/port contract, endpoint indirection, and Kubernetes virtual-address behavior. Part 05 CH10 owns general load-balancer and proxy algorithms; Part 09 owns cloud load-balancer products. |
| EndpointSlice membership and readiness/serving/termination semantics | CH04 Services | Owns how Kubernetes publishes backend endpoints and conditions for Service consumers. CH01 owns Pod readiness and termination; CH04 applies those statuses to endpoint membership. |
| Kubernetes Service-type exposure contracts and headless discovery | CH04 Services | Owns ClusterIP, headless, NodePort, LoadBalancer, and ExternalName API-level distinctions. Provider-specific controller behavior stays in Part 09; external HTTP routing belongs to CH05 Ingress/Gateway. |
| Namespace-scoped Kubernetes Service DNS naming and record shapes | CH04 Services | Owns Kubernetes-generated Service naming, search context, and normal/headless/ExternalName result distinctions. Part 05 CH08 owns DNS protocol, caching, and record mechanics; CH04 recaps those foundations only. |
| Kubernetes Service traffic policy and topology preference | CH04 Services | Owns internal/external locality fields, source-address and endpoint-availability trade-offs, and version-aware traffic-distribution semantics. CH06 owns CNI and packet path; Part 09 owns provider topology. |

## Recap-only concepts

- Pod identity, readiness, and graceful termination: CH01 Pods owns those API and lifecycle semantics.
- Deployment selectors and Pod template labels: CH02 Deployments owns Deployment controller behavior; CH04 uses the resulting labels for Service membership.
- DNS protocol, caching, CNAME, SRV, and resolver behavior: Part 05 CH08 DNS owns these mechanisms; CH04 teaches only Kubernetes Service names and answer shapes.
- Reverse proxy and load-balancer algorithms: Part 05 CH10/CH11 own general mechanics; Kubernetes Service is not an HTTP reverse proxy.
- CNI, network policy, and provider network/load-balancer products: CH06 Networking and Part 09 own implementation details.

## Reconciliation note

CORE_CONCEPTS.md already assigns general DNS/service-discovery mechanics to Part 05 CH08 and managed Kubernetes network integrations to Part 09 CH08. Keep this chapter's ownership to Kubernetes Service API semantics, endpoint membership, and workload-facing trade-offs. During batch review, check CH05 Ingress/Gateway boundaries and ensure no provider-specific load-balancer behavior is promoted to an upstream Kubernetes guarantee.
