import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

//스위치 켜고 끄기
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringBuilder sb = new StringBuilder();

		int switchN = Integer.parseInt(br.readLine());

		// 스위치 서로 변환
		Map<String, String> swap = new HashMap<>();
		swap.put("0", "1");
		swap.put("1", "0");

		String[] status = br.readLine().split(" ");

		int studentN = Integer.parseInt(br.readLine());

		for (int i = 0; i < studentN; i++) {
			String[] student = br.readLine().split(" ");

			int switchNum = Integer.parseInt(student[1]);
			// 남학생이라면 받은 수의 배수인 스위치 변환
			if (student[0].equals("1")) {
				for (int j = switchNum; j <= switchN; j += switchNum) {
					// swap을 이용해 0 <-> 1 변환
					status[j - 1] = swap.get(status[j - 1]); // 인덱스는 -1 해줘야함
				}
			}

			// 여학생이라면..
			else {
				// 일단 자기 변환
				status[switchNum - 1] = swap.get(status[switchNum - 1]); // 위랑 같은 이유로 -1

				// 스위치 번호가 양 끝을 벗어나지 않는 동안
				int move = 1;
				while (switchNum - move >= 1 && switchNum + move <= switchN) {
					// 좌우가 같다면... 변환
					if (status[switchNum - move - 1].equals(status[switchNum + move - 1])) {
						status[switchNum - move - 1] = swap.get(status[switchNum - move - 1]);
						status[switchNum + move - 1] = swap.get(status[switchNum + move - 1]);
					}
					// 다르면 탈출!
					else
						break;
					move++;
				} // 여학생반복문
			}
		} // 스위치변환for문

		// 출력
		for (int i = 0; i < switchN; i++) {
			// 20번째라면 개행
			if (i % 20 == 19)
				sb.append(status[i] + "\n");
			// 아니면 그냥 한칸 띄우기
			else 
				sb.append(status[i] + " ");
		}
		System.out.println(sb);
	}// main
}
