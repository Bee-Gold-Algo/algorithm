import java.util.Scanner;

/*
 * 경비원
 * 블록을 펼쳐서 왼쪽 꼭짓점이 원점이라고 가정
 */
public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int width = sc.nextInt(); // 가로
		int height = sc.nextInt(); // 세로
		int store = sc.nextInt(); // 상점의 개수
		int block = width * 2 + height * 2; // 블록 전체 길이
		int sum = 0; // 총 거리
		int[][] arr = new int[store + 1][3]; // [0]: 동서남북 [1]: 거리 [2]: 원점에서의 거리

		// 동근, 상점 원점에서의 거리 계산
		for (int i = 0; i < store + 1; i++) {
			arr[i][0] = sc.nextInt();
			arr[i][1] = sc.nextInt();

			switch (arr[i][0]) {
			case 1: // 북
				arr[i][2] = arr[i][1];
				break;
			case 2: // 남
				arr[i][2] = width + height + (width - arr[i][1]);
				break;
			case 3: // 서
				arr[i][2] = width * 2 + height + (height - arr[i][1]);
				break;
			case 4: // 동
				arr[i][2] = width + arr[i][1];
				break;
			}
		}

		int dong = arr[store][2]; // 원점-동근 거리

		// 동근-상점 거리 구하기
		for (int i = 0; i < store; i++) {
			int clock = Math.abs(arr[i][2] - dong); // 동근-상점 시계방향 거리
			sum += Math.min(clock, block - clock); // 시계, 반시계 중에서 작은 값 합산
		}
		System.out.println(sum);
	}

}