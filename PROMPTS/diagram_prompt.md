# Diagram Prompt

Use to generate the Mermaid/ASCII diagrams for a chapter after the text draft
exists.

```text
For the <Chapter Name> chapter, produce diagrams for each major flow/
structure discussed:

- Mermaid sequence diagrams for request/response or multi-step flows.
- Mermaid C4 or component diagrams for architecture-level structure.
- ASCII diagrams for byte/packet-level or protocol-level detail.

Save each diagram as its own file under diagrams/<type>/ (sequence/, c4/,
deployment/, erd/, network/, flowcharts/ as appropriate), and reference it
from the chapter file by relative link rather than embedding the full source
inline.

Validate that Mermaid syntax renders without errors.
```
