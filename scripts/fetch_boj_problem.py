#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (뷰포트 모드 고정 - 우회 최적화)
GitHub Actions 환경에서 자연스러운 브라우저 환경 구현
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

def setup_viewport_chrome_driver():
    """뷰포트 모드 Chrome WebDriver 설정 (우회 최적화)"""
    options = Options()
    
    print("  🌐 뷰포트 모드 브라우저 설정 중...")
    
    # 뷰포트 모드 설정 (헤드리스 비활성화)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    
    # GitHub Actions 환경 대응
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    
    # 가상 디스플레이 설정 (GitHub Actions용)
    options.add_argument("--virtual-time-budget=60000")
    options.add_argument("--run-all-compositor-stages-before-draw")
    
    # 자연스러운 브라우저 환경 구성
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-extensions")
    options.add_argument("--allow-running-insecure-content")
    
    # JavaScript와 이미지 로딩 활성화 (자연스러운 환경)
    print("  ⚡ JavaScript 및 이미지 로딩 활성화")
    
    # 로그 레벨 조정
    options.add_argument("--log-level=1")
    options.add_argument("--enable-logging")
    options.add_argument("--v=1")
    
    # 메모리 최적화
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=4096")
    
    # 실제 사용자 브라우저 환경 시뮬레이션
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 고급 우회 설정
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 추가 우회 옵션
    options.add_argument("--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer")
    options.add_argument("--disable-ipc-flooding-protection")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 고급 우회 스크립트
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            // 자동화 탐지 우회
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            });
            
            // 추가 속성 조작
            Object.defineProperty(navigator, 'plugins', {
              get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
              get: () => ['ko-KR', 'ko', 'en-US', 'en']
            });
            
            // 화면 해상도 설정
            Object.defineProperty(screen, 'width', {
              get: () => 1920
            });
            Object.defineProperty(screen, 'height', {
              get: () => 1080
            });
            """
        })
        
        # 브라우저 창 크기 설정
        driver.set_window_size(1920, 1080)
        
        window_size = driver.get_window_size()
        print(f"  ✅ 뷰포트 브라우저 초기화 완료 (해상도: {window_size['width']}x{window_size['height']})")
        
        return driver
    except Exception as e:
        print(f"  ❌ 뷰포트 브라우저 설정 실패: {e}")
        return None

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

def scrape_boj_with_viewport(problem_id):
    """뷰포트 모드로 백준 스크래핑"""
    print("  🌐 뷰포트 모드 스크래핑 시작...")

    driver = setup_viewport_chrome_driver()
    if not driver:
        print("  ❌ 뷰포트 브라우저 설정 실패")
        return None

    try:
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        print(f"  → 페이지 접속: {url}")
        
        # 페이지 로드
        driver.get(url)
        
        # 페이지 로딩 대기
        print("  ⏳ 페이지 로딩 및 JavaScript 실행 대기...")
        time.sleep(3)

        # DOM 요소 로드 대기
        try:
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.ID, "problem-body"))
            )
            print("  ✅ 페이지 DOM 로드 완료")
        except:
            print("  ⚠️ DOM 로드 타임아웃, 현재 상태로 진행...")
        
        # 추가 안정화 대기
        print("  ⏳ 페이지 안정화 대기...")
        time.sleep(5)

        # 페이지 정보 확인
        current_url = driver.current_url
        page_title = driver.title
        html_content = driver.page_source
        
        print(f"  📄 페이지 제목: {page_title}")
        print(f"  🌐 현재 URL: {current_url}")
        print(f"  📏 HTML 크기: {len(html_content):,} 문자")
        
        # 페이지 유효성 검사
        if "존재하지 않는 문제" in html_content or len(html_content) < 1000:
            print("  ❌ 유효하지 않은 페이지 응답")
            return None
        
        # 페이지 스크롤 (모든 요소 로드 보장)
        print("  📜 페이지 스크롤하여 모든 요소 로드...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # 최종 HTML 획득
        final_html = driver.page_source
        print(f"  📏 최종 HTML 크기: {len(final_html):,} 문자")
        
        # 문제 정보 추출
        problem_info = extract_problem_info_from_html(final_html)
        
        if problem_info and len(problem_info.get('samples', [])) > 0:
            print(f"  🎉 뷰포트 스크래핑 성공! (샘플 {len(problem_info['samples'])}개)")
            return problem_info
        else:
            print("  ⚠️ 문제 정보 추출 실패")
            return None
        
    except Exception as e:
        print(f"  ❌ 뷰포트 스크래핑 중 오류: {str(e)[:100]}...")
        return None
    finally:
        if driver:
            try:
                print("  🔧 브라우저 정리 중...")
                driver.quit()
                print("  ✅ 브라우저 종료 완료")
            except:
                pass

def scrape_boj_with_retry(problem_id, max_attempts=3, initial_delay=5):
    """재시도 로직을 포함한 뷰포트 스크래핑"""
    print(f"  🔄 뷰포트 모드 스크래핑 시작 (최대 {max_attempts}회 시도)")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n  📍 시도 {attempt}/{max_attempts}")
        
        if attempt > 1:
            delay = initial_delay * (attempt - 1)
            print(f"  ⏳ {delay}초 대기 후 재시도...")
            time.sleep(delay)
        
        result = scrape_boj_with_viewport(problem_id)
        
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
    """적극적 재시도 전략"""
    print(f"  🚀 적극적 뷰포트 스크래핑 모드 (최대 {max_attempts}회 시도)")
    
    delays = [3, 5, 8, 12, 15]  # 재시도 간격
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n  📍 시도 {attempt}/{max_attempts} (지연: {delays[attempt-1]}초)")
        
        if attempt > 1:
            print(f"  ⏳ {delays[attempt-1]}초 대기 후 재시도...")
            time.sleep(delays[attempt-1])
        
        result = scrape_boj_with_viewport(problem_id)
        
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
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집 (뷰포트 모드 고정)')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    parser.add_argument('--retry-mode', choices=['basic', 'aggressive'], default='basic', 
                       help='재시도 모드 (basic: 3회, aggressive: 5회)')
    args = parser.parse_args()
    
    problem_id = args.problem_id
    
    print(f"📥 문제 {problem_id} 정보 수집 중...")
    print("🌐 뷰포트 모드로 고정 실행 (자연스러운 브라우저 환경)")
    print("  ⚡ JavaScript 및 이미지 로딩 활성화")
    print("  🛡️ 고급 우회 기능 적용")
    
    # 1. solved.ac API로 기본 정보 수집
    print("\n  → solved.ac API 호출...")
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 2. 재시도 모드에 따른 뷰포트 스크래핑
    if args.retry_mode == 'aggressive':
        boj_info = scrape_boj_aggressive_retry(problem_id, max_attempts=5)
    else:
        boj_info = scrape_boj_with_retry(problem_id, max_attempts=3)
    
    # 3. 스크래핑 실패 시 처리
    if not boj_info:
        print("\n  ❌ 모든 뷰포트 스크래핑 시도 실패")
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
        
        if len(complete_info['samples']) > 0:
            print(f"\n✅ 뷰포트 모드 스크래핑 완료:")
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