import java.util.Arrays;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		
		Scanner sc = new Scanner(System.in);
		
		int num = sc.nextInt();
		
		
		for(int i = 0; i<(2*num-1); i++) {
			
			if(i<num) {
				for(int j = 0; j<(i+1); j++) {
					System.out.print("*");
				}
			} else {
				for(int j = 0; j<(2*num-i-1); j++) {
					System.out.print("*");
				}
			}
			
			System.out.println();
		}
	}
}