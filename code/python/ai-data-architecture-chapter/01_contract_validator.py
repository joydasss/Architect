"""Source data contract validator (standard library only).

Validates a batch of records against a versioned contract that covers schema,
semantics (enum values, ranges), null behavior, freshness, and a quality SLO.
Run: python 01_contract_validator.py
"""

from datetime import datetime, timedelta, timezone

CONTRACT = {
    "name": "crm.customer_events",
    "version": "2.1.0",
    "owner": "crm-data-team",
    "freshness_max_lag_minutes": 60,
    "quality_slo": {"min_valid_ratio": 0.98},
    "fields": {
        "customer_id": {"type": str, "nullable": False},
        "event_time": {"type": datetime, "nullable": False},
        "status": {"type": str, "nullable": False,
                   "enum": {"active", "paused", "closed"}},
        "monthly_spend": {"type": float, "nullable": True, "min": 0.0, "max": 50000.0},
        "consent_marketing": {"type": bool, "nullable": False},
    },
}

NOW = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)


def validate_record(rec, contract):
    errors = []
    for name, rule in contract["fields"].items():
        if name not in rec:
            errors.append(f"{name}: missing field")
            continue
        value = rec[name]
        if value is None:
            if not rule["nullable"]:
                errors.append(f"{name}: null not allowed")
            continue
        if not isinstance(value, rule["type"]) or (
                rule["type"] is float and isinstance(value, bool)):
            errors.append(f"{name}: expected {rule['type'].__name__}")
            continue
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{name}: value '{value}' not in enum")
        if "min" in rule and value < rule["min"]:
            errors.append(f"{name}: below min {rule['min']}")
        if "max" in rule and value > rule["max"]:
            errors.append(f"{name}: above max {rule['max']}")
    extra = set(rec) - set(contract["fields"])
    if extra:
        errors.append(f"unexpected fields: {sorted(extra)}")
    return errors


def validate_batch(records, contract, now):
    valid, quarantined = [], []
    for rec in records:
        errs = validate_record(rec, contract)
        (quarantined if errs else valid).append((rec, errs))
    newest = max(r["event_time"] for r in records if isinstance(r.get("event_time"), datetime))
    lag_min = (now - newest).total_seconds() / 60
    ratio = len(valid) / len(records)
    return {
        "valid": len(valid),
        "quarantined": quarantined,
        "valid_ratio": ratio,
        "lag_minutes": lag_min,
        "freshness_ok": lag_min <= contract["freshness_max_lag_minutes"],
        "slo_ok": ratio >= contract["quality_slo"]["min_valid_ratio"],
    }


def make_batch():
    base = NOW - timedelta(minutes=25)
    recs = []
    for i in range(95):
        recs.append({
            "customer_id": f"C{i:04d}",
            "event_time": base - timedelta(minutes=i % 20),
            "status": ["active", "paused", "closed"][i % 3],
            "monthly_spend": float(10 + i),
            "consent_marketing": i % 2 == 0,
        })
    # Five seeded defects.
    recs.append({"customer_id": None, "event_time": base, "status": "active",
                 "monthly_spend": 5.0, "consent_marketing": True})
    recs.append({"customer_id": "C9001", "event_time": base, "status": "suspended",
                 "monthly_spend": 5.0, "consent_marketing": True})
    recs.append({"customer_id": "C9002", "event_time": base, "status": "active",
                 "monthly_spend": -12.0, "consent_marketing": False})
    recs.append({"customer_id": "C9003", "event_time": base, "status": "active",
                 "monthly_spend": "40", "consent_marketing": True})
    recs.append({"customer_id": "C9004", "event_time": base, "status": "active",
                 "monthly_spend": 7.0, "consent_marketing": True, "segment": "x"})
    return recs


if __name__ == "__main__":
    batch = make_batch()
    result = validate_batch(batch, CONTRACT, NOW)
    print(f"contract {CONTRACT['name']} v{CONTRACT['version']} owner={CONTRACT['owner']}")
    print(f"records={len(batch)} valid={result['valid']} quarantined={len(result['quarantined'])}")
    print(f"valid_ratio={result['valid_ratio']:.3f} slo_min={CONTRACT['quality_slo']['min_valid_ratio']}"
          f" slo_ok={result['slo_ok']}")
    print(f"lag_minutes={result['lag_minutes']:.0f} freshness_ok={result['freshness_ok']}")
    for rec, errs in result["quarantined"]:
        print(f"  QUARANTINE {rec['customer_id']}: {'; '.join(errs)}")
    print("decision:", "PUBLISH" if result["slo_ok"] and result["freshness_ok"] else "HOLD previous version")
