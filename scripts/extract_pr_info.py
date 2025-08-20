#!/usr/bin/env python3
"""
scripts/extract_pr_info.py
PR에서 변경된 파일들을 분석하여 문제 정보를 추출
각 파일의 실제 커밋 날짜를 포함하여 처리
"""

import json
import os
import re
import sys
import requests
from pathlib import Path
from datetime import datetime


def get_pr_changed_files():
    """GitHub API를 사용하여 PR에서 변경된 파일 목록을 가져옵니다."""
    pr_number = os.environ.get("PR_NUMBER")
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")

    if not all([pr_number, repo, token]):
        print("❌ 필요한 환경변수가 설정되지 않았습니다.")
        return []

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        files = response.json()
        changed_files = []

        for file_info in files:
            filename = file_info["filename"]
            status = file_info["status"]  # added, modified, removed

            # 삭제된 파일은 제외
            if status != "removed":
                changed_files.append(
                    {
                        "filename": filename,
                        "status": status,
                        "additions": file_info.get("additions", 0),
                        "deletions": file_info.get("deletions", 0),
                    }
                )

        return changed_files

    except Exception as e:
        print(f"❌ PR 파일 목록 가져오기 실패: {e}")
        return []


def get_file_commit_dates(files):
    """각 파일의 최신 커밋 날짜를 가져옵니다."""
    pr_number = os.environ.get("PR_NUMBER")
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")

    if not all([pr_number, repo, token]):
        print("❌ 필요한 환경변수가 설정되지 않았습니다.")
        return {}

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # PR의 커밋 목록 가져오기
    commits_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits"
    
    try:
        response = requests.get(commits_url, headers=headers, timeout=30)
        response.raise_for_status()
        commits = response.json()

        file_dates = {}
        
        # 각 커밋을 순회하면서 파일별 최신 날짜 찾기
        for commit in commits:
            commit_date = commit["commit"]["author"]["date"]
            commit_date_parsed = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
            commit_date_str = commit_date_parsed.strftime("%Y-%m-%d")
            
            commit_sha = commit["sha"]
            
            # 해당 커밋에서 변경된 파일들 가져오기
            commit_url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
            commit_response = requests.get(commit_url, headers=headers, timeout=30)
            
            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                commit_files = commit_data.get("files", [])
                
                for file_info in commit_files:
                    filename = file_info["filename"]
                    # 현재 PR에서 변경된 파일만 처리
                    if filename in [f["filename"] for f in files]:
                        # 파일별로 가장 최신 날짜만 저장 (나중에 커밋된 것이 최신)
                        if filename not in file_dates or commit_date_str >= file_dates[filename]:
                            file_dates[filename] = commit_date_str
                            print(f"📅 {filename} -> {commit_date_str}")

        return file_dates

    except Exception as e:
        print(f"❌ 커밋 날짜 가져오기 실패: {e}")
        return {}


def extract_problem_info_from_path(filepath):
    """파일 경로에서 문제 정보를 추출합니다."""
    path = Path(filepath)

    # 경로 패턴: author/problem_id/solution.java
    # 또는: author/problem_id.java
    parts = path.parts

    if len(parts) < 2:
        return None

    author = parts[0]

    # Java 파일인지 확인
    if not path.suffix.lower() == ".java":
        return None

    # 문제 ID 추출 패턴들
    problem_id = None

    if len(parts) >= 3:
        # author/problem_id/solution.java 패턴
        potential_id = parts[1]
        if potential_id.isdigit():
            problem_id = potential_id
    else:
        # author/problem_id.java 패턴
        stem = path.stem
        # 파일명에서 숫자 추출
        match = re.search(r"(\d+)", stem)
        if match:
            problem_id = match.group(1)

    if not problem_id:
        return None

    return {
        "problem_id": problem_id,
        "author": author,
        "code_file": filepath,
        "language": "java",
    }


def get_pr_author():
    """PR 작성자 정보를 가져옵니다."""
    pr_number = os.environ.get("PR_NUMBER")
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")

    if not all([pr_number, repo, token]):
        return None

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        pr_data = response.json()
        return pr_data["user"]["login"]

    except Exception as e:
        print(f"❌ PR 작성자 정보 가져오기 실패: {e}")
        return None


def filter_by_author(problems, pr_author):
    """PR 작성자의 폴더에 있는 파일들만 필터링합니다."""
    if not pr_author:
        return problems

    filtered = []
    for problem in problems:
        # 작성자가 PR 작성자와 일치하거나, 파일이 PR 작성자 폴더에 있는 경우
        if problem["author"] == pr_author or problem["code_file"].startswith(
            f"{pr_author}/"
        ):
            filtered.append(problem)

    return filtered


def validate_problem_files(problems):
    """문제 파일들이 실제로 존재하는지 확인합니다."""
    valid_problems = []

    for problem in problems:
        filepath = problem["code_file"]

        if os.path.exists(filepath):
            # 파일 크기 확인 (너무 작으면 제외)
            file_size = os.path.getsize(filepath)
            if file_size > 50:  # 최소 50바이트
                valid_problems.append(problem)
                print(
                    f"✅ 유효한 문제 파일: {filepath} (문제 {problem['problem_id']}, 작성자: {problem['author']}, 날짜: {problem.get('submission_date', 'N/A')})"
                )
            else:
                print(f"⚠️ 파일이 너무 작음: {filepath}")
        else:
            print(f"❌ 파일이 존재하지 않음: {filepath}")

    return valid_problems


