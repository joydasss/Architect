// CH15_MongoDB.md Section 10.4 - multi-document ACID transaction
// (Section 4.7's readConcern:"snapshot") modeling a funds transfer across
// two account documents, with retry-on-transient-error logic. Requires a
// replica set or sharded cluster - standalone mongod does not support
// transactions at all (Section 16's testing note).
"use strict";

const { MongoClient } = require("mongodb");

const uri = process.env.MONGODB_URI || "mongodb://localhost:27017/?replicaSet=rs0";

async function transferFunds(client, fromAccountId, toAccountId, amount) {
  const session = client.startSession();

  try {
    // withTransaction retries the whole callback on MongoDB's
    // TransientTransactionError/UnknownTransactionCommitResult labels,
    // the standard pattern for surviving a mid-transaction election
    // (Section 4.3) without hand-rolled retry logic.
    await session.withTransaction(
      async () => {
        const db = client.db("architect_handbook_demo");
        const accounts = db.collection("accounts");

        const from = await accounts.findOne(
          { _id: fromAccountId },
          { session }
        );
        if (!from || from.balance < amount) {
          throw new Error("Insufficient funds - aborting transaction");
        }

        await accounts.updateOne(
          { _id: fromAccountId },
          { $inc: { balance: -amount } },
          { session }
        );
        await accounts.updateOne(
          { _id: toAccountId },
          { $inc: { balance: amount } },
          { session }
        );
      },
      {
        readConcern: { level: "snapshot" },
        writeConcern: { w: "majority" },
        readPreference: "primary",
      }
    );

    console.log(`Transferred ${amount} from ${fromAccountId} to ${toAccountId}`);
  } finally {
    await session.endSession();
  }
}

async function main() {
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db("architect_handbook_demo");
    const accounts = db.collection("accounts");

    await accounts.drop().catch(() => {});
    await accounts.insertMany([
      { _id: "acct-1", balance: 500 },
      { _id: "acct-2", balance: 100 },
    ]);

    await transferFunds(client, "acct-1", "acct-2", 150);

    const updated = await accounts.find({}).toArray();
    console.log(JSON.stringify(updated, null, 2));
  } finally {
    await client.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
