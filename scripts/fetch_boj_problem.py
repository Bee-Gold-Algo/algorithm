#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (Selenium 적용)

[사전 준비]
이 스크립트를 실행하려면 Selenium과 webdriver-manager가 필요합니다.
아래 명령어로 설치해주세요.

pip install selenium webdriver-manager beautifulsoup4 requests
"""

import argparse
import json
import re
import requests
import time
from bs4 import BeautifulSoup

# Selenium 관련 라이브러리 임포트
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_solved_ac_info(problem_id):
    """solved.ac API에서 문제 정보 가져오기 (기존 코드와 동일)"""
    try:
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
        # 타임아웃을 넉넉하게 10초로 설정
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # 한국어 태그 이름을 우선적으로 가져오도록 수정
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
        print(f"solved.ac API 오류: {e}")
    
    return {}

def scrape_boj_with_selenium(problem_id):
    """Selenium을 사용하여 백준 문제 정보를 스크래핑합니다."""
    print("  → Selenium을 사용하여 스크래핑 시도...")

    # Selenium WebDriver 설정
    options = Options()
    options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 백그라운드에서 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3") # 불필요한 로그 메시지 줄이기
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = None
    try:
        # webdriver-manager가 자동으로 chromedriver를 설치하고 경로를 설정해줍니다.
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        driver.get(url)

        # 페이지의 핵심 콘텐츠(problem-body)가 로드될 때까지 최대 15초 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "problem-body"))
        )
        
        # JavaScript가 모두 렌더링된 후의 페이지 소스를 가져옵니다.
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 문제가 존재하지 않는 경우 확인
        if "존재하지 않는 문제" in soup.text:
            print("  ❌ 문제가 존재하지 않습니다.")
            return None

        # 문제 정보 추출
        problem_info = {}
        
        # 문제 설명
        desc_elem = soup.find('div', {'id': 'problem_description'})
        problem_info['description'] = desc_elem.get_text('\n', strip=True) if desc_elem else ""
        
        # 입력 형식
        input_elem = soup.find('div', {'id': 'problem_input'})
        problem_info['input_format'] = input_elem.get_text('\n', strip=True) if input_elem else ""
        
        # 출력 형식
        output_elem = soup.find('div', {'id': 'problem_output'})
        problem_info['output_format'] = output_elem.get_text('\n', strip=True) if output_elem else ""
        
        # 제한사항
        limit_elem = soup.find('div', {'id': 'problem_limit'})
        problem_info['limits'] = limit_elem.get_text('\n', strip=True) if limit_elem else ""
        
        # 샘플 입출력
        samples = []
        for i in range(1, 20): # 최대 20개의 예제를 탐색
            input_id = f'sample-input-{i}'
            output_id = f'sample-output-{i}'
            
            sample_input_elem = soup.find('pre', {'id': input_id})
            sample_output_elem = soup.find('pre', {'id': output_id})
            
            if sample_input_elem and sample_output_elem:
                samples.append({
                    "input": sample_input_elem.get_text(strip=True),
                    "output": sample_output_elem.get_text(strip=True),
                })
            else:
                # 더 이상 예제가 없으면 중단
                break
        
        problem_info['samples'] = samples
        print(f"  ✅ Selenium 스크래핑 성공! (샘플 {len(samples)}개 발견)")
        return problem_info
        
    except Exception as e:
        print(f"  ❌ Selenium 스크래핑 중 오류 발생: {e}")
        return None
    finally:
        # 드라이버가 성공적으로 생성되었다면 종료하여 리소스를 해제합니다.
        if driver:
            driver.quit()

def get_fallback_samples(problem_id):
    """스크래핑 실패 시 알려진 문제들의 샘플 제공 (기존 코드와 동일)"""
    known_samples = {
        "1000": [{"input": "1 2", "output": "3"}],
        "2557": [{"input": "", "output": "Hello World!"}],
        "1001": [{"input": "5 4", "output": "1"}],
        "10998": [{"input": "3 4", "output": "12"}],
        "1008": [{"input": "1 3", "output": "0.3333333333333333"}],
        "10869": [{"input": "7 3", "output": "10\n4\n21\n2\n1"}],
        "10171": [{"input": "", "output": "\\    /\\\n )  ( ')\n(  /  )\n \\(__)|"}],
        "10172": [{"input": "", "output": "|\\_/|\n|q p|   /}\n( 0 )\"\"\"\\\n|\"^\"`    |\n||_/=\\\\__|"}]
    }
    return known_samples.get(str(problem_id), [])

def main():
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집 스크립트')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    args = parser.parse_args()
    
    problem_id = args.problem_id
    
    print(f"📥 문제 {problem_id} 정보 수집 중...")
    
    # 1. solved.ac 정보 수집
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 2. 백준 상세 정보 수집 (Selenium 사용)
    boj_info = scrape_boj_with_selenium(problem_id)
    
    # 3. 스크래핑 실패 시 폴백 처리
    if not boj_info:
        print(f"  ::warning:: 문제 {problem_id}의 상세 정보 스크래핑에 실패했습니다. 기본값을 사용합니다.")
        
        fallback_samples = get_fallback_samples(problem_id)
        
        boj_info = {
            "description": f"문제 설명을 가져오지 못했습니다. 웹사이트에서 직접 확인해주세요.",
            "input_format": "입력 형식을 가져오지 못했습니다.",
            "output_format": "출력 형식을 가져오지 못했습니다.",
            "limits": "제한사항을 가져오지 못했습니다.",
            "samples": fallback_samples
        }
        
        if fallback_samples:
            print(f"  → 알려진 샘플 테스트케이스 {len(fallback_samples)}개를 사용합니다.")
    
    # 4. 정보 통합
    complete_info = {
        "problem_id": problem_id,
        "title": solved_ac_info.get("title", f"문제 {problem_id}"),
        "level": solved_ac_info.get("level", "N/A"),
        "tags": solved_ac_info.get("tags", []),
        **boj_info
    }
    
    # 5. JSON 파일로 저장
    try:
        with open('problem_info.json', 'w', encoding='utf-8') as f:
            json.dump(complete_info, f, ensure_ascii=False, indent=2)
        
        sample_tests = {
            "problem_id": problem_id,
            "test_cases": complete_info['samples']
        }
        
        with open('sample_tests.json', 'w', encoding='utf-8') as f:
            json.dump(sample_tests, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ 문제 정보 수집 완료:")
        print(f"  - 파일: problem_info.json, sample_tests.json")
        print(f"  - 제목: {complete_info['title']} (Level: {complete_info['level']})")
        print(f"  - 태그: {', '.join(complete_info['tags'])}")
        print(f"  - 샘플 테스트케이스: {len(complete_info['samples'])}개")

    except IOError as e:
        print(f"\n❌ 파일 저장 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
