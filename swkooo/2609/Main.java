import java.util.Arrays;
import java.util.Scanner;

//최대공약수와 최소공배수
public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int[] temp = new int[2];
		temp[0] = sc.nextInt();
		temp[1] = sc.nextInt();
		Arrays.sort(temp);
		int small = temp[0];
		int big = temp[1];

		int maxDiv = 0; // 최대공약수
		int minMul = 0; // 최소공배수
		boolean canDiv = false; // 공약수 없는 케이스 체크

		if (big % small == 0) {
			canDiv = true;
			maxDiv = small;
			minMul = big;
		} else {
			// 작은 수 기준으로
			for (int i = 2; i <= small / 2; i++) {
				if (small % i == 0 && big % i == 0) {
					maxDiv = i;
					canDiv = true;
				}
				// 최소공배수는 두 수를 곱하고 최대공약수로 나눈 값

			}
			// 공약수가 있는 경우에만 실행
			if (canDiv) {
				minMul = big * small / maxDiv;
			}
		}
		// 공약수가 없다면
		if (!canDiv) {
			maxDiv = 1;
			minMul = small * big;
		}

		System.out.println(maxDiv);
		System.out.println(minMul);

	}// main
}
