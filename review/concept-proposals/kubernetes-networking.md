# Kubernetes Networking Concept Proposals

Source: `12_Kubernetes/CH06_Networking.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Kubernetes Pod network model and communication-path taxonomy | CH06 Networking | Owns upstream Pod addressing expectations and separation of Pod-to-Pod, Pod-to-Service, and external traffic paths. Part 05 owns IP routing and transport mechanics; Part 09 owns provider virtual networks and managed CNI products. |
| Kubernetes NetworkPolicy isolation and additive ingress/egress rule semantics | CH06 Networking | Owns direction-specific Pod isolation, selector composition, additive allow rules, and the bilateral source-egress/destination-ingress condition. Part 15 owns general threat modeling and security controls; CH13 applies Kubernetes security governance. |
| CNI plugin attachment boundary and NetworkPolicy enforcement prerequisite | CH06 Networking | Owns the upstream contract between Pod sandbox creation, plugin attachment, addressing, and the fact that NetworkPolicy requires an enforcing implementation. Part 05 owns kernel/runtime primitives; Part 09 owns provider CNI integrations. |
| Kubernetes dual-stack address-family coordination | CH06 Networking | Owns Kubernetes API-level alignment across Pod, Service, node, and plugin address families. Provider network and address-allocation mechanics remain with Part 09; Part 05 owns IPv4/IPv6 fundamentals. |

## Recap-only concepts

- IP addressing, CIDR, routing, NAT, DNS, transport protocols, and firewall fundamentals: Part 05 owns the networking mechanics; this chapter applies them to Kubernetes paths.
- Pod shared network namespace and cgroup implementation: Part 05 CH28/CH25 and CH01 Pods own the relevant foundations.
- Service virtual addresses, EndpointSlices, and external exposure types: CH04 Services owns the Service contract; this chapter traces packet/policy interaction only.
- Provider virtual networks, routes, gateways, load balancers, and managed CNI: Part 09 owns provider-specific services and integration contracts.
- General threat modeling and least-privilege security decisions: Part 15 owns the security foundations; CH13 applies them to Kubernetes.

## Reconciliation note

CORE_CONCEPTS.md already assigns provider-level Kubernetes CNI/CSI/IAM/load-balancer integration boundaries to Part 09 CH08. Keep the proposed ownership upstream-facing: Pod network contract, NetworkPolicy semantics, plugin enforcement prerequisite, and address-family coordination. During the Part 12 batch merge, compare the NetworkPolicy proposal with Part 15's security concepts, retaining the Kubernetes API semantics here while linking rather than re-teaching threat modeling.
