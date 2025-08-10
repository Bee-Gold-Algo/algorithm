import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.math.BigInteger;

public class Main {

	static void hanoi(int n, int from, int to, int assis, StringBuilder out) {
		//base case
		if(n == 1) {
			out.append(from).append(" ").append(to).append("\n");
			return;
		}
		
		//재귀
		//1) n-1개를 from -> assis
		// to에 assis를 넣는다 !!!
		hanoi(n-1, from, assis, to, out);
		
		//2)가장 큰 원판 1개를 from -> to
		out.append(from).append(" ").append(to).append("\n");
		
		//3)n-1개를 assis -> to
		hanoi(n-1, assis, to, from, out);
		
	}
	
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		int N = Integer.parseInt(br.readLine());
		
		//하노이 공식 : 2^N -1 
		// 1. N = 1  -> 1번 이동 (from -> assis)
		// 2. N > 1 -> 아래 세 과정 반복
		//				(1) N-1 이동 (from -> assis)
		//				(2) 가장 큰 원 하나 이동 (from -> to)
		//				(3) N-1 이동 (assis -> to)
		//그래서 !! T(N) = T(N-1) + 1 + T(N-1) 
		//		  T(N) = 2 * T(N-1) + 1
		
		//BigInteger.ONE.shiftLeft(N) = 2^N
		BigInteger k = BigInteger.ONE.shiftLeft(N).subtract(BigInteger.ONE);
		
		StringBuilder sb = new StringBuilder();
		sb.append(k).append("\n");
		
		if(N <= 20) {
			StringBuilder moves = new StringBuilder();
			//from = 1, to = 3, assis = 2
			hanoi(N, 1, 3, 2, moves);
			sb.append(moves);
		}
		
		System.out.println(sb.toString());
	}
}
