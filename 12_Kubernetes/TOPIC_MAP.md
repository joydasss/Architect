# Part 12 — Kubernetes Topic Map

This map is the coverage contract for Part 12's fifteen chapters. The part teaches Kubernetes workload and platform architecture through the upstream API model: declarative resources, controllers, scheduling, service discovery, network and storage abstractions, scaling, extensibility, packaging, GitOps, security, observability, and fleet boundaries. Use the Kubernetes documentation for the exact stable API behavior and version used by each chapter. Version-sensitive APIs, feature gates, controller behavior, and tooling must be identified rather than treated as timeless defaults.

## Part-wide ownership boundaries

- Part 12 owns Kubernetes-native resource semantics, controller interactions, workload packaging and reconciliation, cluster-level application architecture, and decisions about Kubernetes operating practices.
- Part 09 CH08 owns cloud-managed Kubernetes service choices: provider control-plane and node responsibilities, managed modes and pools, cloud networking/storage/IAM integration, provider upgrades, and managed-cluster selection. Part 12 may recap these boundaries but must not re-teach provider service mechanics.
- Part 09 CH07 owns cloud container-execution alternatives and image-registry service choices. Part 05 CH28 owns operating-system container primitives such as namespaces and cgroups; Part 05 CH25 owns kernel memory behavior. Part 12 explains how Kubernetes consumes these foundations, not how the kernel implements them.
- Part 07 owns general distributed-systems semantics such as retries, idempotency, consistency, and failure handling. Part 20 owns general architecture patterns such as service decomposition. Part 12 applies those ideas to Kubernetes controllers, resources, and failure domains.
- Part 09 CH05 owns cloud networking products, CH06 storage products, CH09 IAM mechanics, CH10 monitoring products, and CH13 secrets service mechanics. Part 12 owns Kubernetes integration and workload implications; avoid duplicating provider-specific service catalogs.
- Part 13 owns general DevOps and delivery practice. CH11 Helm and CH12 Argo CD own their Kubernetes-specific packaging and reconciliation workflows. Part 14 owns general observability architecture and operations; CH14 applies telemetry concepts to Kubernetes resources and cluster/workload boundaries. Part 15 owns security foundations and threat modeling; CH13 applies them to Kubernetes identity, admission, isolation, and runtime concerns.
- Distinguish upstream Kubernetes API behavior from implementation-specific behavior supplied by kubelet, a container runtime, a Container Network Interface (CNI) plugin, a Container Storage Interface (CSI) driver, a cloud controller, a network data plane, or an optional add-on. Name the implementation dependency where it changes the conclusion.
- Avoid implying that Kubernetes itself supplies a complete ingress controller, network-policy enforcement, storage backend, metrics adapter, policy engine, image scanner, service mesh, or multi-cluster control plane. Identify the contract and its owner.

## Cross-part stakeholder concerns and assumptions

- Application teams need predictable rollout, service discovery, resource allocation, and recovery without becoming cluster administrators.
- Platform teams need an understandable API and controller surface, bounded blast radius, supported versions, safe upgrades, capacity visibility, and sustainable ownership of cluster add-ons.
- Security and compliance stakeholders need workload identity, least privilege, tenant boundaries, policy enforcement, image provenance, secret handling, auditability, and controlled emergency access.
- SRE and operations stakeholders need failure signals at pod, controller, node, cluster, dependency, and user-journey levels, with tested response and recovery procedures.
- Business owners need availability, latency, data durability, recovery objectives, predictable operating cost, and a clear decision when Kubernetes is more operational complexity than value.
- Assume a supported Kubernetes distribution and version, an identified container runtime and networking/storage implementations, cluster ownership, and a deployment authority. Where these are unknown, record them as constraints and evidence gaps.
- Important quality scenarios include: a node drain during a zone disruption without dropping the minimum healthy replicas; a rollout that stalls before exposing an incompatible revision; a network policy change that blocks only the intended tenant path; a persistent-volume restore that recovers both data and application authority; and a fleet upgrade that preserves service objectives across clusters.

## CH01 Pods

**Reader outcome:** Explain the Pod as Kubernetes' scheduling and co-lifecycle unit; design containers in a Pod only when their networking, storage, and lifecycle coupling justifies it.

