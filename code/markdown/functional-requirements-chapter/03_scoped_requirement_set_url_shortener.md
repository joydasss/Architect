# Artifact 3 — Final Scoped Requirement Set: "Design a URL Shortener"

This is the consolidated, testable output of the elicitation dialogue in
[Artifact 1](01_requirements_elicitation_dialogue.md) — the artifact a
candidate would actually hand an interviewer (or a Solution Architect would
attach to a design document) before starting the High-Level Design. Every
requirement follows the Given/When/Then testable-requirement discipline
taught in [Section 4.4](../../../07_System_Design_and_Distributed_Systems/CH01_Functional_Requirements.md#44-writing-testable-and-unambiguous-requirements)
of the chapter, is tagged with a MoSCoW priority
([recapped from Prioritization](../../../02_Design_Thinking_and_Product_Management/CH28_Prioritization.md#moscow-prioritization-mustshouldcouldwont)),
and carries a stable ID for the traceability matrix in
[Artifact 2](02_requirements_traceability_matrix.md).

## In scope

### FR-1 — Create a short URL (Must)
**Given** a valid long URL and an authenticated (or anonymous, per account
policy) request, **when** the client calls `POST /urls` with the long URL,
**then** the system shall generate and return a short URL code, persist the
mapping, and respond with HTTP 201 Created and the short URL in the
response body.

**Acceptance criteria:**
- Long URL must be a syntactically valid absolute URL (reject with 400 Bad
  Request otherwise).
- Generated short code must be URL-safe and unique across the whole system,
  not just per account.

### FR-2 — Idempotent creation per account (Must)
**Given** an account has already shortened a specific long URL, **when**
that same account submits the identical long URL again, **then** the system
shall return the existing short URL rather than creating a duplicate
mapping. **Given** the same long URL submitted by a different account or
anonymously, **when** that request is processed, **then** the system shall
create a new, independent mapping (deduplication is scoped per account, not
global).

### FR-3 — Optional expiration (Should)
**Given** a creation request that includes an `expires_at` timestamp,
**when** that timestamp is in the future, **then** the system shall persist
it and, **when** a redirect request arrives after `expires_at` has passed,
**then** the system shall respond with HTTP 410 Gone instead of redirecting.
**Given** no `expires_at` is supplied, **when** a redirect request arrives at
any future time, **then** the system shall continue to redirect
indefinitely (no default expiration).

### FR-4 — Custom alias with collision handling (Should)
**Given** a creation request that includes a `custom_alias` field, **when**
that alias is not already in use, **then** the system shall use it as the
short code instead of a generated one. **Given** the requested alias is
already in use, **when** the creation request is processed, **then** the
system shall reject the request with HTTP 409 Conflict rather than silently
falling back to a generated code.

### FR-5 — Redirect short URL to long URL (Must)
**Given** a valid, non-expired short code, **when** a client requests
`GET /{code}`, **then** the system shall respond with an HTTP redirect
(301 or 302 — the choice is itself a requirement-level decision affecting
browser caching, and shall be documented explicitly, not left implicit)
to the original long URL. **Given** an unknown short code, **when** a
client requests `GET /{code}`, **then** the system shall respond with
HTTP 404 Not Found.

## Explicitly out of scope (non-goals, stated not omitted)

- **Click analytics / dashboards** — deliberately excluded per the
  elicitation dialogue; recorded as NG-1 so a later reviewer sees a decision,
  not a gap.
- **User authentication/account system internals** — assumed to exist
  upstream; this requirement set only depends on an `account_id` being
  available, not on how accounts are created or authenticated.
- **Abuse/spam prevention (malicious long URLs)** — flagged as a security
  requirement belonging to the chapter's Section 13 discussion and the
  future Security part, not re-derived here as a functional requirement.

## Priority summary (MoSCoW)

| Priority | Requirements |
|---|---|
| Must | FR-1, FR-2, FR-5 |
| Should | FR-3, FR-4 |
| Could | (none proposed at this scope) |
| Won't (this release) | NG-1 (analytics) |

## Why this artifact is the deliverable, not the dialogue itself

The dialogue in Artifact 1 is the *elicitation process* — valuable to show
the technique, but not something a downstream API designer should have to
re-read to extract requirements from. This artifact is the *specification*:
scoped, testable, prioritized, and traceable, which is what actually gets
handed to the High-Level Design and Low-Level Design stages
([forward-referenced](../../../07_System_Design_and_Distributed_Systems/CH01_Functional_Requirements.md#7-architecture-patterns),
not yet drafted in this workspace).
