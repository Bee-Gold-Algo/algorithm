import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
	static int[] dr = { 1, 0 }; // 남, 동
	static int[] dc = { 0, 1 }; // 남, 동
	static int M;
	static int N;

	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringTokenizer st = new StringTokenizer(br.readLine(), " ");
		N = Integer.parseInt(st.nextToken()); // 도시의 가로 크기 (열)
		M = Integer.parseInt(st.nextToken()); // 도시의 세로 크기 (행)

		int[][] map = new int[M][N];

		for (int i = 0; i < M; i++) {
			st = new StringTokenizer(br.readLine(), " ");
			for (int j = 0; j < N; j++) {
				map[i][j] = Integer.parseInt(st.nextToken());
			}
		}

		System.out.println(dfs(map, 0, 0));

	} // main

	private static String dfs(int[][] map, int startR, int startC) {
		if (startR == M - 1 && startC == N - 1) {
			return "Yes";
		}
		map[startR][startC] = 0;

		for (int i = 0; i < 2; i++) {
			int nr = startR;
			int nc = startC;
			nr += dr[i];
			nc += dc[i];
			if (nr < M && nr >= 0 && nc < N && nc >= 0) {
				if (map[nr][nc] == 1) {
					String result = dfs(map, nr, nc);
					if (result.equals("Yes")) {
						return result;
					}
				}
			}
		}
		return "No";
	}

}
