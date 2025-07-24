#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다.
"""

import argparse
import json
import re
import requests
import time
import random
from bs4 import BeautifulSoup

def get_solved_ac_info(problem_id):
    """solved.ac API에서 문제 정보 가져오기"""
    try:
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("titleKo", ""),
                "level": data.get("level", 0),
                "tags": [tag["displayNames"][0]["name"] for tag in data.get("tags", [])]
            }
    except Exception as e:
        print(f"solved.ac API 오류: {e}")
    
    return {}

def get_random_user_agent():
    """랜덤 User-Agent 반환"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return random.choice(user_agents)

def create_session():
    """세션 생성 및 설정"""
    session = requests.Session()
    
    # 고정 헤더 설정
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    })
    
    return session

def scrape_boj_problem_with_session(problem_id, session):
    """세션을 사용하여 백준 문제 스크래핑"""
    url = f"https://www.acmicpc.net/problem/{problem_id}"
    
    try:
        # User-Agent를 매번 새로 설정
        session.headers.update({'User-Agent': get_random_user_agent()})
        
        # 랜덤 지연 (1-3초)
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)
        
        response = session.get(url, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 문제가 존재하지 않는 경우
        if "존재하지 않는" in response.text or response.status_code == 404:
            return None
        
        # 문제 정보 추출
        problem_info = {}
        
        # 문제 설명
        desc_elem = soup.find('div', {'id': 'problem_description'})
        problem_info['description'] = desc_elem.get_text(strip=True) if desc_elem else ""
        
        # 입력 형식
        input_elem = soup.find('div', {'id': 'problem_input'})
        problem_info['input_format'] = input_elem.get_text(strip=True) if input_elem else ""
        
        # 출력 형식
        output_elem = soup.find('div', {'id': 'problem_output'})
        problem_info['output_format'] = output_elem.get_text(strip=True) if output_elem else ""
        
        # 제한사항
        limit_elem = soup.find('div', {'id': 'problem_limit'})
        problem_info['limits'] = limit_elem.get_text(strip=True) if limit_elem else ""
        
        # 샘플 입출력
        samples = []
        sample_inputs = soup.find_all('pre', {'id': re.compile(r'sample-input-\d+')})
        sample_outputs = soup.find_all('pre', {'id': re.compile(r'sample-output-\d+')})
        
        for i, (inp, out) in enumerate(zip(sample_inputs, sample_outputs)):
            samples.append({
                "input": inp.get_text(),
                "output": out.get_text(),
            })
        
        problem_info['samples'] = samples
        return problem_info
        
    except Exception as e:
        raise e

def scrape_boj_problem_alternative_methods(problem_id):
    """여러 방법으로 백준 스크래핑 시도"""
    
    # 방법 1: 일반 requests 라이브러리 (개선된 헤더)
    print("  → 방법 1: 개선된 헤더로 시도...")
    session = create_session()
    
    for attempt in range(2):
        try:
            result = scrape_boj_problem_with_session(problem_id, session)
            if result:
                print("  ✅ 방법 1 성공!")
                return result
        except Exception as e:
            print(f"  ❌ 방법 1 실패 (시도 {attempt + 1}/2): {e}")
            if attempt < 1:
                time.sleep(random.uniform(2.0, 4.0))
    
    # 방법 2: 백준 메인 페이지 먼저 방문 후 문제 페이지 접근
    print("  → 방법 2: 메인 페이지 우회 접근...")
    try:
        session = create_session()
        
        # 1. 메인 페이지 먼저 방문 (쿠키 및 세션 설정)
        session.headers.update({'User-Agent': get_random_user_agent()})
        main_response = session.get('https://www.acmicpc.net/', timeout=15)
        main_response.raise_for_status()
        
        time.sleep(random.uniform(1.5, 2.5))
        
        # 2. 문제 목록 페이지 방문
        problemset_response = session.get('https://www.acmicpc.net/problemset', timeout=15)
        problemset_response.raise_for_status()
        
        time.sleep(random.uniform(1.0, 2.0))
        
        # 3. 실제 문제 페이지 접근
        result = scrape_boj_problem_with_session(problem_id, session)
        if result:
            print("  ✅ 방법 2 성공!")
            return result
            
    except Exception as e:
        print(f"  ❌ 방법 2 실패: {e}")
    
    # 방법 3: 더 긴 지연시간과 함께 재시도
    print("  → 방법 3: 긴 지연시간으로 재시도...")
    try:
        session = create_session()
        session.headers.update({'User-Agent': get_random_user_agent()})
        
        # 5-8초 대기
        time.sleep(random.uniform(5.0, 8.0))
        
        result = scrape_boj_problem_with_session(problem_id, session)
        if result:
            print("  ✅ 방법 3 성공!")
            return result
            
    except Exception as e:
        print(f"  ❌ 방법 3 실패: {e}")
    
    print("  ❌ 모든 스크래핑 방법 실패")
    return None

def get_fallback_samples(problem_id):
    """스크래핑 실패 시 알려진 문제들의 샘플 제공"""
    known_samples = {
        "1000": [{"input": "1 2", "output": "3"}],
        "2557": [{"input": "", "output": "Hello World!"}],
        "1001": [{"input": "1 -1", "output": "0"}],
        "10998": [{"input": "1 2", "output": "2"}],
        "1008": [{"input": "1 3", "output": "0.33333333333333333333"}],
        "10869": [{"input": "7 3", "output": "10\n4\n21\n2\n1"}],
        "10171": [{"input": "", "output": "\\    /\\\n )  ( ')\n(  /  )\n \\(__)|"}],
        "10172": [{"input": "", "output": "|\\_/|\n|q p|   /}\n( 0 )\"\"\"\\\n|\"^\"`    |\n||_/=\\\\__|"}]
    }
    
    return known_samples.get(problem_id, [])

def main():
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    args = parser.parse_args()
    
    problem_id = args.problem_id
    
    print(f"📥 문제 {problem_id} 정보 수집 중...")
    
    # solved.ac 정보 수집
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 백준 상세 정보 수집 (다양한 방법으로 시도)
    boj_info = scrape_boj_problem_alternative_methods(problem_id)
    
    if not boj_info:
        print(f"::warning::문제 {problem_id}의 상세 정보 스크래핑에 실패했습니다. 기본값을 사용합니다.")
        
        # 폴백 샘플 사용
        fallback_samples = get_fallback_samples(problem_id)
        
        boj_info = {
            "description": f"문제 {problem_id} (스크래핑 실패)",
            "input_format": "입력 형식을 확인할 수 없습니다.",
            "output_format": "출력 형식을 확인할 수 없습니다.",
            "limits": "제한사항을 확인할 수 없습니다.",
            "samples": fallback_samples
        }
        
        if fallback_samples:
            print(f"  → 알려진 샘플 테스트케이스 {len(fallback_samples)}개를 사용합니다.")
    
    # 정보 통합
    complete_info = {
        "problem_id": problem_id,
        "title": solved_ac_info.get("title", f"문제 {problem_id}"),
        "level": solved_ac_info.get("level", 0),
        "tags": solved_ac_info.get("tags", []),
        **boj_info
    }
    
    # JSON 파일로 저장
    with open('problem_info.json', 'w', encoding='utf-8') as f:
        json.dump(complete_info, f, ensure_ascii=False, indent=2)
    
    # 샘플 테스트케이스 별도 저장
    sample_tests = {
        "problem_id": problem_id,
        "test_cases": complete_info['samples']
    }
    
    with open('sample_tests.json', 'w', encoding='utf-8') as f:
        json.dump(sample_tests, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 문제 정보 수집 완료:")
    print(f"   - 제목: {complete_info['title']}")
    print(f"   - 샘플 테스트케이스: {len(complete_info['samples'])}개")
    print(f"   - 태그: {', '.join(complete_info['tags'][:3])}")

if __name__ == "__main__":
    main()