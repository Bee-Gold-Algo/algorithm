import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) throws FileNotFoundException {
		Scanner sc = new Scanner(System.in);
		
		int num = sc.nextInt();
		int ans = 665;
		
		int count = 0;
		
		
		while(count<num) {
			ans = ans + 1;
			
			if(String.valueOf(ans).contains("666")) {
				count++;
			}
			
		}
		System.out.println(ans);
		
	}
}
