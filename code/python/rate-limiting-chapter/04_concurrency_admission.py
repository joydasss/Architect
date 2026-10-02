"""Non-blocking concurrency slots plus a bounded waiting-admission count."""

from threading import BoundedSemaphore, Lock


class AdmissionLimiter:
    def __init__(self, max_active: int, max_waiting: int) -> None:
        if max_active <= 0 or max_waiting < 0:
            raise ValueError("active must be positive and waiting non-negative")
        self.slots = BoundedSemaphore(max_active)
        self.max_waiting = max_waiting
        self.waiting = 0
        self.lock = Lock()

    def try_admit(self) -> str:
        if self.slots.acquire(blocking=False):
            return "active"
        with self.lock:
            if self.waiting >= self.max_waiting:
                return "rejected"
            self.waiting += 1
            return "queued"

    def start_queued(self) -> bool:
        if not self.slots.acquire(blocking=False):
            return False
        with self.lock:
            if self.waiting == 0:
                self.slots.release()
                return False
            self.waiting -= 1
        return True

    def finish_active(self) -> None:
        self.slots.release()


def main() -> None:
    limiter = AdmissionLimiter(max_active=2, max_waiting=1)
    assert limiter.try_admit() == "active"
    assert limiter.try_admit() == "active"
    assert limiter.try_admit() == "queued"
    assert limiter.try_admit() == "rejected"

    limiter.finish_active()
    assert limiter.start_queued()
    limiter.finish_active()
    limiter.finish_active()
    print("two active requests admitted; one queued; excess request rejected")
    print("queued request starts when a concurrency slot is released")


if __name__ == "__main__":
    main()