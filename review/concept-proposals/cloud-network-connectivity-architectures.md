# Cloud Network and Connectivity Architecture Concepts

Source: `10_Cloud_Architecture/CH03_Cloud_Network_and_Connectivity_Architectures.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Cloud network topology composition across workload, shared-service, and transit boundaries | CH03 Cloud Network and Connectivity Architectures | Cross-provider architecture choices for isolation, hub-and-spoke, transit, and mesh; Part 05 owns network mechanisms and Part 09 owns provider networking products. |
| Cloud network path and route-ownership contract | CH03 Cloud Network and Connectivity Architectures | Names owners and expected reachability, policy, DNS, observation, and failure behavior for a workload path; generic routing and security mechanics remain with Parts 05 and 15. |

## Recap-only concepts

- IP addressing, routing, DNS, NAT, firewalls, load balancing, VPN, and TLS mechanics: recap and link to Part 05.
- Provider network scopes, private endpoints, and connectivity products: recap and link to Part 09 CH05 and provider chapters.
- Cross-provider and hybrid deployment decision: Part 10 CH10 owns the broader architecture.
