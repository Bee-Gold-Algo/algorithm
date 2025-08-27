import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.PriorityQueue;

public class Main {
	//ArrayList 생성
	static List<Node>[] map;
	
	static class Node implements Comparable<Node>{
		int city;
		int distance;
		
		public Node(int city, int distance) {
			this.city = city;
			this.distance = distance;
		}

		@Override
		public int compareTo(Node n) {
			return this.city - n.city;
		}
	}
	
	//다익스트라,,
	static void dijkstra(int city, int start, int k) {
		int[] distance = new int[city+1];
		Arrays.fill(distance, Integer.MAX_VALUE);
		distance[start] = 0;
		
		//우선순위 큐 생성
		PriorityQueue<Node> pq = new PriorityQueue<>();
		pq.offer(new Node(start,0));
		
		while(!pq.isEmpty()) {
			Node now = pq.poll();
			
			if(distance[now.city] < now.distance) {
				continue;
			}
			
			//정점 now.city 에서 출발하는 모든 간선들의 리스트
			//하나씩 순차적으로 꺼내서 next 객체에 담는다
			for(Node next : map[now.city]) {
				if(distance[next.city] > distance[now.city] + next.distance) {
					distance[next.city] = distance[now.city] + next.distance;
					pq.offer(new Node(next.city, distance[next.city]));
				}
			}
			
		}//while 끝
		
		boolean check = false;
		for (int i = 1; i < city+1; i++) {
			if(distance[i] == k) {
				check = true;
				System.out.println(i);
			}
		}
		
		if(!check)System.out.println(-1);			
	}
	
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		String[] NMKX = br.readLine().split(" "); 
		int city = Integer.parseInt(NMKX[0]); //도시의 개수
		int road = Integer.parseInt(NMKX[1]); //도로의 개수
		int k = Integer.parseInt(NMKX[2]); //거리 정보
		int start = Integer.parseInt(NMKX[3]); //출발 도시의 번호
		
		int from = 0, to = 0;
		map = new ArrayList[city+1];
		for (int i = 0; i <= city; i++) {
			map[i] = new ArrayList<>();
		}
		
		
		for (int i = 0; i < road; i++) {
			String[] AB = br.readLine().split(" ");
			from = Integer.parseInt(AB[0]);
			to = Integer.parseInt(AB[1]);
			map[from].add(new Node(to,1));
		}
		
		dijkstra(city, start, k);
	}
}
