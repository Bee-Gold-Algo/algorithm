import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

//피보나치 함수
public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		StringBuilder sb = new StringBuilder();
		
		int T = sc.nextInt();

		for (int tc = 1; tc <= T; tc++) {
			int N = sc.nextInt();
			if (N == 0)
				sb.append("1 0\n");
			else
			sb.append(Fibo(N-1) +  " " + Fibo(N) + "\n");
		} // tc
		System.out.println(sb);
	}// main

	static int[] memo = new int[40]; // memorize 할 배열... N<= 40이므로 40까지만 준비

	public static int Fibo(int N) {
		if (N == 0) {
			return 0;
		} else if (N == 1) {
			return 1;
		} else {
			int A = memo[N-1];
			int B = memo[N-2];
			if (A == 0) {
				memo[N-1] = Fibo(N-1);
				A = memo[N-1];
			}
			if (B == 0) {
				memo[N-2] = Fibo(N-2);
				B = memo[N-2];
			}
			return A + B;			
		}
	}
} 
