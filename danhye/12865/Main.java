import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
    static int n, k;
    static int[] weight, value;
    static int[][] dp;
	
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        String[] NK = br.readLine().split(" ");
        n = Integer.parseInt(NK[0]); //물품의 수
        k = Integer.parseInt(NK[1]); //버틸 수 있는 무게
        
        weight = new int[n+1];
        value = new int[n+1];
        dp = new int[n+1][k+1];

        for (int i = 1; i < n+1; i++) {
            String[] WV = br.readLine().split(" ");
            weight[i]= Integer.parseInt(WV[0]); //각 물건의 무게
            value[i] = Integer.parseInt(WV[1]); //각 물건의 가치
        }
        
        for (int i = 1; i < n+1 ; i++) {  	
        	for (int j = 0; j < k+1; j++ ) {
				dp[i][j] = dp[i-1][j];
				if(weight[i] <= j) {
					dp[i][j] = Math.max(dp[i][j], dp[i-1][j-weight[i]] + value[i]);
				}
			}
		}
       System.out.println(dp[n][k]);
    }
}