**Coverage and mechanisms:** Pod API shape and immutable identity; one or more containers sharing network namespace, IP, ports, and declared volumes; regular, init, and sidecar container roles; sandbox creation and container startup; restart policy and phase/status distinction; readiness, liveness, and startup probes and their different effects; resource requests/limits and QoS implications; graceful termination, preStop, termination grace, eviction, restart, and rescheduling; environment/configuration injection and downward API; Pod security context recap with CH13 ownership; logs/metrics recap with CH14 ownership. Explain why a Pod is ephemeral and why a higher-level controller normally owns replacement.

**Decision concerns and evidence:** When to colocate helpers versus use separate Deployments; failure coupling, resource contention, rollout coupling, shared identity and secret exposure, startup ordering, and drain behavior. Validate with pod events, probe outcomes, termination traces, resource measurements, and a node-drain scenario.

**Boundaries:** Recap container image/runtime internals to Part 05 and cloud execution choices to Part 09; deployment rollout belongs to CH02; ReplicaSet ownership belongs to CH03.

**Diagram opportunities:** (1) Pod sandbox, containers, shared network and volumes; (2) init/regular/sidecar startup and shutdown ordering; (3) probe state transitions and readiness effects; (4) Pod lifecycle from admission through termination/eviction; (5) scheduling request, node fit, and QoS/resource pressure.

## CH02 Deployments

**Reader outcome:** Design and operate Deployment-based stateless workload rollouts with explicit availability, surge, progress, rollback, and revision semantics.

**Coverage and mechanisms:** Deployment-to-ReplicaSet-to-Pod ownership; selector and template-hash revisioning; desired versus observed replicas; rolling update controls (`maxSurge`, `maxUnavailable`), progress deadlines, paused rollouts, revision history and rollback; readiness and startup gates; rollout behavior during insufficient capacity or failing probes; deployment strategy alternatives including recreate; API compatibility and schema coordination; disruption budgets as a separate voluntary-disruption control rather than a rollout substitute.

**Decision concerns and evidence:** Availability versus rollout speed, surge capacity versus cost, gradual rollout versus recreate, rollback safety after external side effects, and changes that cannot be reversed. Validate with rollout status, events, revision comparison, failure injection, and a test where the new revision never becomes ready.

**Boundaries:** CH03 teaches ReplicaSet reconciliation and adoption mechanics; CH01 owns Pod lifecycle; Part 13 owns general release engineering. Kubernetes rollout behavior is the focus here.

**Diagram opportunities:** (1) Deployment/ReplicaSet/Pod ownership graph; (2) rolling-update timeline with availability and surge; (3) rollout state machine with pause, progress deadline, failure, and rollback; (4) template revision/hash transition; (5) incompatible application/schema change and safe staged rollout.

## CH03 ReplicaSets

**Reader outcome:** Explain the ReplicaSet controller's set-based reconciliation, how it maintains Pod cardinality, and why it is usually managed indirectly through Deployments.

**Coverage and mechanisms:** selector-based ownership; desired replica count versus matching Pods; reconciliation loop and eventual convergence; create/delete decisions; adoption and release of orphan Pods under selector rules; overlapping selector hazards; scale changes and race conditions; labels as set membership; relation to Deployment-managed history and rollouts; appropriate direct ReplicaSet use only where no rollout history is needed.

**Decision concerns and evidence:** Avoid manual Pod replacement, overlapping selectors, and competing controllers. Diagnose excess, missing, or adopted Pods through owner references, selector matches, events, and controller status. Compare direct ReplicaSet management with Deployment ownership.

**Boundaries:** Do not duplicate Deployment rollout strategy or re-teach general controller theory; explain the ReplicaSet-specific controller and link CH02 for the owning higher-level workflow.

**Diagram opportunities:** (1) Desired/observed replica reconciliation loop; (2) selector and label-set membership; (3) orphan Pod adoption/release; (4) Deployment managing successive ReplicaSets; (5) competing selectors causing unexpected ownership/cardinality.

## CH04 Services

**Reader outcome:** Choose and troubleshoot Kubernetes Service abstractions for stable discovery and traffic distribution across ephemeral Pods.

**Coverage and mechanisms:** selector-backed virtual service and EndpointSlice membership; ClusterIP, headless, NodePort, LoadBalancer, and ExternalName intent and trade-offs; kube-proxy or alternative data-plane implementation boundary; port/targetPort/nodePort mapping; session affinity, topology hints/locality where supported, readiness and endpoint withdrawal; named ports; external backends without selectors; DNS names and namespace scope; service versus ingress/gateway responsibility; source-IP and health-check caveats.

