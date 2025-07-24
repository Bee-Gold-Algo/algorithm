#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다. (Playwright 사용)
GitHub Actions 환경에 최적화
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

def scrape_with_playwright(problem_id: str, max_attempts: int = 3):
    """Playwright를 사용하여 안정적으로 문제 정보 스크래핑"""
    print(f"🚀 Playwright 스크래핑 시작 (최대 {max_attempts}회 시도)")
    url = f"https://www.acmicpc.net/problem/{problem_id}"

    with sync_playwright() as p:
        for attempt in range(1, max_attempts + 1):
            browser = None  # browser 변수 초기화
            try:
                print(f"\n  📍 시도 {attempt}/{max_attempts}")
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()

                print(f"  → 페이지 접속: {url}")
                page.goto(url, wait_until='domcontentloaded', timeout=45000)

                # 페이지가 완전히 로드될 때까지 대기
                page.wait_for_selector('#problem-body', timeout=30000)
                print("  ✅ 페이지 DOM 로드 완료")

                # 페이지 스크롤 (동적 콘텐츠 로딩 유도)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1) # 스크롤 후 잠시 대기
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(0.5)

                html_content = page.content()
                print(f"  📄 HTML 크기: {len(html_content):,} 문자")

                problem_info = extract_problem_info_from_html(html_content)

                if problem_info and problem_info.get('samples'):
                    print(f"  🎉 Playwright 스크래핑 성공!")
                    return problem_info
                else:
                    print("  ⚠️ 문제 정보 추출 실패, 재시도합니다.")
                    time.sleep(3) # 실패 시 잠시 대기 후 재시도

            except PlaywrightTimeoutError:
                print(f"  ❌ 시간 초과 오류 발생. 재시도합니다.")
                if attempt < max_attempts:
                    time.sleep(5) # 시간 초과 시 더 길게 대기
            except Exception as e:
                print(f"  ❌ 스크래핑 중 오류 발생: {e}")
                if attempt < max_attempts:
                    time.sleep(5)
            finally:
                if browser:
                    browser.close()

    print("  💥 모든 스크래핑 시도 실패")
    return None

def main():
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집 (Playwright 최적화)')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    args = parser.parse_args()

    problem_id = args.problem_id
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'

    print(f"📥 문제 {problem_id} 정보 수집 중...")
    if is_github_actions:
        print("🤖 GitHub Actions 환경에서 실행 중 (Playwright 사용)")
    else:
        print("🖥️ 로컬 환경에서 실행 중 (Playwright 사용)")

    # 1. solved.ac API로 기본 정보 수집
    print("\n  → solved.ac API 호출...")
    solved_ac_info = get_solved_ac_info(problem_id)

    # 2. Playwright로 스크래핑
    boj_info = scrape_with_playwright(problem_id)

    # 3. 스크래핑 실패 시 처리
    if not boj_info:
        print("\n  ❌ 스크래핑에 최종적으로 실패했습니다.")
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