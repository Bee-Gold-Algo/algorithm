import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayDeque;

public class Main {
	public static void main(String[] args) throws IOException {

		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

		int TC = Integer.parseInt(br.readLine());

		ArrayDeque<Integer> stack = new ArrayDeque<>();
		for (int h = 0; h < TC; h++) {
			String[] inputLine = br.readLine().split(" ");

			if (inputLine[0].equals("push")) {
				stack.push(Integer.parseInt(inputLine[1]));

			} else if (inputLine[0].equals("pop")) {
				if (!stack.isEmpty()) {
					int num = stack.pop();
					System.out.println(num);
				} else {
					// 스택이 비어있는 경우 -1 출력
					System.out.println(-1);
				}

			} else if (inputLine[0].equals("size")) {
				System.out.println(stack.size());

			} else if (inputLine[0].equals("empty")) {
				if (stack.isEmpty()) {
					System.out.println(1);
				} else {
					System.out.println(0);
				}

			} else if (inputLine[0].equals("top")) {
				if (stack.isEmpty()) {
					System.out.println(-1);
				} else {
					System.out.println(stack.peek());
				}
			}
		}
	}
}