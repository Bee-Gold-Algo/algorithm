import java.io.FileInputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) throws IOException {

		System.setIn(new FileInputStream("input.txt"));
		Scanner sc = new Scanner(System.in);
		
		int TC = sc.nextInt();
		
		String[][] data = new String[TC][2];
		
		sc.nextLine();
		
		for(int h = 0; h<TC; h++) {
			data[h]=sc.nextLine().split(" ");
		}
		
		// 나이별로 정렬
		Arrays.sort(data, new Comparator<String[]>() {

		    @Override
		    public int compare(String[] o1, String[] o2) {
		        return Integer.parseInt(o1[0]) - Integer.parseInt(o2[0]);
		    }

		});
		
		for(int i = 0; i<TC; i++) {
			System.out.print(data[i][0]+" ");
			System.out.println(data[i][1]);
		}
		
	}
}