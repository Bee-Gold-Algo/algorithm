import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.Comparator;
import java.util.StringTokenizer;

// 좌표 정렬
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine());

        int[][] points = new int[N][2]; // [0] : x, [1]: y

        // 좌표 배열에 담기
        for(int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            points[i][0] = Integer.parseInt(st.nextToken());
            points[i][1] = Integer.parseInt(st.nextToken());
        }

//        for(int i = 0; i < N-1; i++) {
//            for(int k = i+1; k < N; k++) {
//                // x 끼리 비교
//                if(points[i][0] == points[k][0]) { // 같다면 y 비교
//                    if(points[i][1] > points[k][1]) {
//                        System.out.print("points[i][1] : " + points[i][1]);
//                        System.out.println("points[k][1] : " + points[k][1]);
//                        getChangePosition(points, i, k);
//                    }
//                } else if(points[i][0] > points[k][0]) {
//                    getChangePosition(points, i, k);
//                }
//            }
//        } // => 시간 초과
        Arrays.sort(points, new Comparator<int[]>() {
            @Override
            public int compare(int[] p1, int[] p2) {
                if(p1[0] == p2[0]) {// X 가 같을 때
                    return Integer.compare(p1[1], p2[1]); // Y 비교
                }
                return Integer.compare(p1[0], p2[0]);
            }
        });

        StringBuilder sb = new StringBuilder();
        for(int i = 0; i < N; i++) {
            sb.append(points[i][0]).append(" ").append(points[i][1]).append("\n");
        }

        System.out.println(sb);
    }

//    private static void getChangePosition(int[][] points, int i, int k) {
//        int xTemp = points[i][0];
//        int yTemp = points[i][1];
//
//        points[i][0] = points[k][0];
//        points[i][1] = points[k][1];
//
//        points[k][0] = xTemp;
//        points[k][1] = yTemp;
//    }
}