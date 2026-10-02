"""Event schema evolution: upcasting old events as the domain model changes.

Demonstrates Section 4.4: old events can never be deleted or rewritten
(they are the immutable historical record), so when the domain model's
understanding of an event changes, the event *store* keeps emitting the
old shape it originally recorded, and an upcaster chain transforms each
stored event into the current in-memory shape at read time, one version
step at a time. This is the mechanism that lets the current aggregate
code only ever have to understand the *latest* event shape.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List


# --- Raw stored event envelopes: what actually persists, forever ---
# In a real event store this is typically a (type name, schema version,
# JSON payload) tuple. We model that directly here instead of using
# typed dataclasses for the raw envelope, since the whole point is that
# the stored shape is untyped/versioned data, not a fixed Python class.

RawEvent = Dict[str, Any]


def make_raw(event_type: str, schema_version: int, payload: Dict[str, Any]) -> RawEvent:
    return {"type": event_type, "schema_version": schema_version, "payload": payload}


# --- Current (v3) domain-event shape the aggregate code understands ---

@dataclass(frozen=True)
class UserRegisteredV3:
    user_id: str
    email: str
    full_name: str
    marketing_opt_in: bool


# History of the schema, oldest first, to make the drift concrete:
#
#   v1 (original):    {user_id, email}
#   v2 (added name):  {user_id, email, full_name}       -- split "name" into
#                                                           first/last was
#                                                           rejected; kept
#                                                           full_name, but
#                                                           the field didn't
#                                                           exist in v1 events
#   v3 (added consent): {user_id, email, full_name, marketing_opt_in}
#                                                        -- GDPR-driven field
#                                                           added; must
#                                                           default safely
#                                                           for pre-GDPR events


Upcaster = Callable[[RawEvent], RawEvent]


def upcast_v1_to_v2(raw: RawEvent) -> RawEvent:
    """v1 events never captured a name at all -- upcasting can only supply
    a defensible placeholder, never invent data that was never recorded.
    This is the sharp edge of event schema evolution: upcasting can widen
    or default a shape, but it cannot recover information nobody wrote
    down at the time."""
    payload = dict(raw["payload"])
    payload.setdefault("full_name", "(name not captured pre-v2)")
    return make_raw(raw["type"], schema_version=2, payload=payload)


def upcast_v2_to_v3(raw: RawEvent) -> RawEvent:
    """v2 events predate the GDPR marketing-consent field; the safe,
    compliant default for events recorded before consent was even asked
    is False (opted OUT), never True -- a wrong default here would be a
    compliance bug, not just a data-quality nuisance."""
    payload = dict(raw["payload"])
    payload.setdefault("marketing_opt_in", False)
    return make_raw(raw["type"], schema_version=3, payload=payload)


UPCASTER_CHAIN: Dict[int, Upcaster] = {
    1: upcast_v1_to_v2,
    2: upcast_v2_to_v3,
}

CURRENT_SCHEMA_VERSION = 3


def upcast_to_current(raw: RawEvent) -> UserRegisteredV3:
    """Walk the upcaster chain one version at a time until the raw event
    reaches CURRENT_SCHEMA_VERSION, then deserialize into the one shape
    the rest of the codebase actually works with. Adding a v4 field later
    means adding exactly one new upcaster function here -- every event
    ever stored, at every prior version, continues to load correctly
    with zero rewriting of historical data."""
    while raw["schema_version"] < CURRENT_SCHEMA_VERSION:
        upcaster = UPCASTER_CHAIN[raw["schema_version"]]
        raw = upcaster(raw)
    payload = raw["payload"]
    return UserRegisteredV3(
        user_id=payload["user_id"],
        email=payload["email"],
        full_name=payload["full_name"],
        marketing_opt_in=payload["marketing_opt_in"],
    )


def main() -> None:
    # Three raw events, as they actually exist on disk today, each frozen
    # at whatever schema version was current when they were originally
    # written -- none of them have ever been touched since.
    raw_events: List[RawEvent] = [
        make_raw(
            "UserRegistered",
            schema_version=1,
            payload={"user_id": "u-100", "email": "amara@example.com"},
        ),
        make_raw(
            "UserRegistered",
            schema_version=2,
            payload={
                "user_id": "u-200",
                "email": "diego@example.com",
                "full_name": "Diego Fernandez",
            },
        ),
        make_raw(
            "UserRegistered",
            schema_version=3,
            payload={
                "user_id": "u-300",
                "email": "lin@example.com",
                "full_name": "Lin Wei",
                "marketing_opt_in": True,
            },
        ),
    ]

    for raw in raw_events:
        current = upcast_to_current(raw)
        print(
            f"stored schema_version={raw['schema_version']} -> "
            f"upcasted: {current}"
        )

    # Prove idempotence: upcasting an already-current event is a no-op
    # chain (the while loop never runs) and returns the same data.
    already_current = raw_events[2]
    result = upcast_to_current(already_current)
    assert result.marketing_opt_in is True
    print("v3 event required zero upcasting, as expected")

    # Prove the sharp-edge default: a v1 event's full_name is genuinely
    # unknown, not silently fabricated as real data.
    v1_result = upcast_to_current(raw_events[0])
    assert v1_result.full_name == "(name not captured pre-v2)"
    assert v1_result.marketing_opt_in is False
    print("v1 event upcasted with explicit, auditable placeholder defaults")


if __name__ == "__main__":
    main()
