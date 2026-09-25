/**
 * 03_saga_orchestrator.js
 *
 * A minimal orchestration-style Saga for an "place order" workflow spanning
 * three independently-owned services (Inventory, Payment, Shipping), each of
 * which only supports local ACID transactions within its own database. The
 * orchestrator drives the forward steps in order and, on any failure, runs
 * compensating actions for every step that already succeeded, in reverse
 * order — implementing the chapter's Section 4.14 Saga pattern.
 *
 * Run: node 03_saga_orchestrator.js
 * (Everything below is simulated in-process; swap the step functions for
 * real HTTP/gRPC/message-queue calls to reproduce this against real services.)
 */

'use strict';

class SagaStepError extends Error {
  constructor(step, cause) {
    super(`Saga step "${step}" failed: ${cause.message}`);
    this.step = step;
    this.cause = cause;
  }
}

/**
 * Each step declares a forward action and a compensating action. The
 * compensating action must be idempotent and must succeed even if the
 * forward action only partially completed (e.g. network timeout after the
 * remote side actually committed) — this is what makes Sagas eventually
 * consistent rather than atomic.
 */
function buildOrderSaga({ inventoryService, paymentService, shippingService }) {
  return [
    {
      name: 'reserveInventory',
      action: (ctx) => inventoryService.reserve(ctx.orderId, ctx.items),
      compensate: (ctx) => inventoryService.release(ctx.orderId, ctx.items),
    },
    {
      name: 'chargePayment',
      action: (ctx) => paymentService.charge(ctx.orderId, ctx.totalCents),
      compensate: (ctx) => paymentService.refund(ctx.orderId, ctx.totalCents),
    },
    {
      name: 'scheduleShipment',
      action: (ctx) => shippingService.schedule(ctx.orderId, ctx.address),
      compensate: (ctx) => shippingService.cancel(ctx.orderId),
    },
  ];
}

async function runSaga(steps, context, log) {
  const completed = [];
  try {
    for (const step of steps) {
      log(`-> executing "${step.name}"`);
      try {
        await step.action(context);
      } catch (cause) {
        throw new SagaStepError(step.name, cause);
      }
      completed.push(step);
      log(`   "${step.name}" committed locally`);
    }
    log('Saga completed successfully: all steps committed.');
    return { status: 'COMPLETED' };
  } catch (err) {
    log(`!! ${err.message} — beginning compensation in reverse order`);
    // Compensate every step that already succeeded, LIFO (last-in-first-out),
    // so a later step's compensation (e.g. "release the reservation") never
    // runs before an earlier step it might logically depend on unwinding.
    for (const step of completed.reverse()) {
      try {
        log(`<- compensating "${step.name}"`);
        await step.compensate(context);
        log(`   "${step.name}" compensated`);
      } catch (compErr) {
        // A failed compensation is a serious operational event: the saga is
        // now stuck in a partially-compensated state and needs a dead-letter
        // queue / manual-intervention alert (Section 15 of the chapter) —
        // it must NOT be silently swallowed.
        log(`   !! COMPENSATION FAILED for "${step.name}": ${compErr.message} `
          + '(requires manual intervention / dead-letter queue)');
      }
    }
    return { status: 'COMPENSATED', failedStep: err.step };
  }
}

// --- Simulated downstream services -----------------------------------------

function makeInventoryService(failOnReserve = false) {
  const reserved = new Set();
  return {
    async reserve(orderId, items) {
      await delay(20);
      if (failOnReserve) throw new Error('SKU-4471 out of stock');
      reserved.add(orderId);
    },
    async release(orderId, items) {
      await delay(15);
      reserved.delete(orderId);
    },
  };
}

function makePaymentService(failOnCharge = false) {
  const charged = new Set();
  return {
    async charge(orderId, totalCents) {
      await delay(30);
      if (failOnCharge) throw new Error('card issuer declined transaction');
      charged.add(orderId);
    },
    async refund(orderId, totalCents) {
      await delay(25);
      charged.delete(orderId);
    },
  };
}

function makeShippingService() {
  const scheduled = new Set();
  return {
    async schedule(orderId, address) {
      await delay(15);
      scheduled.add(orderId);
    },
    async cancel(orderId) {
      await delay(10);
      scheduled.delete(orderId);
    },
  };
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// --- Demo: one happy path, one failure that triggers compensation ----------

async function main() {
  const log = (msg) => console.log(msg);

  log('=== Scenario 1: happy path (all three services succeed) ===');
  const happySteps = buildOrderSaga({
    inventoryService: makeInventoryService(false),
    paymentService: makePaymentService(false),
    shippingService: makeShippingService(),
  });
  const happyResult = await runSaga(
    happySteps,
    { orderId: 'ORD-1001', items: ['SKU-4471'], totalCents: 4999, address: '221B Baker St' },
    log,
  );
  log(`Result: ${JSON.stringify(happyResult)}\n`);

  log('=== Scenario 2: payment fails after inventory is already reserved ===');
  const failingSteps = buildOrderSaga({
    inventoryService: makeInventoryService(false),
    paymentService: makePaymentService(true), // simulate a declined charge
    shippingService: makeShippingService(),
  });
  const failResult = await runSaga(
    failingSteps,
    { orderId: 'ORD-1002', items: ['SKU-4471'], totalCents: 4999, address: '221B Baker St' },
    log,
  );
  log(`Result: ${JSON.stringify(failResult)}`);
}

main();
