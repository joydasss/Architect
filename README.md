# Modern Solution Architecture Handbook

A Markdown-based, repo-driven textbook covering the full breadth of a modern
Solutions Architect's body of knowledge, built and maintained with VS Code + AI
agents rather than a single monolithic chat generation.

Source concept: [ChatGPT design discussion](https://chatgpt.com/share/6a6cad63-161c-83ee-8a7c-699d351e3abc).

## Repository map

| Path | Purpose |
|---|---|
| [STYLE_GUIDE.md](STYLE_GUIDE.md) | Single source of truth for tone, structure, and the 27-section chapter template |
| [BOOK_PLAN.md](BOOK_PLAN.md) | Full table of contents (22 parts) with per-chapter status tracking |
| [CORE_CONCEPTS.md](CORE_CONCEPTS.md) | Concept ownership map — prevents chapters from re-explaining the same concept |
| `PROMPTS/` | Canonical, copy-pasteable prompt templates (master/part/chapter/topic/subtopic/review/diagram) |
| `.github/prompts/` | VS Code Copilot slash-command prompts (Planner, Diagram, Code, Reviewer, Editor roles) |
| `.github/agents/` | `chapter-author.agent.md` — tool-restricted agent that drafts one chapter per invocation |
| `NN_Part_Name/` | One folder per part; each contains a `PART_OVERVIEW.md` and chapter files |
| `diagrams/` | Mermaid/ASCII diagram sources, organized by type |
| `code/` | Runnable code samples referenced (not embedded) from chapters |
| `review/concept-proposals/` | Per-chapter staging files listing new concepts a chapter introduces, pending merge into `CORE_CONCEPTS.md` |
| `scripts/build-book.ps1` | Pandoc build script producing PDF/EPUB output in `build/` |

## Authoring workflow (per chapter)

1. **Claim** a chapter in [BOOK_PLAN.md](BOOK_PLAN.md) (set status to `Drafted` once started) to avoid two agents claiming the same chapter.
2. **Plan**: run `.github/prompts/plan-chapter.prompt.md` to expand the chapter outline, checking [CORE_CONCEPTS.md](CORE_CONCEPTS.md) for concepts already owned elsewhere.
3. **Author**: invoke the `chapter-author` custom agent (`.github/agents/chapter-author.agent.md`) with the chapter name. It writes only the chapter file and its own concept-proposal staging file — safe to run in parallel, isolated chat sessions across multiple chapters at once.
4. **Diagram** / **Code**: run `.github/prompts/diagram-chapter.prompt.md` and `.github/prompts/code-chapter.prompt.md`.
5. **Merge**: after a batch of chapters finishes, consolidate their `review/concept-proposals/*.md` staging files into `CORE_CONCEPTS.md`, assigning one owning chapter per concept.
6. **Review**: run `.github/prompts/review-chapter.prompt.md` as a batch across the chapters drafted together — it explicitly checks for duplicated explanations between them.
7. **Edit**: run `.github/prompts/edit-chapter.prompt.md` to convert any duplicated explanations into a short recap + link to the owning chapter, and to fix cross-references.
8. Mark the chapter `Edited` in `BOOK_PLAN.md`.

This loop is what proved itself on the two pilot chapters (HTTP, REST) and is the
same loop to repeat for every remaining chapter — see "Scaling out" below.

## Scaling out

Writing all ~180 chapters is explicit follow-on work, not part of the initial
scaffold. Batch multiple chapters at a time (e.g. 3-5 parallel chat sessions,
each invoking `chapter-author.agent.md` for a different chapter), then run the
Merge → Review → Edit steps sequentially across the batch before starting the
next batch.

## Local tooling

- **Markdownlint** — `.markdownlint.json` at the repo root; install the
  `davidanson.vscode-markdownlint` extension or run `npx markdownlint-cli "**/*.md"`.
- **Mermaid preview** — `bierner.markdown-mermaid` extension (recommended in `.vscode/extensions.json`).
- **Vale** — `.vale.ini` is scaffolded but needs a style package/vocabulary before it's useful; defer full rule authoring until more chapters exist.
- **Pandoc build** — `scripts/build-book.ps1` concatenates chapters (in `BOOK_PLAN.md` order) into a combined PDF/EPUB under `build/`. Requires [Pandoc](https://pandoc.org/) and a LaTeX engine (for PDF) installed locally.
