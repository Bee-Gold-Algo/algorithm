import java.util.*;
import java.io.*;

public class Main{

    static StringBuilder sb = new StringBuilder();
    static boolean[] visit;
    static int[] arr;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        // value 체크 용
        visit = new boolean[N];
        
        //depth 에 따른 값 보관
        arr = new int[M];

        dfs (N, M, 0);   
        System.out.print(sb);
    }

    public static void dfs(int N, int M, int depth) {
        if (M == depth) {
            for (int idx : arr) {
                sb.append(idx + " ");
            }
            sb.append("\n");
            return;
        }

        for (int i = 0 ; i < N; i++) {
            if (visit[i] != true) {
                visit[i] = true;
                arr[depth] = (i + 1);
                dfs(N, M, depth + 1);
                visit[i] = false;
            }
        }
    }
}