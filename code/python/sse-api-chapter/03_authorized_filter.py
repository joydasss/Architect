"""Runnable model showing tenant authorization before filter selection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    allowed_topics: frozenset[str]


@dataclass(frozen=True)
class FeedEvent:
    tenant_id: str
    topic: str
    event_id: str


def select_events(
    principal: Principal,
    requested_tenant: str,
    requested_topics: set[str],
    events: list[FeedEvent],
) -> list[FeedEvent]:
    if requested_tenant != principal.tenant_id:
        raise PermissionError("principal is not authorized for this tenant")
    if not requested_topics:
        raise ValueError("at least one topic must be selected")
    if not requested_topics <= principal.allowed_topics:
        raise PermissionError("filter requests a topic outside the allowed set")
    return [
        event
        for event in events
        if event.tenant_id == principal.tenant_id
        and event.topic in requested_topics
    ]


def main() -> None:
    principal = Principal("user-17", "acme", frozenset({"orders", "deployments"}))
    events = [
        FeedEvent("acme", "orders", "a-41"),
        FeedEvent("acme", "deployments", "a-42"),
        FeedEvent("globex", "orders", "g-18"),
    ]
    selected = select_events(principal, "acme", {"orders"}, events)
    print(f"authorized events: {[event.event_id for event in selected]}")
    try:
        select_events(principal, "acme", {"orders", "payroll"}, events)
    except PermissionError as error:
        print(f"broadened filter rejected: {error}")


if __name__ == "__main__":
    main()