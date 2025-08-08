import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int N = sc.nextInt();

		// 하노이탑 실행횟수 규칙은 2의 N 거듭제곱 - 1 !
		// BigInteger 쓰는 법 배웠다...
		System.out.println(Power(BigInteger.TWO, N).subtract(BigInteger.ONE));

		// N <= 20 인 케이스에 대해 실행과정 출력
		if (N <= 20) {
			hanoi(N, 1, 3, 2);
		}
	}

	// N <= 20 까지만 실행!!
	public static void hanoi(int n, int from, int to, int via) {
		// 기본조건
		if (n == 1) {
			System.out.println(from + " " + to);
		}
		// 재귀조건
		else { 
			hanoi(n - 1, from, via, to); // n-1개를 경유지로
			System.out.println(from + " " + to); // 가장 큰 원판 이동
			hanoi(n - 1, via, to, from); // n-1개를 목적지로
		}
	}

	// 2의 60승 정도만 넘어가도 long으로도 터짐.. BigInteger 사용
	public static BigInteger Power(BigInteger n, int repeat) {
		// 기본조건
		if (repeat == 1) {
			return n;
		}
		// 재귀조건 
		return n.multiply(Power(n, repeat - 1));

	}
}
