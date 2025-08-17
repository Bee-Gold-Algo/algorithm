import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {

		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());

		int[] number = new int[N];

		for (int h = 0; h < N; h++) {
			int v = Integer.parseInt(br.readLine());
			number[h] = v;
				
			}
	
		Arrays.sort(number);
		
		StringBuilder sb = new StringBuilder();
		
		for (int i = 0; i < N; i++) {
			sb.append(number[i]).append("\n");
		}

		System.out.println(sb);
	}

}
