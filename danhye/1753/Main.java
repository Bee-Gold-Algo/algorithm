import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

public class Main {
	
	static List<Node>[] graph; //초기 지도
	
	static class Node implements Comparable<Node> {
		//그래프 만들때,, 실행 돌릴 때 모두 사용
		//정점 idx, 가중치 저장
		int idx = 0;
		int cost = 0;
		
		public Node(int idx, int cost) {
			super();
			this.idx = idx;
			this.cost = cost;
		}
		
		//어떤 노드가 앞에 와야하는 지 판단하기 위해서
		//기본적으로, 더 작은 값이 우선순위 높다 ! ( 앞에 오고, 먼저 꺼내짐 )
		@Override
		public int compareTo(Node n) {
			// 음수 / 0 / 양수 중 하나 반환
			// this.cost < n.cost -> 작으면 음수 반환
			// this.cost == n.cost -> 같으면 0 반환
			// this.const > n.cost -> 더 크면 양수 반환
			return Integer.compare(this.cost, n.cost);
		}
	} // Node 클래스 끝
	
	
	public static void dijkstra(int V, int K) {		
		int[] distance = new int[V+1]; //1부터 시작하니까 ! 편의성을 위해서 V+1
		//배열 초기화
		//Arrays.fill() 메서드 사용
		//Arrays.fill(배열변수, 초기화할 값)
		//Arrays.fill(배열변수, 시작, 끝+1, 초기화할 값)
		Arrays.fill(distance, Integer.MAX_VALUE);
		//출발지의 거리는 0
		distance[K] = 0;
		
		//우선순위 큐 생성
		PriorityQueue<Node> pq = new PriorityQueue<>();
		pq.offer(new Node(K,0)); //우선순위 큐에 시작 값 할당
		
		while(!pq.isEmpty()) { //큐가 빌 때까지 실행
			//now란? PriorityQueue 에서 poll 을 통해 꺼낸
			// 현재까지 발견된 최단 거리가 가장 짧은 정점
			Node now = pq.poll();
			
			//현재 큐에서 꺼낸 노드의 비용이 이미 갱신 된 거리보다 크다면
			//더 이상 처리할 필요가 없으므로 건너뛴다.
			if(distance[now.idx] < now.cost) {
				continue;
			}
			
			// graph? 인접 리스트로 구현된 그래프
			// graph 배열의 각 인덱스 == 정점
			// 그 인덱스에 연결된 ArrayList에는 해당 정점과 연결된 모든 간선 정보가 담겨있다.
			
			//graph[now.idx] ? 정점 now.idx에서 출발하는 모든 간선들의 리스트
			//하나씩 순차적으로 꺼내서 Node next 객체에 담음
			for(Node next : graph[now.idx]) {
				if(distance[next.idx] > distance[now.idx] + next.cost) {
					distance[next.idx] = distance[now.idx] + next.cost;
					pq.offer(new Node(next.idx, distance[next.idx]));
				}
			}
		} //while 문 끝
		
		//출력
		for (int i = 1; i < V + 1; i++) {
			if(distance[i] == Integer.MAX_VALUE) { //경로가 존재하지 않아서 초기 값인 경우
				System.out.println("INF");
			}else {
				System.out.println(distance[i]);
			}
		}
	}
	
	public static void main(String[] args) throws IOException {
		
		//1. 아직 방문하지 않은 정점 중 (boolean 배열 활용) 출발지로부터 가장 가까운 정점을 방문 -> 우선순위 큐
		//2. 해당 정점을 거쳐 갈 수 있는 정점의 거리가 이전 기록한 값보다 작으면 갱신 (배열)
		
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		String[] VE = br.readLine().split(" ");
		int V = Integer.parseInt(VE[0]); //정점의 개수
		int E = Integer.parseInt(VE[1]); //간선의 개수
		int K = Integer.parseInt(br.readLine()); //시작 정점의 번호
		
		graph = new ArrayList[V+1]; 
		for (int i = 0; i <= V; i++) {
			//ArrayList 안에 ArrayList를 담을 수 있도록 생성
			//예시 ) graph[1] = [ (2,5), (3,7) ]
			graph[i] = new ArrayList<>(); 
		}
		
		int from = 0;
		int to = 0;
		int cost = 0;
		for (int i = 0; i < E; i++) {
			String[] uvw = br.readLine().split(" ");
			from = Integer.parseInt(uvw[0]);
			to = Integer.parseInt(uvw[1]); 
			cost = Integer.parseInt(uvw[2]); //가중치
			
			graph[from].add(new Node(to, cost));
		}
		
		//다익스트라 실행
		dijkstra(V, K);
		
	} //main 끝
}
