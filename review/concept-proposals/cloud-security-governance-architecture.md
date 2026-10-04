# Cloud Security, Governance, and Compliance Architecture Concepts

Source: `10_Cloud_Architecture/CH12_Cloud_Security_Governance_and_Compliance_Architecture.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Workload control-to-evidence architecture across provider, platform, and customer responsibilities | CH12 Cloud Security, Governance, and Compliance Architecture | Composes ownership, enforcement, evidence, exception, and response paths; Part 15 owns general security/compliance controls and Part 09 provider mechanics. |
| Cloud guardrail exception lifecycle with accountable risk owner and expiry | CH12 Cloud Security, Governance, and Compliance Architecture | Cross-service governance contract; Part 09 CH15 owns provider landing-zone policy implementation and Part 15 owns general governance foundations. |

## Recap-only concepts

- Threat modeling, cryptography, security control families, and compliance frameworks: Part 15.
- Provider IAM, secret stores, and landing-zone policies: Part 09.
- Organization scopes, network paths, and identity composition: Part 10 CH02-CH04.
