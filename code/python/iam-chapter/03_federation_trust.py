"""Validate synthetic external identity claims before role assumption."""


TRUST = {
    "issuer": "https://token.example.invalid",
    "audience": "cloud-deploy",
    "subject_prefix": "repo:org/orders-api:ref:refs/heads/",
}


def evaluate_claims(claims: dict[str, str]) -> list[str]:
    failures = []
    if claims.get("iss") != TRUST["issuer"]:
        failures.append("issuer does not match trusted identity provider")
    if claims.get("aud") != TRUST["audience"]:
        failures.append("audience is not intended for this workload")
    if not claims.get("sub", "").startswith(TRUST["subject_prefix"]):
        failures.append("subject is outside the approved repository and branch")
    if not failures:
        failures.append("allow: modeled trust conditions pass")
    return failures


def main() -> None:
    assertions = {
        "approved": {
            "iss": TRUST["issuer"],
            "aud": TRUST["audience"],
            "sub": "repo:org/orders-api:ref:refs/heads/main",
        },
        "untrusted-branch": {
            "iss": TRUST["issuer"],
            "aud": TRUST["audience"],
            "sub": "repo:org/orders-api:ref:refs/pull/42",
        },
    }
    for name, claims in assertions.items():
        print(name)
        for result in evaluate_claims(claims):
            print(f"  {result}")


if __name__ == "__main__":
    main()