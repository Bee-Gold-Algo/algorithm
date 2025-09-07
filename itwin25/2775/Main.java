import java.util.Scanner;

public class Main {
	static int ans = 0;

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int T = sc.nextInt();

		for (int tc = 1; tc <= T; tc++) {
			int k = sc.nextInt(); // k층
			int n = sc.nextInt(); // n호
			int[] arr = new int[n + 1];

			for (int i = 1; i <= n; i++) {
				arr[i] = i;
			}
			people(k, n, arr, 0);

			System.out.println(ans);

		} // tc
	} // main

	static void people(int k, int n, int[] arr, int floor) {
		if (floor == k) {
			ans = arr[n];
			return;
		}
		int[] tmp = new int[n + 1];
		for (int i = 1; i <= n; i++) {
			int sum = 0;
			for (int j = 1; j <= i; j++) {
				sum += arr[j];
			}
			tmp[i] = sum;
		}
		people(k, n, tmp, floor + 1);
	}
}
