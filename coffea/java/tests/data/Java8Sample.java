import java.util.Arrays;
import java.util.List;

public final class Java8Sample implements java.io.Serializable {

    private java.time.LocalDateTime someTime;

    public static void main(String []argv) {
        System.out.println("Java 8 Sample");

        simpleLambda();
        simpleStream();
    }

    private static void simpleLambda() {
        Runnable r = () -> System.out.println("Hello world!");
        r.run();
    }

    private static void simpleStream() {
        final List<String> cities = Arrays.asList("Warsaw", "Paris", "Berlin", "London", "Prague");
        cities.stream()
              .filter(s -> s.startsWith("P"))
              .map(String::toUpperCase)
              .sorted()
              .forEach(System.out::println);
    }
}
