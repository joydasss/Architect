"""Runnable model of replay-window expiry and snapshot-based reset."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResetInstruction:
    reason: str
    snapshot_url: str
    snapshot_watermark: int
    resume_after: int


def resume_or_reset(
    cursor: int,
    oldest_retained: int,
    snapshot_watermark: int,
    snapshot_url: str,
) -> tuple[str, ResetInstruction | int]:
    if cursor < oldest_retained - 1:
        instruction = ResetInstruction(
            reason="cursor_expired",
            snapshot_url=snapshot_url,
            snapshot_watermark=snapshot_watermark,
            resume_after=snapshot_watermark,
        )
        return "reset", instruction
    return "replay", cursor


def main() -> None:
    outcome, value = resume_or_reset(
        cursor=72,
        oldest_retained=100,
        snapshot_watermark=125,
        snapshot_url="/v1/tenants/acme/orders/snapshot?at=125",
    )
    if outcome == "reset":
        print(
            f"{value.reason}: fetch {value.snapshot_url}; "
            f"reconnect strictly after {value.resume_after}"
        )
    else:
        print(f"replay strictly after {value}")


if __name__ == "__main__":
    main()