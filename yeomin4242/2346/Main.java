import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException{
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());

        Deque<int[]> deque = new ArrayDeque<int[]>();


        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] arr = new int[N];

        for (int i = 0 ; i < N ; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        for (int i = 1 ; i < N ; i++) {
            deque.addLast(new int[] {(i + 1), arr[i]});
        }

        int element = arr[0];

        StringBuilder sb = new StringBuilder();

        sb.append("1 ");

        while (deque.isEmpty() == false) {

            if (element > 0) {
                for (int j = 1 ; j < Math.abs(element) ; j++) {
                    deque.addLast(deque.removeFirst());
                }
                int[] X = deque.removeFirst();
                element = X[1];
                sb.append(X[0] + " ");
            } else {
                for (int j = 1 ; j < Math.abs(element) ; j++) {
                    deque.addFirst(deque.removeLast());
                }
                int[] X  = deque.removeLast();
                element = X[1];
                sb.append(X[0] + " ");
            }
        }
        System.out.println(sb);
    }
}