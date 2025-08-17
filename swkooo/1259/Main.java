import java.util.Scanner;

//팰린드롬수
public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		
		while(true) {
			String num = sc.nextLine();
			if (num.equals("0")) {
				break;
			}
			char [] numArr = num.toCharArray();
			int leng = numArr.length;
			boolean isPall = true;
			for (int i = 0; i < leng / 2; i++) {
				if (numArr[i] != numArr[leng - 1 - i]) {
					isPall = false;
					break;
				}
			}
			
			if (isPall) {
				System.out.println("yes");
			}
			else {
				System.out.println("no");
			}
		}
	}//main
}
