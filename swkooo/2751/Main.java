import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;

//수 정렬하기 2
public class Main {
    public static void main(String[] args) throws IOException {
        // 스캐너 시간초과나서 버퍼드리더로 바꿈...
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());
        int[] arr = new int[N];

        for (int i = 0; i < N; i++) {
            arr[i] = Integer.parseInt(br.readLine());
        }

        Arrays.sort(arr);

        // 출력
        StringBuilder sb = new StringBuilder();
        for (int num : arr) {
            sb.append(num).append('\n');
        }
        System.out.print(sb);
    }//main
}
