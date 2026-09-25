/**
 * 04_TwoPhaseCommitSimulation.java
 *
 * A dependency-free simulation of the Two-Phase Commit (2PC) protocol
 * (chapter Section 4.15) across a coordinator and three participants,
 * illustrating: (1) the happy path (all participants vote YES), (2) a
 * participant voting NO during the prepare phase (global abort), and (3) a
 * coordinator crash after participants have voted YES but before the global
 * decision is broadcast — the protocol's well-known blocking weakness
 * (Section 15), where a prepared-but-undecided participant must hold its
 * locks and wait rather than unilaterally deciding.
 *
 * Compile:  javac 04_TwoPhaseCommitSimulation.java -d out
 * Run:      java -cp out TwoPhaseCommitSimulation
 */

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class TwoPhaseCommitSimulation {

    enum Vote { YES, NO }
    enum GlobalDecision { COMMIT, ABORT, UNKNOWN_COORDINATOR_CRASHED }

    /** A participant models one shard/service's local resource manager. */
    static class Participant {
        final String name;
        final boolean willVoteNo;
        boolean prepared = false;
        boolean committed = false;
        boolean rolledBack = false;

        Participant(String name, boolean willVoteNo) {
            this.name = name;
            this.willVoteNo = willVoteNo;
        }

        /** Phase 1: write an undo/redo log record, acquire locks, then vote. */
        Vote prepare() {
            if (willVoteNo) {
                System.out.printf("  [%s] cannot satisfy the local constraint -> VOTE NO%n", name);
                return Vote.NO;
            }
            prepared = true; // durably logged "PREPARED" + locks held, awaiting decision
            System.out.printf("  [%s] wrote PREPARE log record, locks held -> VOTE YES%n", name);
            return Vote.YES;
        }

        /** Phase 2: apply the coordinator's durable global decision. */
        void applyDecision(GlobalDecision decision) {
            if (decision == GlobalDecision.COMMIT) {
                committed = true;
                System.out.printf("  [%s] received COMMIT -> releases locks, applies changes%n", name);
            } else if (decision == GlobalDecision.ABORT) {
                rolledBack = true;
                System.out.printf("  [%s] received ABORT -> releases locks, rolls back%n", name);
            } else {
                System.out.printf(
                    "  [%s] STILL PREPARED, no decision received -> BLOCKED holding locks "
                        + "until coordinator recovers or a timeout/heuristic policy fires%n",
                    name);
            }
        }
    }

    /** The coordinator drives both phases and is the single source of truth
     *  for the global decision once it durably logs it. */
    static class Coordinator {
        GlobalDecision run(List<Participant> participants, boolean simulateCrashBeforeBroadcast) {
            System.out.println("Phase 1 (PREPARE): coordinator asks every participant to vote");
            boolean allYes = true;
            for (Participant p : participants) {
                if (p.prepare() == Vote.NO) {
                    allYes = false;
                }
            }

            GlobalDecision decision = allYes ? GlobalDecision.COMMIT : GlobalDecision.ABORT;
            System.out.printf(
                "Coordinator durably logs global decision: %s (this log write is the "
                    + "commit point — once it's on disk, the outcome is fixed)%n",
                decision);

            if (simulateCrashBeforeBroadcast) {
                System.out.println(
                    "!! Coordinator CRASHES immediately after logging the decision, "
                        + "before broadcasting Phase 2 to any participant.");
                for (Participant p : participants) {
                    if (p.prepared) {
                        p.applyDecision(GlobalDecision.UNKNOWN_COORDINATOR_CRASHED);
                    }
                }
                return GlobalDecision.UNKNOWN_COORDINATOR_CRASHED;
            }

            System.out.println("Phase 2 (COMMIT/ABORT): coordinator broadcasts the decision");
            for (Participant p : participants) {
                p.applyDecision(decision);
            }
            return decision;
        }
    }

    static List<Participant> freshParticipants(boolean secondVotesNo) {
        List<Participant> participants = new ArrayList<>();
        participants.add(new Participant("OrderShard", false));
        participants.add(new Participant("InventoryShard", secondVotesNo));
        participants.add(new Participant("LedgerShard", false));
        return participants;
    }

    public static void main(String[] args) {
        Coordinator coordinator = new Coordinator();

        System.out.println("=== Scenario 1: happy path, all participants vote YES ===");
        coordinator.run(freshParticipants(false), false);

        System.out.println("\n=== Scenario 2: InventoryShard votes NO -> global ABORT ===");
        coordinator.run(freshParticipants(true), false);

        System.out.println("\n=== Scenario 3: all vote YES, coordinator crashes before Phase 2 ===");
        System.out.println("(This is 2PC's classic blocking failure mode — see Section 15.)");
        coordinator.run(freshParticipants(false), true);

        System.out.println(
            "\nIn Scenario 3, every prepared participant is now holding locks on rows/shards "
                + "it cannot release until the coordinator recovers its log and re-sends the "
                + "decision (or an operator applies a heuristic/manual resolution). This is why "
                + "2PC is called a BLOCKING protocol: a single coordinator failure can stall "
                + "unrelated transactions on every participant indefinitely.");
    }
}
