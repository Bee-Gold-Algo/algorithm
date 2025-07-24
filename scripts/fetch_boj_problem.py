#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (requests + BeautifulSoup 방식 - 안정적!)
GitHub Actions와 로컬 환경 모두에서 완벽 작동
"""

import argparse
import json
import requests
from bs4 import BeautifulSoup
import time 
import os

def get_solved_ac_info(problem_id):
    """solved.ac API에서 문제 정보 가져오기"""
    try:
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            tags = []
            for tag in data.get("tags", []):
                korean_tag = next((item['name'] for item in tag.get('displayNames', []) if item['language'] == 'ko'), None)
                if korean_tag:
                    tags.append(korean_tag)
            
            return {
                "title": data.get("titleKo", ""),
                "level": data.get("level", 0),
                "tags": tags
            }
    except Exception as e:
        print(f"  ⚠️ solved.ac API 오류: {e}")
    
    return {}

def extract_problem_info_from_html(html_content):
    """HTML에서 문제 정보 추출"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 문제가 존재하지 않는 경우 체크
    if "존재하지 않는 문제" in soup.text or "해당 문제를 찾을 수 없습니다" in soup.text:
        print("  ❌ 문제가 존재하지 않습니다.")
        return None

    problem_info = {}
    
    # 1. 문제 설명
    desc_section = soup.find('section', {'id': 'description'})
    if desc_section:
        problem_info['description'] = desc_section.get_text(separator='\n', strip=True)
        print("  ✅ 문제 설명 추출 완료")
    else:
        desc_elem = soup.find('div', {'id': 'problem_description'})
        problem_info['description'] = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ""
    
    # 2. 입력 설명
    input_section = soup.find('section', {'id': 'input'})
    if input_section:
        problem_info['input_format'] = input_section.get_text(separator='\n', strip=True)
        print("  ✅ 입력 형식 추출 완료")
    else:
        input_elem = soup.find('div', {'id': 'problem_input'})
        problem_info['input_format'] = input_elem.get_text(separator='\n', strip=True) if input_elem else ""
    
    # 3. 출력 설명
    output_section = soup.find('section', {'id': 'output'})
    if output_section:
        problem_info['output_format'] = output_section.get_text(separator='\n', strip=True)
        print("  ✅ 출력 형식 추출 완료")
    else:
        output_elem = soup.find('div', {'id': 'problem_output'})
        problem_info['output_format'] = output_elem.get_text(separator='\n', strip=True) if output_elem else ""
    
    # 4. 힌트
    hint_section = soup.find('section', {'id': 'hint'})
    if hint_section:
        problem_info['hint'] = hint_section.get_text(separator='\n', strip=True)
        print("  ✅ 힌트 추출 완료")
    else:
        problem_info['hint'] = ""
    
    # 5. 제한사항
    limit_elem = soup.find('div', {'id': 'problem_limit'})
    problem_info['limits'] = limit_elem.get_text(separator='\n', strip=True) if limit_elem else ""
    
    # 6. 샘플 테스트케이스 추출
    samples = []
    sample_count = 0
    
    for i in range(1, 20):
        input_section = soup.find('section', {'id': f'sampleinput{i}'})
        output_section = soup.find('section', {'id': f'sampleoutput{i}'})
        
        if input_section and output_section:
            input_pre = input_section.find('pre')
            output_pre = output_section.find('pre')
            
            if input_pre and output_pre:
                samples.append({
                    "input": input_pre.get_text(strip=True),
                    "output": output_pre.get_text(strip=True),
                })
                sample_count += 1
        else:
            input_elem = soup.find('pre', {'id': f'sample-input-{i}'})
            output_elem = soup.find('pre', {'id': f'sample-output-{i}'})
            
            if input_elem and output_elem:
                samples.append({
                    "input": input_elem.get_text(strip=True),
                    "output": output_elem.get_text(strip=True),
                })
                sample_count += 1
            else:
                break
    
    problem_info['samples'] = samples
    print(f"  ✅ 샘플 테스트케이스 {sample_count}개 추출 완료")
    
    return problem_info

