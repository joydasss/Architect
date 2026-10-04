# Kubernetes Ingress Concept Proposals

Source: `12_Kubernetes/CH05_Ingress.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Ingress API resource versus controller implementation boundary | CH05 Ingress | Owns the distinction between declarative host/path/TLS intent and the independently installed controller that realizes it. Part 09 owns provider load balancer products; Part 05 owns generic proxy mechanics. |
| IngressClass selection and controller ownership | CH05 Ingress | Owns `ingressClassName`, IngressClass parameters, defaulting, multiple-controller isolation, and implementation-specific caveats. |
| Ingress host/path match semantics and portability limits | CH05 Ingress | Owns Prefix, Exact, ImplementationSpecific, wildcard host, path precedence, and default backend behavior under the upstream API. Controller-specific extensions remain implementation-specific. |
| Ingress TLS Secret termination boundary | CH05 Ingress | Owns how the Ingress API references TLS material and the fact that termination/backend protocol depend on controller implementation. Part 05 CH15 owns certificate lifecycle; Part 15 owns security foundations. |
| Ingress-to-Gateway API migration decision and mapping | CH05 Ingress | Owns the distinction between frozen but stable Ingress and Gateway API's role-oriented resource model, including migration validation and rollback. Gateway API controller implementation and conformance remain version-specific. |

## Recap-only concepts

- Kubernetes Service selectors, EndpointSlices, and endpoint readiness: CH04 Services owns these backend contracts.
- DNS protocol, caching, certificates, TLS handshake, reverse proxy, and load-balancing mechanics: Part 05 owns the general mechanisms; this chapter applies them to the Ingress boundary.
- Provider load balancer provisioning, certificates, and network integrations: Part 09 owns product and service mechanics.
- General security and authorization threat modeling: Part 15 owns those foundations.

## Reconciliation note

Ingress is not a Service type and an Ingress resource alone does not implement a data path. During the Part 12 merge, preserve the distinction between upstream API guarantees, controller-specific annotations/features, provider load balancer behavior, and Gateway API add-on support. The upstream Kubernetes Ingress API is stable and frozen; do not misclassify it as removed or force a migration absent a workload requirement.
