"""
Chapter: Distributed Transactions - Section 4.2
A Two-Phase Commit (2PC) coordinator/participant simulation focused on the
in-doubt-transaction problem: what happens to participants when the
coordinator crashes after logging its COMMIT decision but before
broadcasting it, and how presumed-abort plus durable-log-replay recovery
resolves it (or, when the log itself is not durable, why a heuristic
decision becomes necessary).
"""

from enum import Enum, auto


class ParticipantState(Enum):
    ACTIVE = auto()
    PREPARED = auto()      # voted YES, holding locks, awaiting decision
    IN_DOUBT = auto()       # prepared but coordinator is unreachable
    COMMITTED = auto()
    ABORTED = auto()
    HEURISTIC_DECISION = auto()  # operator manually resolved an in-doubt transaction


class Participant:
    def __init__(self, name: str):
        self.name = name
        self.state = ParticipantState.ACTIVE

    def prepare(self) -> str:
        self.state = ParticipantState.PREPARED
        return "YES"

    def receive_decision(self, decision: str) -> None:
        self.state = ParticipantState.COMMITTED if decision == "COMMIT" else ParticipantState.ABORTED

    def go_in_doubt(self) -> None:
        assert self.state == ParticipantState.PREPARED
        self.state = ParticipantState.IN_DOUBT

    def presumed_abort(self) -> None:
        """Participant queries a coordinator with no record of this txn -> safely abort."""
        assert self.state == ParticipantState.IN_DOUBT
        self.state = ParticipantState.ABORTED

    def heuristic_decision(self, decision: str) -> None:
        assert self.state == ParticipantState.IN_DOUBT
        self.state = ParticipantState.COMMITTED if decision == "COMMIT" else ParticipantState.ABORTED
        print(f"  [OPERATOR] {self.name}: heuristic decision applied -> {self.state.name}")


class DurableLog:
    """A coordinator's crash-recoverable transaction log."""

    def __init__(self):
        self._entries: dict[str, str] = {}

    def log_commit(self, txn_id: str) -> None:
        self._entries[txn_id] = "COMMIT"

    def lookup(self, txn_id: str) -> str | None:
        return self._entries.get(txn_id)


def scenario_happy_path() -> None:
    print("Scenario 1: happy path - all participants vote YES, coordinator commits.")
    participants = [Participant("Orders Service"), Participant("Billing Service")]
    votes = [p.prepare() for p in participants]
    decision = "COMMIT" if all(v == "YES" for v in votes) else "ABORT"
    for p in participants:
        p.receive_decision(decision)
    for p in participants:
        print(f"  {p.name}: {p.state.name}")
    assert all(p.state == ParticipantState.COMMITTED for p in participants)


def scenario_crash_with_recoverable_log() -> None:
    print("\nScenario 2: coordinator crashes after logging COMMIT, before broadcasting -")
    print("            durable log survives, recovery replay resolves the in-doubt state.")
    participants = [Participant("Orders Service"), Participant("Billing Service")]
    log = DurableLog()
    txn_id = "txn-1001"

    for p in participants:
        assert p.prepare() == "YES"

    log.log_commit(txn_id)  # coordinator durably logs the decision...
    print("  Coordinator crashes here - decision never broadcast.")
    for p in participants:
        p.go_in_doubt()
        print(f"  {p.name}: {p.state.name} (locks held, decision unknown)")

    print("  Coordinator restarts, replays its durable log...")
    recovered_decision = log.lookup(txn_id)
    assert recovered_decision == "COMMIT"
    for p in participants:
        p.receive_decision(recovered_decision)
        print(f"  {p.name}: recovered decision applied -> {p.state.name}")

    assert all(p.state == ParticipantState.COMMITTED for p in participants)
    print("  Result: no heuristic decision needed - durable logging made this safe.")


def scenario_crash_with_unrecoverable_log() -> None:
    print("\nScenario 3: coordinator crashes with NO durable log (in-memory only) -")
    print("            recovery finds no record; presumed abort resolves most participants,")
    print("            but one has waited past the acceptable window and needs a heuristic decision.")
    participants = [Participant("Orders Service"), Participant("Billing Service")]
    for p in participants:
        assert p.prepare() == "YES"

    print("  Coordinator crashes with no durable decision log at all.")
    for p in participants:
        p.go_in_doubt()

    # Coordinator restarts with an empty (unrecoverable) log.
    for p in participants[:1]:
        p.presumed_abort()
        print(f"  {p.name}: presumed abort -> {p.state.name} (no coordinator record found)")

    # The second participant is a legacy resource manager whose local recovery
    # window has expired without ever reaching the coordinator - an operator
    # must make the call.
    participants[1].heuristic_decision("ABORT")

    assert all(p.state == ParticipantState.ABORTED for p in participants)
    print("  Result: both participants ended up ABORTED, but only because presumed")
    print("  abort and the operator's heuristic decision happened to agree - a")
    print("  heuristic mixed outcome was a real risk here, not a guarantee against.")


if __name__ == "__main__":
    scenario_happy_path()
    scenario_crash_with_recoverable_log()
    scenario_crash_with_unrecoverable_log()
