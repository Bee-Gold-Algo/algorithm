import java.util.*;
import java.io.*;

public class Main {
    static int arrSize;

    public static int getSize(int N) {
        int i = 0;
        while ((int)Math.pow(3, ++i) != N) {}
        return i;
    }

    public static void replace(int xIdx, int yIdx, char[][] arr , int size, int startY) {
        if (yIdx < startY + (int)Math.pow(3, size)) {
            int tmp = xIdx;

            while (tmp < arrSize) {
                for (int i = 0 ; i < (int)Math.pow(3, size) ; i++) {
                    arr[yIdx][tmp + i] = ' ';
                }
                tmp += (int)Math.pow(3, size + 1);
            }
            replace(xIdx, yIdx + 1, arr , size, startY);
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());

        char [][] arr = new char[N][N];
        
        for (int i = 0; i < N ; i++) {
            for (int j = 0 ; j < N ; j++) {
                arr[i][j] = '*';
            }
        }

        int size = getSize(N);
        arrSize = N;

        while ((--size) >= 0) {
            int xIdx = (int)Math.pow(3, size);
            int yIdx = (int)Math.pow(3, size);
            while (yIdx + 2 * (int)Math.pow(3, size) <= N) {
                replace(xIdx, yIdx, arr, size, yIdx);
                xIdx = (int)Math.pow(3, size);
                yIdx += (int)Math.pow(3, size + 1);

            }
        }
        
        for (int i = 0 ; i < N ; i++) {
            System.out.println(String.valueOf(arr[i]));
        }

    }
}