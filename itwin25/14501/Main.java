import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int N = sc.nextInt(); // N일
		int[][] schedule = new int[N + 1][2]; // 기간, 수익

		for (int i = 1; i < N + 1; i++) {
			for (int j = 0; j < 2; j++) {
				schedule[i][j] = sc.nextInt();
			}
		}

		int[] dp = new int[N + 2]; // 최대 수익을 담을 배열

		// 점화식?
		for (int i = N; i > 0; i--) {
			// 상담이 가능한가?
			if (schedule[i][0] + i - 1 <= N) {
				// 1. 그치만 안 할래
				int No = dp[i + 1];
				// 2. 하지 뭐
				int Yes = schedule[i][1] + dp[i + schedule[i][0]]; // 오늘 수익 + 오늘 상담 끝난 뒤의 수익
				// 1, 2 중에 최대 수익인 경우를 선택
				dp[i] = Math.max(Yes, No);
			} else { // 불가능.. -> 안 한다
				dp[i] = dp[i + 1];
			}
		}

		System.out.println(dp[1]);
	} // main
}
