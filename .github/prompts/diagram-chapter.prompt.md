---
description: "Generate Mermaid and ASCII diagrams for an already-drafted chapter and save them under diagrams/."
agent: "agent"
tools: [read, edit, search]
argument-hint: "Chapter file path, e.g. 05_Networking_and_OS/CH01_HTTP.md"
---
For the chapter at `${input:chapterFile}`, produce the diagrams called for by
its text (sequence flows, architecture/component structure, packet/protocol
detail):

1. Read the chapter file and identify each place a diagram is described or
   would clarify the explanation.
2. Create Mermaid diagrams for sequence flows and component/C4-style
   structure; create ASCII diagrams for byte/packet-level detail.
3. Save each diagram as its own file under the matching `diagrams/<type>/`
   subfolder (`sequence/`, `c4/`, `deployment/`, `erd/`, `network/`,
   `flowcharts/`), named after the chapter and diagram subject.
4. Insert a relative Markdown link/embed to each diagram at the right spot in
   the chapter file — do not paste the full Mermaid source inline in the
   chapter; reference the file.
5. Double-check every Mermaid code block parses (correct diagram type keyword,
   balanced brackets/arrows).
