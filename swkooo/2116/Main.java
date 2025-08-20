import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

//주사위 쌓기
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());

		// 주사위의 마주보는 인덱스
		Map<Integer, Integer> idxSwap = new HashMap<>();
		idxSwap.put(0, 5);
		idxSwap.put(1, 3);
		idxSwap.put(2, 4);
		idxSwap.put(3, 1);
		idxSwap.put(4, 2);
		idxSwap.put(5, 0);

		int[][] diceArr = new int[N][6];

		// 주사위 배열 입력받기
		for (int i = 0; i < N; i++) {
			String[] line = br.readLine().split(" ");
			for (int j = 0; j < 6; j++) {
				diceArr[i][j] = Integer.parseInt(line[j]);
			}
		}
		
		int[] diceNumArr = {6, 5, 4, 3, 2, 1};
		
		int maxSum = 0;	// 최종 최댓값
		for (int j = 0; j < 6; j++) {
			
			int sum = 0; // 다이스 옆면 눈 최댓값 합 저장
			
			int checkNum = diceArr[0][j];
			int swapNum = diceArr[0][idxSwap.get(j)];
			
			// 첫번째 주사위 중 옆면 가장 큰 수 탐색
			for (int dn : diceNumArr) {
				//내림차순정렬한 6~1로 탐색하는 중 checkNum + swapNum 과 다르면 그게 남은 수 중 가장 큼
				if (dn != checkNum && dn != swapNum) {
					sum += dn;
					break;
				}
			}
			// 밑으로 한칸씩 내려가면서 위아래 연결된 면 탐색
			for (int i = 1; i < N; i++) {
				//체크할 숫자를 위의 행 swapNum으로 변경
				checkNum = swapNum;
				//checkNum의 인덱스 확인
				int idx = 0;
				for (int k = 0; k < 6; k++) {
					if (diceArr[i][k] == checkNum) {
						idx = k;
						break;
					}
				}
				//변경된 checkNum의 인덱스로 swapNum 확인
				swapNum = diceArr[i][idxSwap.get(idx)];
				// 같은 방식으로 옆면 가장 큰 수 탐색
				for (int dn : diceNumArr) {
					if (dn != checkNum && dn != swapNum) {
						sum += dn;
						break;
					}
				}
			}
			//하나 탐색 끝나면 max값 갱신
			maxSum = Math.max(maxSum, sum);
			
		}
		//출력
		System.out.println(maxSum);

	}// main
}
