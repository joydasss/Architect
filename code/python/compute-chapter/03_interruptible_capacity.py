"""Compare stable and interruptible workers for restartable batch work."""


def simulate_jobs(
    job_count: int, stable_workers: int, interruptible_workers: int, interruption_at: int
) -> dict[str, int]:
    stable_completed = min(job_count, stable_workers * interruption_at)
    remaining = job_count - stable_completed
    interruptible_completed = min(remaining, interruptible_workers * interruption_at)
    lost_uncheckpointed = min(interruptible_completed, interruptible_workers)
    completed = stable_completed + interruptible_completed - lost_uncheckpointed
    retry = job_count - completed
    return {"completed": completed, "retry": retry, "lost_work": lost_uncheckpointed}


def main() -> None:
    result = simulate_jobs(
        job_count=120,
        stable_workers=4,
        interruptible_workers=8,
        interruption_at=10,
    )
    print("After interruptible capacity is reclaimed:")
    for name, value in result.items():
        print(f"  {name}: {value}")
    print("A real worker should checkpoint progress and make retries idempotent.")


if __name__ == "__main__":
    main()