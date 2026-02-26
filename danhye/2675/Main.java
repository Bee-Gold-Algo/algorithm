import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int T = Integer.parseInt(br.readLine());
		for (int tc = 0; tc < T; tc++) {
			String[] input = br.readLine().split(" ");
			int num = Integer.parseInt(input[0]);
			String text = input[1];
			
			StringBuilder sb = new StringBuilder();
			for (int i = 0; i < text.length(); i++) {
				char ch = text.charAt(i);
				
				for (int j = 0; j < num; j++) {
					sb.append(ch);
				}
			}
			
			System.out.println(sb);
		}
	}
}
