import java.io.FileInputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) throws IOException {

		Scanner sc = new Scanner(System.in);

		int kilo = sc.nextInt();
		int count = -1;
		
		for(int i=kilo/5; i>=0; i--) {
			int rest = kilo - (i*5);
			if(rest%3==0) {
				count = i+ rest/3;
				break;
			}
		}
		
		System.out.println(count);
	}
}