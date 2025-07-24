#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (Selenium 최적화 버전)
이미지에서 확인된 HTML 구조에 맞춰 정확한 스크래핑
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
    except Exception as e:
        print(f"  ⚠️ solved.ac API 오류: {e}")
    
    return {}

def setup_optimized_chrome_driver():
    """최적화된 Chrome WebDriver 설정"""
    options = Options()
    
    # 기본 헤드리스 설정
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # 성능 최적화
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")  # 이미지 로딩 비활성화
    options.add_argument("--disable-javascript")  # JS 비활성화 (정적 HTML만 필요)
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    
    # 메모리 최적화
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=2048")
    
    # 실제 브라우저처럼 보이도록 설정
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 자동화 탐지 우회
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 자동화 탐지 우회 스크립트
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
            """
        })
        
        return driver
    except Exception as e:
        print(f"  ❌ ChromeDriver 설정 실패: {e}")
        return None

def extract_problem_info_from_html(html_content):
    """HTML에서 문제 정보 추출 (이미지 구조 기반)"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 문제가 존재하지 않는 경우 체크
    if "존재하지 않는 문제" in soup.text or "해당 문제를 찾을 수 없습니다" in soup.text:
        print("  ❌ 문제가 존재하지 않습니다.")
        return None

    problem_info = {}
    
    # 이미지에서 확인된 구조에 따른 정보 추출
    
    # 1. 문제 설명 (section id="description")
    desc_section = soup.find('section', {'id': 'description'})
    if desc_section:
        problem_info['description'] = desc_section.get_text(separator='\n', strip=True)
        print("  ✅ 문제 설명 추출 완료")
    else:
        # 대체 방법: div id="problem_description"
        desc_elem = soup.find('div', {'id': 'problem_description'})
        problem_info['description'] = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ""
    
    # 2. 입력 설명 (section id="input")
    input_section = soup.find('section', {'id': 'input'})
    if input_section:
        problem_info['input_format'] = input_section.get_text(separator='\n', strip=True)
        print("  ✅ 입력 형식 추출 완료")
    else:
        # 대체 방법
        input_elem = soup.find('div', {'id': 'problem_input'})
        problem_info['input_format'] = input_elem.get_text(separator='\n', strip=True) if input_elem else ""
    
    # 3. 출력 설명 (section id="output")
    output_section = soup.find('section', {'id': 'output'})
    if output_section:
        problem_info['output_format'] = output_section.get_text(separator='\n', strip=True)
        print("  ✅ 출력 형식 추출 완료")
    else:
        # 대체 방법
        output_elem = soup.find('div', {'id': 'problem_output'})
        problem_info['output_format'] = output_elem.get_text(separator='\n', strip=True) if output_elem else ""
    
    # 4. 힌트 (section id="hint")
    hint_section = soup.find('section', {'id': 'hint'})
    if hint_section:
        problem_info['hint'] = hint_section.get_text(separator='\n', strip=True)
        print("  ✅ 힌트 추출 완료")
    else:
        problem_info['hint'] = ""
    
    # 5. 제한사항 추출
    limit_elem = soup.find('div', {'id': 'problem_limit'})
    problem_info['limits'] = limit_elem.get_text(separator='\n', strip=True) if limit_elem else ""
    
    # 6. 샘플 테스트케이스 추출 (이미지 구조 기반)
    samples = []
    sample_count = 0
    
    # sampleinput1, sampleinput2, ... 형태로 찾기
    for i in range(1, 20):  # 최대 19개까지 확인
        input_section = soup.find('section', {'id': f'sampleinput{i}'})
        output_section = soup.find('section', {'id': f'sampleoutput{i}'})
        
        if input_section and output_section:
            # section 내부의 pre 태그에서 실제 데이터 추출
            input_pre = input_section.find('pre')
            output_pre = output_section.find('pre')
            
            if input_pre and output_pre:
                samples.append({
                    "input": input_pre.get_text(strip=True),
                    "output": output_pre.get_text(strip=True),
                })
                sample_count += 1
        else:
            # 대체 방법: sample-input-1, sample-output-1 형태
            input_elem = soup.find('pre', {'id': f'sample-input-{i}'})
            output_elem = soup.find('pre', {'id': f'sample-output-{i}'})
            
            if input_elem and output_elem:
                samples.append({
                    "input": input_elem.get_text(strip=True),
                    "output": output_elem.get_text(strip=True),
                })
                sample_count += 1
            else:
                break  # 더 이상 샘플이 없으면 중단
    
    problem_info['samples'] = samples
    print(f"  ✅ 샘플 테스트케이스 {sample_count}개 추출 완료")
    
    return problem_info

