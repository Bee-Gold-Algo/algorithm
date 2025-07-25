#!/usr/bin/env python3
"""
scripts/extract_pr_info.py
PR에서 변경된 파일들을 분석하여 문제 정보를 추출
"""

import json
import os
import re
import sys
import requests
from pathlib import Path

def get_pr_changed_files():
    """GitHub API를 사용하여 PR에서 변경된 파일 목록을 가져옵니다."""
    pr_number = os.environ.get('PR_NUMBER')
    repo = os.environ.get('GITHUB_REPOSITORY')
    token = os.environ.get('GITHUB_TOKEN')
    
    if not all([pr_number, repo, token]):
        print("❌ 필요한 환경변수가 설정되지 않았습니다.")
        return []
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}/files'
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        files = response.json()
        changed_files = []
        
        for file_info in files:
            filename = file_info['filename']
            status = file_info['status']  # added, modified, removed
            
            # 삭제된 파일은 제외
            if status != 'removed':
                changed_files.append({
                    'filename': filename,
                    'status': status,
                    'additions': file_info.get('additions', 0),
                    'deletions': file_info.get('deletions', 0)
                })
        
        return changed_files
        
    except Exception as e:
        print(f"❌ PR 파일 목록 가져오기 실패: {e}")
        return []

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
    if not path.suffix.lower() == '.java':
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
        match = re.search(r'(\d+)', stem)
        if match:
            problem_id = match.group(1)
    
    if not problem_id:
        return None
    
    return {
        'problem_id': problem_id,
        'author': author,
        'code_file': filepath,
        'language': 'java'
    }

def get_pr_author():
    """PR 작성자 정보를 가져옵니다."""
    pr_number = os.environ.get('PR_NUMBER')
    repo = os.environ.get('GITHUB_REPOSITORY')
    token = os.environ.get('GITHUB_TOKEN')
    
    if not all([pr_number, repo, token]):
        return None
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}'
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        pr_data = response.json()
        return pr_data['user']['login']
        
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
        if (problem['author'] == pr_author or 
            problem['code_file'].startswith(f"{pr_author}/")):
            filtered.append(problem)
    
    return filtered

def validate_problem_files(problems):
    """문제 파일들이 실제로 존재하는지 확인합니다."""
    valid_problems = []
    
    for problem in problems:
        filepath = problem['code_file']
        
        if os.path.exists(filepath):
            # 파일 크기 확인 (너무 작으면 제외)
            file_size = os.path.getsize(filepath)
            if file_size > 50:  # 최소 50바이트
                valid_problems.append(problem)
                print(f"✅ 유효한 문제 파일: {filepath} (문제 {problem['problem_id']}, 작성자: {problem['author']})")
            else:
                print(f"⚠️ 파일이 너무 작음: {filepath}")
        else:
            print(f"❌ 파일이 존재하지 않음: {filepath}")
    
    return valid_problems

def main():
    """메인 실행 함수"""
    print("🔍 PR 변경사항 분석 시작...")
    
    # PR에서 변경된 파일들 가져오기
    changed_files = get_pr_changed_files()
    
    if not changed_files:
        print("❌ 변경된 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    print(f"📋 총 {len(changed_files)}개 파일이 변경됨")
    
    # PR 작성자 정보 가져오기
    pr_author = get_pr_author()
    print(f"👤 PR 작성자: {pr_author}")
    
    # 각 파일에서 문제 정보 추출
    all_problems = []
    for file_info in changed_files:
        filepath = file_info['filename']
        print(f"📄 분석 중: {filepath}")
        
        problem_info = extract_problem_info_from_path(filepath)
        if problem_info:
            # 파일 정보 추가
            problem_info['file_status'] = file_info['status']
            problem_info['additions'] = file_info['additions']
            problem_info['deletions'] = file_info['deletions']
            all_problems.append(problem_info)
            print(f"  ✅ 문제 {problem_info['problem_id']} 발견 (작성자: {problem_info['author']})")
        else:
            print(f"  ⚠️ 문제 정보를 추출할 수 없음")
    
    # PR 작성자의 문제들만 필터링
    if pr_author:
        filtered_problems = filter_by_author(all_problems, pr_author)
        print(f"🎯 {pr_author}의 문제들만 필터링: {len(filtered_problems)}개")
    else:
        filtered_problems = all_problems
        print(f"⚠️ PR 작성자 정보 없음, 모든 문제 처리: {len(filtered_problems)}개")
    
    # 파일 존재 여부 확인
    valid_problems = validate_problem_files(filtered_problems)
    
    if not valid_problems:
        print("❌ 유효한 문제 파일이 없습니다.")
        
        # GitHub Actions 출력 설정
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
                f.write("has_valid_problems=false\n")
                f.write("total_problems_count=0\n")
        
        sys.exit(0)
    
    # 결과 저장
    with open('problems_info.json', 'w', encoding='utf-8') as f:
        json.dump(valid_problems, f, ensure_ascii=False, indent=2)
    
    # 요약 정보 출력
    print(f"\n📊 분석 결과 요약")
    print(f"=" * 50)
    print(f"전체 변경 파일: {len(changed_files)}개")
    print(f"추출된 문제: {len(all_problems)}개")
    print(f"필터링된 문제: {len(filtered_problems)}개")
    print(f"유효한 문제: {len(valid_problems)}개")
    
    if valid_problems:
        print(f"\n📝 처리할 문제 목록:")
        for problem in valid_problems:
            print(f"  - 문제 {problem['problem_id']} ({problem['author']}) - {problem['code_file']}")
    
    # GitHub Actions 출력 설정
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
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