import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int num = sc.nextInt();
		int sum = 0;
		int tmp = num;

		while (num != 0) {
			sum += (int) (Math.pow(num % 10, 5));
			num /= 10;
		}
		System.out.println(sum);

	}
}