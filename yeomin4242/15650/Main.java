import java.util.*;
import java.io.*;

public class Main{
    /**
     * 백 트래킹 DFS
     * ASC가 되어야하므로, 비교 과정 하나 더 필요 
     */

    static StringBuilder sb = new StringBuilder();
    static int N;
    static int M;

    static int[] arr;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        StringTokenizer st = new StringTokenizer(br.readLine());

        N = Integer.parseInt(st.nextToken());
        M = Integer.parseInt(st.nextToken());

        arr = new int[M];

        dfs(1, 0);
        System.out.print(sb);
    }

    public static boolean checkDepth(int value) {
        for (int elem : arr) {
            if (elem != 0 && elem >= value) {
                return false;
            }
        }
        return true;
    }

    public static void dfs(int at, int depth) {
        if (M == depth) {
            for (int value : arr) {
                sb.append(value + " ");
            }
            sb.append("\n");
            return;
        }

        for (int i = at ; i <= N ; i++) {
            arr[depth] = i;
            dfs(i + 1, depth + 1);
        }
    }
}
