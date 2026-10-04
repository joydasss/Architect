"""Promote immutable container digests between deployment environments."""


ARTIFACT = {
    "repository": "orders-api",
    "tag": "build-1842",
    "digest": "sha256:8c9f3e-example-digest",
    "source_revision": "4b1d7a9",
}


def deployment_reference(artifact: dict[str, str], environment: str) -> str:
    if not artifact["digest"].startswith("sha256:"):
        raise ValueError("deployment requires a content digest")
    if artifact["tag"] == "latest":
        raise ValueError("mutable latest tag cannot be promoted")
    return f"{environment}: {artifact['repository']}@{artifact['digest']}"


def main() -> None:
    for environment in ("staging", "production"):
        print(deployment_reference(ARTIFACT, environment))
    print(f"Source revision: {ARTIFACT['source_revision']}")


if __name__ == "__main__":
    main()