# Concept Proposals — Role of a Solution Architect chapter

Staged for merge into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). Do not edit
CORE_CONCEPTS.md directly from this chapter's session.

| Concept | Proposed Owner | Scope note |
|---|---|---|
| RACI matrix (for architecture decisions) | Role of a Solution Architect chapter | Responsible/Accountable/Consulted/Informed applied to naming who decides a technical decision |
| Architecture Review Board (ARB) governance model | Role of a Solution Architect chapter | Formal gated-review forum vs. lightweight async review, and when each fits |
| Centralized vs. embedded vs. federated architecture team topology | Role of a Solution Architect chapter | Organizational structures for how the architect role scales with headcount |
| Architecture Decision Record (ADR) | Architecture Documentation (Part 21) — specific chapter TBD | This chapter introduces and uses ADRs for role-workflow purposes (Sections 4-5, 10); full template/format/long-term documentation-strategy ownership belongs to the Documentation part once that chapter exists |
| Architecture fitness functions | Architecture Patterns (Part 20) — specific chapter TBD | This chapter only references the concept (Section 16) to explain how architectural decisions get validated over time; full technique coverage belongs in Architecture Patterns |
| TOGAF / Zachman Framework (Enterprise Architecture frameworks) | Enterprise Architecture (Part 18) — specific chapter TBD | This chapter mentions both only for historical context (Section 2); full framework coverage belongs to Enterprise Architecture |

## Notes for the merge step

- No overlap detected with existing entries in `CORE_CONCEPTS.md` (HTTP/REST
  concepts) — this chapter does not touch transport or API-style concepts.
- Three of the six proposals above point to Parts (15, 17, 18) whose specific
  owning chapter files don't exist yet at drafting time — this chapter links
  to the relevant `PART_OVERVIEW.md` in the meantime. When those chapters are
  drafted, the merge step should update both `CORE_CONCEPTS.md`'s target link
  and this chapter's forward-references to point at the specific chapter file.
- This chapter assumes sibling chapters `CH01_What_is_Software_Architecture.md`
  and `CH03_Architecture_Thinking.md` will exist in this same part folder
  (per the standard `CHxx_Title.md` naming convention already used for this
  chapter) — those files were not visible to this session and may not exist
  yet. If either sibling ends up covering RACI, ADRs, or ARB governance in
  more depth as part of defining architecture/architecture thinking more
  broadly, the batch review should reconcile ownership at that point rather
  than this chapter re-claiming it unilaterally.
