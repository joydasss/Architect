"""Model AWS Region and Availability Zone placement as failure domains."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Component:
    name: str
    azs: tuple[str, ...]
    minimum_healthy: int

    def healthy_after(self, failed_az: str) -> int:
        return sum(az != failed_az for az in self.azs)

    def survives(self, failed_az: str) -> bool:
        return self.healthy_after(failed_az) >= self.minimum_healthy


def main() -> None:
    design = [
        Component("api", ("az-a", "az-b", "az-c"), 2),
        Component("worker", ("az-a", "az-b", "az-c"), 1),
        Component("single-az-cache", ("az-a",), 1),
    ]

    for failed_az in ("az-a", "az-b", "az-c"):
        results = {component.name: component.survives(failed_az) for component in design}
        print(f"failure={failed_az}: {results}")
        assert results["api"]
        assert results["worker"]
    assert not design[2].survives("az-a")
    print("Regional redundancy does not protect a single-AZ component.")


if __name__ == "__main__":
    main()
