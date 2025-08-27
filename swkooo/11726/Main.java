import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

//2xn 타일링
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int n = Integer.parseInt(br.readLine());

		// 사실상 n을 1과 2의 합으로 나타내는 문제와 동일하다!!
		// n-1에 1을 더하고 n-2에 2를 더한 거랑 같음...
		/* 1 -> +1										 1개
		 * 2 -> +1+1, +2								 2개
		 * 3 -> +1+1+1, +1+2, +2+1 						 3개
		 * 4 -> +1+1+1+1, +1+1+2, +1+2+1, +2+1+1, +2+2	 5개 
		 */
		
		// 최대 n+1개의 배열 생성 ... 0번째 인덱스는 0으로
		int[] arrN = new int[n + 2];
		
		arrN[1] = 1;
		arrN[2] = 2;
		
		for (int i = 3; i <= n; i++) {
			arrN[i] = (arrN[i-1] + arrN[i-2]) % 10007;	// 값이 무지막지하게 큰가보구나...
		}
		
		System.out.println(arrN[n]);
	}// main
}
