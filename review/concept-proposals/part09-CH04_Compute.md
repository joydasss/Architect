# Concept Proposals — Compute (CH04, Part 09 Cloud Computing)

New cross-cutting concept introduced by the in-depth rewrite of
[Cloud Compute Selection and Operation](../../09_Cloud_Computing/CH04_Compute.md).
Existing CH04 rows in `CORE_CONCEPTS.md` (service-model selection, shape
matching, capacity procurement, autoscaling controller, image and fleet
lifecycle, placement across failure domains) remain as they are.

| Concept | Suggested owner | Scope note |
|---|---|---|
| Instance metadata service credential exposure and IMDSv2-style protections | [Compute](../../09_Cloud_Computing/CH04_Compute.md) | Link-local metadata endpoint as the source of instance credentials; SSRF path to credential theft; AWS IMDSv2 session token, hop limit, and forwarded-header rejection versus Azure and Google Cloud required-header protections; enforcement through launch templates and organization policy. Section 5.5. IAM (CH09) owns workload identity design and credential-use conditions and should recap and link; Part 15 owns general SSRF threat modeling. |

Related proposals from other chapters that CH04 recaps rather than owns:

- Static stability is proposed for ownership by AWS (CH01) in
  `part09-CH01_AWS.md`. CH04 section 8.5 applies it to zonal fleet sizing
  (n/(n−1) capacity) and links to CH01.
- Provider service quotas and quota-versus-capacity are proposed by AWS
  (CH01). CH04 section 10 teaches compute-specific quota structures and
  scale-out error handling across AWS, Azure, and Google Cloud; the merge step
  should keep CH01 as owner of the general quota model and record CH04 as the
  owner of compute quota and capacity-error handling during scale-out.
