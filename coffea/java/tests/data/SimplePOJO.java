import java.math.BigDecimal;
import java.util.Date;

public final class SimplePOJO implements java.io.Serializable {

    public static final Integer MATRIX_WID = 5;
    public static final Integer MATRIX_HEI = 5;

    private String name = "Sample POJO";

    Integer age = 30;

    Long id = 42L;

    double temperature = 3.14;

    float height = 185.0f; 

    BigDecimal cash = BigDecimal.ZERO;

    protected Double[][] matrix = new Double[MATRIX_WID][MATRIX_HEI];

    Date[] times = new Date[]{new Date()};

    public void doStuff() {
        for (int i=0; i<MATRIX_WID; i++) {
            for (int j=0; j<MATRIX_HEI; j++) {
                if (i == j)
                    matrix[MATRIX_WID][MATRIX_HEI] = 1.0;
                else
                    matrix[MATRIX_WID][MATRIX_HEI] = 0.0;
            }
        }
    }

    public String toString() {
        return name;
    }

}
