import java.math.BigInteger;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int N = sc.nextInt();
		BigInteger cnt = new BigInteger("2").pow(N).subtract(BigInteger.ONE);

		System.out.println(cnt);
		if (N <= 20) {
			hanoi(N, 1, 3, 2);
		}
	}

	public static void hanoi(int N, int from, int to, int via) {
		if (N == 1) {
			System.out.println(from + " " + to);
		} else {
			hanoi(N - 1, from, via, to);
			System.out.println(from + " " + to);
			hanoi(N - 1, via, to, from);
		}
	}
}