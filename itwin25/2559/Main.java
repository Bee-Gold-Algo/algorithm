import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int N = sc.nextInt(); // 전체 날짜의 수
		int K = sc.nextInt(); // 연속적인 날짜의 수
		int[] temp = new int[N]; // 매일 측정한 온도

		for (int i = 0; i < N; i++) {
			temp[i] = sc.nextInt();
		}

		int sum = 0;
		for (int i = 0; i < K; i++) {
			sum += temp[i];
		}

		int max = sum;

		// 온도의 최대 합 찾기
		for (int j = 0; j < N - K; j++) {
			sum = sum - temp[j] + temp[K + j];
			max = Math.max(max, sum);
		}

		System.out.println(max);
	}
}