def remove_duplicate_problems(problems):
    """같은 문제 ID와 작성자를 가진 중복 문제들을 제거합니다.
    가장 최신 날짜의 제출만 유지합니다."""
    
    problem_map = {}
    
    for problem in problems:
        key = (problem["problem_id"], problem["author"])
        submission_date = problem.get("submission_date", "1970-01-01")
        
        if key not in problem_map or submission_date > problem_map[key]["submission_date"]:
            problem_map[key] = problem
    
    unique_problems = list(problem_map.values())
    
    if len(unique_problems) < len(problems):
        removed_count = len(problems) - len(unique_problems)
        print(f"🔄 중복 제거: {removed_count}개 중복 제출 제거됨")
    
    return unique_problems


def main():
    """메인 실행 함수"""
    print("🔍 PR 변경사항 분석 시작...")

    # PR에서 변경된 파일들 가져오기
    changed_files = get_pr_changed_files()

    if not changed_files:
        print("❌ 변경된 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"📋 총 {len(changed_files)}개 파일이 변경됨")

    # 각 파일의 커밋 날짜 가져오기
    print("🕐 각 파일의 커밋 날짜를 가져오는 중...")
    file_commit_dates = get_file_commit_dates(changed_files)

    # PR 작성자 정보 가져오기
    pr_author = get_pr_author()
    print(f"👤 PR 작성자: {pr_author}")

    # 각 파일에서 문제 정보 추출
    all_problems = []
    for file_info in changed_files:
        filepath = file_info["filename"]
        print(f"📄 분석 중: {filepath}")

        problem_info = extract_problem_info_from_path(filepath)
        if problem_info:
            # 파일 정보 추가
            problem_info["file_status"] = file_info["status"]
            problem_info["additions"] = file_info["additions"]
            problem_info["deletions"] = file_info["deletions"]
            
            # 커밋 날짜 추가 (없으면 현재 날짜 사용)
            submission_date = file_commit_dates.get(filepath, datetime.now().strftime("%Y-%m-%d"))
            problem_info["submission_date"] = submission_date
            
            all_problems.append(problem_info)
            print(
                f"  ✅ 문제 {problem_info['problem_id']} 발견 (작성자: {problem_info['author']}, 날짜: {submission_date})"
            )
        else:
            print(f"  ⚠️ 문제 정보를 추출할 수 없음")

    # PR 작성자의 문제들만 필터링
    if pr_author:
        filtered_problems = filter_by_author(all_problems, pr_author)
        print(f"🎯 {pr_author}의 문제들만 필터링: {len(filtered_problems)}개")
    else:
        filtered_problems = all_problems
        print(f"⚠️ PR 작성자 정보 없음, 모든 문제 처리: {len(filtered_problems)}개")

    # 중복 문제 제거 (같은 문제의 최신 제출만 유지)
    unique_problems = remove_duplicate_problems(filtered_problems)

    # 파일 존재 여부 확인
    valid_problems = validate_problem_files(unique_problems)

    if not valid_problems:
        print("❌ 유효한 문제 파일이 없습니다.")

        # GitHub Actions 출력 설정
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
                f.write("has_valid_problems=false\n")
                f.write("total_problems_count=0\n")

        sys.exit(0)

    # 결과 저장
    with open("problems_info.json", "w", encoding="utf-8") as f:
        json.dump(valid_problems, f, ensure_ascii=False, indent=2)

    # 요약 정보 출력
    print(f"\n📊 분석 결과 요약")
    print(f"=" * 50)
    print(f"전체 변경 파일: {len(changed_files)}개")
    print(f"추출된 문제: {len(all_problems)}개")
    print(f"필터링된 문제: {len(filtered_problems)}개")
    print(f"중복 제거 후: {len(unique_problems)}개")
    print(f"유효한 문제: {len(valid_problems)}개")

    if valid_problems:
        print(f"\n📝 처리할 문제 목록:")
        for problem in valid_problems:
            print(
                f"  - 문제 {problem['problem_id']} ({problem['author']}) - {problem['code_file']} - {problem['submission_date']}"
            )

    # GitHub Actions 출력 설정
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"has_valid_problems={'true' if valid_problems else 'false'}\n")
            f.write(f"total_problems_count={len(valid_problems)}\n")

            if valid_problems:
                # 첫 번째 문제의 정보를 기본값으로 설정 (하위 호환성)
                first_problem = valid_problems[0]
                f.write(f"problem_id={first_problem['problem_id']}\n")
                f.write(f"author={first_problem['author']}\n")
                f.write(f"code_file={first_problem['code_file']}\n")
                f.write(f"language={first_problem['language']}\n")

    print("✅ PR 분석 완료")


if __name__ == "__main__":
    main()