import java.util.*;
import java.io.*;

public class Main{
    /**
     * 백 트래킹 DFS
     * 내림차순만 아니면 됨
     * at은 순서보장, 하지만 중복을 허용 시켜줘야함
     * 
     */

    static int N;
    static int M;

    static int[] arr;


    static StringBuilder sb = new StringBuilder();

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        StringTokenizer st = new StringTokenizer(br.readLine());

        N = Integer.parseInt(st.nextToken());
        M = Integer.parseInt(st.nextToken());

        arr = new int[M];

        dfs(1, 0);

        System.out.print(sb);
    }

    public static void dfs(int at, int depth) {
        if (depth == M) {
            for (int value : arr) {
                sb.append(value + " ");
            }
            sb.append("\n");
            return ;
        }


        for (int i = at; i <= N ; i++) {
            arr[depth] = i;
            dfs(i, depth + 1);
        }
    }
}

/**
 * 기존과 다르게 중복과 오름차순을 허용함
 * 따라서 오름차순을 보장하려고 현재 위치(at)를 인자로
 * 넘기는 식에서 위치 말고 값을 넘기는 식으로 해결
 */