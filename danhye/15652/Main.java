import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
	static int N,M;
	static int[] res;
	static StringBuilder sb = new StringBuilder();
	
	public static void check(int idx) {
		//종료조건
		if(idx == M) {
			for (int i = 0; i < idx; i++) {
				sb.append(res[i]).append(" ");
			}
			sb.append("\n");
			return;
		}
				
		for (int i = (idx == 0 ? 1 : res[idx - 1]); i <= N; i++) {
		    res[idx] = i;
		    check(idx + 1);
		}

	}
	
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		StringTokenizer st = new StringTokenizer(br.readLine()," ");
		
		N = Integer.parseInt(st.nextToken()); //자연수 1 ~ N
		M = Integer.parseInt(st.nextToken()); //길이
		res = new int[M];
		

		check(0);
		System.out.println(sb);
	}
}
