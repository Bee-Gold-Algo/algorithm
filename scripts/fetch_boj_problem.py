#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (Playwright 사용)
최신 BOJ 웹사이트 구조에 맞게 업데이트되었으며, GitHub Actions 환경에 최적화되었습니다.
Playwright의 Locator API를 사용하여 안정성을 높였습니다.
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
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            tags = [
                tag['displayNames'][0]['name']
                for tag in data.get("tags", [])
                if tag.get('displayNames') and any(d['language'] == 'ko' for d in tag['displayNames'])
            ]
            
            print(f"  ✅ 제목: {data.get('titleKo', '')}, 레벨: {data.get('level', 0)}")
            return {
                "title": data.get("titleKo", ""),
                "level": data.get("level", 0),
                "tags": tags
            }
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ solvable.ac API 호출 오류: {e}")
    except json.JSONDecodeError:
        print("  ⚠️ solvable.ac API 응답이 올바른 JSON 형식이 아닙니다.")
    
    return {
        "title": f"문제 {problem_id}",
        "level": "N/A",
        "tags": []
    }

def extract_problem_details_with_playwright(page: Page):
    """
    Playwright의 Locator를 사용하여 페이지에서 직접 문제의 상세 정보를 추출합니다.
    Locator는 요소가 나타날 때까지 자동으로 대기하여 안정성을 높입니다.
    """
    # 문제가 없는 경우의 페이지인지 확인
    if page.locator('body:has-text("문제를 찾을 수 없습니다")').count() > 0 or page.locator('body:has-text("존재하지 않는 문제")').count() > 0:
        print("  ❌ 해당 문제 번호를 찾을 수 없습니다.")
        return None

    problem_details = {}

    # 섹션별 정보 추출을 위한 선택자 맵
    sections = {
        'description': '#problem_description',
        'input_format': '#problem_input',
        'output_format': '#problem_output',
        'hint': '#problem_hint',
        'limits': '#problem_limit'
    }

    for key, selector in sections.items():
        locator = page.locator(selector)
        if locator.count() > 0:
            # 요소가 존재하면 텍스트를 추출합니다.
            problem_details[key] = locator.inner_text()
            print(f"  ✅ {key.replace('_', ' ').capitalize()} 정보 추출 완료")
        else:
            problem_details[key] = "" # 해당 섹션이 없으면 빈 문자열로 초기화

    # 예제 테스트케이스 추출
    samples = []
    input_locators = page.locator('pre[id^="sample-input-"]')
    
    for i in range(input_locators.count()):
        input_locator = input_locators.nth(i)
        input_id = input_locator.get_attribute('id')
        
        # 입력 ID에 대응하는 출력 ID를 찾습니다.
        output_selector = f"#{input_id.replace('input', 'output')}"
        output_locator = page.locator(output_selector)

        if output_locator.count() > 0:
            samples.append({
                "input": input_locator.inner_text().strip(),
                "output": output_locator.inner_text().strip(),
            })
        else:
            print(f"  ⚠️ 예제 입력 {i+1}에 대한 출력을 찾지 못했습니다. (Selector: {output_selector})")

    problem_details['samples'] = samples
    print(f"  ✅ 예제 테스트케이스 {len(samples)}개 추출 완료")

    return problem_details

def scrape_with_playwright(problem_id: str, max_retries: int = 3):
    """Playwright를 사용하여 웹 페이지를 안정적으로 스크래핑합니다."""
    url = f"https://www.acmicpc.net/problem/{problem_id}"
    print(f"\n🚀 Playwright로 스크래핑 시작 (최대 {max_retries}회 시도)")
    print(f"   URL: {url}")

    with sync_playwright() as p:
        for attempt in range(1, max_retries + 1):
            browser = None
            try:
                print(f"\n  [시도 {attempt}/{max_retries}]")
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()

                print("  → 페이지 접속 및 대기...")
                page.goto(url, wait_until='domcontentloaded', timeout=60000)

                # 페이지의 핵심 콘텐츠 영역이 로드될 때까지 명시적으로 대기합니다.
                page.wait_for_selector('#problem-body', timeout=45000)
                print("  → 페이지 로드 완료. 정보 추출 시작...")
                
                # Playwright Page 객체를 직접 넘겨 정보를 추출합니다.
                problem_details = extract_problem_details_with_playwright(page)

                if problem_details and problem_details.get('samples'):
                    print("\n  🎉 스크래핑 성공!")
                    return problem_details
                elif problem_details:
                    print("  ⚠️ 예제는 없지만, 다른 정보는 추출되었습니다. 성공으로 간주합니다.")
                    return problem_details
                else:
                    print("  ⚠️ 정보 추출 실패. 재시도합니다.")
                    time.sleep(3)

            except PlaywrightTimeoutError:
                print(f"  ❌ 시간 초과 오류 발생. 네트워크 문제일 수 있습니다. 재시도합니다.")
                if attempt < max_retries:
                    time.sleep(5)
            except Exception as e:
                print(f"  ❌ 스크래핑 중 예상치 못한 오류 발생: {e}")
                if attempt < max_retries:
                    time.sleep(5)
            finally:
                if browser:
                    browser.close()

    print("\n💥 모든 스크래핑 시도에 실패했습니다.")
    return None

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집 스크립트 (Playwright 최적화)')
    parser.add_argument('--problem-id', required=True, help='수집할 백준 문제의 번호')
    args = parser.parse_args()

    problem_id = args.problem_id
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
    env_string = "GitHub Actions" if is_github_actions else "로컬"
    print(f"'{env_string}' 환경에서 문제 {problem_id} 정보 수집을 시작합니다.")

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
            "test_cases": complete_info['samples']
        }
        with open('sample_tests.json', 'w', encoding='utf-8') as f:
            json.dump(sample_tests, f, ensure_ascii=False, indent=2)

        print("\n" + "="*50)
        if complete_info.get('samples'):
            print("✅ 정보 수집 및 파일 저장 완료!")
            print(f"  - 제목: {complete_info['title']} (레벨: {complete_info['level']})")
            print(f"  - 태그: {', '.join(complete_info['tags']) if complete_info['tags'] else '없음'}")
            print(f"  - 추출된 예제: {len(complete_info['samples'])}개")
        else:
            print("⚠️ 정보 수집이 부분적으로 완료되었습니다.")
            print(f"  - 제목: {complete_info['title']} (레벨: {complete_info['level']})")
            print("  - 예제 테스트케이스를 가져오지 못했습니다.")
        
        print("  - 저장된 파일: problem_info.json, sample_tests.json")
        print("="*50)

    except IOError as e:
        print(f"\n❌ 파일 저장 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
