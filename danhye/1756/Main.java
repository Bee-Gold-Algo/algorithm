import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
	
	static int d, n;
	static int[] oven, pizza;
	
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringTokenizer st = new StringTokenizer(br.readLine());
		
		d = Integer.parseInt(st.nextToken()); //오븐의 깊이
		n = Integer.parseInt(st.nextToken()); //피자 반죽의 개수
		
		oven = new int[d+1];
		
		st = new StringTokenizer(br.readLine());
		oven[1] = Integer.parseInt(st.nextToken());
		for (int i = 2; i < d + 1; i++) {
			int a = Integer.parseInt(st.nextToken());
			oven[i] = Math.min(a, oven[i-1]);
		}
		
		
		pizza = new int[n];
		st = new StringTokenizer(br.readLine());
		for (int i = 0; i < n; i++) {
			pizza[i] = Integer.parseInt(st.nextToken());
		}

		int pos = d; //현재 가능한 가장 깊은 깊이
		for (int i = 0; i < n; i++) {
			int p = pizza[i];
			while(pos >= 1 && oven[pos] < p) pos--; //안들어가면 올라와
			if(pos == 0) {
				System.out.println(0);
				return;
			}
			//오븐에 들어가면?
			pos--; //다음피자는 한 칸 위부터
		}
		System.out.println(pos + 1);
	}
}
