import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
	static int N, M;
	static int[] arr;
	static boolean[] visited;
	public static void main(String[] args) throws IOException {
		BufferedReader br  = new BufferedReader (new InputStreamReader(System.in));
		
		StringTokenizer st = new StringTokenizer(br.readLine(), " ");
		N = Integer.parseInt(st.nextToken()); //자연수 N
		M = Integer.parseInt(st.nextToken()); //길이
		
		arr = new int[M];
		visited = new boolean[N];

		check(0, N, M);
	}

	private static void check(int depth, int N , int M) {

		//종료조건
		//깊이가 같아지면 담았던 배열을 출력
		if(depth == M) {
			for(int val : arr) {
				System.out.print(val + " ");
			}
			System.out.println();
			return;
		}
		
		//재귀
		for (int i = 0; i < N; i++) {
			//방문여부 체크
			if(visited[i] == false) {
				visited[i] = true;
				arr[depth] = i + 1;
				check(depth+1, N, M);
				
				visited[i] = false;
			}
		}
		
	}
}
