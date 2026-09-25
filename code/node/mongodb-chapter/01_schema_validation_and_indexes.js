// CH15_MongoDB.md Section 10.1 - JSON Schema validation + compound/partial indexes
// Requires: npm install mongodb
"use strict";

const { MongoClient } = require("mongodb");

const uri = process.env.MONGODB_URI || "mongodb://localhost:27017";

async function main() {
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db("architect_handbook_demo");

    // Drop any prior run's collection so this script is idempotent.
    await db.collection("orders").drop().catch(() => {});

    // $jsonSchema validator: converts schema-on-read into an opt-in
    // schema-on-write guardrail (Section 4.2). validationAction "error"
    // rejects non-conforming writes instead of only warning.
    await db.createCollection("orders", {
      validator: {
        $jsonSchema: {
          bsonType: "object",
          required: ["customerId", "status", "total", "createdAt"],
          properties: {
            customerId: { bsonType: "objectId" },
            status: {
              bsonType: "string",
              enum: ["pending", "paid", "shipped", "cancelled"],
            },
            total: {
              bsonType: "decimal",
              description: "must be a Decimal128 monetary amount",
            },
            createdAt: { bsonType: "date" },
          },
        },
      },
      validationAction: "error",
      validationLevel: "strict",
    });

    const orders = db.collection("orders");

    // Compound index: leading equality field (customerId), trailing sort
    // field (createdAt) - matches the equality-then-sort discipline taught
    // in Section 11.
    await orders.createIndex(
      { customerId: 1, createdAt: -1 },
      { name: "customerId_createdAt" }
    );

    // Partial index: only index "pending" orders, since that is the only
    // status the operational dashboard queries against frequently - keeps
    // the index far smaller than a full index over every status.
    await orders.createIndex(
      { status: 1, createdAt: -1 },
      {
        name: "pending_orders_partial",
        partialFilterExpression: { status: "pending" },
      }
    );

    console.log("Collection 'orders' created with validator + indexes.");

    const indexes = await orders.indexes();
    console.log("Indexes:", JSON.stringify(indexes, null, 2));

    // Demonstrate the validator rejecting a non-conforming document.
    try {
      await orders.insertOne({
        customerId: "not-an-objectid", // wrong bsonType on purpose
        status: "pending",
        total: 42,
        createdAt: new Date(),
      });
    } catch (err) {
      console.log("Expected validation rejection:", err.code, err.codeName);
    }
  } finally {
    await client.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
