import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

//빙고
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		// map에 주어지는 숫자의 좌표값을 int[]로 저장
		Map<Integer, int[]> map = new HashMap<>();

		for (int i = 0; i < 5; i++) {
			String[] line = br.readLine().split(" ");
			for (int j = 0; j < 5; j++) {
				int[] coord = { i, j };
				map.put(Integer.parseInt(line[j]), coord);
			}
		}
		
		//빙고확인할 배열 생성
		int[] bingo = new int[12]; // 0~4까지는 가로빙고, 5~9까지는 세로빙고, 10~11은 대각선 빙고
		
		int bingoCheck = 0;	// 사회자가 부르는 수의 개수
		int bingoCnt = 0;	// 빙고 만들어진 개수
		for (int i = 0; i < 5; i++) {
			String[] line = br.readLine().split(" ");
			for (int j = 0; j < 5; j++) {
				bingoCheck++;	// 숫자 하나 부를때마다 증가
				int[] coord = map.get(Integer.parseInt(line[j]));	// 사회자가 부른 숫자의 좌표값 가져오기

				int rowNum = coord[0];
				int colNum = coord[1];

				bingo[rowNum]++;			//빙고배열에 해당되는 가로빙고 증가
				bingo[colNum + 5]++;		//빙고배열에 해당되는 세로빙고 증가
				
				if (rowNum == colNum) {		//   \로 내려가는 대각선 빙고
					bingo[10]++;
				}
				if (rowNum + colNum == 4) {	//   /로 내려가는 대각선 빙고
					bingo[11]++;
				}
				
				// 빙고 몇개 만들어졌는지 체크
				bingoCnt = 0;
				for (int cnt : bingo) {
					if (cnt == 5) 
						bingoCnt++;
				}
				// 3개 이상 만들어졌으면 break
				if (bingoCnt >= 3) 
					break;
			// 3개 이상 만들어졌으면 break	
			}
			if (bingoCnt >= 3) 
				break;
		}
		
		// 출력
		System.out.println(bingoCheck);

	}// main
}
