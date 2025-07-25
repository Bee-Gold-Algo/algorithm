#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (Playwright 사용)
최신 BOJ 웹사이트 구조에 맞게 업데이트되었으며, GitHub Actions 환경에 최적화되었습니다.
"""

import argparse
import json
import requests
from bs4 import BeautifulSoup
import time
import os

# Playwright 관련 라이브러리 임포트
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def get_solved_ac_info(problem_id):
    """solved.ac API에서 문제의 기본 정보(제목, 레벨, 태그)를 가져옵니다."""
    print("\n solvable.ac API에서 정보 조회 중...")
    try:
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
        # 타임아웃을 10초로 설정하여 무한 대기 방지
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 200 OK가 아닐 경우 예외 발생

        if response.status_code == 200:
            data = response.json()
            tags = []
            # 태그 정보에서 한국어 이름만 추출
            for tag in data.get("tags", []):
                korean_tag = next((item['name'] for item in tag.get('displayNames', []) if item['language'] == 'ko'), None)
                if korean_tag:
                    tags.append(korean_tag)
            
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
    
    # API 호출 실패 시 기본 정보 반환
    return {
        "title": f"문제 {problem_id}",
        "level": "N/A",
        "tags": []
    }

def extract_problem_details_from_html(html_content):
    """BeautifulSoup를 사용하여 HTML에서 문제의 상세 정보를 추출합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 문제가 없는 경우의 페이지인지 확인
    if "문제를 찾을 수 없습니다" in soup.text or "존재하지 않는 문제" in soup.text:
        print("  ❌ 해당 문제 번호를 찾을 수 없습니다.")
        return None

    problem_details = {}

    # 섹션별 정보 추출 (최신 BOJ 웹사이트 구조에 맞춘 선택자 사용)
    sections = {
        'description': 'problem_description',
        'input_format': 'problem_input',
        'output_format': 'problem_output',
        'hint': 'problem_hint',
        'limits': 'problem_limit'
    }

    for key, section_id in sections.items():
        element = soup.find('div', {'id': section_id})
        if element:
            # get_text를 사용하여 텍스트 추출, separator로 줄바꿈 유지
            problem_details[key] = element.get_text(separator='\n', strip=True)
            print(f"  ✅ {key.replace('_', ' ').capitalize()} 정보 추출 완료")
        else:
            problem_details[key] = "" # 해당 섹션이 없으면 빈 문자열로 초기화

    # 예제 테스트케이스 추출
    samples = []
    # 'sample-input-' 또는 'sample_input_'로 시작하는 모든 pre 태그를 찾음
    input_tags = soup.select('pre[id^="sample-input-"], pre[id^="sample_input_"]')
    
    for i, input_tag in enumerate(input_tags, 1):
        # 입력 ID에 대응하는 출력 ID를 생성
        output_id_variations = [
            input_tag['id'].replace('input', 'output'),
            f'sample-output-{i}',
            f'sample_output_{i}'
        ]
        
        output_tag = None
        for out_id in output_id_variations:
            output_tag = soup.find('pre', {'id': out_id})
            if output_tag:
                break

        if output_tag:
            samples.append({
                "input": input_tag.get_text(strip=True),
                "output": output_tag.get_text(strip=True),
            })
        else:
            print(f"  ⚠️ 예제 입력 {i}에 대한 출력을 찾지 못했습니다.")

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
                # Chromium 브라우저 실행 (GitHub Actions 환경을 위한 --no-sandbox 옵션 포함)
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
                # 'domcontentloaded' 상태까지 기다린 후, 추가로 네트워크가 안정될 때까지 대기
                page.goto(url, wait_until='networkidle', timeout=60000)

                # 특정 요소가 나타날 때까지 명시적으로 대기 (페이지 로딩 보장)
                page.wait_for_selector('#problem-body', timeout=45000)
                print("  → 페이지 로드 완료. 정보 추출 시작...")
                
                # 페이지의 전체 HTML 콘텐츠를 가져옴
                html_content = page.content()
                
                # HTML 콘텐츠로부터 상세 정보 추출
                problem_details = extract_problem_details_from_html(html_content)

                # 정보 추출에 성공하고, 특히 예제 케이스가 하나라도 있으면 성공으로 간주
                if problem_details and problem_details.get('samples'):
                    print("\n  🎉 스크래핑 성공!")
                    return problem_details
                else:
                    print("  ⚠️ 정보 추출 실패. 재시도합니다.")
                    time.sleep(3) # 재시도 전 잠시 대기

            except PlaywrightTimeoutError:
                print(f"  ❌ 시간 초과 오류 발생. 네트워크 문제일 수 있습니다. 재시도합니다.")
                if attempt < max_retries:
                    time.sleep(5) # 시간 초과 시 더 길게 대기
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

    # 1. solvable.ac API로 기본 정보 가져오기
    solved_ac_info = get_solved_ac_info(problem_id)

    # 2. Playwright로 웹 스크래핑하여 상세 정보 가져오기
    boj_details = scrape_with_playwright(problem_id)

    # 3. 스크래핑 실패 시 대체 데이터 생성
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

    # 4. API 정보와 스크래핑 정보를 합쳐 최종 결과물 생성
    complete_info = {
        "problem_id": problem_id,
        **solved_ac_info,
        **boj_details
    }

    # 5. 결과를 JSON 파일로 저장
    try:
        # 전체 문제 정보 저장
        with open('problem_info.json', 'w', encoding='utf-8') as f:
            json.dump(complete_info, f, ensure_ascii=False, indent=2)
        
        # 예제 테스트케이스만 별도로 저장
        sample_tests = {
            "problem_id": problem_id,
            "test_cases": complete_info['samples']
        }
        with open('sample_tests.json', 'w', encoding='utf-8') as f:
            json.dump(sample_tests, f, ensure_ascii=False, indent=2)

        print("\n" + "="*50)
        if complete_info['samples']:
            print("✅ 정보 수집 및 파일 저장 완료!")
            print(f"  - 제목: {complete_info['title']} (레벨: {complete_info['level']})")
            print(f"  - 태그: {', '.join(complete_info['tags']) if complete_info['tags'] else '없음'}")
            print(f"  - 추출된 예제: {len(complete_info['samples'])}개")
        else:
            print("⚠️ 정보 수집이 부분적으로 완료되었습니다.")
            print(f"  - 제목: {complete_info['title']} (레벨: {complete_info['level']})")
            print("  - 예제 테스트케이스를 가져오지 못했습니다.")
            print("  - 다음 단계에서 문제가 발생할 수 있으니 `problem_info.json`을 확인해주세요.")
        
        print("  - 저장된 파일: problem_info.json, sample_tests.json")
        print("="*50)

    except IOError as e:
        print(f"\n❌ 파일 저장 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
