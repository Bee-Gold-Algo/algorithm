import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		// 입출력시 BufferedRedaer과 StringBuilder 사용으로 시간 단축
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());
		
		int[] count = new int[10001];
		
		for(int h = 0; h<N; h++) {
			int v = Integer.parseInt(br.readLine());
			count[v]++;
		}
		
		StringBuilder sb = new StringBuilder();
		for(int i = 1; i<=10000; i++) {
			while(count[i]>0) {
				sb.append(i).append("\n");
				count[i]--;
				
			}
		}
		
		System.out.println(sb);
		
	}
}
