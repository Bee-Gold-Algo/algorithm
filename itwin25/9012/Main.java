import java.util.Scanner;
import java.util.Stack;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int T = sc.nextInt();
		sc.nextLine();

		for (int tc = 1; tc <= T; tc++) {
			String s = sc.nextLine();
			Stack<Character> st = new Stack<>();
			String ans = "YES";

			for (int i = 0; i < s.length(); i++) {
				if (s.charAt(i) == '(') {
					st.push(s.charAt(i));
				} else {
					if (st.isEmpty()) {
						ans = "NO";
					} else {
						st.pop();
					}
				}
			}
			if (!st.isEmpty()) {
				ans = "NO";
			}

			System.out.println(ans);

		}
	} // main
}