**Decision concerns and evidence:** Stable service address versus direct Pod discovery; internal-only versus externally exposed; locality versus even distribution; preserving client IP versus proxying; controller-specific behavior. Validate endpoints, DNS lookup, packet path, readiness changes, and connection draining.

**Boundaries:** CH05 owns HTTP ingress and gateway routing; CH06 owns CNI/network policy/data-plane details; Part 09 owns cloud load balancer products.

**Diagram opportunities:** (1) Service selector to EndpointSlices and changing Pod endpoints; (2) request path through ClusterIP data plane; (3) NodePort/LoadBalancer exposure comparison; (4) readiness withdrawal and connection-drain sequence; (5) service DNS and namespace-qualified discovery.

## CH05 Ingress

**Reader outcome:** Design HTTP(S) north-south routing using Kubernetes Ingress resources and controller contracts, and choose when Gateway API or provider-managed routing is more appropriate.

**Coverage and mechanisms:** distinction between Ingress API object and controller implementation; host/path rules, TLS references, class selection, default backend and annotations; controller reconciliation and external load-balancer configuration; request flow and health checking; controller availability and upgrade ownership; TLS termination and certificate lifecycle boundary; path precedence and rewrite portability; status/address reporting; limitations of the Ingress API and the role of Gateway API as a distinct evolving API.

**Decision concerns and evidence:** Shared versus dedicated controllers, tenant isolation, portability versus implementation features, TLS termination boundary, and controller retirement/support risk. Validate route behavior, policy, certificate renewal, controller events, health checks, and failure of the controller or load balancer.

**Boundaries:** Avoid implying that an Ingress resource alone implements routing. Part 09 owns cloud load-balancer products and certificates; Part 05 owns generic reverse proxy/load balancing; Part 15 owns generic TLS/security concepts.

**Diagram opportunities:** (1) Ingress resource-to-controller reconciliation; (2) client-to-load-balancer/controller/service/Pod request path; (3) host/path/TLS rule decision tree; (4) shared versus per-tenant controller trust boundary; (5) Ingress versus Gateway API responsibility/extension comparison.

## CH06 Networking

**Reader outcome:** Explain Kubernetes pod networking, service networking, policy, name resolution, and egress as a set of contracts implemented by cluster components and plugins.

**Coverage and mechanisms:** Kubernetes network model and Pod IP reachability expectation; CNI responsibilities for sandbox attachment and address allocation; Service virtual IP and data-plane implementation; DNS discovery; NetworkPolicy selection and ingress/egress semantics, including default-deny composition and enforcement dependency; host-network and node paths; egress/NAT, externalName and private dependency routing; MTU, address exhaustion, route overlap, dual-stack considerations; network troubleshooting from object to packet path.

**Decision concerns and evidence:** CNI choice, routable Pod IPs versus overlay, policy enforcement and plugin feature support, tenant segmentation, address planning, hybrid connectivity, and failure isolation. Validate actual packet paths, effective policy, DNS, MTU, scale limits, and provider integration.

**Boundaries:** Part 05 owns TCP/IP, DNS, firewalls, NAT, and routing fundamentals; Part 09 owns provider VPC/VNet and managed CNI mechanics; CH04 owns service abstraction; CH05 owns HTTP ingress.

**Diagram opportunities:** (1) Pod-to-Pod, Pod-to-Service, Pod-to-external flows; (2) CNI sandbox attachment and address lifecycle; (3) Service virtual IP packet transformation; (4) NetworkPolicy selector composition and allowed paths; (5) DNS/egress path including node, NAT, and external dependency.

## CH07 Storage

**Reader outcome:** Select Kubernetes storage abstractions and CSI-backed provisioning for workload data based on lifecycle, topology, access, performance, and recovery needs.

**Coverage and mechanisms:** StorageClass and dynamic provisioning; PersistentVolume/PersistentVolumeClaim binding; CSI controller and node responsibilities; access modes and their actual concurrency semantics; volume mode filesystem/block; topology-aware binding and zone constraints; reclaim policy, expansion, snapshots and clones where supported; static versus dynamic provisioning; storageclass defaults; provider-specific provisioner boundaries; backup and restore relationship to Kubernetes object recovery.

