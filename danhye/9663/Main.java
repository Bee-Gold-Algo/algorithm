import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
	static int N;
	static int[] board;
	static int ans;
	
	public static void dfs(int depth) {
		//종료 조건
		if(depth == N) {
			ans++; 
			return;
		}
		
		for (int i = 0; i < N; i++) {
			board[depth] = i;
			if(!possible(depth)) continue;
			else dfs(depth+1);
		}
	}
	
	public static boolean possible(int depth) {
		//board[depth] = i가 가능한 지 확인하는 메서드
		for (int i = 0; i < depth; i++) {
			//직선 체크
			if(board[i] == board[depth]) return false;
			//대각선 체크
			else if(Math.abs(depth - i) == Math.abs(board[depth] - board[i])) return false;
		} // for문 끝
		
		return true;
	}

	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		N = Integer.parseInt(br.readLine());
		board = new int[N]; 
		
		ans = 0;
		dfs(0);
		
		System.out.println(ans);
		
	}
}
