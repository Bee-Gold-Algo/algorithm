import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayDeque;

//수열
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		String[] NK = br.readLine().split(" ");
		int N = Integer.parseInt(NK[0]);
		int K = Integer.parseInt(NK[1]);

		String[] line = br.readLine().split(" ");

		// 숫자 담을 queue생성
		ArrayDeque<Integer> arrDeq = new ArrayDeque<>();

		// 앞에서부터 K개의 수를 담은 queue 만들기
		int sumMax = 0;
		for (int i = 0; i < K; i++) {
			int firstNum = Integer.parseInt(line[i]);
			arrDeq.offer(firstNum);
			sumMax += firstNum; // 초기 queue의 합 저장
		}

		int sum = sumMax; // max값과 비교하기위한 sum 변수
		// K인덱스부터 끝까지
		for (int i = K; i < N; i++) {
			// 숫자 하나 받을 때마다 맨 앞의 숫자 빼기
			int pollNum = arrDeq.poll();
			int pushNum = Integer.parseInt(line[i]);
			arrDeq.addLast(pushNum);

			// 합계도 마찬가지로 나가는 숫자 빼고 들어오는 숫자 더해서 갱신
			sum = sum - pollNum + pushNum;

			// max값 갱신
			sumMax = Math.max(sumMax, sum);
		}

		// 출력
		System.out.println(sumMax);
	}// main
}
