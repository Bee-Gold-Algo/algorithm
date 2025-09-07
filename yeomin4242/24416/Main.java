import java.io.*;
import java.util.*;

/**
 * 값을 하나씩 바꿔보면서 재귀 계속 감
 */


public class Main{

    static int[] dp = new int[100];

    static int fiboCheck1 = 0;
    static int fiboCheck2 = 0;


    public static int fibo1(int n) {
        if (n <= 2) {
            fiboCheck1++;
            return 1;
        } else {
            return (fibo1(n - 1) + fibo1(n - 2));
        }
    }



    public static int fibo2(int n) {
        dp[0] = 1;
        dp[1] = 1;

        for (int i = 2; i < n ; i++) {
            fiboCheck2++;
            dp[i] = dp[i - 1] + dp[i -2];
        }
        return dp[n - 1];
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());

        fibo1(N);
        fibo2(N);

        System.out.println(fiboCheck1 + " " + fiboCheck2);
    }
}