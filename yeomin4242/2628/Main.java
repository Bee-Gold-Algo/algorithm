import java.util.*;
import java.io.*;

/**
 * 가로로 자르는게 0
 * 세로로 자르는게 1
 */

public class Main{
    public static void main(String[] args) throws IOException{
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        StringTokenizer st = new StringTokenizer(br.readLine());

        int X = Integer.parseInt(st.nextToken());
        int Y = Integer.parseInt(st.nextToken());

        int T = Integer.parseInt(br.readLine());
    
        int maxX = 0;
        int maxY = 0;

        int[] xArr = new int[Math.max(X + 1, Y + 1)];
        int[] yArr = new int[Math.max(X + 1, Y + 1)];

        while((--T) >= 0) {
            st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());
            int idx = Integer.parseInt(st.nextToken());
            if (type == 0) {
                xArr[idx] = 1;
            } else {
                yArr[idx] = 1;
            }

        }

        xArr[Y] = 1;
        yArr[X] = 1;

        int cnt = 0;

        for (int i = 0 ; i < Math.max(X + 1, Y + 1) ; i++) {
            if (xArr[i] == 1) {
                maxX = (maxX < cnt) ? cnt : maxX;
                cnt = 0;
            }
            cnt++;
        }

        cnt = 0;

        for (int i = 0 ; i <Math.max(X + 1, Y + 1) ; i++) {
            if (yArr[i] == 1) {
                maxY = (maxY < cnt) ? cnt : maxY;
                cnt = 0;
            }
            cnt++;
        }
    
        System.out.println((maxX) * (maxY));
    }
}