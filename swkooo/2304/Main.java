import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

//창고 다각형
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());

		int[] storage = new int[1001];
		int maxHieght = 0;
		for (int i = 0; i < N; i++) {
			String[] LH = br.readLine().split(" ");

			int L = Integer.parseInt(LH[0]);
			int H = Integer.parseInt(LH[1]);

			storage[L] = H;

			maxHieght = Math.max(maxHieght, H);

		}

		// 넓이 합
		int rangeSum = 0;
		// 첫 기준좌표 및 높이 설정
		int startIdx = 0;
		int currHeight = 0;
		//앞에서부터 탐색...
		for (int i = 0; i < 1001; i++) {
			// 가장 높은 위치의 좌표까지 반복
			if (currHeight == maxHieght)
				break;
			// 기준 높이보다 탐색하는 좌표 높이가 높다면
			if (currHeight < storage[i]) {
				// 기준좌표~탐색좌표 * 기준 높이
				rangeSum += (i - startIdx) * currHeight;

				// 기준 좌표 갱신
				startIdx = i;
				currHeight = storage[i];
			}
		}
		
		int endIdx = 0;	//기준좌표 및 높이 뒤에서부터 다시 설정
		currHeight = 0;
		//뒤에서부터 똑같은 방식으로 탐색
		for (int i = 1000; i >= 0; i--) {
			// 가장 높은 위치의 좌표까지 반복
			if (currHeight == maxHieght)
				break;
			// 기준 높이보다 탐색하는 좌표 높이가 높다면
			if (currHeight < storage[i]) {
				// 기준좌표~탐색좌표 * 기준 높이
				rangeSum += (endIdx - i) * currHeight;

				// 기준 좌표 갱신
				endIdx = i;
				currHeight = storage[i];
			}
		}
		
		//가장 높은 높이가 여러개 있을 경우 생각
		rangeSum += (endIdx - startIdx + 1) * maxHieght;
		
		//출력
		System.out.println(rangeSum);
		
	}// main
}
