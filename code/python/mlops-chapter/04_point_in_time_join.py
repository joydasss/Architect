"""Point-in-time correct feature join versus a naive "latest value" join.

Standard library only. Shows how a naive join leaks a feature value computed
after the label event and inflates apparent training signal.
Each feature row is (entity, event_time, value); times are integer hours.
"""
from bisect import bisect_right

# customer_id -> list of (feature_time, txn_count_24h) sorted by time
FEATURES = {
    "c1": [(0, 2), (24, 3), (48, 40)],   # at hour 48 the card was already compromised
    "c2": [(0, 1), (24, 1), (48, 2)],
}
# training examples: (customer, decision_time, label)  label 1 = fraud confirmed later
EXAMPLES = [("c1", 30, 1), ("c2", 30, 0), ("c1", 10, 0)]


def latest_join(entity, _t):
    return FEATURES[entity][-1][1]


def point_in_time_join(entity, t):
    rows = FEATURES[entity]
    times = [r[0] for r in rows]
    i = bisect_right(times, t) - 1
    return rows[i][1] if i >= 0 else None


if __name__ == "__main__":
    print("customer  decision_t  label  naive(latest)  point_in_time")
    for c, t, y in EXAMPLES:
        print(f"{c:<9} {t:>10}  {y:>5}  {latest_join(c, t):>13}  {point_in_time_join(c, t)!s:>13}")
    naive = [(latest_join(c, t), y) for c, t, y in EXAMPLES]
    pit = [(point_in_time_join(c, t), y) for c, t, y in EXAMPLES]
    for name, rows in (("naive", naive), ("point-in-time", pit)):
        pos = [v for v, y in rows if y == 1]
        neg = [v for v, y in rows if y == 0]
        print(f"{name}: mean feature for fraud={sum(pos)/len(pos):.1f}, non-fraud={sum(neg)/len(neg):.1f}")
