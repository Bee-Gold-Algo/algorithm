import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.LinkedList;
import java.util.List;

//유기농 배추
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringBuilder sb = new StringBuilder();

		int T = Integer.parseInt(br.readLine());

		for (int tc = 1; tc <= T; tc++) {
			String[] MNK = br.readLine().split(" ");
			int M = Integer.parseInt(MNK[0]);
			int N = Integer.parseInt(MNK[1]);
			int K = Integer.parseInt(MNK[2]);

			// 배추밭 배열 만들기
			int[][] farm = new int[N][M];
			for (int k = 0; k < K; k++) {
				String[] line = br.readLine().split(" ");
				farm[Integer.parseInt(line[1])][Integer.parseInt(line[0])] = 1;
			}

			// 델타 탐색 상하좌우
			int[] dr = { -1, 1, 0, 0 };
			int[] dc = { 0, 0, -1, 1 };

			// 연결된 배추밭 좌표 저장할 list
			List<String> check = new LinkedList<>();

			// 연결된 좌표들의 개수
			int cnt = 0;

			// 일단 배추밭 전체를 탐색하는데..
			for (int i = 0; i < N; i++) {
				for (int j = 0; j < M; j++) {

					// 만약 1이 탐색되면
					if (farm[i][j] == 1) {
						// 좌표를 문자열화하여 list에 넣는다.
						String temp = i + " " + j;
						check.add(temp);
						farm[i][j] = 0; // 그 배추는 0으로 없앤다.

						// 배추밭 좌표 list를 도는데...
						for (int cb = 0; cb < check.size(); cb++) {
							// 문자열화 한 좌표를 일단 숫자로 가져오고
							String[] tempArr = check.get(cb).split(" ");
							int y = Integer.parseInt(tempArr[0]);
							int x = Integer.parseInt(tempArr[1]);

							// 델타탐색 실시
							for (int d = 0; d < 4; d++) {
								int yCheck = y + dr[d];
								int xCheck = x + dc[d];
								if (yCheck >= 0 && yCheck < N && xCheck >= 0 && xCheck < M) { // 바운더리 지정
									// 델타탐색한 결과 1이라면.. 즉 인접한 배추가 있다면
									if (farm[yCheck][xCheck] == 1) {
										// 문자열화 하여 list에 넣는다.
										temp = yCheck + " " + xCheck;
										check.add(temp);
										farm[yCheck][xCheck] = 0; // 역시 그 배추는 0으로 없앤다.
									}
								}
							}
						}
						// 중간다리 역활을 하는 배추를 없애더라도 list에 있으므로 계속 확인 가능!
						// 연결된 배추를 전부 없앴다면 cnt 증가.
						cnt++;
					}
				} // 하나 탐색 끝
			}
			// 출력
			sb.append(cnt + "\n");
		} // tc
		System.out.println(sb);
	}// main
}
