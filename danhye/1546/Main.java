import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		int subjects = Integer.parseInt(br.readLine());
		int[] score = new int[subjects];
		
		StringTokenizer st = new StringTokenizer(br.readLine()," ");
		int max = Integer.MIN_VALUE;
		
		for (int i = 0; i < subjects; i++) {
			score[i] = Integer.parseInt(st.nextToken());
			if(score[i] > max) max = (int) score[i];
		}
		
		double sum = 0;
		for (int i = 0; i < subjects; i++) {
			sum += ((double) score[i] / max) * 100;
		}
		
		double avg = sum / subjects;
		System.out.println(avg);
	}
}
