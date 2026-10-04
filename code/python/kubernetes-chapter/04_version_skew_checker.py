"""Check a simplified supported control-plane and node minor-version skew."""


def minor_version(version: str) -> int:
    pieces = version.split(".")
    if len(pieces) < 2 or not pieces[1].isdigit():
        raise ValueError(f"invalid Kubernetes version: {version}")
    return int(pieces[1])


def check_node_version(
    control_plane: str, node: str, max_minor_skew: int = 2
) -> str:
    control_minor = minor_version(control_plane)
    node_minor = minor_version(node)
    skew = control_minor - node_minor
    if skew < 0:
        return "reject: node minor version is newer than the control plane"
    if skew > max_minor_skew:
        return f"reject: minor-version skew {skew} exceeds {max_minor_skew}"
    return f"review: modeled minor-version skew is {skew}"


def main() -> None:
    control_plane = "1.31.4"
    for node_version in ("1.31.2", "1.29.8", "1.27.9", "1.32.0"):
        print(
            f"control={control_plane} node={node_version}: "
            f"{check_node_version(control_plane, node_version)}"
        )
    print("Provider support policy can be stricter than this simplified check.")


if __name__ == "__main__":
    main()