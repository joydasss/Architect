# Data Architecture

Part: [18 — Enterprise Architecture](PART_OVERVIEW.md)

Enterprise data architecture governs meaning, ownership, movement, quality, access, and lifecycle across applications and business domains. It distinguishes authoritative records from copies and derived products, and connects data use to accountable owners. Part 06 owns database and storage mechanics; Part 16 owns AI data techniques; Part 17 owns AI solution composition.

## Organize Data Around Domains and Ownership

Identify information domains such as customer, product, order, workforce, and finance. For each, name a business owner, data producer, data owner or quality lead, authoritative source, consumers, classification, and permitted uses. Domains should reflect meaningful ownership and change boundaries rather than simply mirror applications or reporting departments.

```mermaid
flowchart LR
    Customer[Customer domain] --> OwnerA[Customer business owner]
    Product[Product domain] --> OwnerB[Product business owner]
    Order[Order domain] --> OwnerC[Commerce business owner]
    Customer --> ContractA[Identity and consent contract]
    Product --> ContractB[Catalog and lifecycle contract]
    Order --> ContractC[Order status and event contract]
    ContractA --> Consumers[Applications and analytics consumers]
    ContractB --> Consumers
    ContractC --> Consumers
```

The domain owner is accountable for meaning, access, quality expectations, and change notice, even if platform teams operate storage. Define escalation when two domains disagree about a shared concept. Avoid a single enterprise dictionary that imposes one meaning where legal entities or product lines legitimately differ.

## Identify Systems of Record and Data Products

A system of record is authoritative for a defined data subject and lifecycle, not necessarily the only place a copy exists. Name authority at field or entity level where needed. Data products and replicated views can serve consumers, but their freshness, transformation, access, and failure behavior must be explicit.

```mermaid
flowchart LR
    CustomerSystem[Customer system of record] -->|Change event| CustomerProduct[Customer data product]
    CatalogSystem[Catalog system of record] -->|Change event| CatalogProduct[Catalog data product]
    CustomerProduct --> Commerce[Commerce application]
    CatalogProduct --> Commerce
    CustomerProduct --> Analytics[Analytics platform]
    CatalogProduct --> Analytics
    Commerce -->|Order fact| OrderSystem[Order system of record]
    OrderSystem -->|Order event| CustomerSupport[Support workspace]
```

Document conflict handling and update authority. When two systems can edit the same authoritative attribute, choose a precedence rule. Define a separate reconciliation process for unresolved conflicts. A copy that feeds a decision should expose source and last-updated information where staleness affects use.

## Preserve Lineage and Quality Evidence

Lineage records where data originated, how it changed, and which consumers depend on it. Track source, transformation, business definition, quality checks, owner, and downstream use. This supports impact analysis, audit, incident response, and change planning; it does not prove that data is accurate. Quality dimensions should be selected for the use case, such as validity, completeness, timeliness, consistency, and uniqueness.

```mermaid
flowchart LR
    Source[Source record] --> Capture[Captured event or extract]
    Capture --> Transform[Versioned transformation]
    Transform --> Product[Published data product]
    Product --> Application[Operational consumer]
    Product --> Report[Management reporting]
    Product --> Model[Model or analytical consumer]
    Check[Quality rules and results] --> Product
    Owner[Domain owner and definition] --> Product
    Product --> Impact[Downstream impact map]
```

Choose lineage granularity to answer concrete questions. Table-level lineage may be sufficient for a portfolio view; record-level provenance may be required for regulated decisions. Protect lineage metadata because it can reveal business relationships and sensitive processing paths.

## Govern Master and Reference Data

Master data describes shared business entities such as customers, products, or legal entities. Reference data standardizes classifications such as country, currency, or status. Consolidation requires identity matching, survivorship rules, quality ownership, and a process for corrections. A “golden record” is not automatically correct or universally authoritative; define the purpose and consumers.

```mermaid
sequenceDiagram
    participant SourceA as Customer system A
    participant SourceB as Customer system B
    participant MDM as Master-data service
    participant Owner as Domain owner
    participant Consumers as Subscribed systems
    SourceA->>MDM: Publish customer change and source ID
    SourceB->>MDM: Publish matched or conflicting record
    MDM->>MDM: Resolve identity and apply survivorship policy
    MDM->>Owner: Escalate ambiguous or high-impact conflict
    Owner-->>MDM: Confirm correction or authority
    MDM-->>Consumers: Publish canonical ID and versioned change
    Consumers-->>MDM: Acknowledge or report contract failure
```

Keep source identifiers and provenance so that a correction can be traced back. Consumers need stable canonical identifiers and migration rules when records merge or split. Reference-data changes should be versioned and announced when they affect downstream validation or reporting.

## Manage Access and Lifecycle

Data governance covers collection, use, sharing, retention, archival, and deletion. Classify data and define purpose, lawful basis where applicable, consent, access roles, retention period, and deletion evidence. Analytics and derived datasets need the same attention as operational stores. Part 15 owns security and privacy controls; this chapter establishes the enterprise ownership and lifecycle model.

```mermaid
stateDiagram-v2
    [*] --> Proposed: Define source and purpose
    Proposed --> Approved: Owner and policy approve collection
    Approved --> Active: Validate quality and access
    Active --> Shared: Publish governed product
    Shared --> Restricted: Rights, purpose, or incident changes
    Restricted --> Active: Controls verified and use permitted
    Active --> Archived: Retention or business need ends
    Archived --> Deleted: Retention expires and holds clear
    Restricted --> Deleted: Deletion required and holds clear
    Deleted --> Evidence: Record deletion evidence
    Evidence --> [*]
```

Deletion can be constrained by legal holds, backups, derived artifacts, or distributed consumers. Define how a request propagates and what evidence closes it. Restriction may need to precede physical deletion so the data is not used while remediation proceeds.

## Worked Case: Customer Identity Domain

A retailer has customer records in online commerce, stores, and support. The enterprise names the customer domain owner and documents which system is authoritative for identity, contact preferences, and loyalty status. A master-data service resolves duplicate identities while retaining source identifiers. Each consumer receives a versioned customer data product with consent and freshness metadata.

A contact-preference correction triggers updates to marketing and support. If one consumer fails to acknowledge the change, the data product flags stale access and the domain owner can restrict noncompliant use. Analytics retains only the fields and period needed for approved reporting; a deletion request is traced across operational copies and derived outputs under the applicable retention policy.

## Review Questions

1. What makes a system authoritative for a domain or attribute?
2. Who owns meaning and quality when platform operations are centralized?
3. Which lineage granularity supports the actual audit or impact question?
4. How are ambiguous master-data conflicts resolved and propagated?
5. How do restrictions, retention holds, and deletion interact?

Enterprise data architecture aligns data meaning and lifecycle with business ownership. Identify authoritative sources, govern shared products and master data, preserve useful lineage, and make access and deletion responsibilities explicit across consumers.
