import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.StringTokenizer;

public class Main {
	static boolean[] visited;
	static int[] order;
	static int cnt = 1;

	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringTokenizer st = new StringTokenizer(br.readLine(), " ");

		int N = Integer.parseInt(st.nextToken()); // 정점의 수
		int M = Integer.parseInt(st.nextToken()); // 간선의 수
		int R = Integer.parseInt(st.nextToken()); // 시작 정점

		List<List<Integer>> adj = new ArrayList<>();
		for (int i = 0; i <= N; i++) {
			adj.add(new ArrayList<>());
		}

		for (int i = 0; i < M; i++) {
			st = new StringTokenizer(br.readLine(), " ");
			int u = Integer.parseInt(st.nextToken());
			int v = Integer.parseInt(st.nextToken());

			adj.get(u).add(v);
			adj.get(v).add(u);
		}

		// 인접 정점 오름차순 정렬
		for (int i = 1; i <= N; i++) {
			Collections.sort(adj.get(i));
		}

		visited = new boolean[N + 1];
		order = new int[N + 1];

		dfs(adj, R);

		for (int i = 1; i <= N; i++) {
			System.out.println(order[i]);
		}

	} // main

	private static void dfs(List<List<Integer>> adj, int R) {
		visited[R] = true;
		order[R] = cnt++;

		for (int i = adj.get(R).size() - 1; i >= 0; i--) {
			int V = adj.get(R).get(i);
			if (!visited[V]) {
				dfs(adj, V);
			}
		}
	}

}
