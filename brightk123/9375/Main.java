import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class Main {
	public static void main(String[] args) throws IOException {

		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

		int TC = Integer.parseInt(br.readLine());

		for (int h = 0; h < TC; h++) {
			int N = Integer.parseInt(br.readLine()); // 아이템의 갯수
			
			List<String> categorys = new ArrayList<>();
			List<Integer> itemCount = new ArrayList<>();
			// 1 카테고리 2 해당 카테고리의 아이템 갯수
			
			int count = 0;
			for(int i = 0; i<N; i++) {
				
				String[] inputLine = br.readLine().split(" ");
				String category = inputLine[1];
				
				if(categorys.contains(category)) {
					// 이미 존재하는 카테고리일 경우 아이템의 갯수만 증가
					count = itemCount.get(categorys.indexOf(category)) + 1;
					itemCount.set(categorys.indexOf(category), count);
					
				}else if(!categorys.contains(category)) {
					// 최초 등장한 카테고리일 경우 해당 카테고리 추가 및 아이템 갯수 증가
					categorys.add(category);
					itemCount.add(1);
				}
			}
			// 아이템 조합 경우의 수
			int ways = 1;
			for(int i = 0; i<categorys.size(); i++) {
				ways = ways*(itemCount.get(i)+1); // 해당 카테고리의 아이템을 쓰지 않는 경우도 포함
			}
			
			// 아이템 중 하나 이상은 써야하므로 모든 아이템을 착용하지 않은 경우 1 제외
			ways = ways-1;
			
			System.out.println(ways);
		}
		
		
	}
}