// CH15_MongoDB.md Section 10.3 - per-operation write concern / read
// concern / read preference tuning (Section 4.7). Requires a replica set
// (e.g. a local single-node replica set is enough to exercise the API,
// though "majority" write concern needs a real multi-member set to prove
// its durability guarantee).
"use strict";

const { MongoClient, ObjectId } = require("mongodb");

const uri = process.env.MONGODB_URI || "mongodb://localhost:27017/?replicaSet=rs0";

async function main() {
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db("architect_handbook_demo");
    const orders = db.collection("orders");
    const telemetry = db.collection("last_viewed_products");

    const orderId = new ObjectId();

    // Durability-critical write: order creation. w:"majority" guarantees
    // this write can never be rolled back by a future election
    // (Section 4.3's rollback failure mode), at the cost of waiting for a
    // majority ack instead of just the primary.
    await orders.insertOne(
      {
        _id: orderId,
        customerId: new ObjectId(),
        status: "pending",
        total: 99.99,
        createdAt: new Date(),
      },
      { writeConcern: { w: "majority", j: true, wtimeout: 5000 } }
    );
    console.log("Order write acknowledged by majority:", orderId.toString());

    // Loss-tolerant write on the same request path: "last viewed" tracking.
    // w:1 accepts rollback risk in exchange for lower latency, because
    // losing this write has no customer-facing consequence (Section 4.7).
    await telemetry.updateOne(
      { customerId: orderId },
      { $set: { lastViewed: new Date() } },
      { upsert: true, writeConcern: { w: 1 } }
    );
    console.log("Telemetry write acknowledged by primary only (w:1)");

    // Analytics-style read: offload from the primary via read preference,
    // and pair it with readConcern "majority" so the (possibly stale) data
    // returned is at least guaranteed never to be rolled back.
    const recentPaidOrders = await orders
      .find(
        { status: "paid" },
        {
          readPreference: "secondaryPreferred",
          readConcern: { level: "majority" },
        }
      )
      .limit(10)
      .toArray();

    console.log(`Fetched ${recentPaidOrders.length} paid orders via secondaryPreferred`);
  } finally {
    await client.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
