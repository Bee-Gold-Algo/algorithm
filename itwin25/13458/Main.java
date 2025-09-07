import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int N = sc.nextInt(); // 시험장 갯수
		int[] p = new int[N];
		for (int i = 0; i < N; i++) {
			p[i] = sc.nextInt();
		}
		int A = sc.nextInt(); // 총감독관
		int B = sc.nextInt(); // 부감독관

		long cnt = 0;

		for (int i = 0; i < N; i++) {
			int tmp = p[i] - A; // 학생 수 - 총감독관 감시자 수
			cnt++;
			if (tmp > 0) {
				cnt += (tmp + B - 1) / B;
			}
		}

		System.out.println(cnt);
	} // main
}
