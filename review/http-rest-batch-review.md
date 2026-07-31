# Batch Review — HTTP + REST Pilot Chapters

Reviewed files:
[05_Networking_and_OS/CH01_HTTP.md](../05_Networking_and_OS/CH01_HTTP.md),
[08_API_Architecture/CH01_REST.md](../08_API_Architecture/CH01_REST.md).

## [overlap] REST Section 4 duplicates HTTP-owned concepts

**Finding**: REST chapter, Section 4 ("Core Concepts"), sub-bullets "HTTP
methods as the uniform interface", "Status codes as outcome signaling", and
"Caching via HTTP headers" each fully re-explain concepts already owned by
the HTTP chapter per `CORE_CONCEPTS.md` (HTTP methods/idempotency, HTTP
status codes, HTTP caching headers). This is exactly the isolation-caused
duplication the Concept Ownership Rule exists to prevent — the REST chapter
was authored without visibility into the HTTP chapter's session.

**Fix**: condense each of those three sub-bullets to a 2-3 sentence recap +
link to the corresponding section of
[CH01_HTTP.md](../05_Networking_and_OS/CH01_HTTP.md), keeping only the
REST-specific framing (e.g. "REST relies on HTTP's existing status codes/
methods/caching rather than inventing its own").

## [overlap] REST Section 5 (Internal Working) — minor

**Finding**: the request/response example re-derives conditional-GET/ETag
behavior already covered in HTTP Section 4/5. Acceptable as a short worked
example specific to REST resources, but should explicitly note it's applying
HTTP's caching mechanism rather than re-explaining it.

**Fix**: add one sentence linking back to HTTP's caching-headers explanation
before the example.

## [completeness] Both chapters

All 27 STYLE_GUIDE.md sections are present in both chapters, in the correct
order, with non-trivial content. No missing sections found.

## [accuracy] Both chapters

No factual errors found in the HTTP or REST technical content (methods,
status codes, TLS 1.3 round-trip count, Richardson Maturity Model levels,
HATEOAS definition).

## [cross-reference] Both chapters

- HTTP chapter's "Further reading" links to REST, CDN, API Gateway, and
  Observability — REST and Observability targets exist (REST chapter exists;
  Observability part overview exists); CDN and API Gateway links point to
  `PART_OVERVIEW.md` stubs (05 and 08 respectively) since no dedicated CDN/API
  Gateway chapter file exists yet — acceptable for now, revisit once those
  chapters are drafted.
- REST chapter's "Further reading" links to HTTP (valid), and to API Gateway/
  GraphQL as `PART_OVERVIEW.md` stubs — same caveat as above.

## [consistency] Both chapters

Terminology (e.g. "idempotent", "safe method") matches STYLE_GUIDE.md and is
used consistently between the two chapters.

## Summary

1 significant overlap issue (REST Section 4) requiring an edit pass; 1 minor
overlap note (REST Section 5); no accuracy, completeness, or consistency
issues. Proceed to `edit-chapter.prompt.md` on the REST chapter only — the
HTTP chapter needs no changes and remains the canonical explanation.
