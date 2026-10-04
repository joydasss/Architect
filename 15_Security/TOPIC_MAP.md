# Part 15 — Security Topic Map

This map records the coverage contract for Part 15's sixteen security chapters. The part teaches provider-neutral security principles and mechanisms spanning identity, authorization, cryptography, threat analysis, software lifecycle, containers, and supply chain evidence. Technology-specific implementations remain with their platform owners.

## Part-wide ownership boundaries

- Part 15 owns security foundations, threat modeling, access-control concepts, secure development lifecycle, container/image controls, and software supply chain integrity.
- Part 05 owns network protocol, Transport Layer Security (TLS), certificate, and operating-system mechanics; Part 08 owns API architecture; Part 09 owns provider IAM/key/secret products; Part 12 owns Kubernetes-native security application.
- Part 13 owns delivery workflow implementation; Part 15 defines the security properties and verification evidence those workflows should enforce.
- Security controls require explicit threat assumptions, authority, evidence, failure behavior, exception ownership, and recovery. Compliance checklists do not replace risk analysis.

## Cross-part stakeholders and quality scenarios

- Security engineers need assets, threat actors, trust boundaries, control evidence, and residual risk.
- Developers and platform teams need usable identity, policy, secret, encryption, and artifact-verification controls integrated into delivery.
- Operators need detection, credential revocation, incident containment, and recovery paths.
- Important scenarios include a stolen credential with excessive authority; a vulnerable dependency entering production; a secret copied into logs; an image signature verified against the wrong identity; and a high-risk threat discovered before architecture freeze.

## Risk and Identity Foundations

### CH01 OWASP Top 10

**Reader outcome:** Use the Open Worldwide Application Security Project (OWASP) Top 10 as an awareness and risk-discovery aid without treating it as a complete threat model.
**Coverage:** Current category set, representative application risks, attack preconditions, impact, mitigations, verification, and version awareness.
**Boundaries:** CH12 threat modeling provides system-specific analysis; CH02-03 own authentication/authorization detail; Part 08 owns API architecture.
**Diagram opportunities:** (1) vulnerability-to-attack-path chain; (2) risk category mapped to trust boundary; (3) control/verification layer; (4) exploit precondition and impact tree; (5) Top 10 limitation versus system threat model.

### CH02 Authentication

**Reader outcome:** Verify a claimant's identity using appropriate factors, credential lifecycle, and protocol without confusing identity proof with permission.
**Coverage:** Passwords, multi-factor authentication, federated identity, sessions, credential storage, phishing resistance, recovery, and revocation.
**Boundaries:** Part 05 owns TLS/certificate mechanics; CH06 OAuth and CH07 OIDC own protocol flows; Part 09 owns provider identity services.
**Diagram opportunities:** (1) credential enrollment and login; (2) factor combination; (3) identity federation trust; (4) session/token lifecycle; (5) recovery and revocation path.

### CH03 Authorization

**Reader outcome:** Restrict actions on resources through explicit policy evaluation, least privilege, and separation of duties.
**Coverage:** Subject/action/resource/context, policy models, allow/deny, inheritance, delegation, privilege escalation, review, and audit.
**Boundaries:** CH04 RBAC and CH05 ABAC own concrete authorization models; Part 08 applies authorization to APIs; Part 09 owns provider policy syntax.
**Diagram opportunities:** (1) request-to-policy evaluation; (2) privilege inheritance path; (3) delegation and separation of duties; (4) effective permission analysis; (5) access review and revocation.

### CH04 RBAC (Role-Based Access Control)

**Reader outcome:** Assign permissions through roles and bindings while preventing role explosion and accidental privilege inheritance.
**Coverage:** Users/groups/roles, role assignment, scope, hierarchy, least privilege, administrative roles, lifecycle, and audit.
**Boundaries:** Kubernetes RBAC mechanics belong to Part 12; provider IAM role syntax belongs to Part 09.
**Diagram opportunities:** (1) user-to-role-to-permission graph; (2) scoped role inheritance; (3) role explosion and consolidation; (4) privileged role elevation; (5) joiner/mover/leaver access lifecycle.

