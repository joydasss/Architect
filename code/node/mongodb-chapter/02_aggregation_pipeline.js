// CH15_MongoDB.md Section 10.2 - aggregation pipeline (Section 4.6):
// $match (index-eligible, placed first) -> $group -> $lookup -> $facet
"use strict";

const { MongoClient, ObjectId } = require("mongodb");

const uri = process.env.MONGODB_URI || "mongodb://localhost:27017";

async function main() {
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db("architect_handbook_demo");

    await db.collection("orders").drop().catch(() => {});
    await db.collection("customers").drop().catch(() => {});

    const customers = db.collection("customers");
    const orders = db.collection("orders");

    const alice = new ObjectId();
    const bob = new ObjectId();

    await customers.insertMany([
      { _id: alice, name: "Alice", tier: "gold" },
      { _id: bob, name: "Bob", tier: "silver" },
    ]);

    const now = new Date();
    await orders.insertMany([
      { customerId: alice, orderDate: now, total: 120.5, status: "paid" },
      { customerId: alice, orderDate: now, total: 45.0, status: "paid" },
      { customerId: bob, orderDate: now, total: 300.0, status: "paid" },
      { customerId: bob, orderDate: now, total: 10.0, status: "cancelled" },
    ]);

    await orders.createIndex({ orderDate: 1, status: 1 });

    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

    const pipeline = [
      // Stage 1: $match placed first so it can use the orderDate/status
      // index (Section 4.6's "place $match early" performance rule).
      { $match: { orderDate: { $gte: startOfMonth }, status: "paid" } },

      // Stage 2: aggregate per customer BEFORE joining, so $lookup below
      // runs once per distinct customer rather than once per raw order -
      // the join-explosion mitigation Section 4.6 teaches.
      {
        $group: {
          _id: "$customerId",
          orderCount: { $sum: 1 },
          totalSpend: { $sum: "$total" },
        },
      },

      // Stage 3: $lookup - relational-style join against the referenced
      // customers collection (Section 4.1's reference-vs-embed choice).
      {
        $lookup: {
          from: "customers",
          localField: "_id",
          foreignField: "_id",
          as: "customer",
        },
      },
      { $unwind: "$customer" },

      // Stage 4: $facet - two independent sub-pipelines over the same
      // grouped input in a single round trip (Section 4.6).
      {
        $facet: {
          byCustomer: [
            {
              $project: {
                _id: 0,
                customerName: "$customer.name",
                tier: "$customer.tier",
                orderCount: 1,
                totalSpend: 1,
              },
            },
            { $sort: { totalSpend: -1 } },
          ],
          summary: [
            {
              $group: {
                _id: null,
                totalCustomers: { $sum: 1 },
                grandTotalSpend: { $sum: "$totalSpend" },
              },
            },
          ],
        },
      },
    ];

    const result = await orders.aggregate(pipeline).toArray();
    console.log(JSON.stringify(result, null, 2));
  } finally {
    await client.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
