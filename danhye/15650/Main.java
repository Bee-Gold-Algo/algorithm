import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
	static int N, M;
	static int[] res;
	static StringBuilder sb = new StringBuilder();
	
	private static void check(int idx, int start) {
		//종료조건 
		if(idx == M) {
			for (int i = 0; i < M; i++) {
				sb.append(res[i]).append(" ");
			}
			sb.append("\n");
			return;
		}
		
		//재귀
		//길이가 M이고, 중복 없는 자연수를 res 배열에 담아야해 
		for (int i = start; i <= N; i++) {
			res[idx] = i;
			check(idx+1, i+1);
		}
	}

	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		String[] input = br.readLine().split(" ");
		N = Integer.parseInt(input[0]);  //자연수 N
		M = Integer.parseInt(input[1]); //길이 M
		res = new int[M];

		check(0, 1);
		
		//출력
		System.out.println(sb);
	}
}
