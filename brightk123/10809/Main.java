import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) throws FileNotFoundException {
	
		Scanner sc = new Scanner(System.in);
		
		String word = sc.next();
		
		int[] numbers = new int[26];
		for(int i = 0; i<numbers.length; i++) {
			numbers[i] = -1;
		}
		
		for(int i = 0; i<word.length(); i++) {
			char ch = word.charAt(i);
			int index = ch - 'a';
			
			if(numbers[index] == -1) {
				numbers[index] = i;
			}
			
		}
		
		for(int i = 0; i<numbers.length-1; i++) {
			System.out.print(numbers[i] + " ");
		}
		System.out.println(numbers[numbers.length-1]);
	}
}
