import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

public class Main {
	static boolean[] visited;
	static int cnt = 0;

	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

		int N = Integer.parseInt(br.readLine()); // 컴퓨터의 수
		int M = Integer.parseInt(br.readLine()); // 연결되어 있는 컴퓨터의 번호 쌍

		List<List<Integer>> adj = new ArrayList<>();
		for (int i = 0; i <= N; i++) {
			adj.add(new ArrayList<>());
		}

		for (int i = 0; i < M; i++) {
			StringTokenizer st = new StringTokenizer(br.readLine(), " ");
			int u = Integer.parseInt(st.nextToken());
			int v = Integer.parseInt(st.nextToken());

			adj.get(u).add(v);
			adj.get(v).add(u);
		}

		visited = new boolean[N + 1];

		dfs(adj, 1);
		System.out.println(cnt);

	} // main

	private static void dfs(List<List<Integer>> adj, int R) {
		visited[R] = true;

		for (int c : adj.get(R)) {
			if (!visited[c]) {
				cnt++;
				dfs(adj, c);
			}
		}
	}

}