**Decision concerns and evidence:** Durable database volume versus disposable scratch; zone-local versus portable storage; filesystem versus block; performance class, attach limits, expansion, and recovery objective. Validate binding, attach/detach after reschedule, topology, restore, and application consistency.

**Boundaries:** CH08 owns Pod volume declarations and in-Pod mount lifecycle; Part 09 CH06 owns storage products, durability and service-level contracts; Part 06 owns database internals.

**Diagram opportunities:** (1) PVC-to-PV-to-CSI backend binding lifecycle; (2) scheduling and topology-aware volume binding; (3) attach/mount/unmount across Pod rescheduling; (4) reclaim-policy lifecycle after PVC deletion; (5) snapshot/restore dependency chain including application consistency.

## CH08 Volumes

**Reader outcome:** Choose and operate Pod volume types while reasoning about data lifetime, mount behavior, sharing, security, and rescheduling.

**Coverage and mechanisms:** volume and volumeMount model; emptyDir lifecycle and medium; projected volumes for ConfigMap, Secret, service account token, and downward API; hostPath risks; persistentVolumeClaim reference; subPath behavior and update caveats; read-only and mount propagation where relevant; init/sidecar shared-file patterns; access by multiple containers; container restart versus Pod replacement effects; filesystem ownership and security context recap.

**Decision concerns and evidence:** Ephemeral versus durable state, shared scratch versus separate Pods, projected update behavior, data loss on Pod replacement, and node coupling. Validate mount visibility, ownership, update propagation, restart and reschedule behavior, and backup expectations.

**Boundaries:** CH07 owns storage provisioning and PV/PVC/CSI architecture. Part 05 owns container filesystem internals; CH13 owns secret exposure/access controls.

**Diagram opportunities:** (1) Pod volume declaration-to-container mount graph; (2) lifetime comparison for container, Pod, and PVC-backed data; (3) projected-volume update and application reload path; (4) shared volume across init/sidecar/application containers; (5) hostPath versus PVC placement and failure boundary.

## CH09 Autoscaling

**Reader outcome:** Design Kubernetes scaling loops that respond to workload demand without oscillation, under-capacity, or downstream overload.

**Coverage and mechanisms:** Horizontal Pod Autoscaler (HPA) control loop and metrics; resource versus custom/external metrics; requests as utilization denominator; scale-up/down stabilization and policies; Vertical Pod Autoscaler (VPA) recommendation/restart modes and compatibility caveats; cluster/node autoscaler or provisioner interaction; pending Pods and unschedulable reasons; scale-to-zero/event-driven options as implementation-specific; quotas, warm-up, startup/readiness, PodDisruptionBudgets, and topology; feedback-loop conflicts.

**Decision concerns and evidence:** Replicas versus per-Pod sizing, scheduled versus demand-driven capacity, cold-start tolerance, resource requests quality, metric lag, and downstream limits. Validate step response, scale-down safety, saturation, quota, and peak plus recovery conditions.

**Boundaries:** Part 09 owns provider node capacity products; Part 19 owns performance testing; Part 07 owns generic feedback/concurrency concepts. Keep Kubernetes autoscaler mechanics distinct from application-level elasticity.

**Diagram opportunities:** (1) HPA metrics-to-replica feedback loop; (2) HPA, scheduler, and node autoscaler interaction; (3) scale-out/scale-in timing and hysteresis; (4) CPU request misconfiguration skewing utilization target; (5) scaling under downstream saturation and backpressure.

## CH10 Operators

**Reader outcome:** Explain the Operator pattern and design custom controllers that safely reconcile domain-specific APIs over time.

**Coverage and mechanisms:** custom resource definition (CRD) schema and version lifecycle; custom resource as desired intent; controller watch, work queue, reconcile loop, idempotency and eventual convergence; status and conditions; finalizers and deletion; generation/resourceVersion; retries, conflict handling and exponential backoff at controller level; ownership references; leader election and HA; RBAC, scope, conversion and admission webhooks; upgrade, uninstall, data migration, and recovery; when a controller is preferable to a Helm chart or human runbook.

**Decision concerns and evidence:** ongoing automation value versus control-plane/API burden, blast radius, safe defaulting, reversibility, and support ownership. Validate duplicate events, controller restart, partial reconciliation, CRD version migration, deletion finalizer failure, and least-privilege access.

