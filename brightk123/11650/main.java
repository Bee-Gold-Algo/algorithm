import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.Arrays;
import java.util.Comparator;
import java.util.ArrayList;

public class Main {
	public static void main(String[] args) throws IOException {
		
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		int N = Integer.parseInt(br.readLine());
		
		int[][] arr = new int[N][2];
		
		for(int i = 0; i<N; i++) {
			String line = br.readLine();
			String[] number = line.split(" ");
			arr[i][0] = Integer.parseInt(number[0]);
			arr[i][1] = Integer.parseInt(number[1]);
		}
		
		
		Arrays.sort(arr, new Comparator<int[]>() {

			@Override
			public int compare(int[] a, int[] b) {
				if(a[0]!=b[0]) {
					return a[0] - b[0]; // 0번째 열 기준 오름차순 정렬
					
				}else {
					return a[1]-b[1]; // 0번째 열이 같으면 1번째 열 오름차순
				}
			}
		});
		
		StringBuilder sb = new StringBuilder();
		
		for(int i = 0; i<N; i++) {
			sb.append(arr[i][0]).append(" ");
			sb.append(arr[i][1]).append("\n");
		}
		System.out.println(sb);
	}
}