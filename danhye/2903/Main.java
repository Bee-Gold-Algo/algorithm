import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int n = Integer.parseInt(br.readLine());

// 		아래와 같이 구현하면 메모리 터짐
//		int pow = (int) Math.pow(2,n);
//		int[][] arr = new int[pow][pow];
//		int res = 0;
//		for (int i = 0; i <= pow; i++) {
//			for (int j = 0; j <= pow; j++) {
//				res++;
//			}
//		}
		
		int side = (1<<n) + 1; // 한 변의 점 개수 2^n + 1
		//Math.pow(2,n) 도 가능하나,,,
		// 1 << n 이게 더 간단 ! 2^n와 동일 의미
		int res = side * side;
		System.out.println(res);
	}
}
