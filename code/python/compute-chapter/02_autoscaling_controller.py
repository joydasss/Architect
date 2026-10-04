"""Simulate bounded worker autoscaling from queue demand."""

from math import ceil


def desired_workers(
    queue_depth: int,
    target_queue_per_worker: int,
    minimum: int,
    maximum: int,
) -> int:
    requested = ceil(queue_depth / target_queue_per_worker)
    return min(maximum, max(minimum, requested))


def main() -> None:
    queue_depths = [80, 250, 1200, 700, 90]
    current = 2
    minimum = 2
    maximum = 12
    target_queue_per_worker = 100

    for queue_depth in queue_depths:
        desired = desired_workers(
            queue_depth, target_queue_per_worker, minimum, maximum
        )
        if desired == current:
            action = "hold"
        elif desired > current:
            action = "scale out"
        else:
            action = "scale in"
        print(f"queue={queue_depth:>4} workers={current:>2}->{desired:>2} action={action}")
        current = desired

    print("Production policies also need cooldown, readiness, and downstream limits.")


if __name__ == "__main__":
    main()