**Boundaries:** Part 07 owns general reconciliation/distributed-systems concepts; CH11 owns Helm packaging; CH12 owns GitOps. Operators apply control loops to domain lifecycle.

**Diagram opportunities:** (1) desired custom resource to controller to external state feedback; (2) reconcile loop with retries/idempotency; (3) CRD versions/conversion and stored-object migration; (4) finalizer-driven deletion state machine; (5) operator deployment, RBAC, webhook, and managed-resource trust boundary.

## CH11 Helm

**Reader outcome:** Package, configure, distribute, and upgrade Kubernetes applications with Helm while controlling template complexity, release state, and supply-chain risk.

**Coverage and mechanisms:** chart structure, templates, values, helper templates, dependencies, schemas and validation; rendered manifests and API-version compatibility; install/upgrade/uninstall and release history; hooks and lifecycle hazards; chart repositories and OCI distribution; values layering and secret boundaries; library charts and versioning; testing/linting/diff; rollback limitations when state or CRDs changed; provenance/signature verification; comparison with raw manifests, Kustomize, Operators, and GitOps.

**Decision concerns and evidence:** reusable chart abstraction versus opaque templating, per-environment configuration, chart/app version compatibility, hooks, ownership conflicts, and release rollback. Validate rendered manifests, upgrade from prior release, dependency integrity, secret handling, and failure cleanup.

**Boundaries:** Part 13 owns general delivery pipeline practice; CH12 owns GitOps reconciliation; Part 09 owns registries. Explain Helm-specific mechanics, not generic CI/CD.

**Diagram opportunities:** (1) chart source/values/template/rendered-resource pipeline; (2) values precedence and configuration boundary; (3) Helm release lifecycle and rollback; (4) dependency/provenance supply chain; (5) Helm versus Kustomize/Operator/GitOps decision tree.

## CH12 Argo CD

**Reader outcome:** Design GitOps delivery with Argo CD by making desired-state ownership, synchronization, drift handling, health, and promotion boundaries explicit.

**Coverage and mechanisms:** Git as desired-state source; application and AppProject concepts; repo-server rendering, application controller reconciliation, API server and cache; sync, prune, self-heal, health assessment; automated/manual sync, sync waves/hooks, retry; ApplicationSet/fleet templating; multi-source and environment promotion; bootstrap and root-app patterns; secret integration; RBAC, project isolation and repository credentials; drift and emergency changes; rollback and Git revert differences; HA, upgrades and recovery.

**Decision concerns and evidence:** pull-based versus push-based delivery, source-of-truth integrity, emergency break-glass, prune blast radius, tenant boundaries, monorepo/multi-repo organization, and promotion safety. Validate drift correction, failed sync, deleted resource behavior, repo outage, credential revocation, and recovery from controller failure.

**Boundaries:** Part 13 owns general Git and pipeline mechanics; CH11 owns Helm packaging; CH10 owns Operator controller pattern; Part 15 owns security foundations. Verify current Argo CD version behavior and distinguish project configuration from Kubernetes RBAC.

**Diagram opportunities:** (1) Git-to-repo-server-to-controller-to-cluster reconciliation; (2) desired/actual drift and self-heal/prune decision; (3) multi-environment promotion with artifact/version evidence; (4) app-of-apps/ApplicationSet fleet ownership boundaries; (5) break-glass change and Git reconciliation sequence.

## CH13 Security

**Reader outcome:** Assess Kubernetes security architecture from API access through workload execution, isolation, supply chain, and incident response.

**Coverage and mechanisms:** threat boundaries and shared responsibility; API authentication, authorization, RBAC aggregation and impersonation; service accounts/workload identity and token projection; admission chain and policy; Pod Security Standards and security context; namespace limits and multi-tenancy; network policy enforcement; Secrets encryption/access/rotation; image provenance, registry trust, admission and runtime; node/control-plane responsibility; audit and detection; patching and version lifecycle; incident containment and forensic evidence. Distinguish defense-in-depth from duplicated controls with common authority.

**Decision concerns and evidence:** tenant threat model, cluster-per-tenant versus namespace isolation, privileged workload exceptions, break-glass, supply-chain trust, and residual provider boundary. Validate effective permissions, admission tests, namespace escape assumptions, image policy, network flows, secret rotation, audit retention, and incident exercises.

