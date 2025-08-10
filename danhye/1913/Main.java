import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
	//방향구하기 (상, 우상, 우, 우하, 하, 좌하, 좌, 좌상)
	static final int[] dr = {-1, 0, 1, 0};
	static final int[] dc = {0, 1, 0, -1};

	
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());
		int search = Integer.parseInt(br.readLine());
		
		int[][] arr = new int[N][N];
		int r = N / 2;
		int c = N / 2;
		int dir = 0;
		int val = 1;
		arr[r][c] = val;
		
		//찾을 값의 인덱스 저장
		int sr = 0;
		int sc = 0;
		if (val == search) { sr = r+1; sc = c+1; }
		
		
		int step = 1;
		while( val < N * N ) {
			for(int a = 0; a < 2 && val < N*N; a++){
				for (int b = 0; b < step && val < N*N; b++) {
					r += dr[dir];
					c +=  dc[dir];
					arr[r][c] = ++val;
					if(val == search) {sr = r+1;  sc = c+1;}
				}
				dir = (dir + 1) % 4;
			}
			step++;
		}
		
		//출력
		for (int i = 0; i < N; i++) {
			for (int j = 0; j < N; j++) {
				System.out.print(arr[i][j] + " ");
			}
			System.out.println();
		}
		System.out.println(sr + " " + sc);
			
		}
	}

