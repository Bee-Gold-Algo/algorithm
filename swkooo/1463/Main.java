import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

//1로 만들기
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());
		
		int[] answer = new int[1000001];	// 10의 6승 미만이라고 했으므로 일단 최대한 큰 배열 생성
		
		// 기본값 넣어놓기
		answer[1] = 0;
		answer[2] = 1;
		answer[3] = 1;
		
		// 그 다음부턴 값을 저장해놓고 -1 한것, (가능하면) /3 한것, /2 한것 의 값을 비교해 최솟값 찾기
		for (int i = 4; i <= N; i++) {
			int check = answer[i-1] + 1;
			
			if (i % 3 == 0) {
				check = Math.min(check, (answer[i / 3] + 1));
			}
			if (i % 2 == 0) {
				check = Math.min(check, (answer[i / 2] + 1));
			}
			answer[i] = check;
		}
		
		// 출력
		System.out.println(answer[N]);
		
	}// main
}
