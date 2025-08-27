import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int N = sc.nextInt(); // 스위치 개수
		int[] nowS = new int[N + 1]; // 스위치 상태
		for (int i = 1; i <= N; i++) {
			nowS[i] = sc.nextInt();
		}

		int S = sc.nextInt(); // 학생 수

		for (int i = 0; i < S; i++) {
			int gender = sc.nextInt();
			int num = sc.nextInt();
			if (gender == 1) { // 남학생
				for (int k = num; k <= N; k += num) {
					nowS[k] = 1 - nowS[k];
				}
			} else { // 여학생
				nowS[num] = 1 - nowS[num];
				int left = num - 1;
				int right = num + 1;
				while (left >= 1 && right <= N && nowS[left] == nowS[right]) {
					nowS[left] = 1 - nowS[left];
					nowS[right] = 1 - nowS[right];

					left--;
					right++;
				}
			}
		}

		for (int i = 1; i <= N; i++) {
			System.out.print(nowS[i] + " ");
			if (i % 20 == 0) {
				System.out.println();
			}
		}
	}

}