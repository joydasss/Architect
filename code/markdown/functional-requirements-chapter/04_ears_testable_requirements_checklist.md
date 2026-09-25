# Artifact 4 — Testable-Requirement Writing Checklist (EARS-Style)

A reference checklist and before/after set for converting vague requirement
prose into testable statements, using the Easy Approach to Requirements
Syntax (EARS) sentence patterns. See
[Section 4.4](../../../07_System_Design_and_Distributed_Systems/CH01_Functional_Requirements.md#44-writing-testable-and-unambiguous-requirements)
of the chapter for the underlying mechanism.

## The five EARS sentence patterns

1. **Ubiquitous** (always true, no trigger): "The system shall &lt;response&gt;."
2. **Event-driven**: "When &lt;trigger&gt;, the system shall &lt;response&gt;."
3. **State-driven**: "While &lt;state&gt;, the system shall &lt;response&gt;."
4. **Unwanted behavior**: "If &lt;undesired trigger/condition&gt;, then the
   system shall &lt;response&gt;."
5. **Optional feature**: "Where &lt;feature is included&gt;, the system
   shall &lt;response&gt;."

## Ambiguous-word blocklist (flag these on sight)

| Ambiguous word/phrase | Why it fails testability | Fix |
|---|---|---|
| "fast", "quickly", "responsive" | No measurable threshold | State a number or move to the Non-Functional Requirements spec with an explicit metric |
| "user-friendly", "intuitive" | Not independently verifiable by two different testers | Replace with a specific behavior or a measured usability-test pass criterion (recapped from [Usability Testing](../../../02_Design_Thinking_and_Product_Management/CH10_Usability_Testing.md)) |
| "handle", "support", "manage" | Verb doesn't specify an observable system response | Replace with an explicit Given/When/Then outcome |
| "as needed", "if necessary" | Hides an undocumented decision rule | State the actual triggering condition |
| "etc.", "and so on" | Open-ended scope, unenforceable boundary | Enumerate the full set explicitly or state a non-goal |
| "should probably", "ideally" | Signals an unresolved decision masquerading as a requirement | Escalate and resolve before sign-off — do not encode indecision into the spec |

## Before / after examples

### Example 1
- **Before:** "The system should handle user login quickly."
- **After (Event-driven + explicit metric moved to NFR):** "When a client
  submits valid credentials to `POST /login`, the system shall respond with
  an authentication token and HTTP 200 within the latency budget defined in
  NFR-12 (Non-Functional Requirements chapter, not re-derived here)."

### Example 2
- **Before:** "The system supports file uploads."
- **After (Event-driven, with the boundary made explicit):** "When a client
  submits `POST /files` with a payload under 50 MB and a supported MIME
  type (`image/png`, `image/jpeg`, `application/pdf`), the system shall
  store the file and return a file ID. If the payload exceeds 50 MB or the
  MIME type is unsupported, then the system shall reject the request with
  HTTP 413 or HTTP 415 respectively."

### Example 3
- **Before:** "Notifications should be sent to users as needed."
- **After (State-driven + Event-driven pair):** "While a user has
  notification preferences enabled for order-status changes, when an order
  transitions to `shipped`, the system shall send exactly one notification
  to that user's registered channel within 60 seconds of the transition."

### Example 4 (unwanted-behavior pattern for an explicit non-goal boundary)
- **Before:** "The system should prevent abuse."
- **After:** "If more than 100 short-URL-creation requests are received
  from the same account within 60 seconds, then the system shall reject
  subsequent requests with HTTP 429 until the window resets." (Note: this
  crosses into rate-limiting, a security/NFR concern — flagged, not fully
  specified here, to show where a Functional Requirement legitimately hands
  off to a Non-Functional Requirement rather than absorbing it.)

## Pre-signoff checklist (apply to every requirement before it enters the spec)

- [ ] Is the trigger (When/While/If) explicit, or is it implicit ("as
      needed")?
- [ ] Is the system's response an observable, checkable behavior (a status
      code, a persisted value, a visible state change) rather than an
      adjective?
- [ ] Could two different engineers write two different test cases that
      both legitimately claim to satisfy this sentence? If yes, it is not
      testable yet.
- [ ] Does this requirement belong here, or is it actually a non-functional
      requirement (latency, availability, security) wearing functional
      clothing? Cross-reference against the sibling Non-Functional
      Requirements chapter before finalizing.
- [ ] Does this requirement have a stable ID for the traceability matrix
      (see [Artifact 2](02_requirements_traceability_matrix.md))?
