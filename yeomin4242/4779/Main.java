import java.util.*;
import java.io.*;

/*

프랙탈 느낌
입력값 N을 받음, N == 0이면 -하나 반환
나머지 는 pow(3, N) 해서 문자열 개수 정함

3^N 을 3^(N - 1) 단위로 나눔 그럼 총 3개 씩 나옴
이걸 재귀적으로 반복

그래서 N이 0과 같으면 탈출
*/

public class Main{

    public static void divide(char[] arr, int input) {
        if (input != 0) {
            int N = 0;
            while (Math.pow(3, input - 1) + N <= arr.length) {
                for (int i = (int)(Math.pow(3, input - 1) + N) ; i < (int)Math.pow(3, input) - (int)Math.pow(3, input - 1) + N; i++) {
                    arr[i] = ' ';
                }
                N += Math.pow(3, input); 
            }
            divide(arr, input - 1);
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        StringBuilder sb = new StringBuilder();

        String input = "";

        while((input = br.readLine()) != null) {
            int num = Integer.parseInt(input);
            if (num == 0) {
                sb.append("-" + "\n");
            } else {
                int size = (int)Math.pow(3, num);

                char[] arr = new char[size];

                for (int i = 0 ; i < size ; i++) {
                    arr[i] = '-';
                }

                divide(arr, num);
                sb.append(String.valueOf(arr) + "\n");
            }
        }
        System.out.print(sb);
    }  
}