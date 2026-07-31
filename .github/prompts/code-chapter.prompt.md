---
description: "Produce or validate runnable code samples for a chapter under code/<language>/, referenced (not embedded) from the chapter."
agent: "agent"
tools: [read, edit, search, execute]
argument-hint: "Chapter file path and target language(s), e.g. 05_Networking_and_OS/CH01_HTTP.md java,python,node"
---
For the chapter at `${input:chapterFile}`, produce minimal, runnable code
samples in `${input:languages}` (default: pick languages relevant to the
chapter's topic per [STYLE_GUIDE.md](../../STYLE_GUIDE.md) coverage list).

1. Read the chapter's "Implementation" and "Complete Code Examples" sections
   to see what's already described.
2. Write each sample under `code/<language>/<chapter-id>/`, keeping samples
   small and focused (one concept per file) rather than one large program.
3. Replace any large inline code listings in the chapter with a short snippet
   plus a relative link to the full sample under `code/`.
4. If a runtime is available, execute/compile the sample to confirm it runs;
   note in the chapter or a code comment if it couldn't be verified locally.
