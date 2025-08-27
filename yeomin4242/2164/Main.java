import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());

        if (N == 1) {
            System.out.println(1);
            return ;
        }

        Queue<Integer> queue = new LinkedList<Integer>();

        for (int i = 1 ; i <= N ; i++) {
            queue.add(i);
        }

        int idx = 1;

        while (true) {
            int num = queue.remove();
            if (idx % 2 == 0) {
                queue.add(num);
            }
            if (queue.size() == 1){
                break;
            }
            idx++;
        }

        System.out.println(queue.peek());
    }
}