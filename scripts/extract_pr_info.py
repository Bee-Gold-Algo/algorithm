# scripts/extract_pr_info.py
import os
import re
import sys
import json
import subprocess

def get_pr_info(pr_number, repo):
    """PR 기본 정보를 가져옵니다."""
    print(f"🔍 PR #{pr_number} 기본 정보 조회 중...")
    try:
        command = ['gh', 'api', f'/repos/{repo}/pulls/{pr_number}']
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        pr_data = json.loads(result.stdout)
        
        pr_author = pr_data['user']['login']
        print(f"👤 PR 작성자: {pr_author}")
        return pr_author
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ PR 정보 조회 실패: {e}", file=sys.stderr)
        return None

def get_pr_changed_files(pr_number, repo):
    """PR에서 변경된 파일 목록을 가져옵니다."""
    print(f"🔍 PR #{pr_number}의 변경된 파일 목록 조회 중...")
    try:
        command = ['gh', 'api', f'/repos/{repo}/pulls/{pr_number}/files']
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        files = json.loads(result.stdout)
        
        changed_files = []
        for file in files:
            if file['filename'].endswith('/Main.java'):
                changed_files.append({
                    'filename': file['filename'],
                    'status': file['status'],  # added, modified, deleted
                    'changes': file.get('changes', 0),
                    'additions': file.get('additions', 0),
                    'deletions': file.get('deletions', 0)
                })
        
        print(f"✅ 변경된 Main.java 파일: {len(changed_files)}개")
        for file in changed_files:
            print(f"   📄 {file['filename']} ({file['status']})")
        
        return changed_files
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ 변경된 파일 조회 실패: {e}", file=sys.stderr)
        return []

def extract_info_from_path(file_path):
    """파일 경로에서 작성자와 문제 번호를 추출합니다."""
    match = re.search(r'^([^/]+)/(\d+)/Main\.java$', file_path)
    if match:
        author, problem_id = match.groups()
        return author, problem_id
    return None, None

def filter_author_files(changed_files, pr_author):
    """PR 작성자의 파일만 필터링합니다."""
    print(f"\n🔍 PR 작성자({pr_author})의 파일만 필터링 중...")
    
    author_files = []
    other_files = []
    
    for file_info in changed_files:
        filename = file_info['filename']
        author, problem_id = extract_info_from_path(filename)
        
        if not author or not problem_id:
            print(f"   ⚠️ {filename}: 잘못된 경로 형식, 무시됨")
            continue
            
        if author == pr_author:
            print(f"   ✅ {filename}: PR 작성자의 파일 (문제 {problem_id})")
            author_files.append({
                'author': author,
                'problem_id': problem_id,
                'code_file': filename,
                'language': 'java',
                'status': file_info['status'],
                'changes': file_info.get('changes', 0)
            })
        else:
            print(f"   ➖ {filename}: 다른 사용자({author})의 파일, 분석 제외")
            other_files.append(filename)
    
    if other_files:
        print(f"💡 참고: {len(other_files)}개의 다른 사용자 파일은 분석에서 제외됩니다.")
    
    return author_files

def select_primary_problem(author_files):
    """여러 문제 중 기본으로 처리할 문제를 선택합니다."""
    if not author_files:
        return None
    
    # 우선순위: 새로 추가된 파일 > 수정된 파일, 문제 번호가 큰 것 우선
    added_files = [f for f in author_files if f['status'] == 'added']
    if added_files:
        primary = max(added_files, key=lambda x: int(x['problem_id']))
        print(f"🎯 기본 처리 대상: 새로 추가된 문제 {primary['problem_id']}")
    else:
        primary = max(author_files, key=lambda x: int(x['problem_id']))
        print(f"🎯 기본 처리 대상: 수정된 문제 {primary['problem_id']}")
    
    return primary

def create_problems_summary(author_files):
    """문제 요약 정보를 생성합니다."""
    if not author_files:
        return ""
    
    if len(author_files) == 1:
        file = author_files[0]
        status_text = "새로 추가" if file['status'] == 'added' else "수정"
        return f"📊 **이번 PR**: 문제 {file['problem_id']} ({status_text})"
    
    added_count = len([f for f in author_files if f['status'] == 'added'])
    modified_count = len([f for f in author_files if f['status'] == 'modified'])
    
    summary_lines = [f"📊 **이번 PR 변경사항** (총 {len(author_files)}개)"]
    
    if added_count > 0:
        added_problems = [f['problem_id'] for f in author_files if f['status'] == 'added']
        summary_lines.append(f"   📁 새로 추가: {added_count}개 (문제 {', '.join(added_problems)})")
    
    if modified_count > 0:
        modified_problems = [f['problem_id'] for f in author_files if f['status'] == 'modified']
        summary_lines.append(f"   📝 수정: {modified_count}개 (문제 {', '.join(modified_problems)})")
    
    return "\\n".join(summary_lines)

