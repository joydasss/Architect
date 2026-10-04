"""Build dependency-safe migration waves from a synthetic workload inventory."""

from collections import defaultdict, deque


def plan_waves(dependencies):
    """Return topological waves or raise ValueError for unknown nodes/cycles."""
    nodes = set(dependencies)
    for requirements in dependencies.values():
        unknown = set(requirements) - nodes
        if unknown:
            raise ValueError(f"unknown dependencies: {sorted(unknown)}")

    remaining = {name: set(requirements) for name, requirements in dependencies.items()}
    dependents = defaultdict(set)
    for name, requirements in remaining.items():
        for requirement in requirements:
            dependents[requirement].add(name)

    ready = deque(sorted(name for name, requirements in remaining.items() if not requirements))
    waves = []
    migrated = set()
    while ready:
        wave = list(ready)
        ready.clear()
        waves.append(wave)
        migrated.update(wave)
        next_wave = set()
        for name in wave:
            for dependent in dependents[name]:
                remaining[dependent].discard(name)
                if not remaining[dependent]:
                    next_wave.add(dependent)
        ready.extend(sorted(next_wave - migrated))

    if len(migrated) != len(nodes):
        raise ValueError("dependency cycle prevents safe wave planning")
    return waves


if __name__ == "__main__":
    workload_dependencies = {
        "identity": set(),
        "database": {"identity"},
        "api": {"database", "identity"},
        "worker": {"database"},
        "frontend": {"api"},
    }
    result = plan_waves(workload_dependencies)
    assert result == [["identity"], ["database"], ["api", "worker"], ["frontend"]]
    try:
        plan_waves({"a": {"b"}, "b": {"a"}})
    except ValueError as error:
        assert "cycle" in str(error)
    else:
        raise AssertionError("cycle was not detected")
    print("Migration waves:", result)