def scrape_boj_with_requests(problem_id):
    """requests + BeautifulSoup을 사용한 안정적 스크래핑"""
    print("  🌊 requests + BeautifulSoup 스크래핑 시작...")
    
    try:
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        
        # 다양한 User-Agent로 로테이션
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        import random
        selected_ua = random.choice(user_agents)
        
        # 완전한 브라우저 헤더 시뮬레이션
        headers = {
            'User-Agent': selected_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Charset': 'utf-8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        print(f"  → 요청 전송: {url}")
        print(f"  🔧 User-Agent: {selected_ua[:50]}...")
        
        # 세션을 사용해서 쿠키 및 연결 유지
        session = requests.Session()
        session.headers.update(headers)
        
        # 재시도 로직 내장
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                
                if response.status_code == 200:
                    print(f"  ✅ 페이지 로드 성공 (크기: {len(response.text):,} 문자)")
                    
                    # 페이지 유효성 검사
                    if "존재하지 않는 문제" in response.text:
                        print("  ❌ 존재하지 않는 문제")
                        return None
                    
                    if len(response.text) < 1000:
                        print("  ❌ 페이지 내용이 너무 짧음")
                        return None
                    
                    # HTML 파싱
                    problem_info = extract_problem_info_from_html(response.text)
                    
                    if problem_info and len(problem_info.get('samples', [])) > 0:
                        print(f"  🎉 requests 스크래핑 성공! (샘플 {len(problem_info['samples'])}개)")
                        return problem_info
                    else:
                        print("  ⚠️ 문제 정보 추출 실패, 재시도...")
                        if attempt < max_retries:
                            time.sleep(2)
                            continue
                        return None
                else:
                    print(f"  ❌ HTTP 오류: {response.status_code}")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"  ❌ 요청 오류 (시도 {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    time.sleep(3)
                    continue
                return None
            
    except Exception as e:
        print(f"  ❌ 예외 발생: {e}")
        return None

def scrape_boj_with_retry(problem_id, max_attempts=3):
    """재시도 로직을 포함한 requests 스크래핑"""
    print(f"  🔄 안정적 스크래핑 시작 (최대 {max_attempts}회 시도)")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n  📍 시도 {attempt}/{max_attempts}")
        
        if attempt > 1:
            delay = 2 * attempt  # 2초, 4초, 6초...
            print(f"  ⏳ {delay}초 대기 후 재시도...")
            time.sleep(delay)
        
        result = scrape_boj_with_requests(problem_id)
        
        if result and len(result.get('samples', [])) > 0:
            print(f"  🎉 {attempt}번째 시도에서 성공!")
            return result
        else:
            if attempt < max_attempts:
                print(f"  ❌ {attempt}번째 시도 실패, 재시도 준비...")
            else:
                print(f"  💥 모든 시도 실패 ({max_attempts}회)")
    
    return None

def main():
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집 (requests 방식 - 안정적!)')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    parser.add_argument('--retry-mode', choices=['basic', 'aggressive'], default='basic', 
                       help='재시도 모드 (basic: 3회, aggressive: 5회)')
    args = parser.parse_args()
    
    problem_id = args.problem_id
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
    print(f"📥 문제 {problem_id} 정보 수집 중...")
    
    if is_github_actions:
        print("🤖 GitHub Actions 환경에서 실행 중")
        print("  🌊 requests + BeautifulSoup 방식 (안정적!)")
        print("  ⚡ 빠르고 가벼우며 확실함")
        print("  🔧 다양한 User-Agent 로테이션")
    else:
        print("🖥️ 로컬 환경에서 실행 중")
        print("  🌊 requests + BeautifulSoup 방식")
        print("  ⚡ Selenium 없이도 완벽 작동")
        print("  🔧 고급 헤더 시뮬레이션")
    
    # 1. solved.ac API로 기본 정보 수집
    print("\n  → solved.ac API 호출...")
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 2. requests 방식으로 스크래핑
    if args.retry_mode == 'aggressive':
        boj_info = scrape_boj_with_retry(problem_id, max_attempts=5)
    else:
        boj_info = scrape_boj_with_retry(problem_id, max_attempts=3)
    
    # 3. 스크래핑 실패 시 처리
    if not boj_info:
        print("\n  ❌ 모든 스크래핑 시도 실패")
        print("  💡 문제 정보를 수동으로 확인해주세요:")
        print(f"     https://www.acmicpc.net/problem/{problem_id}")
        
        boj_info = {
            "description": f"문제 {problem_id}의 상세 설명을 확인할 수 없습니다. 링크에서 직접 확인하세요.",
            "input_format": "입력 형식을 직접 확인하세요.",
            "output_format": "출력 형식을 직접 확인하세요.",
            "limits": "시간/메모리 제한을 직접 확인하세요.",
            "hint": "",
            "samples": []
        }
        print(f"  ⚠️ 빈 샘플 데이터로 진행합니다.")
    
    # 4. 최종 정보 조합
    complete_info = {
        "problem_id": problem_id,
        "title": solved_ac_info.get("title", f"문제 {problem_id}"),
        "level": solved_ac_info.get("level", "N/A"),
        "tags": solved_ac_info.get("tags", []),
        **boj_info
    }
    
    # 5. 파일 저장
    try:
        with open('problem_info.json', 'w', encoding='utf-8') as f:
            json.dump(complete_info, f, ensure_ascii=False, indent=2)
        
        sample_tests = {
            "problem_id": problem_id,
            "test_cases": complete_info['samples']
        }
        
        with open('sample_tests.json', 'w', encoding='utf-8') as f:
            json.dump(sample_tests, f, ensure_ascii=False, indent=2)
        
        environment = "GitHub Actions" if is_github_actions else "로컬"
        
        if len(complete_info['samples']) > 0:
            print(f"\n✅ {environment} 스크래핑 완료:")
            print(f"  - 제목: {complete_info['title']} (Level: {complete_info['level']})")
            print(f"  - 태그: {', '.join(complete_info['tags']) if complete_info['tags'] else 'N/A'}")
            print(f"  - 샘플 테스트: {len(complete_info['samples'])}개")
            print(f"  - 파일: problem_info.json, sample_tests.json")
            print(f"  🎉 requests 방식이 Selenium보다 훨씬 안정적이네요!")
        else:
            print(f"\n⚠️ {environment} 정보 수집 부분적 완료:")
            print(f"  - 제목: {complete_info['title']} (Level: {complete_info['level']})")
            print(f"  - 태그: {', '.join(complete_info['tags']) if complete_info['tags'] else 'N/A'}")
            print(f"  - 샘플 테스트: 0개 (스크래핑 실패)")
            print(f"  - 파일: problem_info.json, sample_tests.json")
            print(f"  ⚠️ 주의: 샘플 테스트가 없어 다음 단계에서 문제가 발생할 수 있습니다.")

    except IOError as e:
        print(f"\n❌ 파일 저장 오류: {e}")

if __name__ == "__main__":
    main()