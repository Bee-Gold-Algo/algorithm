import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException{
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());

        Deque<Integer> deque = new ArrayDeque<Integer>();

        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < N ; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());

            int num = Integer.parseInt(st.nextToken());

            switch (num) {
                case 1:
                    {
                        int X = Integer.parseInt(st.nextToken());
                        deque.addFirst(X);
                        break;
                    }
                case 2:
                    {
                        int X = Integer.parseInt(st.nextToken());
                        deque.addLast(X);
                        break;
                    }
                case 3:
                    if (deque.isEmpty()) {
                        sb.append(-1).append("\n");
                    } else {
                        int X = deque.removeFirst();
                        sb.append(X).append("\n");
                    }   break;
                case 4:
                    if (deque.isEmpty()) {
                        sb.append(-1).append("\n");
                    } else {
                        int X = deque.removeLast();
                        sb.append(X).append("\n");
                    }   break;
                case 5:
                    sb.append(deque.size()).append("\n");
                    break;
                case 6:
                    if (deque.isEmpty()) {
                        sb.append(1).append("\n");
                    } else {
                        sb.append(0).append("\n");
                    }   break;
                case 7:
                    if (deque.isEmpty()) {
                        sb.append(-1).append("\n");
                    } else {
                        sb.append(deque.getFirst()).append("\n");
                    }   break;
                case 8:
                    if (deque.isEmpty()) {
                        sb.append(-1).append("\n");
                    } else {
                        sb.append(deque.getLast()).append("\n");
                    }   break;
                default:
                    break;
            }

            if (i + 1 == N) {
                sb.deleteCharAt(sb.length() - 1);
            }
        }
        System.out.println(sb);
    }
}