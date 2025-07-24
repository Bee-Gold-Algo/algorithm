#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (GitHub Actions 환경 최적화)

[사전 준비]
pip install selenium beautifulsoup4 requests webdriver-manager
"""

import argparse
import json
import requests
from bs4 import BeautifulSoup
import time
import os

# Selenium 관련 라이브러리 임포트
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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
    except requests.exceptions.RequestException as e:
        print(f"solved.ac API 요청 오류: {e}")
    except Exception as e:
        print(f"solved.ac API 처리 중 알 수 없는 오류: {e}")
    
    return {}

def setup_chrome_driver():
    """Chrome WebDriver 설정 (GitHub Actions 최적화)"""
    options = Options()
    
    # 필수 옵션들
    options.add_argument("--headless=new")  # 새로운 헤드리스 모드 사용
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")  # JS 비활성화로 속도 향상
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    
    # 메모리 사용량 최적화
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=4096")
    
    # User Agent 설정
    options.add_argument("user-agent=Mozilla/5.0 (Linux; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 자동화 탐지 우회
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # webdriver-manager를 사용하여 ChromeDriver 자동 관리
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 자동화 탐지 우회 스크립트 실행
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
            """
        })
        
        return driver
    except Exception as e:
        print(f"ChromeDriver 설정 실패: {e}")
        return None

def scrape_boj_with_selenium(problem_id):
    """Selenium을 사용하여 백준 문제 정보를 스크래핑합니다."""
    print("  → Selenium을 사용하여 스크래핑 시도...")

    driver = setup_chrome_driver()
    if not driver:
        print("  ❌ WebDriver 초기화 실패")
        return None

    try:
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        print(f"  → 접속 중: {url}")
        
        driver.get(url)

        # 페이지 로드 대기 (최대 20초)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "problem-body"))
        )
        
        # 추가 로딩 시간
        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        if "존재하지 않는 문제" in soup.text:
            print("  ❌ 문제가 존재하지 않습니다.")
            return None

        problem_info = {}
        
        # 문제 정보 추출
        desc_elem = soup.find('div', {'id': 'problem_description'})
        problem_info['description'] = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ""
        
        input_elem = soup.find('div', {'id': 'problem_input'})
        problem_info['input_format'] = input_elem.get_text(separator='\n', strip=True) if input_elem else ""
        
        output_elem = soup.find('div', {'id': 'problem_output'})
        problem_info['output_format'] = output_elem.get_text(separator='\n', strip=True) if output_elem else ""
        
        limit_elem = soup.find('div', {'id': 'problem_limit'})
        problem_info['limits'] = limit_elem.get_text(separator='\n', strip=True) if limit_elem else ""
        
        # 샘플 테스트케이스 추출
        samples = []
        for i in range(1, 20):
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
                break
        
        problem_info['samples'] = samples
        print(f"  ✅ Selenium 스크래핑 성공! (샘플 {len(samples)}개 발견)")
        return problem_info
        
    except Exception as e:
        print(f"  ❌ Selenium 스크래핑 중 오류 발생: {e}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def scrape_boj_with_requests(problem_id):
    """requests를 사용한 백업 스크래핑 방법"""
    print("  → requests를 사용하여 백업 스크래핑 시도...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if "존재하지 않는 문제" in soup.text:
            print("  ❌ 문제가 존재하지 않습니다.")
            return None

        problem_info = {}
        
        desc_elem = soup.find('div', {'id': 'problem_description'})
        problem_info['description'] = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ""
        
        input_elem = soup.find('div', {'id': 'problem_input'})
        problem_info['input_format'] = input_elem.get_text(separator='\n', strip=True) if input_elem else ""
        
        output_elem = soup.find('div', {'id': 'problem_output'})
        problem_info['output_format'] = output_elem.get_text(separator='\n', strip=True) if output_elem else ""
        
        limit_elem = soup.find('div', {'id': 'problem_limit'})
        problem_info['limits'] = limit_elem.get_text(separator='\n', strip=True) if limit_elem else ""
        
        samples = []
        for i in range(1, 20):
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
                break
        
        problem_info['samples'] = samples
        print(f"  ✅ requests 스크래핑 성공! (샘플 {len(samples)}개 발견)")
        return problem_info
        
    except Exception as e:
        print(f"  ❌ requests 스크래핑 중 오류 발생: {e}")
        return None

def get_fallback_samples(problem_id):
    """스크래핑 실패 시 알려진 문제들의 샘플 제공"""
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
    
    # solved.ac API로 기본 정보 수집
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 스크래핑 시도 (Selenium -> requests -> fallback 순서)
    boj_info = scrape_boj_with_selenium(problem_id)
    
    if not boj_info:
        print("  → Selenium 실패, requests로 재시도...")
        boj_info = scrape_boj_with_requests(problem_id)
    
    if not boj_info:
        print(f"  → 모든 스크래핑 방법 실패, 기본값 사용...")
        
        fallback_samples = get_fallback_samples(problem_id)
        boj_info = {
            "description": "문제 설명을 가져오지 못했습니다. 웹사이트에서 직접 확인해주세요.",
            "input_format": "입력 형식을 가져오지 못했습니다.",
            "output_format": "출력 형식을 가져오지 못했습니다.",
            "limits": "제한사항을 가져오지 못했습니다.",
            "samples": fallback_samples
        }
        
        if fallback_samples:
            print(f"  → 알려진 샘플 테스트케이스 {len(fallback_samples)}개를 사용합니다.")
    
    # 결과 저장
    complete_info = {
        "problem_id": problem_id,
        "title": solved_ac_info.get("title", f"문제 {problem_id}"),
        "level": solved_ac_info.get("level", "N/A"),
        "tags": solved_ac_info.get("tags", []),
        **boj_info
    }
    
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