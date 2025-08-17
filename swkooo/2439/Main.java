import java.util.Scanner;

public interface Main {
	public static void main(String[] args) {
		//백준 별 찍기 - 2
		Scanner sc = new Scanner(System.in);
		int N = sc.nextInt();
		
		// n만큼 i의 값을 반복
		for(int i = 1; i <= N; i++) {
			// 공백의 갯수 N-i번 출력
			for(int j = 0; j < N - i; j++) {
				System.out.print(" ");
			}
			// 별의 갯수 i번 출력
			for(int j = 0; j < i; j++) {
				System.out.print("*");
			}
			// 개행
			System.out.println();
		}
	}	
}
