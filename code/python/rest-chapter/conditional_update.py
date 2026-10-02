"""Demonstrate a resource-version precondition preventing a lost update."""

from dataclasses import dataclass


class PreconditionFailed(Exception):
    pass


@dataclass
class Order:
    order_id: int
    status: str
    version: int

    @property
    def etag(self) -> str:
        return f'"order-{self.order_id}-v{self.version}"'


class OrderStore:
    def __init__(self) -> None:
        self.orders = {42: Order(42, "pending", 1)}

    def update_status(self, order_id: int, expected_etag: str, status: str) -> Order:
        order = self.orders.get(order_id)
        if order is None:
            raise KeyError(order_id)
        if expected_etag != order.etag:
            raise PreconditionFailed(
                f"stale representation: expected {expected_etag}, current {order.etag}"
            )
        order.status = status
        order.version += 1
        return order


def main() -> None:
    store = OrderStore()
    client_a_etag = store.orders[42].etag
    client_b_etag = store.orders[42].etag

    first = store.update_status(42, client_a_etag, "confirmed")
    print(f"client A updated: status={first.status}, ETag={first.etag}")

    try:
        store.update_status(42, client_b_etag, "cancelled")
    except PreconditionFailed as error:
        print("client B rejected as stale:", error)
    else:
        raise AssertionError("stale update must not overwrite the newer state")

    current = store.orders[42]
    assert (current.status, current.version) == ("confirmed", 2)
    print("final resource state:", current)


if __name__ == "__main__":
    main()