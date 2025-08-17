import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int T = Integer.parseInt(sc.nextLine());

		for (int tc = 0; tc < T; tc++) {
			String str = sc.nextLine();
			StringBuilder r = new StringBuilder();
			StringBuilder ans = new StringBuilder();

			for (int i = 0; i < str.length(); i++) {
				if (str.charAt(i) == ' ') {
					ans.append(r.reverse() + " ");
					r.setLength(0);
					continue;
				}
				r.append(str.charAt(i));
			}

			System.out.println(ans.append(r.reverse()).toString());
		}
	}
}