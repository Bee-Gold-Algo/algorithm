import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int K = sc.nextInt(); // 제곰미터 당 참외의 개수
		int[][] land = new int[6][2]; // 밭 정보
		int maxWL = 0; // 제일 긴 가로 길이
		int maxHL = 0; // 제일 긴 세로 길이
		int maxWI = 0; // 긴 가로 인덱스
		int maxHI = 0; // 긴 세로 인덱스

		// 가장 긴 가로, 세로 구하기
		for (int i = 0; i < 6; i++) {
			land[i][0] = sc.nextInt(); // 방향
			land[i][1] = sc.nextInt(); // 길이
			if (land[i][0] == 1 || land[i][0] == 2) {
				if (land[i][1] > maxWL) { // 가로 구하기
					maxWL = land[i][1];
					maxWI = i;
				}
			} else { // 세로 구하기
				if (land[i][1] > maxHL) {
					maxHL = land[i][1];
					maxHI = i;
				}
			}
		}

		int minHL = land[(maxWI + 3) % 6][1]; // 작은 네모의 세로 = 긴 가로에서 3칸 전긴
		int minWL = land[(maxHI + 3) % 6][1]; // 작은 네모의 가로 = 긴 세로에서 3칸 전진

		int sum = (maxWL * maxHL) - (minHL * minWL);

		System.out.println(sum * K);
	}
}