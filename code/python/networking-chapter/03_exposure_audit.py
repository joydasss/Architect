"""Review synthetic ingress and egress rules for broad exposure."""


RULES = [
    {"direction": "ingress", "source": "203.0.113.0/24", "port": 443, "purpose": "public-api"},
    {"direction": "ingress", "source": "0.0.0.0/0", "port": 22, "purpose": "admin"},
    {"direction": "egress", "source": "0.0.0.0/0", "port": "any", "purpose": "default-route"},
]


def review_rule(rule: dict[str, object]) -> str:
    if rule["direction"] == "ingress" and rule["source"] == "0.0.0.0/0":
        if rule["port"] == 22:
            return "high: administrative ingress is open to every IPv4 source"
        return "review: ingress is globally reachable; confirm intended edge protection"
    if rule["direction"] == "egress" and rule["source"] == "0.0.0.0/0":
        return "review: unrestricted egress can bypass destination policy"
    return "ok: rule has a scoped source in this simplified check"


def main() -> None:
    for rule in RULES:
        print(f"{rule['direction']} {rule['purpose']}: {review_rule(rule)}")


if __name__ == "__main__":
    main()