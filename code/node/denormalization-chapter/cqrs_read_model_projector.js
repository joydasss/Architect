/**
 * CQRS-style read-model projector: consumes write-side domain events and
 * maintains a denormalized, query-optimized read model.
 *
 * Referenced from 06_Databases_and_Storage/CH02_Denormalization.md (Section 10).
 *
 * The write model (not shown) is normalized and emits one event per state
 * transition. This projector subscribes to that event stream and maintains a
 * duplicated, denormalized `customerOrderView` keyed for the exact read the
 * UI needs (one document per customer, embedding their recent orders) —
 * trading write-amplification (every order event now fans out to a second
 * write here) for a read path that needs no joins at all.
 */
'use strict';

class InMemoryReadModelStore {
  constructor() {
    this.byCustomerId = new Map();
  }

  upsertCustomer(customerId, name) {
    if (!this.byCustomerId.has(customerId)) {
      this.byCustomerId.set(customerId, { customerId, name, orders: [], lifetimeTotalCents: 0 });
    }
  }

  getView(customerId) {
    return this.byCustomerId.get(customerId) ?? null;
  }
}

class CustomerOrderProjector {
  /**
   * @param {InMemoryReadModelStore} store
   */
  constructor(store) {
    this.store = store;
    // Tracks the last applied event sequence number per customer so a
    // redelivered (at-least-once) event is a safe no-op instead of double-counting.
    this.appliedSequence = new Map();
  }

  /** Apply one event from the write-side event stream, idempotently. */
  apply(event) {
    const lastApplied = this.appliedSequence.get(event.customerId) ?? -1;
    if (event.sequence <= lastApplied) {
      return; // Already-applied event replayed by an at-least-once broker — ignore.
    }

    switch (event.type) {
      case 'CustomerRegistered':
        this.store.upsertCustomer(event.customerId, event.name);
        break;

      case 'OrderPlaced': {
        this.store.upsertCustomer(event.customerId, event.customerName);
        const view = this.store.getView(event.customerId);
        view.orders.push({
          orderId: event.orderId,
          status: 'PLACED',
          totalCents: event.totalCents,
          placedAt: event.occurredAt,
        });
        view.lifetimeTotalCents += event.totalCents;
        break;
      }

      case 'OrderCancelled': {
        const view = this.store.getView(event.customerId);
        if (!view) break; // Projector started after this customer's history — see Section 15.
        const order = view.orders.find((o) => o.orderId === event.orderId);
        if (order && order.status !== 'CANCELLED') {
          order.status = 'CANCELLED';
          view.lifetimeTotalCents -= order.totalCents;
        }
        break;
      }

      default:
        // Forward-compatible: unknown event types are ignored, not fatal,
        // so the write side can add new event types without breaking this projector.
        return;
    }

    this.appliedSequence.set(event.customerId, event.sequence);
  }
}

function demo() {
  const store = new InMemoryReadModelStore();
  const projector = new CustomerOrderProjector(store);

  const events = [
    { type: 'CustomerRegistered', customerId: 'c1', name: 'Priya N.', sequence: 0 },
    {
      type: 'OrderPlaced',
      customerId: 'c1',
      customerName: 'Priya N.',
      orderId: 'o1',
      totalCents: 4599,
      occurredAt: '2026-02-01T10:00:00Z',
      sequence: 1,
    },
    {
      type: 'OrderPlaced',
      customerId: 'c1',
      customerName: 'Priya N.',
      orderId: 'o2',
      totalCents: 1200,
      occurredAt: '2026-02-02T09:30:00Z',
      sequence: 2,
    },
    { type: 'OrderCancelled', customerId: 'c1', orderId: 'o2', sequence: 3 },
    // Redelivered duplicate of the first OrderPlaced event — must be a no-op.
    {
      type: 'OrderPlaced',
      customerId: 'c1',
      customerName: 'Priya N.',
      orderId: 'o1',
      totalCents: 4599,
      occurredAt: '2026-02-01T10:00:00Z',
      sequence: 1,
    },
  ];

  for (const event of events) projector.apply(event);

  console.log(JSON.stringify(store.getView('c1'), null, 2));
  // lifetimeTotalCents should be 4599 (o1 only; o2 cancelled; duplicate ignored).
}

if (require.main === module) demo();

module.exports = { InMemoryReadModelStore, CustomerOrderProjector };
