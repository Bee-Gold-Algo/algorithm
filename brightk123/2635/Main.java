import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) throws IOException {

		Scanner sc = new Scanner(System.in);

		int num = sc.nextInt();
		int maxCountcal = 0;
		List<Integer> result = new ArrayList<>();
		
		
		for(int i = num; i>0; i--) {
			numbers.add(num);
			numbers.add(i);
			cal(num,i);
			
			if(countCal > maxCountcal) {
				maxCountcal = countCal;
				result.clear();
				for(int k = 0; k<numbers.size(); k++) {
					result.add(numbers.get(k));
				}
				
			}
			countCal = 0;
			numbers.clear();
		}
		
		System.out.println(maxCountcal+2);
		for(int i = 0; i<result.size()-1; i++) {
			System.out.print(result.get(i)+" ");
		}
		System.out.println(result.get(result.size()-1));
		
	}
	
	public static int countCal = 0;
	public static List<Integer> numbers = new ArrayList<>();
	
	public static int cal (int num1, int num2) {
		if(num2>num1) {
			return -1;
		}
		int ans = num1 - num2;
		numbers.add(ans);
		countCal++;
		
		return cal(num2, ans);
	}
}