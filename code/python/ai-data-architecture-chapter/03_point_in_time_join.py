"""Point-in-time join versus naive latest-value join (standard library).

Shows label leakage: a naive join attaches the latest feature value to every
training row, including values that did not exist at prediction time.
Run: python 03_point_in_time_join.py
"""

from bisect import bisect_right

# (customer, feature_time_day, support_tickets_30d)
FEATURES = {
    "A": [(1, 0), (10, 1), (20, 6), (30, 9)],
    "B": [(1, 2), (10, 2), (20, 2), (30, 3)],
}
# (customer, prediction_day, churned_within_14_days)
LABELS = [("A", 12, 0), ("A", 18, 1), ("B", 12, 0), ("B", 18, 0)]


def latest_value(cust):
    return FEATURES[cust][-1][1]


def as_of(cust, ts):
    rows = FEATURES[cust]
    i = bisect_right([t for t, _ in rows], ts) - 1
    return rows[i][1] if i >= 0 else None


if __name__ == "__main__":
    print("cust day label naive pit")
    leaks = 0
    for c, day, y in LABELS:
        naive, pit = latest_value(c), as_of(c, day)
        leaks += naive != pit
        print(f"{c:>4} {day:>3} {y:>5} {naive:>5} {pit:>3}")
    print(f"rows where naive != point-in-time: {leaks} of {len(LABELS)}")
