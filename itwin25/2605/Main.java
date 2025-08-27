import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int N = sc.nextInt(); // 학생 수
		List<Integer> line = new ArrayList<>();

		for (int j = 1; j <= N; j++) {
			int K = sc.nextInt(); // j번째 학생이 뽑은 숫자
			if (K != 0) {
				// j번째 학생 옮기기
				line.add(j - K - 1, j);
			} else {
				line.add(j);
			}
		}

		StringBuilder sb = new StringBuilder();

		for (Integer n : line) {
			sb.append(n).append(" ");
		}
		System.out.println(sb.toString().trim());
	}
}