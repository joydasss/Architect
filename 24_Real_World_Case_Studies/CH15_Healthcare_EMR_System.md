# Healthcare Electronic Medical Record System

Part: [24 — Real-World Architecture Case Studies](PART_OVERVIEW.md)

This case study designs an Electronic Medical Record (EMR) system that supports patient identity, encounters, clinical documentation, orders, results, consent, audit, interoperability, and downtime operations. The architecture must protect confidentiality while preserving safe access to current clinical information. Assumptions: the system serves multiple care locations and integrates with external laboratories and referral services; applicable regulations and clinical policies are verified with local owners.

## Frame Clinical Workflows and Safety Goals

Clinical data is authored by different roles and changes over time. An encounter may include notes, diagnoses, medications, orders, results, and amendments. Distinguish draft, signed, corrected, and imported information. Define which workflows require human attestation and which views may display delayed or incomplete data.

```mermaid
flowchart LR
    Patient[Patient identity and consent] --> Encounter[Clinical encounter]
    Clinician[Clinician workflow] --> Encounter
    Encounter --> Notes[Notes and diagnoses]
    Encounter --> Orders[Orders and referrals]
    Orders --> Lab[External laboratory]
    Lab --> Results[Results and provenance]
    Results --> Encounter
    Encounter --> Audit[Audit and access evidence]
    Patient --> Access[Consent-aware access policy]
    Access --> Encounter
```

The architecture should make data provenance, author, timestamp, source, and correction history visible. Clinical users need to distinguish verified from imported or patient-reported content. A fast interface must not imply that data is complete when an integration is delayed.

## Resolve Patient Identity Safely

Patient matching combines stable identifiers, demographic attributes, and context. False merges can expose or alter another person's record; false splits can hide critical history. Use confidence thresholds and human review for ambiguous matches. Do not treat a probabilistic match as authorization to merge records automatically.

```mermaid
flowchart TD
    Registration[Registration or external record] --> Identity[Collect verified identifiers]
    Identity --> Match[Match against patient index]
    Match --> Confidence{Match confidence and uniqueness}
    Confidence -->|High and policy permits| Link[Link to patient record]
    Confidence -->|Ambiguous| Review[Identity specialist review]
    Confidence -->|No match| Create[Create provisional record]
    Review -->|Confirmed| Link
    Review -->|Unresolved| Quarantine[Hold and prevent unsafe merge]
    Link --> Audit[Record evidence and reviewer]
    Create --> Audit
```

Define correction and merge procedures, including downstream systems, audit, and patient notification where required. Identity errors must be reversible through controlled correction, not hidden by overwriting identifiers.

## Enforce Consent and Purpose at Access

Access depends on authenticated user, clinical relationship, role, purpose, location, emergency context, and consent policy. Consent may differ by data type and care relationship. Emergency access (“break glass”) should be time-bounded, justified, visible to auditors, and reviewed after use.

```mermaid
sequenceDiagram
    actor Clinician
    participant App as Clinical application
    participant Policy as Consent and purpose policy
    participant Record as EMR record service
    participant Audit
    Clinician->>App: Request patient record
    App->>Policy: Check identity, role, relationship, and purpose
    Policy-->>App: Permit, deny, or require exception
    App->>Record: Read permitted data scope
    Record-->>App: Record sections with provenance
    App->>Audit: Record access, purpose, and policy result
    App-->>Clinician: Display authorized record
```

Do not rely solely on UI visibility to enforce access. Apply policy at service boundaries and propagate the permitted scope to downstream queries and caches. Audit access without copying unnecessary clinical content into logs.

## Interoperate With External Care Systems

Interoperability exchanges patient identity, encounters, orders, results, and referrals with external organizations. Contracts must define identifiers, provenance, time semantics, acknowledgements, corrections, and error handling. Imported data remains attributable to its source; it should not silently become locally verified clinical advice.

```mermaid
flowchart LR
    EMR[Local EMR] --> Adapter[Interoperability adapter]
    Adapter --> Contract[Versioned clinical data contract]
    Contract --> Lab[Laboratory system]
    Contract --> Referral[Referral partner]
    Lab -->|Result and source ID| Adapter
    Referral -->|Status and acknowledgment| Adapter
    Adapter --> Validate[Validate identity, schema, and provenance]
    Validate -->|Pass| Record[Attach to correct encounter]
    Validate -->|Ambiguous or invalid| Queue[Clinical integration review queue]
    Record --> Audit[Audit and source lineage]
```

External availability and formats vary. Queue retries safely, deduplicate by source identifiers, and route clinical ambiguity to an accountable role. Reconciliation should identify missing or duplicate results before clinicians rely on the record.

## Design Downtime Access and Recovery

Care may continue during network, identity, or application outages. Define which read-only information can be accessed locally, how freshness is labeled, which actions are unavailable, and how offline changes are reconciled. Downtime procedures need controlled access, audit continuity, and a process for reconciling handwritten or temporary records.

```mermaid
stateDiagram-v2
    [*] --> Normal
    Normal --> Degraded: Network or identity dependency impaired
    Degraded --> Downtime: Critical EMR path unavailable
    Downtime --> ReadOnly: Approved cached records accessible
    ReadOnly --> Recovery: Core service restored
    Downtime --> Recovery: Core service restored
    Recovery --> Reconcile: Validate temporary records and timestamps
    Reconcile --> Normal: Merge verified updates and audit
    Reconcile --> Review: Conflict or patient identity ambiguity
    Review --> Normal: Authorized resolution recorded
```

Define data age limits for offline views and which clinical actions require real-time verification. Do not make stale cached information appear current. Test downtime access, recovery, duplicate documentation prevention, and identity conflict resolution with clinical and operational teams.

## Worked Case: Emergency Department Result Review

A clinician orders a laboratory test during an emergency visit. The EMR verifies patient identity and clinician authority, records the order, and sends it to the lab. The lab returns a result with a source identifier and timestamp. The EMR validates the patient and encounter mapping, attaches the result with provenance, and notifies the clinician. If the network is unavailable, the workflow marks the order pending and uses the approved downtime process.

A delayed result arrives after the encounter is closed. The system links it to the original encounter and alerts the responsible clinical role rather than creating a duplicate visit. Consent and audit policies govern access and disclosure. During reconciliation, an identity mismatch routes to a specialist for review; the result is not merged into a likely patient record automatically.

## Review Questions

1. How are authored, imported, draft, and corrected clinical records distinguished?
2. What evidence is sufficient for an automatic patient match?
3. Which identity, purpose, and consent attributes constrain access?
4. How are delayed or duplicate external results reconciled?
5. What can clinicians access and document during downtime?

EMR architecture must preserve clinical context, patient identity, consent, and provenance across normal and degraded operation. Keep access policy authoritative, route ambiguous matching to human review, and exercise downtime and reconciliation with the people who deliver care.
