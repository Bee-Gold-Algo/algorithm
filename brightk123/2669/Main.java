import java.io.FileInputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) throws IOException {

		Scanner sc = new Scanner(System.in);

		int sum = 0;

		boolean[][] square = new boolean[100][100];

		for (int i = 0; i < 4; i++) {

			int xl = sc.nextInt();
			int yl = sc.nextInt();
			int xr = sc.nextInt();
			int yr = sc.nextInt();

			for (int k = xl; k < xr; k++) {
				for (int l = yl; l < yr; l++) {
					square[l][k] = true;
				}
			}
		}

		int ans = 0;

		for (int i = 0; i < 100; i++) {
			for (int j = 0; j < 100; j++) {
				if (square[i][j]) {
					ans++;
				}
			}
		}

		System.out.println(ans);

	}
}