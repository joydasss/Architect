# Part 09 CH13 Secrets Management Concept Proposals

Propose adding these ownership entries to `CORE_CONCEPTS.md` during the next concept-registry merge. They cover provider key-service mechanics that the rewritten chapter teaches in full and that no existing row assigns. They do not overlap the Part 15 proposals in `CH09_Secrets_Management.md`, which remain the owners of the provider-neutral delivery contract and the exposure response sequence; Part 15 CH10 Encryption remains the owner of the general envelope-encryption model.

| Concept | Proposed owner | Notes |
|---|---|---|
| Cloud key-service envelope encryption APIs and data key caching | [Secrets Management](../../09_Cloud_Computing/CH13_Secrets_Management.md) | AWS KMS `GenerateDataKey`/`Decrypt`/`ReEncrypt` and encryption context, Key Vault `wrapKey`/`unwrapKey`, Cloud KMS `encrypt`/`decrypt` with AAD and client-generated DEKs; caching bounds versus quota and revocation; general envelope model stays with Part 15 CH10 |
| Cloud key authorization: KMS key policies and grants, Key Vault and Managed HSM data roles, Cloud KMS IAM | [Secrets Management](../../09_Cloud_Computing/CH13_Secrets_Management.md) | Key-resource authorization specifics; general cloud IAM evaluation stays with Part 09 CH09 IAM |
| Customer-managed key lifecycle: availability dependency, deletion waiting periods, rotation scope | [Secrets Management](../../09_Cloud_Computing/CH13_Secrets_Management.md) | Disabled key as outage, provider deletion and recovery windows, what key rotation does and does not re-encrypt; storage-side recovery impact stays with Part 09 CH06 Storage |
| Secret-store and key-service quota budgeting | [Secrets Management](../../09_Cloud_Computing/CH13_Secrets_Management.md) | Unit conversion across per-vault, per-project, and per-Region quotas; steady-state versus startup-burst sizing; generic rate limiting stays with Part 08 CH11 |
