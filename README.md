# Modern Solution Architecture Handbook

A Markdown-based, repo-driven textbook covering the full breadth of a modern
Solutions Architect's body of knowledge, built and maintained with VS Code + AI
agents rather than a single monolithic chat generation.

Source concept: [ChatGPT design discussion](https://chatgpt.com/share/6a6cad63-161c-83ee-8a7c-699d351e3abc).

## Repository map

| Path | Purpose |
|---|---|
| [STYLE_GUIDE.md](STYLE_GUIDE.md) | Single source of truth for tone, depth, concept ownership, and flexible chapter structure |
| [BOOK_PLAN.md](BOOK_PLAN.md) | Full table of contents (26 parts) with per-chapter status tracking |
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

### Headroom with VS Code Copilot (Windows)

[Headroom](https://github.com/headroomlabs-ai/headroom) provides a local
compression proxy for native VS Code Copilot chat and inline completions. Keep
using Copilot's normal model picker; no custom model or MCP server is required.
This does not configure Copilot CLI or other extensions that use their own
endpoints.

Prerequisites: Python 3.10 or newer, VS Code with Copilot enabled and signed in,
and a GitHub account with Copilot access. Install the Python CLI (not the npm SDK)
in the workspace's ignored virtual environment:

```powershell
# Create the environment only if .venv does not already exist.
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install "headroom-ai[proxy]"
```

In **Terminal > Run Task**, use the tasks in
[.vscode/tasks.json](.vscode/tasks.json):

1. **Headroom: Sign in to GitHub** - complete the separate GitHub device login.
   Headroom manages its own credential outside the repository; do not copy
   credentials into workspace settings.
2. **Headroom: Check GitHub sign-in** - confirm authentication.
3. **Headroom: Start Copilot proxy** - leave this task running while using
   Copilot. It listens on `127.0.0.1:8787` and adds Headroom's managed endpoint
   overrides to VS Code **user** settings, affecting other windows using those
   settings too. It is not started automatically when the workspace opens.
4. Verify the proxy from another terminal:

   ```powershell
   Invoke-RestMethod http://127.0.0.1:8787/health
   ```

   Check that health reports the Copilot API as the OpenAI upstream, then send a
   Copilot chat prompt and confirm the request appears in Headroom's metrics.
   `.\.venv\Scripts\headroom.exe savings` reports savings from actual traffic.

**Stop and undo:** press `Ctrl+C` in the proxy task's terminal, then run
**Headroom: Undo Copilot integration** to restore direct Copilot access.
Stopping the proxy alone leaves the endpoint overrides in place, so Copilot
requests fail until the proxy is restarted or the integration is undone.
Undo removes Headroom's settings block, not its saved GitHub authorization.

For a non-default VS Code profile, Insiders, portable VS Code, or a remote
extension host, follow the
[official integration guide](https://docs.headroomlabs.ai/docs/vscode-copilot).
Use the same explicit `--settings-file` on both `wrap vscode` and `unwrap vscode`
when targeting a different settings file; the tasks above use stable VS Code's
default user settings. The extension host must be able to reach the proxy's
loopback address. If port 8787 is occupied, stop the existing proxy or pass
`--port 8788` to `wrap vscode` and use that port for the health check.
