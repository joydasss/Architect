"""Freshness lag and ACL revocation latency model for a RAG system.

Standard library only. Models the end-to-end freshness lag as the sum of
pipeline stages, and the worst-case time an access revocation takes to become
effective given sync interval, index propagation, and cache TTL.
All numbers are illustrative.
"""

# --- End-to-end freshness lag (minutes), worst case and typical ---
stages = [
    # name, typical, worst
    ("change detection (poll every 15 min)", 7.5, 15.0),
    ("fetch + parse queue wait", 2.0, 10.0),
    ("chunk + embed", 3.0, 12.0),
    ("index write + refresh", 1.0, 5.0),
    ("gate + alias promotion (micro-batch)", 5.0, 15.0),
    ("cache TTL on answers", 5.0, 10.0),
]
typ = sum(s[1] for s in stages)
worst = sum(s[2] for s in stages)
print("Freshness lag stages")
for name, t, w in stages:
    print(f"  {name:42s} typical {t:5.1f}  worst {w:5.1f}")
print(f"  {'TOTAL':42s} typical {typ:5.1f}  worst {worst:5.1f}")
slo = 60.0
print(f"  SLO {slo:.0f} min: worst-case budget {'met' if worst <= slo else 'NOT met'}"
      f" ({slo - worst:+.1f} min headroom)")

# --- ACL revocation latency (minutes) ---
acl = [
    ("source ACL change event delivered", 1.0, 5.0),
    ("ACL sync into index metadata or authz store", 5.0, 30.0),
    ("retrieval-scope cache TTL (principal groups)", 5.0, 5.0),
    ("answer cache TTL (if key lacks ACL version)", 0.0, 10.0),
]
r_typ = sum(a[1] for a in acl)
r_worst = sum(a[2] for a in acl)
print("\nRevocation latency stages")
for name, t, w in acl:
    print(f"  {name:48s} typical {t:5.1f}  worst {w:5.1f}")
print(f"  {'TOTAL':48s} typical {r_typ:5.1f}  worst {r_worst:5.1f}")

# With live check against the source/authz service at query time, the sync and
# answer-cache terms vanish; only group-membership cache TTL remains.
live = 5.0
print(f"  With live authz check at query time: worst {live:.1f} min")
print(f"  With ACL version in cache key and no answer reuse across versions: "
      f"worst {r_worst - 10.0:.1f} min")
