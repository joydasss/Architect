"""Flag idle or overprovisioned synthetic resources for human review."""


RESOURCES = [
    {"name": "api-prod", "average_cpu": 0.42, "peak_cpu": 0.81, "critical": True},
    {"name": "dev-runner", "average_cpu": 0.03, "peak_cpu": 0.12, "critical": False},
    {"name": "failover-reserve", "average_cpu": 0.01, "peak_cpu": 0.04, "critical": True},
]


def review_resource(resource: dict[str, object]) -> str:
    if resource["average_cpu"] < 0.05 and resource["peak_cpu"] < 0.15:
        if resource["critical"]:
            return "review: low utilization but marked critical; verify reserve purpose"
        return "candidate: consider scheduling off or reducing capacity"
    if resource["average_cpu"] < 0.5 and resource["peak_cpu"] < 0.9:
        return "review: profile memory, latency, and redundancy before resizing"
    return "retain: measured load may justify current capacity"


def main() -> None:
    for resource in RESOURCES:
        print(f"{resource['name']}: {review_resource(resource)}")


if __name__ == "__main__":
    main()