import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		int width = sc.nextInt(); // 종이의 가로 길이
		int height = sc.nextInt(); // 종이의 세로 길이
		int N = sc.nextInt(); // 칼로 자를 점선의 개수
		List<Integer> wCut = new ArrayList<>(); // 가로로 자르는 점선 정보
		List<Integer> hCut = new ArrayList<>(); // 세로로 자르는 점선 정보

		wCut.add(0);
		hCut.add(0);

		for (int i = 0; i < N; i++) {
			int tmp = sc.nextInt();
			if (tmp == 0) {
				wCut.add(sc.nextInt());
			} else {
				hCut.add(sc.nextInt());
			}
		}

		wCut.add(height);
		hCut.add(width);

		// 정렬
		Collections.sort(wCut);
		Collections.sort(hCut);

		int maxW = 0;
		int maxH = 0;

		// 가장 긴 세로 길이 구하기
		for (int i = 1; i < wCut.size(); i++) {
			maxH = Math.max(maxH, wCut.get(i) - wCut.get(i - 1));
		}

		// 가장 긴 가로 길이 구하기
		for (int i = 1; i < hCut.size(); i++) {
			maxW = Math.max(maxW, hCut.get(i) - hCut.get(i - 1));
		}

		System.out.println(maxW * maxH);
	}
}