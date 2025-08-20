import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {

    public static void main(String[] args) throws NumberFormatException, IOException {
        // T1 = 1/1
        // T2 = 1/2 2/1
        // T3 = 3/1 2/2 1/3
        // T4 = 1/4 2/3 3/2 4/1
        // T5 = 5/1 4/2 3/3 2/4 1/5

        // 짝수(기존대로) ->
        // 홀수(거꾸로) -> 분모/분자
        // - > 해당 라인의 수/1 ~ 1/해당라인의 수
        // -> 분모/1 - 분모-1/1+1 -분모-2/2+1..

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int x = Integer.parseInt(br.readLine());

        int crossCount = 1, prevCountSum = 0;
        StringBuilder sb = new StringBuilder();

        while(true) {

            // 해당 대각선 + 직전 대각선 누적합
            if(x <= crossCount + prevCountSum) {
                int index = x - (prevCountSum + 1);
                if(crossCount % 2 == 0) {
                    // 짝수니까 작은데서 큰데로 증가하게 해야함
                    sb.append("").append(1+index).append("/").append(crossCount - index);
                    System.out.println(sb);
                    break;

                } else {
                    // 홀수니까 분모가 큰 데서 작은데로 향하게 해야함
                    // +- 해야하는 넘버
                    sb.append("").append(crossCount - index).append("/").append(1+index);
                    System.out.println(sb);
                    break;
                }
            }
            prevCountSum += crossCount;
            crossCount++;
        }
    }
}