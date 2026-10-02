# Orders API contract workflow

This directory contains a complete OpenAPI 3.1.1 description and an illustrative client-tool workflow. The tools below are pinned in `package.json`, but they are not installed in the handbook repository and these commands have not been executed here. Generated files are build outputs and are intentionally not checked in by this example.

## Install and lint

Run from this directory:

```sh
npm install
npm run lint
```

For a production repository, commit the resulting lock file and use `npm ci` so transitive tool versions are reproducible. The GitHub Actions example separately installs Redocly CLI and oasdiff in its isolated runner.

## Generate client types

```sh
npm run generate:types
```

This generates TypeScript declarations from the contract; it does not generate or execute an HTTP client. A client library can consume the generated types while its transport, authentication, retries, and error handling remain explicit application choices.

## Start a mock for consumer development

```sh
npm run mock -- --port 4010
```

Prism uses the specification and its examples to serve a development mock. A mock response demonstrates the documented shape, not the production service's state transitions, authorization, callback delivery, idempotency, or business invariants.

## Check a running provider

Start the real Orders API in a local test environment, then place Prism's proxy in front of it:

```sh
npx prism proxy openapi.yaml http://127.0.0.1:8080/v1
```

Point a contract-test client at Prism's local listener and exercise the documented success and error cases. Prism can report request or response mismatches as traffic passes through; provider tests should still assert domain-specific outcomes and fail the test suite on unexpected behavior. Keep credentials and production data out of this workflow.

For generated/property-based provider tests, add an approved test runner such as Schemathesis and run it against the deployed test service using that runner's pinned CLI and the contract file. The handbook does not claim that such a run has occurred here, and this example does not include or assume a running Orders implementation.
