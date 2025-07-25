#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 크롤링으로만 수집합니다. (GitHub Actions 최적화)
Anti-bot 시스템을 우회하여 안정적인 크롤링을 수행합니다.
"""

import argparse
import json
import requests
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError
import time
import os
import random
import re

def get_solved_ac_info(problem_id):
    """solved.ac API에서 문제의 기본 정보(제목, 레벨, 태그)를 가져옵니다."""
    print("\n📡 solved.ac API에서 정보 조회 중...")
    try:
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            # 한국어 태그 이름을 우선적으로 찾아서 추출합니다.
            tags = []
            for tag_data in data.get("tags", []):
                korean_name = next((d['name'] for d in tag_data.get('displayNames', []) if d['language'] == 'ko'), None)
                if korean_name:
                    tags.append(korean_name)
            
            print(f"  ✅ solved.ac 정보: {data.get('titleKo', '')}, 레벨: {data.get('level', 0)}")
            return {
                "title": data.get("titleKo", f"문제 {problem_id}"),
                "level": data.get("level", "N/A"),
                "tags": tags
            }
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ solved.ac API 호출 오류: {e}")
    except json.JSONDecodeError:
        print("  ⚠️ solved.ac API 응답이 올바른 JSON 형식이 아닙니다.")
    
    # API 호출 실패 시 기본 정보를 반환합니다.
    return {
        "title": f"문제 {problem_id}",
        "level": "N/A",
        "tags": []
    }

def save_debug_info(page: Page, prefix: str):
    """실패 시 디버깅을 위해 스크린샷과 HTML을 저장합니다."""
    try:
        screenshot_path = f"{prefix}_screenshot.png"
        html_path = f"{prefix}_page.html"
        
        print(f"  ℹ️ 디버그 정보 저장 중...")
        page.screenshot(path=screenshot_path, full_page=True)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
            
        print(f"  ✅ 디버그 정보 저장 완료: {screenshot_path}, {html_path}")
    except Exception as e:
        print(f"  ⚠️ 디버그 정보 저장 중 오류 발생: {e}")

def wait_for_element_with_retry(page: Page, selectors: list, timeout: int = 30000):
    """여러 선택자를 시도하여 요소가 나타날 때까지 대기합니다."""
    for selector in selectors:
        try:
            print(f"  - '{selector}' 요소 대기 중...")
            page.wait_for_selector(selector, state='visible', timeout=timeout)
            print(f"  ✅ '{selector}' 요소 발견!")
            return True
        except PlaywrightTimeoutError:
            print(f"  - '{selector}' 요소를 찾지 못했습니다.")
            continue
    return False

def extract_text_content(page: Page, selectors: list) -> str:
    """여러 선택자를 시도하여 텍스트 내용을 추출합니다."""
    for selector in selectors:
        try:
            locator = page.locator(selector)
            if locator.count() > 0:
                content = locator.first.text_content(timeout=10000)
                if content and content.strip():
                    return content.strip()
        except Exception:
            continue
    return ""

def extract_problem_details_comprehensive(page: Page):
    """포괄적인 크롤링으로 문제 상세 정보를 추출합니다."""
    print("  🔍 문제 상세 정보 추출 시작...")
    
    # 페이지가 로드될 때까지 기다리기
    time.sleep(3)
    
    # 여러 가능한 컨테이너 확인
    container_selectors = [
        '#problem-body',
        '.problem-body', 
        '#problemset',
        '.container',
        'main',
        'body'
    ]
    
    if not wait_for_element_with_retry(page, container_selectors, 45000):
        print("  ❌ 문제 컨테이너를 찾을 수 없습니다.")
        return None

    # "문제를 찾을 수 없습니다" 체크
    error_messages = [
        '*:text("문제를 찾을 수 없습니다")',
        '*:text("Problem not found")',
        '*:text("404")',
        '.error-message'
    ]
    
    for error_selector in error_messages:
        if page.locator(error_selector).count() > 0:
            print(f"  ❌ 오류 메시지 발견: {error_selector}")
            return None

    problem_details = {}

    # 문제 설명 추출
    description_selectors = [
        '#problem_description',
        '.problem_description',
        'div[id*="description"]',
        'div[class*="description"]',
        '.problem-text',
        'section:has-text("문제") + section',
        'div:has-text("문제") + div',
        'h2:text("문제") + div',
        '.panel:has(h3:text("문제")) .panel-body',
        '#problem_description > p',
        '.problem-statement'
    ]
    
    description = extract_text_content(page, description_selectors)
    if description:
        problem_details['description'] = description
        print("  ✅ 문제 설명 추출 완료")
    else:
        print("  ⚠️ 문제 설명을 찾지 못했습니다.")
        # 전체 페이지에서 긴 텍스트 블록 찾기
        try:
            all_text_elements = page.locator('div, p, section').all()
            for element in all_text_elements:
                text = element.text_content()
                if text and len(text.strip()) > 50 and '문제' in text:
                    problem_details['description'] = text.strip()
                    print("  ✅ 문제 설명을 전체 검색으로 발견")
                    break
        except:
            pass

    # 입력 형식 추출
    input_selectors = [
        '#problem_input',
        '.problem_input',
        'div[id*="input"]',
        'div[class*="input"]',
        'section:has-text("입력") + section',
        'div:has-text("입력") + div',
        'h2:text("입력") + div',
        '.panel:has(h3:text("입력")) .panel-body'
    ]
    
    input_format = extract_text_content(page, input_selectors)
    if input_format:
        problem_details['input_format'] = input_format
        print("  ✅ 입력 형식 추출 완료")

    # 출력 형식 추출
    output_selectors = [
        '#problem_output',
        '.problem_output',
        'div[id*="output"]',
        'div[class*="output"]',
        'section:has-text("출력") + section',
        'div:has-text("출력") + div',
        'h2:text("출력") + div',
        '.panel:has(h3:text("출력")) .panel-body'
    ]
    
    output_format = extract_text_content(page, output_selectors)
    if output_format:
        problem_details['output_format'] = output_format
        print("  ✅ 출력 형식 추출 완료")

    # 제한사항 추출
    limits_selectors = [
        '#problem_limit',
        '.problem_limit',
        'div[id*="limit"]',
        'div[class*="limit"]',
        'section:has-text("제한") + section',
        'div:has-text("제한") + div',
        'h2:text("제한") + div',
        '.panel:has(h3:text("제한")) .panel-body'
    ]
    
    limits = extract_text_content(page, limits_selectors)
    if limits:
        problem_details['limits'] = limits
        print("  ✅ 제한사항 추출 완료")

    # 힌트 추출
    hint_selectors = [
        '#problem_hint',
        '.problem_hint',
        'div[id*="hint"]',
        'div[class*="hint"]',
        'section:has-text("힌트") + section',
        'div:has-text("힌트") + div',
        'h2:text("힌트") + div',
        '.panel:has(h3:text("힌트")) .panel-body'
    ]
    
    hint = extract_text_content(page, hint_selectors)
    if hint:
        problem_details['hint'] = hint
        print("  ✅ 힌트 추출 완료")

    # 예제 테스트케이스 추출
    samples = []
    sample_input_selectors = [
        'pre[id^="sample-input-"]',
        'pre[class*="sample-input"]',
        '.sampledata input',
        '.sample-input',
        'pre:has-text("입력")',
        'div[class*="sample"] pre'
    ]
    
    print("  🔍 예제 테스트케이스 검색 중...")
    
    # 다양한 방법으로 예제 찾기
    for selector in sample_input_selectors:
        try:
            input_elements = page.locator(selector).all()
            if len(input_elements) > 0:
                print(f"  - '{selector}'로 {len(input_elements)}개의 예제 입력 발견")
                
                for i, input_element in enumerate(input_elements):
                    try:
                        input_text = input_element.text_content()
                        if input_text and input_text.strip():
                            # 해당 출력 찾기
                            input_id = input_element.get_attribute('id')
                            output_text = ""
                            
                            if input_id and 'input' in input_id:
                                output_id = input_id.replace('input', 'output')
                                output_element = page.locator(f'#{output_id}')
                                if output_element.count() > 0:
                                    output_text = output_element.text_content()
                            
                            # ID 방식이 실패하면 다음 pre 요소 찾기
                            if not output_text:
                                next_pre = input_element.locator('xpath=following::pre[1]')
                                if next_pre.count() > 0:
                                    output_text = next_pre.text_content()
                            
                            samples.append({
                                "input": input_text.strip(),
                                "output": output_text.strip() if output_text else ""
                            })
                    except Exception as e:
                        print(f"    ⚠️ 예제 {i+1} 처리 중 오류: {e}")
                        continue
                
                if samples:
                    break
        except Exception as e:
            continue
    
    # 예제를 찾지 못한 경우 페이지 전체에서 검색
    if not samples:
        print("  🔍 전체 페이지에서 예제 검색 중...")
        try:
            # 모든 pre 태그에서 입출력 패턴 찾기
            all_pre_elements = page.locator('pre').all()
            for i, pre in enumerate(all_pre_elements):
                text = pre.text_content()
                if text and text.strip():
                    # 간단한 패턴으로 입력/출력 구분
                    if len(text.strip().split('\n')) <= 3 and len(text.strip()) < 100:
                        if i + 1 < len(all_pre_elements):
                            next_text = all_pre_elements[i + 1].text_content()
                            if next_text and next_text.strip():
                                samples.append({
                                    "input": text.strip(),
                                    "output": next_text.strip()
                                })
                                if len(samples) >= 3:  # 최대 3개까지만
                                    break
        except Exception as e:
            print(f"  ⚠️ 전체 예제 검색 중 오류: {e}")

    problem_details['samples'] = samples
    if samples:
        print(f"  ✅ 예제 테스트케이스 {len(samples)}개 추출 완료")
    else:
        print("  ⚠️ 예제 테스트케이스를 찾지 못했습니다.")

    return problem_details if any(v for v in problem_details.values() if v) else None

def advanced_crawling_strategy(problem_id: str, max_retries: int = 5):
    """고급 크롤링 전략으로 백준 문제 정보를 수집합니다."""
    url = f"https://www.acmicpc.net/problem/{problem_id}"
    print(f"\n🚀 고급 크롤링 시작 (최대 {max_retries}회 시도)")
    print(f"   URL: {url}")

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]

    with sync_playwright() as p:
        for attempt in range(1, max_retries + 1):
            browser = None
            page = None
            try:
                print(f"\n  🎯 [시도 {attempt}/{max_retries}]")
                
                # 랜덤 User-Agent 선택
                user_agent = random.choice(user_agents)
                print(f"  🎭 User-Agent: {user_agent[:50]}...")
                
                # 강화된 브라우저 설정
                browser_args = [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-web-security",
                    "--allow-running-insecure-content",
                    "--ignore-certificate-errors",
                    "--ignore-ssl-errors",
                    "--ignore-certificate-errors-spki-list",
                    "--disable-extensions",
                    "--disable-plugins",
                    "--disable-images",  # 이미지 로딩 비활성화로 속도 향상
                    f"--user-agent={user_agent}"
                ]
                
                browser = p.chromium.launch(
                    headless=True,
                    args=browser_args
                )
                
                # 실제 브라우저 환경 시뮬레이션
                context = browser.new_context(
                    user_agent=user_agent,
                    viewport={'width': 1920, 'height': 1080},
                    ignore_https_errors=True,
                    java_script_enabled=True,
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"Linux"',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        'DNT': '1'
                    }
                )
                
                page = context.new_page()
                page.set_default_timeout(120000)

                # 단계별 접근
                print("  🌐 페이지 접속 중...")
                
                # 먼저 메인 페이지 방문 (세션 설정)
                try:
                    page.goto('https://www.acmicpc.net/', wait_until='domcontentloaded', timeout=60000)
                    time.sleep(random.uniform(1, 3))
                except:
                    print("  ⚠️ 메인 페이지 접근 실패, 직접 문제 페이지로 이동")
                
                # 문제 페이지 접근
                print(f"  📄 문제 페이지 로딩... (시도 {attempt})")
                page.goto(url, wait_until='domcontentloaded', timeout=120000)
                
                # 랜덤 대기 (사람처럼 행동)
                wait_time = random.uniform(3, 8)
                print(f"  ⏳ {wait_time:.1f}초 대기 (사람 행동 모방)...")
                time.sleep(wait_time)
                
                # 스크롤링으로 페이지 활성화
                print("  📜 페이지 스크롤링...")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
                time.sleep(1)
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(1)
                
                # 네트워크 안정화 대기
                try:
                    page.wait_for_load_state('networkidle', timeout=30000)
                except:
                    print("  ⚠️ 네트워크 안정화 대기 시간 초과, 계속 진행")
                
                print("  🔍 문제 정보 추출 시작...")
                problem_details = extract_problem_details_comprehensive(page)

                if problem_details and problem_details.get('description'):
                    print("\n  🎉 크롤링 성공!")
                    return problem_details
                else:
                    print("  ⚠️ 유효한 문제 정보를 찾지 못했습니다.")
                    save_debug_info(page, f"attempt_{attempt}")
                    
                    # 재시도 전 대기시간 증가
                    retry_wait = 5 + (attempt * 3) + random.uniform(0, 5)
                    print(f"  ⏳ {retry_wait:.1f}초 후 재시도...")
                    time.sleep(retry_wait)

            except Exception as e:
                print(f"  ❌ 시도 {attempt}에서 오류 발생: {e}")
                if page:
                    save_debug_info(page, f"error_attempt_{attempt}")
                
                if attempt < max_retries:
                    error_wait = 10 + (attempt * 5) + random.uniform(0, 10)
                    print(f"  ⏳ {error_wait:.1f}초 후 재시도...")
                    time.sleep(error_wait)
                else:
                    print("  💥 최대 재시도 횟수를 초과했습니다.")
            finally:
                if browser:
                    browser.close()

    print("\n💥 모든 크롤링 시도에 실패했습니다.")
    return None

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='백준 문제 정보 크롤링 전용 스크립트')
    parser.add_argument('--problem-id', required=True, help='수집할 백준 문제의 번호')
    args = parser.parse_args()

    problem_id = args.problem_id
    
    # solved.ac API로 기본 정보 수집
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 크롤링으로 상세 정보 수집
    print(f"\n🎯 문제 {problem_id} 크롤링 시작...")
    boj_details = advanced_crawling_strategy(problem_id)

    if not boj_details:
        print(f"\n❌ 문제 {problem_id} 크롤링 최종 실패")
        print("GitHub Actions 아티팩트에서 디버그 정보를 확인하세요.")
        exit(1)  # 실패 시 종료 코드 1로 종료

    # 최종 정보 조합
    complete_info = { 
        "problem_id": problem_id, 
        **solved_ac_info, 
        **boj_details 
    }

    try:
        with open('problem_info.json', 'w', encoding='utf-8') as f:
            json.dump(complete_info, f, ensure_ascii=False, indent=2)
        
        sample_tests = { 
            "problem_id": problem_id, 
            "test_cases": complete_info.get('samples', []) 
        }
        with open('sample_tests.json', 'w', encoding='utf-8') as f:
            json.dump(sample_tests, f, ensure_ascii=False, indent=2)

        print("\n" + "="*60)
        print("🎉 크롤링 및 파일 저장 완료!")
        print(f"  📝 제목: {complete_info['title']} (레벨: {complete_info['level']})")
        print(f"  🏷️ 태그: {', '.join(complete_info.get('tags', []))}")
        print(f"  📊 추출된 예제: {len(complete_info.get('samples', []))}개")
        print(f"  📄 문제 설명 길이: {len(complete_info.get('description', ''))}자")
        print("  💾 저장된 파일: problem_info.json, sample_tests.json")
        print("="*60)

    except IOError as e:
        print(f"\n❌ 파일 저장 중 오류가 발생했습니다: {e}")
        exit(1)

if __name__ == "__main__":
    main()