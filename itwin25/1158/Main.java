import java.util.LinkedList;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int N = sc.nextInt(); // 사람 수
		int K = sc.nextInt(); // K번째 사람 제거

		LinkedList<Integer> list = new LinkedList<>();
		String[] ans = new String[N]; // 답을 저장할 배열

		for (int i = 1; i <= N; i++) {
			list.add(i);
		}

		int idx = -1; // 시작 인덱스

		// 요세푸스 순열 구하기
		for (int j = 0; j < N; j++) {
			idx += K;
			if (idx < list.size()) {
				ans[j] = list.remove(idx).toString();
				idx--; // 제거하고 인덱스 하나 감소
			} else {
				idx %= list.size();
				ans[j] = list.remove(idx).toString();
				idx--;
			}
		}

		System.out.println("<" + String.join(", ", ans) + ">");

	}
}