def set_github_output(name, value):
    """GitHub Actions의 출력을 설정합니다."""
    output_file = os.environ.get('GITHUB_OUTPUT')
    if output_file:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"{name}={value}\n")
    print(f"📤 GITHUB_OUTPUT: {name}={value}")

def main():
    pr_number = os.environ.get('PR_NUMBER')
    repo = os.environ.get('GITHUB_REPOSITORY')

    if not pr_number or not repo:
        print("❌ 환경 변수 PR_NUMBER 또는 GITHUB_REPOSITORY가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    # 1. PR 작성자 정보 가져오기
    pr_author = get_pr_info(pr_number, repo)
    if not pr_author:
        print("❌ PR 작성자 정보를 가져올 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    # 2. PR에서 변경된 Main.java 파일들 가져오기
    changed_files = get_pr_changed_files(pr_number, repo)
    
    if not changed_files:
        print("❌ PR에서 변경된 Main.java 파일을 찾을 수 없습니다.", file=sys.stderr)
        # 더미 값 설정
        set_github_output('author', pr_author)
        set_github_output('problem_id', '0000')
        set_github_output('code_file', 'dummy/Main.java')
        set_github_output('language', 'java')
        set_github_output('has_valid_problems', 'false')
        set_github_output('problems_summary', '❌ 변경된 Main.java 파일이 없습니다.')
        return

    # 3. PR 작성자의 파일만 필터링
    author_files = filter_author_files(changed_files, pr_author)
    
    if not author_files:
        print("❌ PR 작성자의 유효한 문제 파일이 없습니다.", file=sys.stderr)
        # 더미 값 설정
        set_github_output('author', pr_author)
        set_github_output('problem_id', '0000')
        set_github_output('code_file', 'dummy/Main.java')
        set_github_output('language', 'java')
        set_github_output('has_valid_problems', 'false')
        set_github_output('problems_summary', f'❌ {pr_author}님의 유효한 문제 파일이 없습니다.')
        return

    # 4. 기본 처리할 문제 선택
    primary_problem = select_primary_problem(author_files)
    
    # 5. GitHub Actions 출력 설정
    set_github_output('author', primary_problem['author'])
    set_github_output('problem_id', primary_problem['problem_id'])
    set_github_output('code_file', primary_problem['code_file'])
    set_github_output('language', primary_problem['language'])
    set_github_output('has_valid_problems', 'true')
    
    # 6. 파일 상태별 카운트
    added_count = len([f for f in author_files if f['status'] == 'added'])
    modified_count = len([f for f in author_files if f['status'] == 'modified'])
    
    set_github_output('total_problems_count', str(len(author_files)))
    set_github_output('added_problems_count', str(added_count))
    set_github_output('modified_problems_count', str(modified_count))
    set_github_output('is_multiple_problems', 'true' if len(author_files) > 1 else 'false')
    
    # 7. 문제 요약 정보
    problems_summary = create_problems_summary(author_files)
    set_github_output('problems_summary', problems_summary)
    
    # 8. 분석 결과를 JSON으로 저장
    analysis_result = {
        'pr_author': pr_author,
        'pr_number': pr_number,
        'author_files': author_files,
        'primary_problem': primary_problem,
        'summary': {
            'total_count': len(author_files),
            'added_count': added_count,
            'modified_count': modified_count
        }
    }
    
    with open('pr_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    # 9. 결과 출력
    print(f"\n🎉 분석 완료!")
    print(f"👤 PR 작성자: {pr_author}")
    print(f"📊 분석 대상: {len(author_files)}개 문제")
    print(f"   📁 새로 추가: {added_count}개")
    print(f"   📝 수정: {modified_count}개")
    print(f"🎯 테스트 대상: 문제 {primary_problem['problem_id']} ({primary_problem['status']})")
    
    if len(author_files) > 1:
        print("💡 여러 문제가 변경되었지만, 가장 우선순위가 높은 문제를 테스트합니다.")

if __name__ == "__main__":
    main()