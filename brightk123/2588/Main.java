import java.util.Arrays;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		
		Scanner sc = new Scanner(System.in);
		
		int numA = sc.nextInt();
		int numB = sc.nextInt();
		
		int firstNum = numA*(numB%10);
		int seconNum = numA*((numB%100)/10);
		int thirdNum = numA*(numB/100);
		int fourthNum = firstNum+seconNum*10+thirdNum*100;
		
		System.out.println(firstNum);
		System.out.println(seconNum);
		System.out.println(thirdNum);
		System.out.println(fourthNum);
		
		
		
		
	}
}
