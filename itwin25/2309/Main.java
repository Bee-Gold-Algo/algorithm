import java.util.ArrayList;
import java.util.Comparator;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		ArrayList<Integer> list = new ArrayList<>(); // 난쟁이 담을 곳
		int sum = 0; // 모든 난쟁이들의 키

		for (int i = 0; i < 9; i++) {
			list.add(sc.nextInt());
			sum += list.get(i);
		}

		sum -= 100;
		// 100을 뺀 나머지랑 같으면 제거
		loop1: for (int i = 0; i < 8; i++) {
			for (int j = i + 1; j < 9; j++) {
				if (list.get(i) + list.get(j) == sum) {
					list.remove(j);
					list.remove(i);
					break loop1;
				}
			}
		}

		list.sort(Comparator.naturalOrder());

		for (int n : list) {
			System.out.println(n);
		}
	}
}