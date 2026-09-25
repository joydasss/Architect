"""01_single_table_design.py

Demonstrates single-table design (CH17_DynamoDB.md Section 4.1): a single
DynamoDB table holding multiple entity types (Order, Customer, OrderItem)
distinguished by overloaded partition-key/sort-key prefixes, plus a Global
Secondary Index (GSI) enabling a second access pattern (all orders for a
given status) without a second table or a full table scan.

Requires: boto3, and either a reachable DynamoDB endpoint (local via
`docker run -p 8000:8000 amazon/dynamodb-local`) or real AWS credentials.

    pip install boto3
"""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

import boto3

TABLE_NAME = os.environ.get("DDB_TABLE_NAME", "OrdersSingleTable")
ENDPOINT_URL = os.environ.get("DDB_ENDPOINT_URL", "http://localhost:8000")


def get_resource():
    """Return a boto3 DynamoDB resource, pointed at local or real AWS."""
    return boto3.resource(
        "dynamodb",
        endpoint_url=ENDPOINT_URL,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


def create_table(ddb) -> None:
    """Create the single table with a GSI for the 'orders by status' access pattern.

    PK/SK overload multiple entity types in one table (Section 4.1):
      Customer item:   PK=CUSTOMER#<id>          SK=METADATA
      Order item:      PK=CUSTOMER#<id>          SK=ORDER#<orderId>
      Order-item item: PK=ORDER#<orderId>         SK=ITEM#<sku>
    GSI1 inverts the key: GSI1PK=STATUS#<status>, GSI1SK=ORDER#<orderId>,
    so "all PENDING orders" is a single Query against the GSI instead of a
    table Scan filtering every item in the table.
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
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1-StatusIndex",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",  # on-demand capacity (Section 4.3)
    ).wait_until_exists()


def put_customer(table, customer_id: str, name: str, email: str) -> None:
    table.put_item(
        Item={
            "PK": f"CUSTOMER#{customer_id}",
            "SK": "METADATA",
            "entityType": "Customer",
            "name": name,
            "email": email,
        }
    )


def put_order(
    table,
    customer_id: str,
    order_id: str,
    status: str,
    total: Decimal,
) -> None:
    """Write the order under the customer's partition AND project it into GSI1.

    A single item carries both the base table's PK/SK and the GSI1PK/GSI1SK
    attributes; DynamoDB automatically maintains the GSI's own copy of the
    item whenever the base item changes (Section 4.4's async-propagation
    mechanism), so writers never issue a second write.
    """
    table.put_item(
        Item={
            "PK": f"CUSTOMER#{customer_id}",
            "SK": f"ORDER#{order_id}",
            "entityType": "Order",
            "status": status,
            "total": total,
            "GSI1PK": f"STATUS#{status}",
            "GSI1SK": f"ORDER#{order_id}",
        }
    )


def get_customer_with_orders(table, customer_id: str) -> list[dict[str, Any]]:
    """One Query satisfies 'customer + all their orders' (Section 4.1's payoff):
    a single partition-key Query retrieves the customer's METADATA item and
    every ORDER# item in one round trip, sorted by SK -- no join required.
    """
    response = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": f"CUSTOMER#{customer_id}"},
    )
    return response["Items"]


def get_orders_by_status(table, status: str) -> list[dict[str, Any]]:
    """Second access pattern via GSI1: all orders in a given status, across
    every customer, without scanning the base table (Section 4.4).
    """
    response = table.query(
        IndexName="GSI1-StatusIndex",
        KeyConditionExpression="GSI1PK = :gsi1pk",
        ExpressionAttributeValues={":gsi1pk": f"STATUS#{status}"},
    )
    return response["Items"]


def main() -> None:
    ddb = get_resource()
    try:
        create_table(ddb)
    except ddb.meta.client.exceptions.ResourceInUseException:
        pass  # table already exists (re-running the demo)

    table = ddb.Table(TABLE_NAME)
    put_customer(table, "C1", "Ada Lovelace", "ada@example.com")
    put_order(table, "C1", "O1001", "PENDING", Decimal("129.99"))
    put_order(table, "C1", "O1002", "SHIPPED", Decimal("54.50"))

    print("Customer + orders (single Query, one partition):")
    for item in get_customer_with_orders(table, "C1"):
        print(" ", item)

    print("\nAll PENDING orders (GSI1 Query, cross-customer):")
    for item in get_orders_by_status(table, "PENDING"):
        print(" ", item)


if __name__ == "__main__":
    main()
