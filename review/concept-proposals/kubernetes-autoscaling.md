# Kubernetes Autoscaling Concept Proposals

Source: `12_Kubernetes/CH09_Autoscaling.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| HPA feedback control, metric contract, and scaling behavior | CH09 Autoscaling | Owns `autoscaling/v2` signals, target metrics, multiple-metric selection, readiness handling, tolerance, stabilization, and rate policies. Part 19 owns general performance measurement and capacity planning. |
| Workload replica scaling versus Pod resource resizing | CH09 Autoscaling | Owns the Kubernetes HPA/VPA distinction and interaction risks. CH01 owns Pod requests/limits; VPA installation and mode-specific behavior must be version-checked. |
| Workload-to-node autoscaling handoff | CH09 Autoscaling | Owns the control-loop interaction from added replicas to Pending Pods and node provisioning/consolidation. Part 09 owns provider capacity, managed-cluster integrations, quotas, and product-specific configurations. |
| Node autoscaler scheduling-constraint contract | CH09 Autoscaling | Owns how requests, affinity, taints, topology, and volume constraints determine schedulability and autoscaler feasibility. CH06 owns Kubernetes scheduling semantics in depth; CH07 owns volume provisioning/topology. |
| Event-driven and scheduled workload scaling | CH09 Autoscaling | Owns the Kubernetes integration pattern and scaling-to-zero constraints. KEDA and metric adapters are add-ons; event source contracts and business-level demand forecasts remain with their domain owners. |

## Recap-only concepts

- Deployment replica authority, rollout behavior, and Git desired-state conflicts: CH02 Deployments.
- Pod requests, limits, readiness, startup, and disruption behavior: CH01 Pods.
- Kubernetes scheduler placement and topology mechanisms: CH06 Networking and scheduling constraints; CH07 Storage topology.
- Metrics instrumentation, service objectives, and performance experiments: Part 14 Observability and Part 19 Performance Engineering.
- Cloud quotas, machine products, managed-cluster node groups, pricing, and provider autoscaling integration: Part 09 Cloud Computing.

## Reconciliation note

Keep this chapter focused on Kubernetes control loops and their interfaces. Do not make provider node types or managed-cluster behavior normative here. Distinguish official core APIs from separately installed VPA, KEDA, and metrics adapters, and attach feature maturity to the upstream version under discussion.
