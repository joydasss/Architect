"""Compare hybrid-link capacity before and after losing one path."""


def capacity_after_failure(paths: dict[str, int], failed_path: str) -> int:
    return sum(capacity for name, capacity in paths.items() if name != failed_path)


def main() -> None:
    paths = {"site-a-tunnel": 400, "site-b-tunnel": 400}
    required_mbps = 500
    print(f"Configured capacity: {sum(paths.values())} Mbps")
    for failed_path in paths:
        remaining = capacity_after_failure(paths, failed_path)
        status = "meets" if remaining >= required_mbps else "misses"
        print(f"After {failed_path} fails: {remaining} Mbps, {status} {required_mbps} Mbps")
    print("Independent circuits and provider routes must be validated separately.")


if __name__ == "__main__":
    main()