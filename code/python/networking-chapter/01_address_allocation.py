"""Detect overlapping network allocations using Python's ipaddress module."""

from ipaddress import ip_network


ALLOCATIONS = {
    "enterprise": "10.0.0.0/16",
    "production": "10.10.0.0/16",
    "development": "10.20.0.0/16",
    "partner": "10.10.8.0/21",
}


def find_overlaps(allocations: dict[str, str]) -> list[tuple[str, str]]:
    networks = {name: ip_network(cidr) for name, cidr in allocations.items()}
    names = list(networks)
    overlaps = []
    for index, first_name in enumerate(names):
        for second_name in names[index + 1 :]:
            if networks[first_name].overlaps(networks[second_name]):
                overlaps.append((first_name, second_name))
    return overlaps


def main() -> None:
    for name, cidr in ALLOCATIONS.items():
        print(f"{name:>12}: {cidr}")
    overlaps = find_overlaps(ALLOCATIONS)
    if overlaps:
        for first, second in overlaps:
            print(f"OVERLAP: {first} conflicts with {second}")
    else:
        print("No overlaps found.")


if __name__ == "__main__":
    main()