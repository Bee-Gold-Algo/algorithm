import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

public class Main {
	public static List<Node>[] go;
	public static List<Node>[] comback;

	public static class Node implements Comparable<Node>{
		int village;
		int time; //소요시간
		
		public Node(int village, int time) {
			this.village = village;
			this.time = time;
		}

		@Override
		public int compareTo(Node n) {
			return this.time - n.time;
		}
	}
	
	public static int[] dijkstra(int students, int party, List<Node>[] list ) {
		//파티에 가는 배열
		int[] time = new int[students + 1];
		Arrays.fill(time, Integer.MAX_VALUE);
		
		//우선순위 큐 생성
		PriorityQueue<Node> pq = new PriorityQueue<>();
		
		time[party] = 0;
		pq.offer(new Node(party,0));
		
		while(!pq.isEmpty()) {
			Node now = pq.poll();
			
			if(time[now.village] < now.time) continue;
			
			for(Node next : list[now.village]) {
				if(time[next.village] > time[now.village] + next.time) {
					time[next.village] = time[now.village] + next.time;
					pq.offer(new Node(next.village, time[next.village]));
				}
			}
		} //while 끝
		return time;
	}
	
	public static void main(String[] args) throws IOException {
		//입력 받기
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		String[] NMX = br.readLine().split(" ");
		int students = Integer.parseInt(NMX[0]); //학생수
		int road = Integer.parseInt(NMX[1]); //도로수
		int party = Integer.parseInt(NMX[2]); //파티 장소, 중심
		
		int start = 0, end = 0, time = 0;
		
		go = new ArrayList[students+1];
		comback = new ArrayList[students+1];
		for (int i = 0; i <= students ; i++) {
			go[i] = new ArrayList<>();
			comback[i] = new ArrayList<>();
		}
		
		for (int i = 0; i < road; i++) {
			String[] input = br.readLine().split(" ");
			start = Integer.parseInt(input[0]);
			end = Integer.parseInt(input[1]);
			time = Integer.parseInt(input[2]);
			go[start].add(new Node(end, time));
			comback[end].add(new Node(start, time));
		}
		
		//다익스트라 메소드 실행
		//파티에 가는 최장시간 찾기
		int[] gotoParty = dijkstra(students, party, go);
		int[] backtoHome = dijkstra(students, party, comback);
		int max = Integer.MIN_VALUE;
		
		for (int i = 1; i <= students; i++) {
			int sum = gotoParty[i] + backtoHome[i];
			if(max < sum) max = sum;
		}
		
		System.out.println(max);
	}
}
