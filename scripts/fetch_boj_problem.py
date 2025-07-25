#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (Playwright 사용)
안정성 강화를 위해 페이지 로딩 전략 및 요소 추출 방식을 전면 개선했습니다.
GitHub Actions 환경에서의 디버깅을 위한 기능이 추가되었습니다.
"""

import argparse
import json
import requests
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError
import time
import os

def get_solved_ac_info(problem_id):
    """solved.ac API에서 문제의 기본 정보(제목, 레벨, 태그)를 가져옵니다."""
    print("\n solvable.ac API에서 정보 조회 중...")
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
            
            print(f"  ✅ 제목: {data.get('titleKo', '')}, 레벨: {data.get('level', 0)}")
            return {
                "title": data.get("titleKo", f"문제 {problem_id}"),
                "level": data.get("level", "N/A"),
                "tags": tags
            }
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ solvable.ac API 호출 오류: {e}")
    except json.JSONDecodeError:
        print("  ⚠️ solvable.ac API 응답이 올바른 JSON 형식이 아닙니다.")
    
    # API 호출 실패 시 기본 정보를 반환합니다.
    return {
        "title": f"문제 {problem_id}",
        "level": "N/A",
        "tags": []
    }

def save_debug_info(page: Page, prefix: str):
    """실패 시 디버깅을 위해 스크린샷과 HTML을 저장합니다."""
    try:
        # GitHub Actions에서 아티팩트로 저장할 수 있도록 파일 생성
        screenshot_path = f"{prefix}_screenshot.png"
        html_path = f"{prefix}_page.html"
        
        print(f"  ℹ️ 오류 발생! 디버그 정보를 저장합니다...")
        page.screenshot(path=screenshot_path, full_page=True)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
            
        print(f"  ℹ️ 디버그 정보 저장 완료: {screenshot_path}, {html_path}")
        print("     GitHub Actions 실행 결과의 'Artifacts'에서 해당 파일들을 다운로드하여 확인하세요.")
    except Exception as e:
        print(f"  ⚠️ 디버그 정보 저장 중 오류 발생: {e}")


def extract_problem_details_with_playwright(page: Page):
    """
    Playwright의 Locator를 사용하여 페이지에서 직접 문제의 상세 정보를 추출합니다.
    각 요소 탐색을 try-except로 감싸 안정성을 확보했습니다.
    """
    try:
        # 안정성의 핵심: 페이지의 핵심 콘텐츠 영역이 나타날 때까지 명시적으로 대기합니다.
        print("  - 핵심 콘텐츠(#problem-body)가 나타날 때까지 대기...")
        page.wait_for_selector('#problem-body', state='visible', timeout=30000)
        print("  - 핵심 콘텐츠 로드 확인.")
    except PlaywrightTimeoutError:
        print("  ❌ 페이지에서 핵심 콘텐츠(#problem-body)를 시간 내에 찾지 못했습니다.")
        return None

    if page.locator('*:text("문제를 찾을 수 없습니다")', state='visible').count() > 0:
        print("  ❌ 해당 문제 번호를 찾을 수 없습니다.")
        return None

    problem_details = {}

    def safe_get_text(selector: str) -> str:
        """주어진 선택자에 해당하는 요소의 텍스트를 안전하게 추출합니다."""
        try:
            locator = page.locator(selector)
            if locator.count() > 0:
                content = locator.first.text_content(timeout=5000)
                return content.strip() if content else ""
        except PlaywrightTimeoutError:
            print(f"  - 요소(selector='{selector}')를 시간 내에 찾지 못했습니다.")
        except Exception as e:
            print(f"  - 요소(selector='{selector}') 추출 중 오류 발생: {e}")
        return ""

    sections = {
        'description': '#problem_description',
        'input_format': '#problem_input',
        'output_format': '#problem_output',
        'limits': '#problem_limit',
        'hint': '#problem_hint'
    }

    for key, selector in sections.items():
        problem_details[key] = safe_get_text(selector)
        if problem_details[key]:
            print(f"  ✅ {key.replace('_', ' ').capitalize()} 정보 추출 완료")

    samples = []
    try:
        page.wait_for_selector('pre[id^="sample-input-"]', timeout=5000)
        input_locators = page.locator('pre[id^="sample-input-"]')
        count = input_locators.count()
        
        for i in range(count):
            input_locator = input_locators.nth(i)
            input_id = input_locator.get_attribute('id')
            output_selector = f"#{input_id.replace('input', 'output')}"
            
            input_text = input_locator.text_content()
            output_text = safe_get_text(output_selector)

            if output_text:
                samples.append({"input": input_text.strip(), "output": output_text})
            else:
                 print(f"  ⚠️ 예제 입력 {i+1}에 대한 출력을 찾지 못했습니다.")
    except PlaywrightTimeoutError:
        print("  - 예제 테스트케이스를 찾을 수 없습니다.")

    problem_details['samples'] = samples
    if samples:
        print(f"  ✅ 예제 테스트케이스 {len(samples)}개 추출 완료")

    return problem_details if any(problem_details.values()) else None


def scrape_with_playwright(problem_id: str, max_retries: int = 3):
    """Playwright를 사용하여 웹 페이지를 안정적으로 스크래핑합니다."""
    url = f"https://www.acmicpc.net/problem/{problem_id}"
    print(f"\n🚀 Playwright로 스크래핑 시작 (최대 {max_retries}회 시도)")
    print(f"   URL: {url}")

    with sync_playwright() as p:
        for attempt in range(1, max_retries + 1):
            browser = None
            page = None
            try:
                print(f"\n  [시도 {attempt}/{max_retries}]")
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                # `default_timeout` 인자를 제거하여 오류를 해결합니다.
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                # 페이지별 타임아웃은 page.goto 등에서 개별적으로 설정합니다.
                page.set_default_timeout(60000)

                print("  → 페이지 접속 및 기본 콘텐츠 로드 대기...")
                page.goto(url, wait_until='domcontentloaded', timeout=90000)

                print("  → 페이지 로드 확인. 상세 정보 추출 시작...")
                problem_details = extract_problem_details_with_playwright(page)

                if problem_details:
                    print("\n  🎉 스크래핑 성공!")
                    return problem_details
                else:
                    print("  ⚠️ 페이지에서 유효한 정보를 찾지 못했습니다. 재시도합니다.")
                    save_debug_info(page, f"failure_attempt_{attempt}")
                    time.sleep(3)

            except Exception as e:
                print(f"  ❌ 시도 {attempt}에서 심각한 오류 발생: {e}")
                if page:
                    save_debug_info(page, f"error_attempt_{attempt}")
                if attempt < max_retries:
                    print("     재시도합니다...")
                    time.sleep(5 + attempt * 2)
                else:
                    print("     최대 재시도 횟수를 초과했습니다.")
            finally:
                if browser:
                    browser.close()

    print("\n💥 모든 스크래핑 시도에 실패했습니다.")
    return None

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집 스크립트 (안정성 강화 버전)')
    parser.add_argument('--problem-id', required=True, help='수집할 백준 문제의 번호')
    args = parser.parse_args()

    problem_id = args.problem_id
    
    solved_ac_info = get_solved_ac_info(problem_id)
    boj_details = scrape_with_playwright(problem_id)

    if not boj_details:
        print("\n  스크래핑에 최종 실패하여, 수동 확인이 필요한 기본 정보를 생성합니다.")
        boj_details = {
            "description": f"문제 설명을 가져오는 데 실패했습니다. 링크에서 직접 확인해주세요: https://www.acmicpc.net/problem/{problem_id}",
            "input_format": "입력 형식을 직접 확인해주세요.",
            "output_format": "출력 형식을 직접 확인해주세요.",
            "limits": "시간/메모리 제한을 직접 확인해주세요.",
            "hint": "",
            "samples": []
        }

    complete_info = { "problem_id": problem_id, **solved_ac_info, **boj_details }

    try:
        with open('problem_info.json', 'w', encoding='utf-8') as f:
            json.dump(complete_info, f, ensure_ascii=False, indent=2)
        
        sample_tests = { "problem_id": problem_id, "test_cases": complete_info.get('samples', []) }
        with open('sample_tests.json', 'w', encoding='utf-8') as f:
            json.dump(sample_tests, f, ensure_ascii=False, indent=2)

        print("\n" + "="*50)
        # description 필드가 비어있지 않은지 확인하여 성공 여부 판단
        if complete_info.get('description') and "실패" not in complete_info.get('description'):
             print("✅ 정보 수집 및 파일 저장 완료!")
        else:
             print("⚠️ 정보 수집이 부분적으로 완료되었거나 실패했습니다.")
        
        print(f"  - 제목: {complete_info['title']} (레벨: {complete_info['level']})")
        print(f"  - 추출된 예제: {len(complete_info.get('samples', []))}개")
        print("  - 저장된 파일: problem_info.json, sample_tests.json")
        print("="*50)

    except IOError as e:
        print(f"\n❌ 파일 저장 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
