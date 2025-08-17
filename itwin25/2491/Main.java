import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int N = sc.nextInt(); // 수열의 길이
		int[] arr = new int[N]; // 수열
		int cnt = 1; // 커지고 작아지는 길이
		int max = 1; // 최대 길이

		for (int i = 0; i < N; i++) {
			arr[i] = sc.nextInt();
		}

		// 커지는 것 중에 최대
		for (int i = 0; i < N - 1; i++) {
			if (arr[i] <= arr[i + 1]) {
				cnt++;
				max = Math.max(max, cnt);
			} else {
				cnt = 1;
			}
		}

		cnt = 1; // cnt 초기화

		// 작아지는 것 중에 최대
		for (int i = 0; i < N - 1; i++) {
			if (arr[i] >= arr[i + 1]) {
				cnt++;
				max = Math.max(max, cnt);
			} else {
				cnt = 1;
			}
		}

		System.out.println(max);
	}

}