import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		
		Scanner sc = new Scanner(System.in);
		
		int num = sc.nextInt();
		
		
		while(num != (-1)) {
			
			System.out.print(num);

			List<String> divisors = new ArrayList<>();
			
			int divisor = 0;
			//약수 구해서 리스트에 입력
			for(int i = num; i>1; i--) {
				if(num%i==0) {
					divisor = num/i;
					divisors.add(String.valueOf(divisor));
				}
			}
//			System.out.println(divisors);
			
			//완전수 계산을 위해 리스트 -> 정수형 변환
			int[] intDivisors = new int[divisors.size()];
			int sum = 0;
			
			for(int i = 0; i<divisors.size(); i++) {
				intDivisors[i] = Integer.parseInt(divisors.get(i));
				sum = sum + intDivisors[i];
//				System.out.print(sum);
			}
			
			// 완전수 여부에 따른 출력 형식
			if(sum==num && num!=(-1)) {
				System.out.print(" = ");
				for(int i = 0; i<intDivisors.length-1; i++) {
					System.out.print(intDivisors[i] + " + ");
				}
				System.out.println(intDivisors[intDivisors.length-1]);
			}else if(sum!=num && num!=(-1)) {
				System.out.println(" is NOT perfect.");
			}
			
			if(sc.hasNextInt()) {
				num = sc.nextInt();
			} else {
				break;
			}
			
			
		}
		
	}
}