**Boundaries:** Part 15 owns general threat modeling and security concepts; Part 09 owns cloud IAM, key, network, and security services; CH06 owns Kubernetes network policy mechanics; CH14 owns telemetry architecture.

**Diagram opportunities:** (1) Kubernetes API authentication/authorization/admission request path; (2) human, CI, node, and workload identity trust graph; (3) image build-to-admission-to-runtime provenance path; (4) namespace/pod/network multi-tenant boundary map; (5) compromise detection, containment, evidence preservation, and recovery sequence.

## CH14 Observability

**Reader outcome:** Instrument and operate Kubernetes workloads by correlating application outcomes with Pod, controller, node, cluster, and dependency state.

**Coverage and mechanisms:** signals and ownership for application versus platform; resource and object-state metrics; logs, events, traces, and audit; labels and metadata cardinality; scrape and collection architecture; control-plane and managed-cluster visibility limitations; instrumentation sidecars/agents and daemonsets; probes versus monitoring; alerting on user objectives, pending workloads, saturation, restarts, volume and network failures; autoscaling metric source; retention, cost, tenancy, and access; debugging sequence from user symptom to Kubernetes object and node.

**Decision concerns and evidence:** instrumentation cost versus diagnostic value, shared telemetry isolation, managed-service visibility, cardinality, sampling, and alert ownership. Validate a failure injection from application symptom through alert, dashboard, owner response, and recovery evidence.

**Boundaries:** Part 14 owns generic observability practices and SLO mechanics; Part 09 CH10 owns cloud monitoring products. This chapter applies those methods to Kubernetes signals and control-plane boundaries.

**Diagram opportunities:** (1) workload/cluster signal source-to-collector-to-store topology; (2) user symptom correlation across service, Pod, node, and dependency; (3) metric-cardinality and tenant attribution path; (4) alert lifecycle from objective breach through response; (5) troubleshooting decision tree for Pending, CrashLoopBackOff, and service timeout.

## CH15 Multi-Cluster

**Reader outcome:** Decide when multiple clusters are justified and design fleet lifecycle, workload placement, traffic, identity, data, governance, and failure behavior.

**Coverage and mechanisms:** drivers for multiple clusters (security, blast radius, scale, region, lifecycle, compliance, team autonomy); cluster boundaries versus namespaces; fleet inventory and version policy; configuration and policy consistency; workload placement and failover; service discovery and inter-cluster traffic; identity federation and trust; data replication/authority; observability correlation; fleet upgrades; GitOps and policy propagation; disaster recovery versus active-active; control-plane/fleet-manager failure; cluster lifecycle and decommissioning.

**Decision concerns and evidence:** added platform cost and operational overhead versus isolation and independent lifecycle; central fleet control versus autonomy; active-active versus recovery standby; data locality and consistency. Validate a cluster-loss scenario, fleet rollout, identity revocation, data-authority transition, and recovery exercise.

**Boundaries:** Part 09 CH08 owns provider fleet products and region/account mechanics; Part 10 CH10 owns hybrid/multi-cloud architecture; Part 07 owns distributed data and service semantics; CH12 owns GitOps implementation; Part 14 owns observability platform patterns.

**Diagram opportunities:** (1) fleet topology and central versus workload ownership; (2) cluster-selection decision tree; (3) workload failover and data-authority transition; (4) fleet version/policy rollout with canary and rollback; (5) multi-cluster service and identity trust paths.

## Part-wide diagram quality expectation

The map names five distinct visual opportunities per chapter as a planning floor. Drafted chapters must use at least five substantive, nonredundant visuals placed by their explanations. Do not count tables, code blocks, or cosmetic variants. Use Kubernetes object ownership diagrams, request paths, controller state machines, packet/data-flow views, and decision trees where they clarify actual mechanics. Keep Mermaid syntax renderer-compatible and avoid hard tabs.

## Version and source discipline

For each chapter, verify current upstream Kubernetes API behavior and mark implementation-specific or version-sensitive statements. Prefer upstream documentation for Kubernetes objects and concepts; use official Helm and Argo CD documentation for their own tools. Provider docs belong in Part 09 links only where an integration boundary is being explained. Examples must identify required API versions, CRD/controller prerequisites, and whether they are illustrative manifests or deployable configuration.
