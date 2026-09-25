# Artifact 2 — Requirements Traceability Matrix (RTM) Example

A Requirements Traceability Matrix (RTM) proves, for every requirement, that
something built and something tested actually corresponds to it — and, read
in reverse, that every API endpoint and schema decision traces back to a
requirement someone actually asked for rather than a feature invented mid-
implementation. This example continues the URL-shortener scoped requirement
set from [Artifact 3](03_scoped_requirement_set_url_shortener.md). See
[Section 4.5](../../../07_System_Design_and_Distributed_Systems/CH01_Functional_Requirements.md#45-requirement-traceability)
of the chapter for the underlying mechanism and failure modes this artifact
demonstrates.

## Forward traceability: requirement -> design -> test

| Req ID | Requirement (summary) | Design Artifact | API / Data-Model Element | Test Case ID | Status |
|---|---|---|---|---|---|
| FR-1 | Create a short URL from a long URL | HLD Section 3.2 (Write Path) | `POST /urls` request/response schema; `urls.long_url` column | TC-101, TC-102 | Implemented |
| FR-2 | Idempotent dedup of identical long URL per account | HLD Section 3.2; LLD Section 5.1 (unique index) | `urls` table unique index on `(account_id, long_url_hash)` | TC-103, TC-104 | Implemented |
| FR-3 | Optional expiration; expired short URL returns 410 | HLD Section 3.3 (Read Path) | `urls.expires_at`; `GET /{code}` response branch | TC-105, TC-106, TC-107 | Implemented |
| FR-4 | Custom alias with collision check | HLD Section 3.2; LLD Section 5.2 (alias validation) | `POST /urls` optional `custom_alias` field; `urls.code` uniqueness constraint | TC-108, TC-109 | Implemented |
| FR-5 | Redirect short URL to long URL (HTTP 301/302) | HLD Section 3.3 (Read Path) | `GET /{code}` | TC-110, TC-111 | Implemented |
| NG-1 | Click analytics (explicit non-goal) | — (out of scope, recorded not designed) | — | — | Not Applicable — traced as an explicit exclusion, not a gap |

## Backward traceability: design/code element -> requirement

This is the direction that catches **scope creep** and **gold-plating**:
every implemented endpoint, column, or business rule must point back to a
row above. If it doesn't, one of two things happened — either a requirement
was elicited but never entered into the matrix (a process gap the traceability
exercise itself catches), or an engineer added a capability nobody asked
for (the "gold-plating" anti-pattern, Section 19 of the chapter).

| Implemented Element | Traces Back To | Note |
|---|---|---|
| `urls.click_count` column (found in code review) | **No matching Req ID** | Flagged: analytics was an explicit non-goal (NG-1) — this column should be removed or NG-1 should be re-opened as a requirement change, not silently implemented |
| `DELETE /{code}` endpoint | **No matching Req ID** | Flagged: deletion was never elicited; escalate to product owner — either add FR-6 (delete short URL) with acceptance criteria, or remove the endpoint before release |
| Rate limiting on `POST /urls` | **No matching Req ID** (this is an NFR, not an FR) | Correctly out of this FR-scoped matrix; belongs in the sibling Non-Functional Requirements traceability matrix instead — recorded here only to show the FR/NFR matrix boundary explicitly |

## Coverage summary (the metric a status review actually reads)

| Metric | Count | Note |
|---|---|---|
| Total functional requirements | 5 (FR-1..FR-5) | Excludes explicit non-goals |
| Requirements with a test case | 5 / 5 (100%) | Every FR row has at least one TC ID |
| Design elements without a traced requirement | 2 (`click_count`, `DELETE /{code}`) | Both flagged for disposition before release — this is the traceability matrix doing its job, not a failure of the matrix |

## Why this artifact is a matrix, not a paragraph

A prose changelog can describe *what* was built; only a matrix makes it
mechanically checkable that *every* requirement has a design/test pair and
*every* design/test element has a requirement — the two-directional check
is what catches both silent scope gaps (a requirement nobody built) and
silent scope creep (a capability nobody requested), which is exactly the
failure mode Section 4.5 of the chapter describes for traceability drift.
