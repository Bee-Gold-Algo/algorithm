import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Stack;

public class Main{
	
	static int city, bus, from, to, cost, start, end;
	static List<Node>[] map;
	static int[] costArr;
	//경로 추적할 배열
	static int[] path;
	
	static class Node implements Comparable<Node>{
		int city;
		int cost;
		
		public Node(int city, int cost) {
			this.city = city;
			this.cost = cost;
		}

		@Override
		public int compareTo(Node n) {
			return this.cost - n.cost;
		}
	}
	
	static void dijkstra() {
		costArr = new int[city+1];
		path = new int[city+1];
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
					path[next.city] = now.city;
					pq.offer(new Node(next.city, costArr[next.city]));
				}
			}
		}//while 끝
	}
	
	//출력 메서드 
	static void print() {
		//첫째 줄 출발 ~ 도착까지의 최소 비용
		System.out.println(costArr[end]);
		//둘째 줄 최소 비용 갖는 경로에 포함되어 있는 도시의 개수
		Stack<Integer> route = new Stack<>();
		int current = end;
		while(current != 0) {
			route.push(current);
			current = path[current]; //path[next.city] = now.city; 이니까 !
		}
		System.out.println(route.size());
		//셋째 줄 도시 순서대로 출력
		while(!route.isEmpty()) { //스택이 비어 있지 않으면 계속 수행
			System.out.print(route.pop() + " ");
		}
	}
	
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		city = Integer.parseInt(br.readLine());
		bus = Integer.parseInt(br.readLine());
		
		map = new ArrayList[city+1];
		for (int i = 0; i < city + 1; i++) {
			map[i] = new ArrayList<>();
		}
		
		for (int i = 0; i < bus; i++) {
			String[] input = br.readLine().split(" ");
			from = Integer.parseInt(input[0]);
			to = Integer.parseInt(input[1]);
			cost = Integer.parseInt(input[2]);
			map[from].add(new Node(to,cost));
		}
		
		String[] input = br.readLine().split(" ");
		start = Integer.parseInt(input[0]);
		end = Integer.parseInt(input[1]);
		
		//다익스트라 메서드 실행
		dijkstra();
		print();
	}//main 끝
}
