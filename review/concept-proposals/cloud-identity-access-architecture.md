# Cloud Identity and Access Architecture Concepts

Source: `10_Cloud_Architecture/CH04_Cloud_Identity_and_Access_Architecture.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Cross-provider cloud identity architecture across workforce, workload, deployment, and recovery principals | CH04 Cloud Identity and Access Architecture | Composes trust, authorization scopes, credential delivery, lifecycle, and recovery across workload boundaries; Part 09 CH09 owns provider IAM evaluation and Part 05 owns authentication/federation protocols. |

## Recap-only concepts

- Provider IAM policy evaluation, workload federation products, and cross-scope trust mechanics: Part 09 CH09.
- OAuth, OpenID Connect, Security Assertion Markup Language, and token protocol behavior: Part 05 owners.
- Secret-store lifecycle and security threat modeling: Part 09 CH13 and Part 15.
