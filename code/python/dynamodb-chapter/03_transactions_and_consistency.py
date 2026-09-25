"""03_transactions_and_consistency.py

Demonstrates DynamoDB Transactions (CH17_DynamoDB.md Section 4.8) and the
eventual-vs-strong read consistency choice (Section 4.6). TransactWriteItems
atomically moves funds between two accounts with a ConditionExpression
guarding against overdraft; a follow-up read shows the difference between
an eventually consistent GetItem (may briefly return stale data on a GSI or
right after a write to a different replica) and a strongly consistent one.

Requires: boto3, and a reachable DynamoDB endpoint (local or real AWS).

    pip install boto3
"""

from __future__ import annotations

import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("DDB_ACCOUNTS_TABLE_NAME", "AccountsTable")
ENDPOINT_URL = os.environ.get("DDB_ENDPOINT_URL", "http://localhost:8000")


def get_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=ENDPOINT_URL,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


def create_accounts_table(ddb) -> None:
    ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "AccountId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "AccountId", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    ).wait_until_exists()


def transfer_funds(client, from_account: str, to_account: str, amount: Decimal) -> bool:
    """Atomically debit one account and credit another using TransactWriteItems.

    DynamoDB Transactions use a two-phase-commit-style protocol internally
    (Section 4.8): a prepare phase validates every ConditionExpression across
    all items (here, "balance >= amount" on the debit side) and acquires a
    transient per-item lock, then a commit phase applies all writes or none.
    A failed condition on ANY item aborts the entire transaction -- there is
    no partial transfer.
    """
    try:
        client.transact_write_items(
            TransactItems=[
                {
                    "Update": {
                        "TableName": TABLE_NAME,
                        "Key": {"AccountId": {"S": from_account}},
                        "UpdateExpression": "SET Balance = Balance - :amt",
                        "ConditionExpression": "Balance >= :amt",
                        "ExpressionAttributeValues": {":amt": {"N": str(amount)}},
                    }
                },
                {
                    "Update": {
                        "TableName": TABLE_NAME,
                        "Key": {"AccountId": {"S": to_account}},
                        "UpdateExpression": "SET Balance = Balance + :amt",
                        "ExpressionAttributeValues": {":amt": {"N": str(amount)}},
                    }
                },
            ]
        )
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "TransactionCanceledException":
            # At least one ConditionExpression failed (e.g. insufficient funds);
            # DynamoDB rolled back every item in the transaction -- no partial write.
            return False
        raise


def read_balance(table, account_id: str, strongly_consistent: bool) -> Decimal:
    """Contrast eventual (default) vs. strongly consistent reads (Section 4.6).

    Strongly consistent reads always route to the partition's current leader
    replica and cost double the RCU of an eventually consistent read of the
    same item -- never available against a Global Secondary Index, only the
    base table or a Local Secondary Index.
    """
    response = table.get_item(
        Key={"AccountId": account_id}, ConsistentRead=strongly_consistent
    )
    return response["Item"]["Balance"]


def main() -> None:
    ddb = get_resource()
    client = ddb.meta.client
    try:
        create_accounts_table(ddb)
    except ddb.meta.client.exceptions.ResourceInUseException:
        pass

    table = ddb.Table(TABLE_NAME)
    table.put_item(Item={"AccountId": "ACC-1", "Balance": Decimal("100.00")})
    table.put_item(Item={"AccountId": "ACC-2", "Balance": Decimal("0.00")})

    ok = transfer_funds(client, "ACC-1", "ACC-2", Decimal("40.00"))
    print(f"Transfer of 40.00 ACC-1 -> ACC-2 succeeded: {ok}")

    overdraft_attempt = transfer_funds(client, "ACC-1", "ACC-2", Decimal("1000.00"))
    print(f"Transfer of 1000.00 (overdraft) succeeded: {overdraft_attempt} "
          f"(expected False -- ConditionExpression rejected it atomically)")

    eventual = read_balance(table, "ACC-1", strongly_consistent=False)
    strong = read_balance(table, "ACC-1", strongly_consistent=True)
    print(f"ACC-1 balance (eventually consistent read): {eventual}")
    print(f"ACC-1 balance (strongly consistent read):    {strong}")


if __name__ == "__main__":
    main()
