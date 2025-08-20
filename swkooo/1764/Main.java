import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

//듣보잡
public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringBuilder sb = new StringBuilder();

		String[] NM = br.readLine().split(" ");
		int N = Integer.parseInt(NM[0]);
		int M = Integer.parseInt(NM[1]);

		// 먼저 set으로 중복체크
		Set<String> noHear = new HashSet<>();
		// 중복이 아니면 듣보잡 리스트에 넣기
		List<String> noLookHear = new LinkedList<>();

		// 먼저 듣잡 set넣기
		for (int i = 0; i < N; i++) {
			noHear.add(br.readLine());
		}

		// 듣잡에 일단 넣어봐
		for (int i = 0; i < M; i++) {
			int preSize = noHear.size();
			String check = br.readLine();
			noHear.add(check);

			// set 사이즈 변화가 없으면 듣보잡리스트에 넣기
			if (noHear.size() == preSize) {
				noLookHear.add(check);
			}
		}
		
		//정렬
		Collections.sort(noLookHear);

		// 출력
		sb.append(noLookHear.size() + "\n");
		for (String str : noLookHear) {
			sb.append(str + "\n");
		}
		System.out.println(sb);

	}// main
}
