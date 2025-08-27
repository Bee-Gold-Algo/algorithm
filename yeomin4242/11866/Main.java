import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        int[] arr = new int[N + 1];

        for (int i = 1 ; i <= N ; i++) {
            arr[i] = i;
        }

        int cnt = 0;
        int allignCnt = 0;

        StringBuilder sb = new StringBuilder("<");

        int sum = 0;

        for (int idx = 0 ; ; ++idx) {
            if (arr[idx] != 0) {
                cnt++;
            }

            if (cnt == K) {
                arr[idx] = 0;
                sb.append(idx);
                sum++;
                if (sum == N) { 
                    break;
                } else {
                    sb.append(", ");
                }
                cnt = 0;
            }
            idx %= N;
        }
        sb.append(">");
        System.out.println(sb);
    };
}