"""
Chapter: Distributed Transactions - Section 4.3
A Three-Phase Commit (3PC) coordinator/participant simulation demonstrating:
  1. The non-blocking recovery path: coordinator crashes after every
     participant acknowledges PreCommit, and every participant safely
     self-commits on timeout with no coordinator contact needed.
  2. The residual network-partition split-brain weakness: a partition at
     the PreCommit boundary causes some participants to self-commit and
     others to self-abort - the exact outcome 3PC exists to prevent,
     occurring without any coordinator crash at all.
"""

from enum import Enum, auto


class ParticipantState(Enum):
    ACTIVE = auto()
    CAN_COMMIT_VOTED = auto()   # voted YES in phase 1
    PRECOMMIT_ACKED = auto()    # durably recorded "group decided to commit"
    COMMITTED = auto()
    ABORTED = auto()


class Participant:
    def __init__(self, name: str):
        self.name = name
        self.state = ParticipantState.ACTIVE

    def can_commit_vote(self) -> str:
        self.state = ParticipantState.CAN_COMMIT_VOTED
        return "YES"

    def ack_precommit(self) -> None:
        assert self.state == ParticipantState.CAN_COMMIT_VOTED
        self.state = ParticipantState.PRECOMMIT_ACKED

    def do_commit(self) -> None:
        self.state = ParticipantState.COMMITTED

    def self_commit_on_timeout(self) -> None:
        """Safe because reaching PRECOMMIT_ACKED is only possible if every
        participant voted YES - no one can still decide to abort."""
        assert self.state == ParticipantState.PRECOMMIT_ACKED
        self.state = ParticipantState.COMMITTED

    def self_abort_on_timeout(self) -> None:
        """Safe because a global commit could not have been decided without
        this participant ever reaching PreCommit."""
        assert self.state == ParticipantState.CAN_COMMIT_VOTED
        self.state = ParticipantState.ABORTED


def scenario_non_blocking_recovery() -> None:
    print("Scenario 1: coordinator crashes after every participant ACKs PreCommit -")
    print("            every participant independently self-commits on timeout.")
    participants = [Participant("A"), Participant("B"), Participant("C")]

    # Phase 1: CanCommit
    votes = [p.can_commit_vote() for p in participants]
    assert all(v == "YES" for v in votes)

    # Phase 2: PreCommit - every participant acknowledges
    for p in participants:
        p.ack_precommit()

    print("  Coordinator crashes here - DoCommit (phase 3) is never sent.")
    for p in participants:
        p.self_commit_on_timeout()
        print(f"  {p.name}: timed out waiting for DoCommit -> self-{p.state.name}")

    assert all(p.state == ParticipantState.COMMITTED for p in participants)
    print("  Result: no blocking, no coordinator contact needed - 3PC's entire point.")


def scenario_partition_split_brain() -> None:
    print("\nScenario 2: network partition splits participants right at the")
    print("            PreCommit boundary - split-brain, with NO coordinator crash.")
    group_a = [Participant("A1"), Participant("A2"), Participant("A3")]
    group_b = [Participant("B1"), Participant("B2")]
    all_participants = group_a + group_b

    for p in all_participants:
        assert p.can_commit_vote() == "YES"

    # Coordinator sends PreCommit to everyone, but a partition drops the
    # message to group_b before it arrives.
    for p in group_a:
        p.ack_precommit()
    print("  Group A received and acknowledged PreCommit.")
    print("  Network partition drops the PreCommit message to Group B.")

    # Both groups independently time out on their own clocks.
    for p in group_a:
        p.self_commit_on_timeout()
        print(f"  {p.name}: timed out at PRECOMMIT_ACKED -> self-{p.state.name}")
    for p in group_b:
        p.self_abort_on_timeout()
        print(f"  {p.name}: timed out at CAN_COMMIT_VOTED -> self-{p.state.name}")

    committed = [p for p in all_participants if p.state == ParticipantState.COMMITTED]
    aborted = [p for p in all_participants if p.state == ParticipantState.ABORTED]
    print(f"\n  Committed: {[p.name for p in committed]}")
    print(f"  Aborted:   {[p.name for p in aborted]}")
    assert committed and aborted, "expected a genuine split-brain outcome"
    print("  Result: a real split-brain - some participants committed, others")
    print("  aborted, for what should have been one atomic transaction. This is")
    print("  3PC's residual weakness: non-blocking under crash failures, but not")
    print("  partition-tolerant.")


if __name__ == "__main__":
    scenario_non_blocking_recovery()
    scenario_partition_split_brain()
