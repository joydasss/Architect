"""02_capacity_and_throttling_demo.py

Demonstrates Read Capacity Unit (RCU) / Write Capacity Unit (WCU) accounting
and hot-partition throttling under provisioned capacity (CH17_DynamoDB.md
Section 4.3). Writes a burst of items skewed onto one partition key,
provisions deliberately low throughput, and shows the resulting
ProvisionedThroughputExceededException -- the direct, observable evidence of
per-partition (not per-table) capacity limits.

Requires: boto3, and a reachable DynamoDB endpoint (local or real AWS).

    pip install boto3
"""

from __future__ import annotations

import os
import time

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("DDB_HOT_TABLE_NAME", "HotPartitionDemo")
ENDPOINT_URL = os.environ.get("DDB_ENDPOINT_URL", "http://localhost:8000")


def get_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=ENDPOINT_URL,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


def create_low_capacity_table(ddb) -> None:
    """Provisioned mode with deliberately tiny WCU (Section 4.3): each
    partition can sustain roughly 1,000 WCU/s of its own regardless of the
    table-level total, but here the table-level ceiling itself is set low
    enough to reproduce throttling quickly for demonstration purposes.
    """
    ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    ).wait_until_exists()


def hammer_single_partition_key(table, hot_key: str, item_count: int) -> dict[str, int]:
    """Write item_count items, all sharing one partition key.

    A skewed key distribution concentrates every write onto one physical
    partition's capacity share (Section 4.2/4.3's hot-partition mechanism)
    even though the table's aggregate provisioned WCU may look sufficient
    on paper -- this is the gap between table-level and per-partition
    capacity that adaptive capacity (Section 4.3) exists to narrow.
    """
    successes = 0
    throttles = 0
    for i in range(item_count):
        try:
            table.put_item(
                Item={"PK": hot_key, "SK": f"ITEM#{i:05d}", "payload": "x" * 200}
            )
            successes += 1
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ProvisionedThroughputExceededException":
                throttles += 1
            else:
                raise
    return {"successes": successes, "throttles": throttles}


def main() -> None:
    ddb = get_resource()
    try:
        create_low_capacity_table(ddb)
    except ddb.meta.client.exceptions.ResourceInUseException:
        pass

    table = ddb.Table(TABLE_NAME)

    print("Writing 500 items to a single hot partition key with 5 WCU provisioned...")
    start = time.monotonic()
    result = hammer_single_partition_key(table, hot_key="TENANT#viral-customer", item_count=500)
    elapsed = time.monotonic() - start

    print(f"Completed in {elapsed:.2f}s: {result['successes']} succeeded, "
          f"{result['throttles']} throttled (ProvisionedThroughputExceededException).")
    print("Fix per Section 4.3: shard the hot key (e.g. TENANT#id#<0-9>) so writes "
          "spread across multiple physical partitions, or switch to on-demand capacity.")


if __name__ == "__main__":
    main()
