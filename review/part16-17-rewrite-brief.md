# Part 16 and Part 17 in-depth rewrite brief

Shared instructions for rewriting each chapter of Part 16 (AI, ML, and GenAI)
and Part 17 (AI Architecture). One author rewrites exactly one chapter.

## Hard rules

- Do NOT run any git command and do NOT connect to GitHub. Only read and write
  local files.
- Write ONLY: (a) your assigned chapter file, (b) new runnable example files in
  your own folder `code/python/<chapter-slug>-chapter/` (see "Code"), and
  (c) optionally `review/concept-proposals/<part>-<chapter-id>.md` for genuinely
  new cross-cutting concepts. Do not edit `CORE_CONCEPTS.md`, `BOOK_PLAN.md`,
  `PART_OVERVIEW.md`, `TOPIC_MAP.md`, or any other chapter.
- The terminal is shared with other sessions running in parallel. Always use
  literal absolute paths. Never rely on shell variables from earlier commands.
  Do not run commands that write outside your own files.
- Keep the chapter's existing file name. Other chapters link to it.

## Read first

1. `STYLE_GUIDE.md` (single source of truth) and `.markdownlint.json`.
2. Your part's `TOPIC_MAP.md` entry for your chapter (scope and depth contract)
   and the part's `PART_OVERVIEW.md`.
3. `CORE_CONCEPTS.md`: rows naming your chapter as owner (teach fully) and rows
   owned by other chapters that you touch (2-3 sentence recap plus link).
4. The existing chapter in full. It is a short draft (about 1,200-1,900 words).
   Keep what is correct, but you are rewriting and deepening, not lightly
   editing. Part 16 CH01-CH03 are the house model for depth, math, and voice:
   skim the opening and one mid-chapter section of
   `16_AI_and_GenAI/CH03_Regression_and_Classification.md`.
5. Neighbouring chapters that your chapter links to, enough to avoid
   contradicting or re-teaching them.

## Depth target (this is the point of the task)

- Finished chapter: **at least 23,000 words**, counted excluding Mermaid
  diagram blocks (diagrams are in addition to the word target). Count with the
  command in "Measuring". Aim for 23,000-27,000.
- The words must be teaching content, not padding. Fenced code and display
  equations together should stay under about 15 percent of the words. Tables
  count, but a table never replaces explanation.
- Depth comes from, for each central topic: the governing model and intuition,
  the mechanism worked step by step (derivations for Part 16 math topics,
  request paths and state machines for Part 17 systems), variants and
  alternatives with the reason one is chosen, failure modes and edge cases,
  security/privacy/operational consequences, and at least one worked example
  with concrete numbers and the arithmetic shown. Add decision criteria and
  heuristics a practitioner can apply.
- Add a worked end-to-end case study (decisions, rejected alternatives,
  validation evidence), common mistakes with cause and consequence, a
  design-review checklist, 6-10 exercises with brief answer outlines or
  answers, and a summary.
- Add topics the existing draft and TOPIC_MAP missed when a senior practitioner
  would expect them. The task message for your chapter lists "must add" topics.
  If you find further genuine gaps inside your chapter's scope, include them.
  Stay inside the chapter's ownership boundary: recap and link topics owned
  elsewhere instead of re-teaching.
- Do not pad. If you run out of substantive material, deepen with more worked
  examples, edge cases, failure analysis, comparisons of alternatives, and
  production scenarios rather than restating points.

## Diagrams

At least **nine** distinct, substantive diagrams per chapter, including every
diagram opportunity in the TOPIC_MAP entry. Vary forms (flowchart, sequence,
state machine, timeline, quadrant, decision tree, ER/class, trust boundary).
Each diagram sits next to its explanation and is followed by prose on what it
shows and its implications. ASCII is fine for matrices, tensors, or byte-level
layouts (and does not count toward the nine).

Mermaid must render:

- Quote labels containing parentheses, slashes, colons, commas, `#`, `=`, `%`,
  or `<`/`>`: `A["Label (detail)"]`.
- No bare `end` node id; no semicolons inside labels; use `<br/>` for line
  breaks inside quoted labels.
- In sequence diagrams avoid `;` and unbalanced quotes in messages.
- In `stateDiagram-v2` use simple state ids and put descriptions after `:`.
- Do not put LaTeX or `$` in Mermaid labels.
- `quadrantChart` and `timeline` are allowed; keep labels short and unquoted
  where the syntax requires.

## Math (Part 16 only; also allowed in Part 17 where useful)

