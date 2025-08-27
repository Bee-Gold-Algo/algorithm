import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

//1, 2, 3 더하기
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int T = Integer.parseInt(br.readLine());
		
		// 정수 n을 나타내는 방법은
		/* n-3을 나타내는 방법에서 3을 더하거나... -> +1 					 / 1가지
		 * n-2를 나타내는 방법에서 2를 더하거나... -> +1+1, +2 				 / 2가지
		 * n-1을 나타내는 방법에서 1을 더하면됨.   -> +1+1+1, +1+2, +2+1, +3 / 4가지
		 * 
		 *... 이게 맞나? 
		 */
		
		// 최대 10까지만 주어지므로 미리 그보다 1큰 배열 만들어 놓기
		int[] nSum = new int[11];
		
		nSum[1] = 1;
		nSum[2] = 2;
		nSum[3] = 4;
		
		// 4~ 이후 값은 이전 값들 3개의 합
		for (int i = 4; i < 11; i++) {
			nSum[i] = nSum[i-1] + nSum[i-2] + nSum[i-3]; 
		}
		
		for (int tc = 1; tc <= T; tc++) {
			int n = Integer.parseInt(br.readLine());
			
			// 출력
			System.out.println(nSum[n]);
			
		}//tc
		
	}//main
}
