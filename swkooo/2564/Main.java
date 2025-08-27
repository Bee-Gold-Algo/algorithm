import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

// 경비원
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		String[] WH = br.readLine().split(" ");

		int width = Integer.parseInt(WH[0]);
		int height = Integer.parseInt(WH[1]);

		int N = Integer.parseInt(br.readLine());

		int[][] store = new int[N][2]; // [0]은 방향, [1]은 떨어진 거리

		for (int i = 0; i < N; i++) {
			String[] line = br.readLine().split(" ");
			store[i][0] = Integer.parseInt(line[0]);
			store[i][1] = Integer.parseInt(line[1]);
		}

		String[] xLoc = br.readLine().split(" ");
		int xWay = Integer.parseInt(xLoc[0]);
		int xDist = Integer.parseInt(xLoc[1]);

		int minDIstance = 0;
		for (int i = 0; i < N; i++) {
			if (store[i][0] == xWay) { // 동근이랑 같은 방향에 위치한다면
				minDIstance += Math.abs(xDist - store[i][1]); // 뺀 값의 절대값
			}
			if (xWay == 1) { // 동근이가 북쪽에 있다면
				switch (store[i][0]) {
				case 2:
					int minA = height + (xDist + store[i][1]);
					int minB = height + width * 2 - (xDist + store[i][1]);
					minDIstance += Math.min(minA, minB);
					break;
				case 3:
					minDIstance += xDist + store[i][1];
					break;
				case 4:
					minDIstance += (width - xDist) + store[i][1];
					break;
				} 
			}
			if (xWay == 2) { // 동근이가 남쪽에 있다면
				switch (store[i][0]) {
				case 1:
					int minA = height + (xDist + store[i][1]);
					int minB = height + width * 2 - (xDist + store[i][1]);
					minDIstance += Math.min(minA, minB);
					break;
				case 3:
					minDIstance += xDist + (height - store[i][1]);
					break;
				case 4:
					minDIstance += (width - xDist) + (height - store[i][1]);
					break;
				} 
			}
			if (xWay == 3) { // 동근이가 서쪽에 있다면
				switch (store[i][0]) {
				case 1:
					minDIstance += xDist + store[i][1];
					break;
				case 2:
					minDIstance += (height - xDist) + store[i][1];
					break;
				case 4:
					int minA = width + (xDist + store[i][1]);
					int minB = width + height * 2 - (xDist + store[i][1]);
					minDIstance += Math.min(minA, minB);
					break;
				} 
			}
			if (xWay == 4) { // 동근이가 동쪽에 있다면
				switch (store[i][0]) {
				case 1:
					minDIstance += xDist + (width - store[i][1]);
					break;
				case 2:
					minDIstance += (height - xDist) + (width - store[i][1]);
					break;
				case 3:
					int minA = width + (xDist + store[i][1]);
					int minB = width + height * 2 - (xDist + store[i][1]);
					minDIstance += Math.min(minA, minB);
					break;
				} 
			}
		}
		System.out.println(minDIstance);

	}// main
}
