// Minimal HTTP client using java.net.http, demonstrating status-code branching.
// Referenced from 05_Networking_and_OS/CH01_HTTP.md (Section 10).
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public final class SimpleHttpClient {

    public static String getProduct(String host, String path) throws Exception {
        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .build();

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://" + host + path))
                .header("Accept", "application/json")
                .GET()
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        int status = response.statusCode();
        if (status == 200) {
            return response.body();
        }
        if (status == 304) {
            return null; // caller's cached copy is still fresh
        }
        if (status >= 400 && status < 500) {
            throw new IllegalArgumentException("Client error " + status + ": " + response.body());
        }
        if (status >= 500) {
            throw new IllegalStateException("Server error " + status + ": " + response.body());
        }
        throw new IllegalStateException("Unexpected status " + status);
    }

    public static void main(String[] args) throws Exception {
        System.out.println(getProduct("example.com", "/product/42"));
    }
}