def scrape_boj_optimized(problem_id):
    """최적화된 Selenium 스크래핑"""
    print("  → 최적화된 Selenium 스크래핑 시작...")

    driver = setup_optimized_chrome_driver()
    if not driver:
        return None

    try:
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        print(f"  → 접속 중: {url}")
        
        # 페이지 로드
        driver.get(url)

        # problem-body가 로드될 때까지 대기 (이미지에서 확인된 구조)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "problem-body"))
            )
            print("  ✅ 페이지 로드 완료")
        except:
            print("  ⚠️ problem-body 요소를 찾지 못했습니다. 일반적인 방법으로 진행...")
        
        # 추가 로딩 대기
        time.sleep(2)

        # HTML 소스 가져오기
        html_content = driver.page_source
        
        # 문제 정보 추출
        problem_info = extract_problem_info_from_html(html_content)
        
        if problem_info and len(problem_info.get('samples', [])) > 0:
            print(f"  ✅ 스크래핑 성공!")
            return problem_info
        else:
            print("  ⚠️ 문제 정보를 찾지 못했습니다.")
            return None
        
    except Exception as e:
        print(f"  ❌ 스크래핑 중 오류: {str(e)[:100]}...")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def get_comprehensive_fallback_samples(problem_id):
    """확장된 fallback 샘플 데이터"""
    samples_db = {
        # 기본 입출력
        "1000": [{"input": "1 2", "output": "3"}],
        "2557": [{"input": "", "output": "Hello World!"}],
        "1001": [{"input": "5 4", "output": "1"}],
        "10998": [{"input": "3 4", "output": "12"}],
        "1008": [{"input": "1 3", "output": "0.3333333333333333"}],
        "10869": [{"input": "7 3", "output": "10\n4\n21\n2\n1"}],
        
        # 조건문
        "1330": [{"input": "1 2", "output": "<"}],
        "9498": [{"input": "100", "output": "A"}],
        "2753": [{"input": "2000", "output": "1"}],
        "14681": [{"input": "12\n5", "output": "1"}],
        "2884": [{"input": "10 10", "output": "9 50"}],
        
        # 반복문
        "2739": [{"input": "2", "output": "2 * 1 = 2\n2 * 2 = 4\n2 * 3 = 6\n2 * 4 = 8\n2 * 5 = 10\n2 * 6 = 12\n2 * 7 = 14\n2 * 8 = 16\n2 * 9 = 18"}],
        "10950": [{"input": "5\n1 1\n2 3\n3 4\n9 8\n5 2", "output": "2\n5\n7\n17\n7"}],
        "2741": [{"input": "3", "output": "1\n2\n3"}],
        "2742": [{"input": "3", "output": "3\n2\n1"}],
        "11021": [{"input": "5\n1 1\n2 3\n3 4\n9 8\n5 2", "output": "Case #1: 2\nCase #2: 5\nCase #3: 7\nCase #4: 17\nCase #5: 7"}],
        
        # 배열
        "10818": [{"input": "5\n20 10 35 30 7", "output": "7 35"}],
        "2562": [{"input": "3\n29\n38\n12\n57\n74\n40\n85\n61", "output": "85\n7"}],
        "3052": [{"input": "1\n2\n3\n4\n5\n6\n7\n8\n9\n0", "output": "10"}],
        
        # 문자열
        "11654": [{"input": "A", "output": "65"}],
        "11720": [{"input": "5\n54321", "output": "15"}],
        "10809": [{"input": "baekjoon", "output": "1 0 -1 -1 2 -1 -1 -1 -1 4 3 -1 -1 7 5 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1"}],
        
        # 그래프 출력
        "10171": [{"input": "", "output": "\\    /\\\n )  ( ')\n(  /  )\n \\(__)|"}],
        "10172": [{"input": "", "output": "|\\_/|\n|q p|   /}\n( 0 )\"\"\"\\\n|\"^\"`    |\n||_/=\\\\__|"}],
        
        # 수학
        "1712": [{"input": "1000 70 170", "output": "11"}],
        "2292": [{"input": "13", "output": "3"}],
        "1193": [{"input": "14", "output": "2/4"}],
        "2869": [{"input": "2 1 5", "output": "4"}],
        
        # 재귀
        "10872": [{"input": "10", "output": "3628800"}],
        "10870": [{"input": "10", "output": "55"}],
        "2447": [{"input": "3", "output": "***\n* *\n***"}]
    }
    
    return samples_db.get(str(problem_id), [{"input": "Sample input", "output": "Sample output"}])

def main():
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집 (최적화된 Selenium)')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    args = parser.parse_args()
    
    problem_id = args.problem_id
    
    print(f"📥 문제 {problem_id} 정보 수집 중...")
    
    # 1. solved.ac API로 기본 정보 수집
    print("  → solved.ac API 호출...")
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 2. 최적화된 Selenium 스크래핑 시도
    boj_info = scrape_boj_optimized(problem_id)
    
    # 3. 실패 시 fallback 데이터 사용
    if not boj_info:
        print("  → 스크래핑 실패, fallback 데이터 사용...")
        
        fallback_samples = get_comprehensive_fallback_samples(problem_id)
        boj_info = {
            "description": f"문제 {problem_id}의 상세 설명입니다. https://www.acmicpc.net/problem/{problem_id} 에서 확인하세요.",
            "input_format": "입력 형식을 확인하세요.",
            "output_format": "출력 형식을 확인하세요.",
            "limits": "시간/메모리 제한을 확인하세요.",
            "hint": "",
            "samples": fallback_samples
        }
        print(f"  ✅ fallback 샘플 {len(fallback_samples)}개 사용")
    
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
            
        print(f"\n✅ 문제 정보 수집 완료:")
        print(f"  - 제목: {complete_info['title']} (Level: {complete_info['level']})")
        print(f"  - 태그: {', '.join(complete_info['tags']) if complete_info['tags'] else 'N/A'}")
        print(f"  - 샘플 테스트: {len(complete_info['samples'])}개")
        print(f"  - 파일: problem_info.json, sample_tests.json")

    except IOError as e:
        print(f"\n❌ 파일 저장 오류: {e}")

if __name__ == "__main__":
    main()