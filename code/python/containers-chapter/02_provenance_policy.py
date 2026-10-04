"""Evaluate minimum synthetic evidence required for image promotion."""


REQUIRED_EVIDENCE = {
    "source_revision",
    "builder_identity",
    "scan_passed",
    "dependency_manifest",
    "image_digest",
}


def evaluate_provenance(attestation: dict[str, object]) -> list[str]:
    missing = REQUIRED_EVIDENCE - attestation.keys()
    findings = [f"deny: missing evidence {', '.join(sorted(missing))}"] if missing else []
    if attestation.get("scan_passed") is False:
        findings.append("deny: vulnerability policy failed")
    if not findings:
        findings.append("allow: modeled provenance checks pass")
    return findings


def main() -> None:
    examples = {
        "approved": {
            "source_revision": "4b1d7a9",
            "builder_identity": "trusted-ci",
            "scan_passed": True,
            "dependency_manifest": "sha256:deps-example",
            "image_digest": "sha256:image-example",
        },
        "incomplete": {
            "source_revision": "4b1d7a9",
            "scan_passed": False,
            "image_digest": "sha256:image-unknown",
        },
    }
    for name, attestation in examples.items():
        print(name)
        for finding in evaluate_provenance(attestation):
            print(f"  {finding}")


if __name__ == "__main__":
    main()