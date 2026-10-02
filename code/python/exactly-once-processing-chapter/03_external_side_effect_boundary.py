"""Show why an outbox alone cannot make a remote provider exactly once."""

import sqlite3


class Provider:
    def __init__(self, honors_keys: bool) -> None:
        self.honors_keys = honors_keys
        self.effects: list[tuple[str | None, int]] = []
        self.results_by_key: dict[str, str] = {}

    def charge(self, key: str, amount: int) -> str:
        if self.honors_keys and key in self.results_by_key:
            return self.results_by_key[key]
        result = f"charge-{len(self.effects) + 1}"
        self.effects.append((key if self.honors_keys else None, amount))
        if self.honors_keys:
            self.results_by_key[key] = result
        return result


def create_outbox() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE outbox (operation_id TEXT PRIMARY KEY, amount INTEGER NOT NULL, sent INTEGER NOT NULL)"
    )
    with connection:
        connection.execute(
            "INSERT INTO outbox(operation_id, amount, sent) VALUES ('order-42-payment', 2500, 0)"
        )
    return connection


def dispatch(connection: sqlite3.Connection, provider: Provider, lose_response: bool) -> None:
    row = connection.execute(
        "SELECT operation_id, amount FROM outbox WHERE sent = 0"
    ).fetchone()
    if row is None:
        return
    operation_id, amount = row
    result = provider.charge(operation_id, amount)
    if lose_response:
        raise TimeoutError(f"provider acted but response was lost ({result})")
    with connection:
        connection.execute(
            "UPDATE outbox SET sent = 1 WHERE operation_id = ?", (operation_id,)
        )


def run_case(honors_keys: bool) -> int:
    connection = create_outbox()
    provider = Provider(honors_keys=honors_keys)
    try:
        dispatch(connection, provider, lose_response=True)
    except TimeoutError as error:
        print(f"first call: {error}")
    # The outbox is still pending, so the relay retries the same logical operation.
    dispatch(connection, provider, lose_response=False)
    effects = len(provider.effects)
    state = connection.execute("SELECT sent FROM outbox").fetchone()[0]
    print(f"provider_keys={honors_keys}: visible_effects={effects}, outbox_sent={state}")
    connection.close()
    return effects


def main() -> None:
    keyed_effects = run_case(honors_keys=True)
    unkeyed_effects = run_case(honors_keys=False)
    assert keyed_effects == 1
    assert unkeyed_effects == 2


if __name__ == "__main__":
    main()