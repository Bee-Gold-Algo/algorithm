import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
    static int[] switches;
    public static void main(String[] args) throws NumberFormatException, IOException {

        // 입력
        // 1. 스위치의 개수 ( 1 ~ 100)
        // 2. 각 스위치의 상태
        // 3. 학생 수
        // 4. 넷째 ~ 마지막 줄 까지 (한 학생의 성별, 학생이 받은 수)
        // 남 - 1, 여 - 2

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine()); // 스위치 수
        switches = new int[N+1]; 			// 스위치 상태 배열

        StringTokenizer st = new StringTokenizer(br.readLine());
        for(int n = 1; n <= N; n++) {
            switches[n] = Integer.parseInt(st.nextToken());
        }

//		System.out.println(Arrays.toString(switches));
//		[0(비워두기), 0, 1, 0, 1, 0, 0, 0, 1]

        int M = Integer.parseInt(br.readLine()); // 학생 수
        for(int m = 0; m < M; m++) {
            st = new StringTokenizer(br.readLine());
            int gender = Integer.parseInt(st.nextToken());
            int number = Integer.parseInt(st.nextToken());

            changeSwitch(gender, number);
        }

        for(int i = 1; i < switches.length; i++) { // 1 ~ 40, 1 ~
            System.out.print(switches[i] + " ");
            if(i % 20 == 0) {
                System.out.println();
            }
        }
    }

    private static int[] changeSwitch(int gender, int number) {
        if(gender == 1) { // 남자
            for(int i = number; i < switches.length; i++) {
                if(i % number == 0) {
                    switches[i] = (switches[i] == 1)? 0 : 1;
                }
            }
        } else { // 여자 (수가 좌우대칭 구간을 찾아야함)
            int start = number; // 3
            int end = number;    // 3
            for(int i = 1; i < switches.length/2; i++) {   // 9 / 2  = 4 (0,1,2,3)

                if(number-i < 1 || number+i >= switches.length) {
                    break;
                }

                if(switches[number - i] != switches[number + i]) {
                    break;
                } else {
                    start = number - i;  // 3-3 = 0/  3-2 = 1
                    end = number + i;	//
                }

            }

            // 0, 4 (switches[0] =
            for(int i = start; i <= end; i++) {
                switches[i] = (switches[i] == 1)? 0 : 1;
            }

        }

        return switches;
    }
}
