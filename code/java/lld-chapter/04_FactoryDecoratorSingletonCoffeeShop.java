/**
 * Implements CH04_Low_Level_Design.md Sections 4.8, 4.11, 4.12 (Factory
 * Method, Decorator, Singleton) and Section 10 example 4: a coffee-ordering
 * model where a Factory Method builds the base beverage, Decorators layer
 * add-ons without subclass explosion, and a Singleton models the shop's
 * single shared order counter/register.
 *
 * Run:
 *   javac 04_FactoryDecoratorSingletonCoffeeShop.java -d out
 *   java -cp out FactoryDecoratorSingletonCoffeeShop
 */
public class FactoryDecoratorSingletonCoffeeShop {

    // ---------------------------------------------------------------
    // Component + Decorator (Section 4.11): both concrete beverages and
    // add-on decorators implement the same interface, so decorators can
    // wrap either a base beverage or another decorator interchangeably.
    // ---------------------------------------------------------------
    interface Beverage {
        String description();
        double cost();
    }

    static class Espresso implements Beverage {
        public String description() { return "Espresso"; }
        public double cost() { return 2.50; }
    }

    static class FilterCoffee implements Beverage {
        public String description() { return "Filter Coffee"; }
        public double cost() { return 2.00; }
    }

    abstract static class BeverageDecorator implements Beverage {
        protected final Beverage wrapped;
        BeverageDecorator(Beverage wrapped) { this.wrapped = wrapped; }
    }

    static class MilkDecorator extends BeverageDecorator {
        MilkDecorator(Beverage wrapped) { super(wrapped); }
        public String description() { return wrapped.description() + " + Milk"; }
        public double cost() { return wrapped.cost() + 0.50; }
    }

    static class ExtraShotDecorator extends BeverageDecorator {
        ExtraShotDecorator(Beverage wrapped) { super(wrapped); }
        public String description() { return wrapped.description() + " + Extra Shot"; }
        public double cost() { return wrapped.cost() + 0.75; }
    }

    // ---------------------------------------------------------------
    // Factory Method (Section 4.8): callers ask for a beverage by name and
    // never construct a concrete Espresso/FilterCoffee directly -- new
    // beverage types are added by extending the factory, not call sites.
    // ---------------------------------------------------------------
    static class BeverageFactory {
        static Beverage create(String type) {
            switch (type) {
                case "ESPRESSO": return new Espresso();
                case "FILTER_COFFEE": return new FilterCoffee();
                default: throw new IllegalArgumentException("Unknown beverage: " + type);
            }
        }
    }

    // ---------------------------------------------------------------
    // Singleton (Section 4.12): exactly one register instance per process,
    // lazily created, thread-safe via the initialization-on-demand holder
    // idiom (avoids synchronizing every access, unlike a naive double-
    // checked-locking implementation).
    // ---------------------------------------------------------------
    static class CashRegister {
        private double totalRevenue = 0.0;

        private CashRegister() { }

        private static class Holder {
            static final CashRegister INSTANCE = new CashRegister();
        }

        static CashRegister getInstance() {
            return Holder.INSTANCE;
        }

        synchronized void record(double amount) {
            totalRevenue += amount;
        }

        synchronized double totalRevenue() {
            return totalRevenue;
        }
    }

    public static void main(String[] args) {
        Beverage order1 = new ExtraShotDecorator(new MilkDecorator(
                BeverageFactory.create("ESPRESSO")));
        System.out.println(order1.description() + " = $" + order1.cost());

        Beverage order2 = new MilkDecorator(BeverageFactory.create("FILTER_COFFEE"));
        System.out.println(order2.description() + " = $" + order2.cost());

        CashRegister register = CashRegister.getInstance();
        register.record(order1.cost());
        register.record(order2.cost());
        System.out.println("Total revenue: $" + register.totalRevenue());

        // Same instance everywhere in the process -- proves the Singleton
        // contract rather than just asserting it in prose.
        System.out.println("Same register instance? " + (register == CashRegister.getInstance()));
    }
}
