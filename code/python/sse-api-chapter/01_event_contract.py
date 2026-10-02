"""Runnable reference model for a versioned public feed event contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from typing import Any


@dataclass(frozen=True)
class OrderStatusChanged:
    event_id: str
    tenant_id: str
    order_id: str
    status: str
    occurred_at: str
    schema_version: int = 1
    event_type: str = "order.status_changed"

    def validate(self) -> None:
        if not self.event_id or not self.tenant_id or not self.order_id:
            raise ValueError("event identity and scope fields are required")
        if self.status not in {"accepted", "processing", "shipped", "cancelled"}:
            raise ValueError("status is outside the public v1 value set")
        if self.schema_version != 1:
            raise ValueError("unsupported schema version")

    def public_payload(self) -> dict[str, Any]:
        self.validate()
        return {
            "id": self.event_id,
            "type": self.event_type,
            "schema_version": self.schema_version,
            "occurred_at": self.occurred_at,
            "data": {
                "order_id": self.order_id,
                "status": self.status,
            },
        }


def main() -> None:
    event = OrderStatusChanged(
        event_id="tenant-acme-000042",
        tenant_id="acme",
        order_id="ord_8f21",
        status="shipped",
        occurred_at=datetime.now(timezone.utc).isoformat(),
    )
    print(json.dumps(event.public_payload(), indent=2))


if __name__ == "__main__":
    main()