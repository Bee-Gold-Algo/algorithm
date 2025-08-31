import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
	static int[][] arr;
	static boolean[] visited;
	static int node, line;
	static int res = 0;
	
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		node = Integer.parseInt(br.readLine());
		line = Integer.parseInt(br.readLine());
		
		arr = new int[node+1][node+1];
		visited = new boolean[node+1];
		
		for (int i = 0; i < line; i++) {
			String[] input = br.readLine().split(" ");
			
			int a = Integer.parseInt(input[0]);
			int b = Integer.parseInt(input[1]);
			
			arr[a][b] = arr[b][a] = 1;
		}
		
		dfs(1);
		
		System.out.println(res-1);
	}

	private static void dfs(int start) {
		
		visited[start] = true;
		res++;
		
		for (int i = 1; i <= node; i++) {
			if(arr[start][i] == 1 && !visited[i])
				dfs(i);
		}
		
	}
}
