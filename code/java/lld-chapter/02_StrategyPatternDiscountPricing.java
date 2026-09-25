import java.math.BigDecimal;
import java.util.List;

/**
 * Implements CH04_Low_Level_Design.md Section 4.9 (Strategy pattern) and
 * Section 10 example 2: interchangeable discount-pricing algorithms selected
 * and swapped at runtime without the caller (Checkout) branching on type.
 *
 * Run:
 *   javac 02_StrategyPatternDiscountPricing.java -d out
 *   java -cp out StrategyPatternDiscountPricing
 */
public class StrategyPatternDiscountPricing {

    // The Strategy interface: the family of interchangeable algorithms.
    interface DiscountStrategy {
        BigDecimal apply(BigDecimal subtotal);
    }

    static class NoDiscount implements DiscountStrategy {
        public BigDecimal apply(BigDecimal subtotal) {
            return subtotal;
        }
    }

    static class PercentageOffDiscount implements DiscountStrategy {
        private final BigDecimal percentage; // e.g. 0.10 for 10% off

        PercentageOffDiscount(BigDecimal percentage) {
            this.percentage = percentage;
        }

        public BigDecimal apply(BigDecimal subtotal) {
            return subtotal.subtract(subtotal.multiply(percentage));
        }
    }

    static class FlatAmountOffDiscount implements DiscountStrategy {
        private final BigDecimal amountOff;

        FlatAmountOffDiscount(BigDecimal amountOff) {
            this.amountOff = amountOff;
        }

        public BigDecimal apply(BigDecimal subtotal) {
            BigDecimal result = subtotal.subtract(amountOff);
            return result.max(BigDecimal.ZERO);
        }
    }

    // The context: holds a reference to a strategy and delegates, never
    // branching on which concrete discount is active -- this is the
    // property that satisfies OCP (Section 4.4) when a new discount type
    // (e.g. loyalty-tier discount) is added later.
    static class Checkout {
        private DiscountStrategy discountStrategy;

        Checkout(DiscountStrategy discountStrategy) {
            this.discountStrategy = discountStrategy;
        }

        void setDiscountStrategy(DiscountStrategy discountStrategy) {
            this.discountStrategy = discountStrategy; // swapped at runtime
        }

        BigDecimal total(List<BigDecimal> lineItemPrices) {
            BigDecimal subtotal = lineItemPrices.stream()
                    .reduce(BigDecimal.ZERO, BigDecimal::add);
            return discountStrategy.apply(subtotal);
        }
    }

    public static void main(String[] args) {
        List<BigDecimal> cart = List.of(
                new BigDecimal("49.99"), new BigDecimal("19.99"), new BigDecimal("5.00"));

        Checkout checkout = new Checkout(new NoDiscount());
        System.out.println("No discount: " + checkout.total(cart));

        checkout.setDiscountStrategy(new PercentageOffDiscount(new BigDecimal("0.10")));
        System.out.println("10% off: " + checkout.total(cart));

        checkout.setDiscountStrategy(new FlatAmountOffDiscount(new BigDecimal("15.00")));
        System.out.println("$15 off: " + checkout.total(cart));
    }
}