### CH05 ABAC (Attribute-Based Access Control)

**Reader outcome:** Evaluate access using subject, resource, action, and environmental attributes with governance over attribute quality and policy complexity.
**Coverage:** Attribute sources, policy expressions, contextual decisions, delegation, policy testing, explainability, and failure behavior.
**Boundaries:** CH04 owns role-centric policy; Part 09 owns provider ABAC implementations.
**Diagram opportunities:** (1) subject/resource/context attribute evaluation; (2) attribute provenance path; (3) policy decision and explanation; (4) attribute change revoking access; (5) ABAC versus RBAC decision tree.

### CH06 OAuth

**Reader outcome:** Apply OAuth delegated authorization flows with correct client, grant, scope, redirect, and token handling.
**Coverage:** Roles, authorization code with Proof Key for Code Exchange (PKCE), client credentials, scopes, consent, refresh rotation, token storage, and threat mitigations.
**Boundaries:** Part 05 CH19 owns protocol mechanics; CH07 OIDC adds authentication; Part 08 owns API contract security.
**Diagram opportunities:** (1) authorization code with PKCE; (2) service-to-service client credentials; (3) scope/consent grant; (4) refresh-token rotation and reuse; (5) public versus confidential client boundary.

### CH07 OIDC (OpenID Connect)

**Reader outcome:** Authenticate users through OpenID Connect (OIDC) while validating issuer, audience, nonce, signature, and session behavior.
**Coverage:** Discovery, ID token, claims, JWKS, authorization code, logout, session management, identity mapping, and federation.
**Boundaries:** Part 05 CH20 owns OIDC wire flow; CH06 owns OAuth authorization; Part 09 owns provider identity products.
**Diagram opportunities:** (1) OIDC login and callback; (2) issuer discovery and key validation; (3) claims-to-local-identity mapping; (4) RP session/logout; (5) federation trust configuration.

### CH08 Zero Trust

**Reader outcome:** Apply continuous, context-aware verification and least privilege across users, workloads, devices, networks, and data.
**Coverage:** Never-trust assumptions, identity-centric policy, device/workload posture, segmentation, continuous evaluation, control-plane/data-plane enforcement, and migration.
**Boundaries:** Part 09 owns provider implementations; Part 12 applies Zero Trust to Kubernetes; Part 05 owns network primitives.
**Diagram opportunities:** (1) request decision across identity/device/resource context; (2) implicit perimeter versus segmented access; (3) workload identity-to-service path; (4) continuous posture re-evaluation; (5) staged Zero Trust adoption.

## Data and Cryptographic Controls

### CH09 Secrets Management

**Reader outcome:** Store, deliver, rotate, and revoke secrets with minimized copies and explicit consumer refresh behavior.
**Coverage:** Secret classification, vault/KMS boundaries, dynamic credentials, access policy, rotation, caching, auditing, and incident response.
**Boundaries:** Part 09 owns provider secret services; Part 12 CH08/CH13 own Kubernetes secret and volume use; CH14 owns provider observability products.
**Diagram opportunities:** (1) workload identity to secret retrieval; (2) rotation with overlapping versions; (3) dynamic credential issuance; (4) secret cache and refresh; (5) leak detection and revocation.

### CH10 Encryption

**Reader outcome:** Choose and operate encryption in transit, at rest, and in use with key ownership, lifecycle, and threat limits stated.
**Coverage:** Symmetric/asymmetric primitives at the conceptual level, TLS, disk/database encryption, envelope encryption, key rotation, cryptographic agility, and performance.
**Boundaries:** Part 05 owns TLS and protocol details; Part 09 owns managed key services; this chapter owns general security properties and trade-offs.
**Diagram opportunities:** (1) data in transit/at rest/in use; (2) envelope encryption hierarchy; (3) key rotation with decrypt-old/encrypt-new; (4) key access and separation of duties; (5) encryption boundary and residual plaintext exposure.

