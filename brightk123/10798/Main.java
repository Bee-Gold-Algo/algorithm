import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		
		Scanner sc = new Scanner(System.in);
		
		String[][] arr1 = new String[5][15];
		
		for(int i = 0; i<5; i++) {
			String letters = sc.nextLine();
			String[] letter = letters.split("");
//			System.out.println(Arrays.toString(letter));
			
			for(int j = 0; j<letter.length; j++) {
				arr1[i][j] = letter[j];
			}
		}
		
//		System.out.println(Arrays.deepToString(arr1));
		
		for(int j = 0; j<15; j++){
			for(int i = 0; i<5; i++) {
				if(arr1[i][j] != null) {
					System.out.print(arr1[i][j]);
				}else {
					continue;
				}
			}
		}
		
	}
}
