#!/usr/bin/env python3
"""
scripts/extract_pr_info.py
PR에서 여러 문제와 코드 정보를 추출합니다.
"""

import os
import re
import json
import sys
import requests
from pathlib import Path

def get_changed_files_from_api():
    """GitHub API를 사용하여 PR의 변경된 파일 목록을 가져옵니다."""
    try:
        repo = os.environ['GITHUB_REPOSITORY']
        pr_number = os.environ['PR_NUMBER']
        token = os.environ['GITHUB_TOKEN']
        
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        files_data = response.json()
        changed_files = []
        
        for file_info in files_data:
            if file_info['status'] in ['added', 'modified']:
                changed_files.append({
                    'filename': file_info['filename'],
                    'status': file_info['status'],
                    'additions': file_info.get('additions', 0),
                    'deletions': file_info.get('deletions', 0)
                })
        
        print(f"📂 GitHub API로 발견된 변경 파일: {len(changed_files)}개")
        return changed_files
        
    except Exception as e:
        print(f"❌ GitHub API 호출 실패: {e}")
        return []

def extract_problem_info_from_path(file_path):
    """파일 경로에서 문제 정보를 추출합니다."""
    # 패턴: 사용자명/문제번호/Main.java 또는 사용자명/문제번호_문제이름/Main.java
    patterns = [
        r'([^/]+)/(\d+)/Main\.java$',
        r'([^/]+)/(\d+)_[^/]+/Main\.java$',
        r'([^/]+)/(\d+)/[^/]+\.java$',
        r'([^/]+)/(\d+)_[^/]+/[^/]+\.java$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, file_path)
        if match:
            author = match.group(1)
            problem_id = match.group(2)
            
            # 유효한 문제 번호인지 확인 (1-30000 범위)
            try:
                problem_num = int(problem_id)
                if 1 <= problem_num <= 30000:
                    return {
                        'author': author,
                        'problem_id': problem_id,
                        'file_path': file_path,
                        'language': 'Java'
                    }
            except ValueError:
                continue
    
    return None

def extract_multiple_problems():
    """PR에서 여러 문제 정보를 추출합니다."""
    print("🔍 PR에서 여러 문제 정보 추출 시작...")
    
    # GitHub API로 변경된 파일 목록 가져오기
    changed_files = get_changed_files_from_api()
    
    if not changed_files:
        print("⚠️ 변경된 파일이 없습니다.")
        return []
    
    # 문제 정보 추출
    problems = []
    seen_problems = set()  # 중복 방지
    
    for file_info in changed_files:
        file_path = file_info['filename']
        print(f"📁 분석 중: {file_path}")
        
        problem_info = extract_problem_info_from_path(file_path)
        if problem_info:
            # 중복 체크 (같은 작성자의 같은 문제)
            key = f"{problem_info['author']}-{problem_info['problem_id']}"
            if key not in seen_problems:
                problems.append(problem_info)
                seen_problems.add(key)
                print(f"  ✅ 문제 발견: {problem_info['author']} - {problem_info['problem_id']}")
            else:
                print(f"  ⚠️ 중복 문제 건너뜀: {key}")
        else:
            print(f"  ❌ 유효하지 않은 파일: {file_path}")
    
    return problems

def select_priority_problem(problems):
    """여러 문제 중 우선순위가 높은 문제를 선택합니다."""
    if not problems:
        return None
    
    # 우선순위: 문제 번호가 작은 것부터
    sorted_problems = sorted(problems, key=lambda x: int(x['problem_id']))
    return sorted_problems[0]

def main():
    """메인 실행 함수"""
    print("🎯 PR 정보 추출 시작")
    
    # 여러 문제 추출
    problems = extract_multiple_problems()
    
    if not problems:
        print("❌ 분석할 수 있는 문제가 없습니다.")
        
        # GitHub Actions Output 설정
        set_github_output("has_valid_problems", "false")
        set_github_output("problem_id", "0000")
        set_github_output("author", "unknown")
        set_github_output("code_file", "")
        set_github_output("language", "Java")
        set_github_output("total_problems_count", "0")
        set_github_output("is_multiple_problems", "false")
        set_github_output("problems_json", "[]")
        return
    
    # 우선순위 문제 선택
    priority_problem = select_priority_problem(problems)
    
    # 문제 목록을 JSON으로 저장
    with open('problems_list.json', 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)
    
    # GitHub Actions Output 설정
    set_github_output("has_valid_problems", "true")
    set_github_output("problem_id", priority_problem['problem_id'])
    set_github_output("author", priority_problem['author'])
    set_github_output("code_file", priority_problem['file_path'])
    set_github_output("language", priority_problem['language'])
    set_github_output("total_problems_count", str(len(problems)))
    set_github_output("is_multiple_problems", "true" if len(problems) > 1 else "false")
    set_github_output("problems_json", json.dumps(problems, ensure_ascii=False))
    
    # 결과 출력
    print(f"\n📊 추출 결과:")
    print(f"  총 문제 수: {len(problems)}개")
    print(f"  우선순위 문제: {priority_problem['problem_id']} ({priority_problem['author']})")
    
    if len(problems) > 1:
        print(f"  다른 문제들:")
        for problem in problems:
            if problem != priority_problem:
                print(f"    - {problem['problem_id']} ({problem['author']})")
    
    print(f"  💾 문제 목록 저장: problems_list.json")

def set_github_output(name, value):
    """GitHub Actions output 설정"""
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write(f"{name}={value}\n")
    else:
        print(f"Output: {name}={value}")

if __name__ == "__main__":
    main()