### CH11 PKI (Public Key Infrastructure)

**Reader outcome:** Design certificate authorities, certificate issuance, trust chains, renewal, and revocation as an operational system.
**Coverage:** X.509 certificates, CA hierarchy, signing, SAN/usage, issuance protocols, trust distribution, revocation, rotation, and key custody.
**Boundaries:** Part 05 CH15 owns certificate/TLS operations; Part 09 owns cloud certificate services.
**Diagram opportunities:** (1) root/intermediate/leaf chain; (2) issuance and validation; (3) renewal and trust-store update; (4) compromise and revocation; (5) key custody/CA separation.

### CH12 Threat Modeling

**Reader outcome:** Identify assets, actors, trust boundaries, abuse cases, and mitigations early enough to change architecture.
**Coverage:** System decomposition, data-flow diagrams, attacker goals, STRIDE and complementary methods, attack trees, risk ranking, assumptions, mitigation ownership, and refresh triggers.
**Boundaries:** Part 01 owns general architecture decisions; domain chapters provide control mechanics; this chapter owns reusable threat-analysis method.
**Diagram opportunities:** (1) system data-flow and trust boundaries; (2) STRIDE threat-to-element matrix; (3) attack tree; (4) risk-ranked mitigation backlog; (5) threat-model update after architecture change.

## Secure Engineering and Supply Chain

### CH13 Secure SDLC (Software Development Lifecycle)

**Reader outcome:** Integrate security requirements, review, testing, release, and response into the software lifecycle with evidence and accountable owners.
**Coverage:** Security requirements, design review, code review, static/dynamic/dependency testing, secrets, release gates, vulnerability handling, and feedback loops.
**Boundaries:** Part 13 owns CI/CD tools; Part 15 owns security practices and acceptance evidence.
**Diagram opportunities:** (1) security activities across development lifecycle; (2) code-to-release evidence gates; (3) vulnerability intake and triage; (4) exception/expiry workflow; (5) incident learning back into requirements.

### CH14 Container Security

**Reader outcome:** Reduce container and orchestration risk across image build, runtime identity, isolation, host exposure, and patch lifecycle.
**Coverage:** Image minimization, non-root execution, capabilities, seccomp, namespaces/cgroups, runtime isolation, secrets, registry access, node hardening, and Kubernetes controls.
**Boundaries:** Part 05 CH28 owns container primitives; Part 12 CH13 applies Kubernetes security; Part 09 owns container registry products.
**Diagram opportunities:** (1) image-to-runtime trust chain; (2) container/host isolation boundary; (3) privilege/capability reduction; (4) admission-to-runtime image policy; (5) node compromise blast radius.

### CH15 Supply Chain Security

**Reader outcome:** Verify provenance and integrity across source, dependencies, build systems, artifacts, registries, and deployment.
**Coverage:** Dependency risks, build isolation, artifact signing, provenance/attestation, software bill of materials (SBOM) usage, registry policy, key trust, verification, and incident response.
**Boundaries:** Part 13 implements pipeline stages; CH16 owns SBOM inventory practices; Part 09 owns registry services.
**Diagram opportunities:** (1) source-to-build-to-artifact chain; (2) dependency provenance graph; (3) signer identity and trust roots; (4) admission verification decision; (5) compromised dependency response and rebuild.

### CH16 SBOM (Software Bill of Materials)

**Reader outcome:** Produce and use a machine-readable inventory of software components to support vulnerability, license, provenance, and incident response.
**Coverage:** Component identity, direct/transitive dependencies, formats, generation points, merge/correlation, vulnerability matching, freshness, ownership, and distribution.
**Boundaries:** CH15 owns end-to-end supply chain security; Part 13 owns build pipeline integration; Part 09 owns registry storage.
**Diagram opportunities:** (1) source/build/artifact SBOM generation; (2) dependency graph and component lineage; (3) vulnerability matching and triage; (4) SBOM update across release versions; (5) incident query from component to deployed workload.
