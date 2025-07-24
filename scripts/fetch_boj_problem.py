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

def scrape_boj_problem(problem_id):
    """백준에서 문제 정보 스크래핑 (재시도 로직 추가)"""
    url = f"https://www.acmicpc.net/problem/{problem_id}"
    
    # ⭐️ 1. 실제 브라우저처럼 보이도록 헤더 정보 강화
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    # ⭐️ 2. 최대 3번, 간격을 두고 재시도
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            # 4xx, 5xx 에러가 발생하면 예외를 발생시킴
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 문제가 존재하지 않는 경우 (이때는 재시도할 필요 없음)
            if "존재하지 않는" in response.text or response.status_code == 404:
                return None
            
            # --- 성공 시, 문제 정보 추출 ---
            problem_info = {}
            
            desc_elem = soup.find('div', {'id': 'problem_description'})
            problem_info['description'] = desc_elem.get_text(strip=True) if desc_elem else ""
            
            input_elem = soup.find('div', {'id': 'problem_input'})
            problem_info['input_format'] = input_elem.get_text(strip=True) if input_elem else ""
            
            output_elem = soup.find('div', {'id': 'problem_output'})
            problem_info['output_format'] = output_elem.get_text(strip=True) if output_elem else ""
            
            limit_elem = soup.find('div', {'id': 'problem_limit'})
            problem_info['limits'] = limit_elem.get_text(strip=True) if limit_elem else ""
            
            samples = []
            sample_inputs = soup.find_all('pre', {'id': re.compile(r'sample-input-\d+')}) # ID 형식 변경됨
            sample_outputs = soup.find_all('pre', {'id': re.compile(r'sample-output-\d+')}) # ID 형식 변경됨
            
            for i, (inp, out) in enumerate(zip(sample_inputs, sample_outputs)):
                samples.append({
                    "input": inp.get_text(strip=True),
                    "output": out.get_text(strip=True),
                })
            
            problem_info['samples'] = samples
            return problem_info # 성공했으므로 결과 반환 및 함수 종료
            
        except requests.exceptions.RequestException as e:
            print(f"백준 스크래핑 오류 (시도 {attempt + 1}/3): {e}")
            if attempt < 2:  # 마지막 시도가 아니라면
                wait_time = 2 ** (attempt + 1) # 2, 4초 간격으로 대기
                print(f"{wait_time}초 후 재시도합니다...")
                time.sleep(wait_time)
            else:
                print("최종 스크래핑에 실패했습니다.")
    
    return None # 모든 재시도 실패 시 None 반환

def main():
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    args = parser.parse_args()
    
    problem_id = args.problem_id
    
    print(f"📥 문제 {problem_id} 정보 수집 중...")
    
    # solved.ac 정보 수집
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 백준 상세 정보 수집 (내부적으로 재시도 로직 포함)
    boj_info = scrape_boj_problem(problem_id)
    
    if not boj_info:
        print(f"::error::문제 {problem_id}의 상세 정보를 가져올 수 없습니다.")
        # 빈 정보로라도 계속 진행
        boj_info = {
            "description": "스크래핑 실패", "input_format": "", "output_format": "",
            "limits": "", "samples": []
        }
    
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