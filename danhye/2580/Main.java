import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

public class Main {
	static int[][] board;
	static List<int[]> blanks = new ArrayList<>();
	static boolean solved = false;
	
	private static void dfs(int depth) {
		//정답 하나만 출력
		if(solved) return;
		
		//종료
		if(depth == blanks.size()) {
			StringBuilder sb = new StringBuilder();
			for (int i = 0; i < 9; i++) {
				for (int j = 0; j < 9; j++) {
					sb.append(board[i][j]).append(" ");
				}
				sb.append("\n");
			}
			System.out.println(sb);
			solved = true;
			return;
		}
		
		int r = blanks.get(depth)[0];
		int c = blanks.get(depth)[1];
		
		for (int n = 1; n <= 9; n++) {
			if(isValid(r, c, n)) { //들어갈 수 있는 숫자이면
				board[r][c] = n;
				dfs(depth + 1);
				board[r][c] = 0;
			}
		}
	}

	private static boolean isValid(int r, int c, int n) {
		//열 체크
		for (int i = 0; i < 9; i++) {
			if(board[r][i] == n) return false;
		}
		//행 체크
		for (int i = 0; i < 9; i++) {
			if(board[i][c] == n) return false;
		}
		
		//3x3 체크
		int sr = (r/3) * 3, sc = (c/3) * 3;
		for (int i = sr; i < sr + 3; i++) {
			for (int j = sc; j < sc + 3; j++) {
				if(board[i][j] == n) return false;
			}
		}
		return true;
	}

	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		board = new int[9][9];
		
		for (int i = 0; i < 9; i++) {
			StringTokenizer st = new StringTokenizer(br.readLine(), " ");
			for (int j = 0; j < 9; j++) {
				board[i][j] = Integer.parseInt(st.nextToken());
				//0인 좌표 저장해두기
				if(board[i][j] == 0) blanks.add(new int[] {i,j});
			}
		} //입력 받기 끝
		
		dfs(0);
	}
}
