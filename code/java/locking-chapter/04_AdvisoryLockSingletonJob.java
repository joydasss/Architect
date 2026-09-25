import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.concurrent.CountDownLatch;

/**
 * Advisory-lock-based singleton scheduled job.
 *
 * Implements CH10_Locking.md Section 4.8: PostgreSQL session-level advisory
 * locks used to guarantee "only one instance of this job runs at a time"
 * across simulated concurrent job-runner instances, without any of them
 * needing to know about the others.
 *
 * Setup:
 *   createdb locking_demo   # or point JDBC_URL below at an existing database
 *   Ensure the PostgreSQL JDBC driver jar is on the classpath.
 *
 * Run:
 *   javac AdvisoryLockSingletonJob.java -d out
 *   java -cp out:&lt;path-to-postgresql-jdbc.jar&gt; AdvisoryLockSingletonJob
 */
public class AdvisoryLockSingletonJob {

    private static final String JDBC_URL = "jdbc:postgresql://localhost/locking_demo";
    // Arbitrary, application-chosen key identifying "the nightly report job"
    // (Section 4.8) -- unrelated to any table/row, purely a coordination token.
    private static final long JOB_LOCK_KEY = 987654321L;

    public static void main(String[] args) throws InterruptedException {
        int instanceCount = 3;
        CountDownLatch latch = new CountDownLatch(instanceCount);

        for (int i = 1; i <= instanceCount; i++) {
            final String instanceName = "job-runner-" + i;
            Thread t = new Thread(() -> {
                runAsSingleton(instanceName);
                latch.countDown();
            });
            t.start();
        }

        latch.await();
        System.out.println("All job-runner instances finished.");
    }

    private static void runAsSingleton(String instanceName) {
        try (Connection conn = DriverManager.getConnection(JDBC_URL)) {
            // Section 4.8: try to acquire the advisory lock without blocking.
            // Exactly one concurrent caller will succeed; the rest see false
            // and skip their run immediately.
            boolean acquired;
            try (PreparedStatement ps = conn.prepareStatement(
                    "SELECT pg_try_advisory_lock(?)")) {
                ps.setLong(1, JOB_LOCK_KEY);
                try (ResultSet rs = ps.executeQuery()) {
                    rs.next();
                    acquired = rs.getBoolean(1);
                }
            }

            if (!acquired) {
                System.out.println(
                        "[" + instanceName + "] lock already held elsewhere -- skipping this run");
                return;
            }

            try {
                System.out.println("[" + instanceName + "] acquired lock, running job...");
                simulateJobWork();
                System.out.println("[" + instanceName + "] job complete");
            } finally {
                // Explicitly release -- session-level advisory locks otherwise
                // persist until the connection/session ends.
                try (PreparedStatement ps = conn.prepareStatement(
                        "SELECT pg_advisory_unlock(?)")) {
                    ps.setLong(1, JOB_LOCK_KEY);
                    ps.execute();
                }
            }
        } catch (Exception e) {
            System.err.println("[" + instanceName + "] error: " + e.getMessage());
        }
    }

    private static void simulateJobWork() throws InterruptedException {
        Thread.sleep(500);
    }
}
