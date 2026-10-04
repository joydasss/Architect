"""Choose the most specific matching route from a synthetic route table."""

from ipaddress import ip_address, ip_network


ROUTES = [
    ("10.0.0.0/8", "private-transit"),
    ("10.40.0.0/16", "shared-services"),
    ("0.0.0.0/0", "nat-egress"),
]


def find_next_hop(destination: str) -> str | None:
    address = ip_address(destination)
    matches = [
        (ip_network(cidr), next_hop)
        for cidr, next_hop in ROUTES
        if address in ip_network(cidr)
    ]
    if not matches:
        return None
    return max(matches, key=lambda route: route[0].prefixlen)[1]


def main() -> None:
    for destination in ("10.40.8.12", "10.55.1.5", "192.0.2.10"):
        print(f"{destination:>12} -> {find_next_hop(destination)}")


if __name__ == "__main__":
    main()