Use `$...$` inline and `$$...$$` display math, as CH03 does. Define every
symbol. Show derivations step by step when the chapter owns the concept.
Sanity-check every worked number by recomputing it (run a tiny script if
unsure). Do not state a numeric result you have not verified.

## Accuracy (AI facts drift fast; the current date is October 2026)

- Do not invent model names, benchmark scores, prices, context lengths, laws,
  standards, or library APIs. Use web search to check anything time-sensitive:
  current model families and their documented capabilities, API features,
  library versions, pricing, regulations, and standards. Cite official
  documentation, papers, or standards inline with links where you rely on them.
- Mark drifting facts "at the time of writing" and tell the reader what to
  verify. Prefer teaching the mechanism and how to look the number up over
  quoting a number you could not confirm.
- Distinguish research results from production evidence. State the assumptions
  behind illustrative numbers and label them illustrative.
- For papers, give author(s) and year. Do not fabricate citations. If unsure of
  a citation, describe the idea without one.

## Prose

- Expand every acronym at first use in the chapter, then use the expanded form
  or acronym consistently.
- Plain, direct language. Explain why a choice is made over its alternatives.
- Avoid filler, puffery, and AI-sounding vocabulary (delve, leverage, robust,
  landscape, pivotal, foster, seamless, tapestry, crucial). Avoid chains of
  em-dashes; prefer periods and commas. No "it is not X, it is Y" constructions
  and no rhetorical question openers.
- Headings: `#` title, `##` numbered sections (`## 1. Introduction`), `###`
  numbered subsections (`### 3.2 ...`). Satisfy `.markdownlint.json`: blank
  lines around headings, lists, fences, and tables; fenced blocks have a
  language tag; no trailing spaces; no double blank lines; single trailing
  newline; no bare URLs; no duplicate sibling headings; no bold text used as a
  heading.
- Header format (second line after the title):
  - Part 16: `Part: [16 — Artificial Intelligence, Machine Learning, and Generative AI](PART_OVERVIEW.md) · Status: Revised (in-depth rewrite)`
  - Part 17: `Part: [17 — AI Architecture](PART_OVERVIEW.md) · Status: Revised (in-depth rewrite)`

## Suggested structure (not mandatory)

1. Introduction: reader outcomes, why it matters to a solution architect, and a
   scope/ownership table linking neighbours (recap and link, no re-teaching).
2. Background and foundational model.
3. Many central-topic sections taught in depth (split broad topics into
   several `##` or `###` sections).
4. Implementation and practice: short correct code, configuration, or pseudo
   code; link longer runnable code.
5. Performance, scalability, cost where relevant, with worked arithmetic.
6. Security, privacy, safety, and governance consequences.
7. Operations and observability; testing and evaluation of this component.
8. Failure modes and quality-attribute scenarios (stimulus, response, measure).
9. Comparison table of alternatives and trade-off analysis.
10. Case study, common mistakes, checklist, exercises, summary.
11. Code examples section linking the files you created, one sentence each.

## Code

Create 3-4 small runnable Python files in
`code/python/<chapter-slug>-chapter/` (slug = lowercase chapter topic with
hyphens, e.g. `decision-trees-chapter`), numbered `01_...py`. Prefer the
standard library and NumPy only; if you need scikit-learn or PyTorch, keep the
script small, guard imports, and say so in the file docstring. Each script
prints a result that the chapter quotes or reproduces. Run each script if
Python is available (check with `python --version`) and make sure the chapter's
quoted output matches. If you cannot run Python, say so in your report and keep
the scripts simple enough to verify by reading. Link them from the chapter by
relative path (`../code/python/<slug>-chapter/01_x.py`). Check every link
target exists.

## Measuring

Word count excluding Mermaid blocks (use your chapter's literal path):

```powershell
$t = [IO.File]::ReadAllText('<path>'); $n = [regex]::Replace($t, '(?s)```mermaid.*?```', ''); ($n -split '\s+' | Where-Object { $_ }).Count
```

Also check: Mermaid block count, `##` count, even number of fence lines, no
double blank lines, all relative links resolve.

Write the chapter in several pieces: `fs_write` the first piece, then
`fs_append` each later piece (each piece roughly 3,000-5,000 words). After
finishing, re-read the whole file once for numbering continuity, balanced
fences, well-formed Mermaid, link validity, and acronym expansion. If the count
is under 23,000, keep adding substantive material until it is not.

## Report back (KEEP IT SHORT: at most 120 words)

One compact paragraph or list: final word count (excluding Mermaid), Mermaid
count, `##` count, code files created, whether scripts were run, concept
proposal file if any, and up to three facts you could not verify. No section-
by-section coverage listing.
