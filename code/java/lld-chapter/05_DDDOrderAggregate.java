import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Implements CH04_Low_Level_Design.md Sections 4.13-4.16 (DDD tactical
 * patterns) and Section 10 example 5: an Order aggregate enforcing its own
 * invariants, built from a Value Object (Money), an Entity (OrderLine) held
 * inside the aggregate boundary, a Repository interface, and a Domain Event
 * raised when the aggregate transitions state.
 *
 * Run:
 *   javac 05_DDDOrderAggregate.java -d out
 *   java -cp out DDDOrderAggregate
 */
public class DDDOrderAggregate {

    // ---------------------------------------------------------------
    // Value Object (Section 4.13): immutable, defined entirely by its
    // attributes (no identity), equality is structural.
    // ---------------------------------------------------------------
    static final class Money {
        private final BigDecimal amount;
        private final String currency;

        Money(BigDecimal amount, String currency) {
            if (amount.signum() < 0) {
                throw new IllegalArgumentException("Money cannot be negative");
            }
            this.amount = amount;
            this.currency = currency;
        }

        Money add(Money other) {
            requireSameCurrency(other);
            return new Money(this.amount.add(other.amount), currency);
        }

        Money multiply(int quantity) {
            return new Money(this.amount.multiply(BigDecimal.valueOf(quantity)), currency);
        }

        private void requireSameCurrency(Money other) {
            if (!this.currency.equals(other.currency)) {
                throw new IllegalStateException("Currency mismatch: " + currency + " vs " + other.currency);
            }
        }

        @Override
        public boolean equals(Object o) {
            if (!(o instanceof Money)) return false;
            Money other = (Money) o;
            return amount.compareTo(other.amount) == 0 && currency.equals(other.currency);
        }

        @Override
        public int hashCode() { return Objects.hash(amount.stripTrailingZeros(), currency); }

        @Override
        public String toString() { return amount + " " + currency; }
    }

    // ---------------------------------------------------------------
    // Domain Event (Section 4.16): an immutable fact, named in the past
    // tense, raised by the aggregate when something domain-significant
    // happened -- consumed by handlers outside the aggregate's boundary.
    // ---------------------------------------------------------------
    interface DomainEvent { }

    static final class OrderPlaced implements DomainEvent {
        final UUID orderId;
        final Money total;
        OrderPlaced(UUID orderId, Money total) {
            this.orderId = orderId;
            this.total = total;
        }
        @Override
        public String toString() { return "OrderPlaced{orderId=" + orderId + ", total=" + total + "}"; }
    }

    static final class OrderCancelled implements DomainEvent {
        final UUID orderId;
        OrderCancelled(UUID orderId) { this.orderId = orderId; }
        @Override
        public String toString() { return "OrderCancelled{orderId=" + orderId + "}"; }
    }

    // ---------------------------------------------------------------
    // Entity nested inside the aggregate (Section 4.14): has identity
    // (sku) but is not independently reachable from outside the Order
    // aggregate root -- callers never hold a bare OrderLine reference.
    // ---------------------------------------------------------------
    static final class OrderLine {
        private final String sku;
        private final int quantity;
        private final Money unitPrice;

        OrderLine(String sku, int quantity, Money unitPrice) {
            if (quantity <= 0) {
                throw new IllegalArgumentException("Quantity must be positive");
            }
            this.sku = sku;
            this.quantity = quantity;
            this.unitPrice = unitPrice;
        }

        Money lineTotal() { return unitPrice.multiply(quantity); }
        String sku() { return sku; }
    }

    enum OrderState { DRAFT, PLACED, CANCELLED }

    // ---------------------------------------------------------------
    // Aggregate Root (Section 4.14): the only entry point external code is
    // allowed to reference; every mutation goes through a root method that
    // enforces the aggregate's invariants atomically.
    // ---------------------------------------------------------------
    static final class Order {
        private final UUID id;
        private final List<OrderLine> lines = new ArrayList<>();
        private OrderState state = OrderState.DRAFT;
        private final List<DomainEvent> pendingEvents = new ArrayList<>();
        private static final int MAX_LINES_PER_ORDER = 100; // invariant

        Order(UUID id) { this.id = id; }

        UUID id() { return id; }
        OrderState state() { return state; }

        // Invariant enforced here, not by the caller: an order cannot be
        // edited once placed, and cannot exceed MAX_LINES_PER_ORDER.
        void addLine(String sku, int quantity, Money unitPrice) {
            if (state != OrderState.DRAFT) {
                throw new IllegalStateException("Cannot add lines to a non-draft order");
            }
            if (lines.size() >= MAX_LINES_PER_ORDER) {
                throw new IllegalStateException("Order exceeds max line count");
            }
            lines.add(new OrderLine(sku, quantity, unitPrice));
        }

        Money total() {
            Money currentTotal = new Money(BigDecimal.ZERO, "USD");
            for (OrderLine line : lines) {
                currentTotal = currentTotal.add(line.lineTotal());
            }
            return currentTotal;
        }

        // Invariant: an order with zero lines can never be placed.
        void place() {
            if (lines.isEmpty()) {
                throw new IllegalStateException("Cannot place an order with no lines");
            }
            if (state != OrderState.DRAFT) {
                throw new IllegalStateException("Order already placed or cancelled");
            }
            state = OrderState.PLACED;
            pendingEvents.add(new OrderPlaced(id, total()));
        }

        void cancel() {
            if (state != OrderState.PLACED) {
                throw new IllegalStateException("Only a placed order can be cancelled");
            }
            state = OrderState.CANCELLED;
            pendingEvents.add(new OrderCancelled(id));
        }

        // The aggregate accumulates events internally; the application
        // layer drains and publishes them after a successful transaction.
        List<DomainEvent> drainEvents() {
            List<DomainEvent> events = new ArrayList<>(pendingEvents);
            pendingEvents.clear();
            return events;
        }
    }

    // ---------------------------------------------------------------
    // Repository (Section 4.15): collection-like interface for retrieving
    // and persisting whole aggregates -- never exposes OrderLine directly.
    // ---------------------------------------------------------------
    interface OrderRepository {
        void save(Order order);
        Optional<Order> findById(UUID id);
    }

    static final class InMemoryOrderRepository implements OrderRepository {
        private final java.util.Map<UUID, Order> store = new java.util.HashMap<>();
        public void save(Order order) { store.put(order.id(), order); }
        public Optional<Order> findById(UUID id) { return Optional.ofNullable(store.get(id)); }
    }

    public static void main(String[] args) {
        OrderRepository repository = new InMemoryOrderRepository();

        Order order = new Order(UUID.randomUUID());
        order.addLine("SKU-1", 2, new Money(new BigDecimal("9.99"), "USD"));
        order.addLine("SKU-2", 1, new Money(new BigDecimal("24.50"), "USD"));
        System.out.println("Draft total: " + order.total());

        order.place();
        repository.save(order);
        for (DomainEvent event : order.drainEvents()) {
            System.out.println("Publishing event: " + event);
        }

        try {
            order.addLine("SKU-3", 1, new Money(new BigDecimal("5.00"), "USD"));
        } catch (IllegalStateException e) {
            System.out.println("Invariant enforced: " + e.getMessage());
        }

        Order reloaded = repository.findById(order.id()).orElseThrow();
        reloaded.cancel();
        for (DomainEvent event : reloaded.drainEvents()) {
            System.out.println("Publishing event: " + event);
        }
    }
}
