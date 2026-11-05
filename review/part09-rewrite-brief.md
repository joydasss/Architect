# Part 09 in-depth rewrite brief

Shared instructions for rewriting each Part 09 (Cloud Computing) chapter. One
author rewrites exactly one chapter.

## Hard rules

- Do NOT run any git command and do NOT connect to GitHub. Only read and write
  local files.
- Write ONLY your assigned chapter file. If you introduce a genuinely new
  cross-cutting concept not already in `CORE_CONCEPTS.md`, you may also write
  `review/concept-proposals/<chapter-id>.md`. Do not edit `CORE_CONCEPTS.md`,
  `PART_OVERVIEW.md`, `TOPIC_MAP.md`, code files, or any other chapter.
- Keep the existing code-example links working. The runnable files already
  exist under `code/python/<chapter-folder>/`. Read them so the prose that
  references them is accurate. Do not create or edit code files.
- Only link to files that exist. Check the target path with a file search
  before adding any cross-part link. No other file links into Part 09 chapter
  anchors, so you may change headings freely.

## Read first

1. `STYLE_GUIDE.md` (single source of truth; follow it exactly).
2. `09_Cloud_Computing/PART_OVERVIEW.md` and your chapter's entry plus the
   "Part-wide ownership boundaries" in `09_Cloud_Computing/TOPIC_MAP.md`. The
   topic-map entry is the scope and depth contract.
3. `CORE_CONCEPTS.md`: the rows that name your chapter as owner (you must teach
   these fully), and rows owned by other chapters that your chapter touches
   (recap in 2-3 sentences and link; do not re-teach).
4. The existing chapter in full. It is a shallow draft on the retired 27-section
   template. Keep anything correct and useful, but you are rewriting, not
   lightly editing.

## Depth target

The current drafts are about 4,500-6,700 words and mostly give one paragraph
per topic. The rewrite must teach. Target roughly 11,000-15,000 words of real
content (about 25-35 finished pages). Do not pad. Depth comes from:

- For each central topic: the governing model, how it works internally
  (request paths, evaluation order, state machines, data flows), the AWS,
  Azure, and Google Cloud Platform (GCP) specifics where they materially
  differ (real product names, scopes, defaults, and limits), decision criteria
  and alternatives with the reason one is chosen over another, failure modes
  and edge cases, and at least one worked scenario with concrete numbers.
- Supporting topics: concise but never an unexplained label.
- Worked calculations where they help (capacity, cost, transfer time, lag,
  RPO/RTO, quota headroom). Show the arithmetic.
- Quality-attribute scenarios with stimulus, expected response, and a
  measurable success criterion, especially for the part-wide scenarios: account
  compromise contained by organizational boundaries, zonal failure, quota or
  capacity limit during scale-out, identity or key rotation, migration with
  reversible cutover (use the ones relevant to the chapter).
- Short, correct configuration or policy snippets (JSON, YAML, HCL, CLI) when
  they make a mechanism concrete. Keep them small; large listings belong in
  `code/`.

## Accuracy

- Provider facts change. For specific limits, quotas, defaults, and product
  names you are not sure are current, use web search to check the official
  documentation, and say "at the time of writing; verify current quotas" for
  numbers that drift. Never invent a quota number. Prefer describing the
  mechanism and where to find the limit over quoting a number you cannot
  confirm. Cite official docs inline with links where you used them.
- Use current names (for example Microsoft Entra ID, not Azure Active
  Directory; Google Cloud, Amazon Elastic Kubernetes Service (EKS) Auto Mode,
  AWS IAM Identity Center) where verified.
- Do not imply that similarly named products give identical guarantees.

## Structure

The 27-section template is retired. Organize around the subject and the
reader's journey. Keep this header format:

```markdown
# Chapter: <Title>

Part: [09 — Cloud Computing](PART_OVERVIEW.md) · Status: Revised (in-depth rewrite)
```

Then a suggested (not mandatory) flow:

1. Introduction: what the reader will be able to do, scope, and explicit
   ownership boundaries with links.
2. A foundational model section.
3. Several central-topic sections (use `##` and `###`, numbered), each taught
   as described above. Split broad topics into multiple sections.
4. Cross-cutting sections where they add substance: security, operations and
   observability, failure scenarios and quality scenarios, performance/limits,
   cost.
5. A provider comparison table that compares guarantees, scopes, and
   responsibilities (not just product names).
6. A worked end-to-end case study that applies the chapter's reasoning to one
   realistic organization, including the decisions, rejected alternatives,
   and validation evidence.
7. Common mistakes and anti-patterns (each with cause and consequence).
8. A design-review checklist, a few interview/design exercises, and a summary.
9. Code examples section linking the existing files with one sentence each on
   what they demonstrate.

## Diagrams

At least eight distinct, substantive diagrams, including all five diagram
opportunities in your topic-map entry. Vary forms: hierarchy, sequence,
state machine, decision tree, failure-domain map, trust boundary, timeline,
packet path. Place each next to its explanation and follow it with prose that
explains what it shows and its implications.

Mermaid must render. Rules that avoid common breakage:

- Quote node labels containing parentheses, slashes, colons, commas, `#`, or
  other punctuation: `A["Label (detail)"]`.
- No `end` as a bare node id; no semicolons inside labels; use `<br/>` for line
  breaks inside quoted labels.
- In sequence diagrams avoid `;` and unbalanced quotes in messages.
- In `stateDiagram-v2` use simple state ids and put descriptions after `:`.

Wide diagrams may use the landscape wrapper described in `STYLE_GUIDE.md`.
Use it sparingly.

## Prose

- Expand every acronym at first use in the chapter.
- Plain, direct language. Explain why a choice is made over the alternatives.
- Avoid filler, puffery, and AI-sounding vocabulary (delve, leverage, robust,
  landscape, pivotal, foster, seamless). Avoid chains of em-dashes; prefer
  periods and commas. No "It's not X, it's Y" constructions.
- Markdown must satisfy `.markdownlint.json` in the repo root (read it).

## Writing mechanics

The chapter is long. Write it in several pieces: `fs_write` the first part
(header through the first few sections), then `fs_append` each later part.
After finishing, re-read the whole file once to check: heading numbering is
consistent, every Mermaid block is closed and well-formed, all code links
point to existing files, acronyms are expanded, and every topic-map item is
covered. Fix problems with targeted edits.

## Report back

Return: final word count (use `(Get-Content <file> | Measure-Object -Word).Words`
in PowerShell), number of diagrams, number of `##` sections, the list of
topic-map items and where each is covered, any concept proposals written, and
any facts you could not verify.
