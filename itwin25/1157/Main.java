import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		String s = sc.nextLine();
		int arr[] = new int[26];
		int max = -1;
		char ans = ' ';

		s = s.toLowerCase();

		for (int i = 0; i < s.length(); i++) {
			arr[s.charAt(i) - 97]++;
		}

		for (int i = 0; i < 26; i++) {
			if (arr[i] > max) {
				max = arr[i];
				ans = (char) (i + 97);
			} else if (arr[i] == max) {
				ans = '?';
			}

		}

		System.out.println(Character.toUpperCase(ans));

	} // main
}
