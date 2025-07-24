#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (재시도 로직 포함 Selenium 최적화 버전)
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
    """최적화된 Selenium 스크래핑 (단일 시도)"""
    print("    → Selenium 스크래핑 시작...")

    driver = setup_optimized_chrome_driver()
    if not driver:
        print("    ❌ Chrome Driver 설정 실패")
        return None

    try:
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        print(f"    → 접속 중: {url}")
        
        # 페이지 로드
        driver.get(url)

        # problem-body가 로드될 때까지 대기
        try:
            WebDriverWait(driver, 30).until(  # 60초 → 30초로 단축
                EC.presence_of_element_located((By.ID, "problem-body"))
            )
            print("    ✅ 페이지 로드 완료")
        except:
            print("    ⚠️ problem-body 요소를 찾지 못했습니다. 일반적인 방법으로 진행...")
        
        # 추가 로딩 대기 (단축)
        time.sleep(3)  # 5초 → 3초로 단축

        # HTML 소스 가져오기
        html_content = driver.page_source
        
        # 페이지 응답 확인
        if "존재하지 않는 문제" in html_content or len(html_content) < 1000:
            print("    ❌ 유효하지 않은 페이지 응답")
            return None
        
        # 문제 정보 추출
        problem_info = extract_problem_info_from_html(html_content)
        
        if problem_info and len(problem_info.get('samples', [])) > 0:
            print(f"    ✅ 스크래핑 성공! (샘플 {len(problem_info['samples'])}개)")
            return problem_info
        else:
            print("    ⚠️ 문제 정보를 찾지 못했습니다.")
            return None
        
    except Exception as e:
        print(f"    ❌ 스크래핑 중 오류: {str(e)[:100]}...")
        return None
    finally:
        if driver:
            try:
                driver.quit()
                print("    🔧 Chrome Driver 종료")
            except:
                pass

def scrape_boj_with_strategy(problem_id, strategy):
    """특정 전략으로 스크래핑"""
    print(f"    → 전략적 스크래핑 시작 (타임아웃: {strategy['timeout']}초)")

    driver = setup_optimized_chrome_driver()
    if not driver:
        return None

    try:
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        print(f"    → 접속 중: {url}")
        
        # 페이지 로드
        driver.get(url)

        # 전략에 따른 대기
        try:
            WebDriverWait(driver, strategy['timeout']).until(
                EC.presence_of_element_located((By.ID, "problem-body"))
            )
            print("    ✅ 페이지 로드 완료")
        except:
            print("    ⚠️ 타임아웃, 일반적인 방법으로 진행...")
        
        # 전략에 따른 추가 대기
        time.sleep(strategy['extra_wait'])

        # HTML 소스 가져오기
        html_content = driver.page_source
        
        # 문제 정보 추출
        problem_info = extract_problem_info_from_html(html_content)
        
        if problem_info and len(problem_info.get('samples', [])) > 0:
            print(f"    ✅ 전략적 스크래핑 성공!")
            return problem_info
        else:
            print("    ⚠️ 전략적 스크래핑 실패")
            return None
        
    except Exception as e:
        print(f"    ❌ 전략적 스크래핑 중 오류: {str(e)[:50]}...")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def scrape_boj_with_retry(problem_id, max_attempts=3, initial_delay=5):
    """여러 번 시도하는 백준 스크래핑 함수"""
    print(f"  🔄 백준 스크래핑 시작 (최대 {max_attempts}회 시도)")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n  📍 시도 {attempt}/{max_attempts}")
        
        # 재시도 간격 (점진적 증가)
        if attempt > 1:
            delay = initial_delay * (attempt - 1)
            print(f"  ⏳ {delay}초 대기 중...")
            time.sleep(delay)
        
        # 스크래핑 시도
        result = scrape_boj_optimized(problem_id)
        
        if result and len(result.get('samples', [])) > 0:
            print(f"  🎉 {attempt}번째 시도에서 성공!")
            return result
        else:
            if attempt < max_attempts:
                print(f"  ❌ {attempt}번째 시도 실패, 재시도 준비...")
            else:
                print(f"  💥 모든 시도 실패 ({max_attempts}회)")
    
    return None

