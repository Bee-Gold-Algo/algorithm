import java.util.*;
import java.io.*;

public class Main {
    public static void main(String args[]) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        StringTokenizer st = new StringTokenizer(br.readLine());

        double x = Integer.parseInt(st.nextToken());
        double y = Integer.parseInt(st.nextToken());
        double sum = x / y;

        System.out.printf("%.9f",sum);
    }
}
