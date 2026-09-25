"""04_streams_and_global_tables.py

Demonstrates DynamoDB Streams change-data-capture (CH17_DynamoDB.md Section
4.5) with a polling consumer that mirrors what a Lambda trigger does
internally, plus a conceptual client-side helper illustrating how Global
Tables (Section 4.7) route writes to the nearest regional replica while a
"last writer wins" resolver reconciles concurrent cross-region updates.

Requires: boto3, and a reachable DynamoDB Streams-enabled endpoint (local
DynamoDB Local's Streams support is limited; this is best run against a
real AWS table with StreamViewType=NEW_AND_OLD_IMAGES enabled).

    pip install boto3
"""

from __future__ import annotations

import os
import time
from typing import Any

import boto3

TABLE_NAME = os.environ.get("DDB_STREAM_TABLE_NAME", "InventoryTable")
REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_clients():
    ddb = boto3.resource("dynamodb", region_name=REGION)
    streams_client = boto3.client("dynamodbstreams", region_name=REGION)
    return ddb, streams_client


def create_table_with_stream(ddb) -> str:
    """Enable a stream capturing both old and new item images on every write.

    NEW_AND_OLD_IMAGES (Section 4.5) lets a consumer compute a delta (e.g.
    "quantity dropped from 12 to 9") without a separate read -- the stream
    record itself carries both versions of the item.
    """
    table = ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "Sku", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "Sku", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
        StreamSpecification={
            "StreamEnabled": True,
            "StreamViewType": "NEW_AND_OLD_IMAGES",
        },
    )
    table.wait_until_exists()
    description = ddb.meta.client.describe_table(TableName=TABLE_NAME)
    return description["Table"]["LatestStreamArn"]


def poll_stream_once(streams_client, stream_arn: str) -> list[dict[str, Any]]:
    """Read one batch of stream records, mirroring the shard-iterator model
    a Lambda event-source mapping manages automatically (Section 4.5): each
    stream has one or more shards, each shard needs its own iterator, and
    records must be read in order per shard (DynamoDB Streams guarantees
    per-item ordering, not global ordering across a whole partition-less
    stream).
    """
    stream_description = streams_client.describe_stream(StreamArn=stream_arn)
    shard_id = stream_description["StreamDescription"]["Shards"][0]["ShardId"]

    iterator_response = streams_client.get_shard_iterator(
        StreamArn=stream_arn,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON",
    )
    shard_iterator = iterator_response["ShardIterator"]

    records_response = streams_client.get_records(ShardIterator=shard_iterator)
    return records_response["Records"]


def apply_last_writer_wins(local_item: dict[str, Any], incoming_item: dict[str, Any]) -> dict[str, Any]:
    """Simplified Global Tables conflict resolver (Section 4.7).

    Real Global Tables resolve concurrent cross-region writes using each
    item's internal last-write-timestamp metadata automatically -- this
    function only illustrates the *policy* (last writer wins by timestamp),
    not DynamoDB's actual internal resolution wire protocol.
    """
    if incoming_item["_updatedAtEpoch"] >= local_item["_updatedAtEpoch"]:
        return incoming_item
    return local_item


def main() -> None:
    ddb, streams_client = get_clients()
    try:
        stream_arn = create_table_with_stream(ddb)
    except ddb.meta.client.exceptions.ResourceInUseException:
        description = ddb.meta.client.describe_table(TableName=TABLE_NAME)
        stream_arn = description["Table"]["LatestStreamArn"]

    table = ddb.Table(TABLE_NAME)
    table.put_item(Item={"Sku": "SKU-100", "Quantity": 12})
    time.sleep(1)  # let the stream record propagate before polling
    table.update_item(
        Key={"Sku": "SKU-100"},
        UpdateExpression="SET Quantity = :q",
        ExpressionAttributeValues={":q": 9},
    )
    time.sleep(1)

    records = poll_stream_once(streams_client, stream_arn)
    print(f"Read {len(records)} stream record(s) from shard 0:")
    for record in records:
        event_name = record["eventName"]
        new_image = record.get("dynamodb", {}).get("NewImage", {})
        old_image = record.get("dynamodb", {}).get("OldImage", {})
        print(f"  {event_name}: old={old_image} new={new_image}")

    print("\nGlobal Tables conflict-resolution policy demo (last writer wins):")
    us_east_version = {"Sku": "SKU-100", "Quantity": 9, "_updatedAtEpoch": 1000}
    eu_west_version = {"Sku": "SKU-100", "Quantity": 7, "_updatedAtEpoch": 1005}
    winner = apply_last_writer_wins(us_east_version, eu_west_version)
    print(f"  Resolved item after concurrent cross-region write: {winner}")


if __name__ == "__main__":
    main()
