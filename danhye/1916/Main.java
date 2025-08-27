import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

public class Main {
	
	static List<Node>[] map;
	
	static int city,bus,from,to,cost,start,end;
	static int[] costArr;
	
	public static class Node implements Comparable<Node>{
		int city;
		int cost;
		
		public Node(int city, int cost) {
			this.city = city;
			this.cost = cost;
		}

		@Override
		public int compareTo(Node n) {
			return this.cost - this.cost;
		}
	}
	
	public static void dijkstra() {
		costArr = new int[city+1];
		Arrays.fill(costArr, Integer.MAX_VALUE);
		costArr[start] = 0;
		
		//우선순위 큐 생성
		PriorityQueue<Node> pq = new PriorityQueue<>();
		pq.offer(new Node(start,0));
		
		while(!pq.isEmpty()) {
			Node now = pq.poll();
			
			if(costArr[now.city] < now.cost) continue;
			
			for(Node next : map[now.city]) {
				if(costArr[next.city] > costArr[now.city] + next.cost) {
					costArr[next.city] = costArr[now.city] + next.cost;
					pq.offer(new Node(next.city, costArr[next.city]));
				}
			}
		}//while문 끝
		
		System.out.println(costArr[end]);
	}
	
	
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		city = Integer.parseInt(br.readLine());
		bus = Integer.parseInt(br.readLine());
		
		from = 0;
		to = 0;
		cost = 0;
		
		map = new ArrayList[city+1];
		for (int i = 0; i < city + 1; i++) {
			map[i] = new ArrayList<>();
		}
		
		for (int i = 0; i < bus; i++) {
			String[] input = br.readLine().split(" ");
			from = Integer.parseInt(input[0]);
			to = Integer.parseInt(input[1]);
			cost = Integer.parseInt(input[2]);
			
			map[from].add(new Node(to, cost));
		}
		
		String[] input = br.readLine().split(" ");
		start = Integer.parseInt(input[0]);
		end = Integer.parseInt(input[1]);
		
		//다익스트라 실행
		dijkstra();
	}
}
