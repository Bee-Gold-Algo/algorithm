import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int num = sc.nextInt();
		int result = 0;

		for (int i = 1; i < num; i++) {
			if (i + sum(i) == num) {
				result = i;
				break;
			}
		}
		System.out.println(result);

	}

	// 각 자리수의 값
	public static int sum(int num) {
		int tmp = 0;
		while (num > 0) {
			tmp += num % 10;
			num /= 10;
		}
		return tmp;
	}
}