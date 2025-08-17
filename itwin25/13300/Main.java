import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int N = sc.nextInt(); // 총 학생 수
		int K = sc.nextInt(); // 방 최대 인원
		int[][] arr = new int[7][2];
		int cnt = 0; // 방 갯수

		for (int i = 0; i < N; i++) {
			int S = sc.nextInt(); // 성별, 0:
			int Y = sc.nextInt(); // 학년

			arr[Y][S]++; // 학년별로 여, 남 학생 수 담기
		}

		// 필요한 방의 수 계산
		for (int i = 1; i < 7; i++) {
			for (int j = 0; j < 2; j++) {
				if (arr[i][j] != 0) {
					cnt += (arr[i][j] / K) + (arr[i][j] % K);
				}
			}
		}

		System.out.println(cnt);

	}
}