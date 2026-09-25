import java.util.ArrayList;
import java.util.List;

/**
 * Implements CH04_Low_Level_Design.md Section 4.10 (Observer pattern) and
 * Section 10 example 3: an order publishes state-change events to an
 * arbitrary number of independently-added subscribers, none of which the
 * order (the subject) has any compile-time knowledge of.
 *
 * Run:
 *   javac 03_ObserverPatternOrderNotifications.java -d out
 *   java -cp out ObserverPatternOrderNotifications
 */
public class ObserverPatternOrderNotifications {

    enum OrderStatus { PLACED, PAID, SHIPPED, DELIVERED }

    // The Observer interface: anything that wants to react to order events.
    interface OrderStatusObserver {
        void onStatusChanged(String orderId, OrderStatus oldStatus, OrderStatus newStatus);
    }

    // The Subject: owns the list of observers and the notification mechanism.
    // It has zero knowledge of what a CustomerSmsNotifier or WarehouseFeed
    // actually does -- that is what decouples publisher from subscriber.
    static class Order {
        private final String orderId;
        private OrderStatus status = OrderStatus.PLACED;
        private final List<OrderStatusObserver> observers = new ArrayList<>();

        Order(String orderId) {
            this.orderId = orderId;
        }

        void subscribe(OrderStatusObserver observer) {
            observers.add(observer);
        }

        void unsubscribe(OrderStatusObserver observer) {
            observers.remove(observer);
        }

        void advanceTo(OrderStatus newStatus) {
            OrderStatus old = this.status;
            this.status = newStatus;
            for (OrderStatusObserver observer : observers) {
                observer.onStatusChanged(orderId, old, newStatus);
            }
        }
    }

    static class CustomerSmsNotifier implements OrderStatusObserver {
        public void onStatusChanged(String orderId, OrderStatus oldStatus, OrderStatus newStatus) {
            System.out.println("[SMS] Order " + orderId + " is now " + newStatus);
        }
    }

    static class WarehousePickFeed implements OrderStatusObserver {
        public void onStatusChanged(String orderId, OrderStatus oldStatus, OrderStatus newStatus) {
            if (newStatus == OrderStatus.PAID) {
                System.out.println("[WAREHOUSE] Queue pick list for order " + orderId);
            }
        }
    }

    static class AnalyticsSink implements OrderStatusObserver {
        public void onStatusChanged(String orderId, OrderStatus oldStatus, OrderStatus newStatus) {
            System.out.println("[ANALYTICS] " + orderId + ": " + oldStatus + " -> " + newStatus);
        }
    }

    public static void main(String[] args) {
        Order order = new Order("ORD-42");
        order.subscribe(new CustomerSmsNotifier());
        order.subscribe(new WarehousePickFeed());
        AnalyticsSink analytics = new AnalyticsSink();
        order.subscribe(analytics);

        order.advanceTo(OrderStatus.PAID);
        order.advanceTo(OrderStatus.SHIPPED);

        order.unsubscribe(analytics); // subscribers can detach independently
        order.advanceTo(OrderStatus.DELIVERED);
    }
}
