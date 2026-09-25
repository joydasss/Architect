import java.util.ArrayList;
import java.util.List;

/**
 * Implements CH04_Low_Level_Design.md Section 4 (SOLID subsections) and
 * Section 10 example 1: a single before/after pair showing a Single
 * Responsibility Principle (SRP) + Open/Closed Principle (OCP) violation,
 * then a refactor that fixes both without touching call sites unnecessarily.
 *
 * Run:
 *   javac 01_SolidViolationAndRefactor.java -d out
 *   java -cp out SolidViolationAndRefactor
 */
public class SolidViolationAndRefactor {

    // ---------------------------------------------------------------
    // BEFORE: violates SRP (formatting + persistence + notification all in
    // one class) and OCP (adding a new report type means editing this
    // method's if/else chain instead of extending the system).
    // ---------------------------------------------------------------
    static class BadOrderReportService {
        void generateAndSendReport(String orderId, String reportType) {
            String content;
            // OCP violation: every new report type requires editing this method.
            if (reportType.equals("INVOICE")) {
                content = "Invoice for order " + orderId;
            } else if (reportType.equals("PACKING_SLIP")) {
                content = "Packing slip for order " + orderId;
            } else {
                throw new IllegalArgumentException("Unknown report type: " + reportType);
            }
            // SRP violation: this class also owns "persistence" concerns...
            System.out.println("[DB] Saving report: " + content);
            // ...and "notification" concerns, all under one reason to change.
            System.out.println("[EMAIL] Sending report to customer: " + content);
        }
    }

    // ---------------------------------------------------------------
    // AFTER: SRP restores one reason to change per class; OCP is satisfied
    // by extending via a new ReportFormatter implementation instead of
    // editing existing code (this is also the Strategy pattern from
    // Section 4.9, used here as the OCP-satisfying seam).
    // ---------------------------------------------------------------
    interface ReportFormatter {
        String format(String orderId);
    }

    static class InvoiceFormatter implements ReportFormatter {
        public String format(String orderId) {
            return "Invoice for order " + orderId;
        }
    }

    static class PackingSlipFormatter implements ReportFormatter {
        public String format(String orderId) {
            return "Packing slip for order " + orderId;
        }
    }

    // A new report type (e.g. CreditNoteFormatter) can be added later by
    // implementing ReportFormatter -- zero lines of existing code change.
    interface ReportRepository {
        void save(String content);
    }

    static class InMemoryReportRepository implements ReportRepository {
        private final List<String> saved = new ArrayList<>();
        public void save(String content) {
            saved.add(content);
            System.out.println("[DB] Saving report: " + content);
        }
    }

    interface ReportNotifier {
        void notifyCustomer(String content);
    }

    static class EmailReportNotifier implements ReportNotifier {
        public void notifyCustomer(String content) {
            System.out.println("[EMAIL] Sending report to customer: " + content);
        }
    }

    static class GoodOrderReportService {
        private final ReportRepository repository;
        private final ReportNotifier notifier;

        GoodOrderReportService(ReportRepository repository, ReportNotifier notifier) {
            this.repository = repository;
            this.notifier = notifier;
        }

        // Depends on the ReportFormatter abstraction, not a concrete type --
        // satisfies both OCP (new formatters plug in) and DIP (Section 4.7:
        // this method depends on an interface, never on a concrete class).
        void generateAndSendReport(String orderId, ReportFormatter formatter) {
            String content = formatter.format(orderId);
            repository.save(content);
            notifier.notifyCustomer(content);
        }
    }

    public static void main(String[] args) {
        System.out.println("--- BEFORE (SRP + OCP violation) ---");
        new BadOrderReportService().generateAndSendReport("ORD-1", "INVOICE");

        System.out.println("--- AFTER (SRP + OCP + DIP satisfied) ---");
        GoodOrderReportService service = new GoodOrderReportService(
                new InMemoryReportRepository(), new EmailReportNotifier());
        service.generateAndSendReport("ORD-1", new InvoiceFormatter());
        service.generateAndSendReport("ORD-1", new PackingSlipFormatter());
    }
}
