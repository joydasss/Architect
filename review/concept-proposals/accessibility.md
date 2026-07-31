# Concept Proposals: accessibility

Chapter: 02_Design_Thinking_and_Product_Management/CH11_Accessibility.md

Proposed cross-cutting concept ownership entries for merge review:

| Concept | Suggested Owning Chapter | Scope Note |
|---|---|---|
| Accessibility-by-design as an architecture quality attribute | Accessibility (02_Design_Thinking_and_Product_Management/CH11_Accessibility.md) | Treat accessibility as an Architecturally Significant Requirement (ASR)-class quality attribute with cross-layer contracts, not a late user-interface audit. |
| Assistive technology interaction model (DOM -> accessibility tree -> assistive output) | Accessibility (02_Design_Thinking_and_Product_Management/CH11_Accessibility.md) | Defines how semantic structure and state announcements are consumed by assistive technologies and why this shapes component/API design. |
| Focus lifecycle contract (entry, trap, return, async updates) | Accessibility (02_Design_Thinking_and_Product_Management/CH11_Accessibility.md) | Standardizes deterministic focus behavior across dialogs, route changes, validation, and asynchronous interface updates. |
| Structured accessibility error contract (field mapping + recovery hints) | Accessibility (02_Design_Thinking_and_Product_Management/CH11_Accessibility.md) | Cross-boundary error taxonomy enabling actionable, assistive-technology-compatible user recovery. |
| Layered accessibility test strategy (automation + manual + AT task validation) | Accessibility (02_Design_Thinking_and_Product_Management/CH11_Accessibility.md) | Defines complementary evidence model and release-gate expectations for accessibility-critical journeys. |