def scrape_boj_aggressive_retry(problem_id, max_attempts=5):
    """더 적극적인 재시도 전략"""
    print(f"  🚀 적극적 스크래핑 모드 (최대 {max_attempts}회 시도)")
    
    # 다양한 대기 시간과 설정으로 시도
    strategies = [
        {"delay": 3, "timeout": 20, "extra_wait": 2},   # 빠른 시도
        {"delay": 5, "timeout": 30, "extra_wait": 3},   # 기본 시도  
        {"delay": 8, "timeout": 45, "extra_wait": 5},   # 느린 시도
        {"delay": 12, "timeout": 60, "extra_wait": 8},  # 매우 느린 시도
        {"delay": 15, "timeout": 90, "extra_wait": 10}, # 초느린 시도
    ]
    
    for attempt in range(1, min(max_attempts + 1, len(strategies) + 1)):
        strategy = strategies[attempt - 1]
        print(f"\n  📍 시도 {attempt}/{max_attempts} (전략: {strategy['timeout']}초 타임아웃)")
        
        # 재시도 간격
        if attempt > 1:
            print(f"  ⏳ {strategy['delay']}초 대기 중...")
            time.sleep(strategy['delay'])
        
        # 맞춤형 스크래핑 시도
        result = scrape_boj_with_strategy(problem_id, strategy)
        
        if result and len(result.get('samples', [])) > 0:
            print(f"  🎉 {attempt}번째 시도에서 성공!")
            return result
        else:
            if attempt < max_attempts:
                print(f"  ❌ {attempt}번째 시도 실패, 다른 전략으로 재시도...")
            else:
                print(f"  💥 모든 전략 실패 ({max_attempts}회)")
    
    return None

def main():
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집 (재시도 로직 포함)')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    parser.add_argument('--retry-mode', choices=['basic', 'aggressive'], default='basic', 
                       help='재시도 모드 (basic: 3회, aggressive: 5회)')
    args = parser.parse_args()
    
    problem_id = args.problem_id
    
    print(f"📥 문제 {problem_id} 정보 수집 중...")
    
    # 1. solved.ac API로 기본 정보 수집
    print("  → solved.ac API 호출...")
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 2. 재시도 모드에 따른 스크래핑
    if args.retry_mode == 'aggressive':
        boj_info = scrape_boj_aggressive_retry(problem_id, max_attempts=5)
    else:
        boj_info = scrape_boj_with_retry(problem_id, max_attempts=3)
    
    # 3. 스크래핑 실패 시 처리
    if not boj_info:
        print("\n  ❌ 모든 스크래핑 시도 실패")
        print("  💡 문제 정보를 수동으로 확인해주세요:")
        print(f"     https://www.acmicpc.net/problem/{problem_id}")
        
        # 최소한의 구조만 제공 (빈 샘플)
        boj_info = {
            "description": f"문제 {problem_id}의 상세 설명을 확인할 수 없습니다. 링크에서 직접 확인하세요.",
            "input_format": "입력 형식을 직접 확인하세요.",
            "output_format": "출력 형식을 직접 확인하세요.",
            "limits": "시간/메모리 제한을 직접 확인하세요.",
            "hint": "",
            "samples": []  # 빈 샘플 리스트
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
        
        if len(complete_info['samples']) > 0:
            print(f"\n✅ 문제 정보 수집 완료:")
            print(f"  - 제목: {complete_info['title']} (Level: {complete_info['level']})")
            print(f"  - 태그: {', '.join(complete_info['tags']) if complete_info['tags'] else 'N/A'}")
            print(f"  - 샘플 테스트: {len(complete_info['samples'])}개")
            print(f"  - 파일: problem_info.json, sample_tests.json")
        else:
            print(f"\n⚠️ 문제 정보 수집 부분적 완료:")
            print(f"  - 제목: {complete_info['title']} (Level: {complete_info['level']})")
            print(f"  - 태그: {', '.join(complete_info['tags']) if complete_info['tags'] else 'N/A'}")
            print(f"  - 샘플 테스트: 0개 (스크래핑 실패)")
            print(f"  - 파일: problem_info.json, sample_tests.json")
            print(f"  ⚠️ 주의: 샘플 테스트가 없어 다음 단계에서 문제가 발생할 수 있습니다.")

    except IOError as e:
        print(f"\n❌ 파일 저장 오류: {e}")

if __name__ == "__main__":
    main()