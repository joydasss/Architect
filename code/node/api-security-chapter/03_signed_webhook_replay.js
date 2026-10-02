const assert = require("node:assert/strict");
const { createHmac, timingSafeEqual } = require("node:crypto");

function sign(timestamp, rawBody, secret) {
  return createHmac("sha256", secret)
    .update(`${timestamp}.`)
    .update(rawBody)
    .digest("hex");
}

function verifyWebhook({ rawBody, timestamp, signature, secret, nowSeconds, seen }) {
  const parsedTimestamp = Number(timestamp);
  if (!Number.isSafeInteger(parsedTimestamp) || Math.abs(nowSeconds - parsedTimestamp) > 300) {
    throw new Error("webhook timestamp outside accepted window");
  }

  const expected = Buffer.from(sign(parsedTimestamp, rawBody, secret), "hex");
  let supplied;
  try {
    supplied = Buffer.from(signature, "hex");
  } catch {
    throw new Error("invalid webhook signature");
  }
  if (supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) {
    throw new Error("invalid webhook signature");
  }

  const replayKey = `${parsedTimestamp}:${signature}`;
  if (seen.has(replayKey)) {
    throw new Error("webhook replay detected");
  }

  const event = JSON.parse(rawBody);
  seen.add(replayKey);
  return event;
}

const secret = "synthetic-test-secret";
const nowSeconds = 1_800_000_000;
const timestamp = String(nowSeconds);
const rawBody = '{"eventId":"evt-1","type":"invoice.paid"}';
const signature = sign(timestamp, rawBody, secret);
const seen = new Set();
const event = verifyWebhook({ rawBody, timestamp, signature, secret, nowSeconds, seen });
assert.equal(event.eventId, "evt-1");
assert.throws(
  () => verifyWebhook({ rawBody, timestamp, signature, secret, nowSeconds, seen }),
  /replay detected/,
);
assert.throws(
  () => verifyWebhook({ rawBody: `${rawBody} `, timestamp, signature, secret, nowSeconds, seen: new Set() }),
  /invalid webhook signature/,
);
assert.throws(
  () => verifyWebhook({ rawBody, timestamp: String(nowSeconds - 301), signature, secret, nowSeconds, seen: new Set() }),
  /outside accepted window/,
);
console.log("webhook signature and replay-window checks passed");
