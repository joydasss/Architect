import java.util.*;

/**
 * Classic System R-style dynamic-programming join order enumeration.
 *
 * Companion to 06_Databases_and_Storage/CH04_Query_Optimizers.md, Section 10
 * (Section 4.5's join-order search space).
 *
 * Given N relations and pairwise join selectivities, this enumerates every
 * subset of relations exactly once (2^N subsets), and for each subset keeps
 * only the CHEAPEST way to join that subset -- discarding every other plan
 * for the same subset, because whichever plan is cheapest for a subset stays
 * cheapest no matter what relation joins onto it next (the optimal-
 * substructure property that makes dynamic programming valid here).
 *
 * This is why real optimizers can afford exhaustive join-order search up to
 * roughly 8-12 tables (2^12 = 4096 subsets is trivial) but must switch to a
 * greedy or randomized heuristic beyond that, since 2^N explodes past that
 * point (2^20 is over a million subsets).
 */
public class JoinOrderDynamicProgramming {

    record Relation(String name, long rowCount) {}

    /** selectivity[i][j] = fraction of the cross product (i rows * j rows)
     * that survives the join predicate between relation i and relation j;
     * 1.0 means "no join predicate between these two" (an expensive
     * cross join) -- the optimizer should naturally avoid such orders. */
    static double[][] selectivity;
    static Relation[] relations;

    public static void main(String[] args) {
        relations = new Relation[] {
            new Relation("orders", 1_000_000),
            new Relation("customers", 50_000),
            new Relation("order_items", 4_000_000),
            new Relation("products", 20_000),
        };

        // Symmetric selectivity matrix; 1.0 = no direct join predicate exists.
        selectivity = new double[][] {
            /*              orders customers order_items products */
            /* orders    */ {1.0,  0.00002,  1.0,        1.0},
            /* customers */ {0.00002, 1.0,   1.0,        1.0},
            /* order_items*/{1.0,  1.0,      0.00000025, 0.00005},
            /* products  */ {1.0,  1.0,      0.00005,    1.0},
        };
        // orders <-> order_items has no direct entry above by mistake fix:
        selectivity[0][2] = 0.0000025; selectivity[2][0] = 0.0000025;

        Map<Set<Integer>, PlanCost> best = solve(relations.length);

        Set<Integer> all = new HashSet<>();
        for (int i = 0; i < relations.length; i++) all.add(i);
        PlanCost optimal = best.get(all);

        System.out.println("Optimal join order (dynamic programming, "
                + (1 << relations.length) + " subsets considered):");
        System.out.println("  " + optimal.orderDescription);
        System.out.printf("  Estimated cost: %,.0f%n", optimal.cost);
        System.out.printf("  Estimated result cardinality: %,.0f rows%n", optimal.rowEstimate);
    }

    record PlanCost(double cost, double rowEstimate, String orderDescription) {}

    static Map<Set<Integer>, PlanCost> solve(int n) {
        Map<Set<Integer>, PlanCost> best = new HashMap<>();

        // Base case: every single-relation "subset" costs 0 to access
        // (ignoring scan cost for clarity -- a real optimizer folds base
        // table access cost in here too).
        for (int i = 0; i < n; i++) {
            Set<Integer> singleton = Set.of(i);
            best.put(singleton, new PlanCost(0.0, relations[i].rowCount(), relations[i].name()));
        }

        // Enumerate subsets in increasing size order so every subset's
        // sub-subsets are already solved when we need them.
        List<Set<Integer>> allSubsets = enumerateSubsets(n);
        allSubsets.sort(Comparator.comparingInt(Set::size));

        for (Set<Integer> subset : allSubsets) {
            if (subset.size() < 2) continue;

            PlanCost cheapest = null;

            // Try every way to split this subset into two smaller,
            // already-solved subsets joined together.
            for (Set<Integer> left : properNonEmptySubsets(subset)) {
                Set<Integer> right = new HashSet<>(subset);
                right.removeAll(left);
                if (right.isEmpty()) continue;

                PlanCost leftPlan = best.get(left);
                PlanCost rightPlan = best.get(right);
                if (leftPlan == null || rightPlan == null) continue;

                double joinSelectivity = bestCrossSelectivity(left, right);
                double resultRows = leftPlan.rowEstimate() * rightPlan.rowEstimate() * joinSelectivity;

                // Cost model: cost of computing both sides, plus a hash-join
                // -shaped cost proportional to the smaller side (build) plus
                // the larger side (probe).
                double buildProbeCost = Math.min(leftPlan.rowEstimate(), rightPlan.rowEstimate())
                        + Math.max(leftPlan.rowEstimate(), rightPlan.rowEstimate());
                double totalCost = leftPlan.cost() + rightPlan.cost() + buildProbeCost;

                String description = "(" + leftPlan.orderDescription() + " JOIN "
                        + rightPlan.orderDescription() + ")";

                if (cheapest == null || totalCost < cheapest.cost()) {
                    cheapest = new PlanCost(totalCost, resultRows, description);
                }
            }

            if (cheapest != null) {
                best.put(subset, cheapest);
            }
        }

        return best;
    }

    static double bestCrossSelectivity(Set<Integer> left, Set<Integer> right) {
        double best = 1.0; // default: no direct predicate, i.e. a cross join
        for (int i : left) {
            for (int j : right) {
                best = Math.min(best, selectivity[i][j]);
            }
        }
        return best;
    }

    static List<Set<Integer>> enumerateSubsets(int n) {
        List<Set<Integer>> subsets = new ArrayList<>();
        for (int mask = 1; mask < (1 << n); mask++) {
            Set<Integer> subset = new HashSet<>();
            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) != 0) subset.add(i);
            }
            subsets.add(subset);
        }
        return subsets;
    }

    static List<Set<Integer>> properNonEmptySubsets(Set<Integer> set) {
        List<Integer> elements = new ArrayList<>(set);
        int n = elements.size();
        List<Set<Integer>> result = new ArrayList<>();
        for (int mask = 1; mask < (1 << n) - 1; mask++) {
            Set<Integer> subset = new HashSet<>();
            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) != 0) subset.add(elements.get(i));
            }
            result.add(subset);
        }
        return result;
    }
}
