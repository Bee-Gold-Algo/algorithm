import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		int T = Integer.parseInt(br.readLine());
		for (int tc = 0; tc < T; tc++) {
			//1센트, 1달러 = 100센트
			int c = Integer.parseInt(br.readLine());
			
			//쿼터($0.25), 다임($0.10), 니켈($0.05), 페니($0.01)
			int q = 0, d = 0, n = 0, p = 0;
						
			if(c / 25 > 0) {
				q = c / 25;
				c -= q * 25;
			}
			if(c / 10 > 0) {
				d = c / 10;
				c -= d * 10;
			}
			if(c / 5 > 0) {
				n = c / 5;
				c -= n * 5;
			}
			if(c / 1 > 0) {
				p = c / 1;
			}
			
			System.out.println(q + " " + d + " " + n + " " + p);
		}
	}
}
