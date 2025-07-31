#!/usr/bin/env python3
"""
머지된 PR의 파일 변경사항을 분석하여 제출된 알고리즘 문제를 파악하는 스크립트
"""

import json
import re
import os
from pathlib import Path


def extract_problem_number_from_path(file_path):
    """파일 경로에서 백준 문제 번호를 추출"""
    # 다양한 패턴으로 문제 번호 추출 시도
    patterns = [
        r"/(\d{4,5})\.",  # /1234.cpp, /12345.py 등
        r"/(\d{4,5})_",  # /1234_problem.cpp 등
        r"/boj_?(\d{4,5})",  # /boj1234.cpp, /boj_1234.py 등
        r"/(\d{4,5})/",  # /1234/ 폴더 구조
        r"_(\d{4,5})\.",  # file_1234.cpp 등
        r"-(\d{4,5})\.",  # file-1234.cpp 등
    ]

    for pattern in patterns:
        match = re.search(pattern, file_path)
        if match:
            return match.group(1)

    return None


def analyze_pr_files():
    """PR에서 변경된 파일들을 분석하여 problems_info.json 생성"""

    # PR 파일 정보 로드
    if not os.path.exists("pr_files.json"):
        print("❌ pr_files.json 파일이 없습니다.")
        return

    with open("pr_files.json", "r") as f:
        pr_files = json.load(f)

    print(f"🔍 PR에서 변경된 파일 수: {len(pr_files)}")

    problems_found = []

    # 변경된 파일들 분석
    for file_info in pr_files:
        filename = file_info.get("filename", "")
        status = file_info.get("status", "")
        additions = file_info.get("additions", 0)

        print(f"📁 파일: {filename} (상태: {status}, 추가: {additions}줄)")

        # 알고리즘 솔루션 파일인지 확인
        if is_algorithm_file(filename):
            problem_number = extract_problem_number_from_path(filename)
            if problem_number:
                problems_found.append(
                    {
                        "problem_number": problem_number,
                        "file_path": filename,
                        "status": status,
                        "additions": additions,
                    }
                )
                print(f"  ✅ 문제 {problem_number} 발견")

    # problems_info.json 생성
    if problems_found:
        problems_info = {
            "problems": problems_found,
            "total_count": len(problems_found),
            "analysis_source": "merged_pr",
        }

        with open("problems_info.json", "w", encoding="utf-8") as f:
            json.dump(problems_info, f, ensure_ascii=False, indent=2)

        print(
            f"✅ {len(problems_found)}개의 문제 정보를 problems_info.json에 저장했습니다."
        )

        # 발견된 문제들 출력
        for problem in problems_found:
            print(f"  📋 문제 {problem['problem_number']}: {problem['file_path']}")
    else:
        print("ℹ️ 알고리즘 문제 파일이 발견되지 않았습니다.")


def is_algorithm_file(filename):
    """파일이 알고리즘 솔루션 파일인지 확인"""

    # 제외할 파일들
    exclude_patterns = [
        r"\.md$",  # README 등
        r"\.txt$",  # 텍스트 파일
        r"\.json$",  # JSON 파일
        r"\.yml$",
        r"\.yaml$",  # 워크플로우 파일
        r"\.git",  # Git 관련
        r"scripts/",  # 스크립트 폴더
        r"\.github/",  # GitHub 설정
    ]

    for pattern in exclude_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            return False

    # 포함할 파일 확장자
    include_extensions = [".py", ".cpp", ".c", ".java", ".js", ".go", ".rs", ".kt"]

    file_extension = Path(filename).suffix.lower()
    return file_extension in include_extensions


def main():
    print("🔍 머지된 PR 파일 분석 시작")
    analyze_pr_files()
    print("✅ 분석 완료")


if __name__ == "__main__":
    main()
