# scripts/extract_pr_info.py
import os
import re
import sys
import json
import subprocess

def get_pr_files(pr_number, repo):
    """GitHub API를 사용해 PR의 변경된 파일 목록을 가져옵니다."""
    print(f"🔍 GitHub API를 통해 PR #{pr_number}의 파일 목록을 조회합니다.")
    try:
        command = [
            'gh', 'api',
            f'/repos/{repo}/pulls/{pr_number}/files'
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        files = json.loads(result.stdout)
        filenames = [file['filename'] for file in files]
        print(f"✅ API 호출 성공. {len(filenames)}개의 파일 발견.")
        return filenames
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ GitHub API 호출 실패: {e}", file=sys.stderr)
        return []

def find_all_solution_files(files):
    """파일 목록에서 모든 Main.java 파일을 찾습니다."""
    solution_files = []
    for file_path in files:
        if file_path.endswith('/Main.java'):
            solution_files.append(file_path)
    
    print(f"🎯 솔루션 파일 {len(solution_files)}개 발견:")
    for file_path in solution_files:
        print(f"   - {file_path}")
    
    return solution_files

def extract_info_from_path(file_path):
    """파일 경로에서 작성자와 문제 번호를 추출합니다."""
    # 정규식 패턴: <작성자>/<문제번호>/Main.java
    match = re.search(r'^([^/]+)/(\d+)/Main\.java$', file_path)
    if match:
        author, problem_id = match.groups()
        print(f"   👤 작성자: {author}, 🔢 문제 번호: {problem_id}")
        return author, problem_id
    print(f"   ⚠️ 경로 패턴 매칭 실패: {file_path}", file=sys.stderr)
    return None, None

def extract_all_problems_info(solution_files):
    """모든 솔루션 파일에서 정보를 추출합니다."""
    problems_info = []
    
    for file_path in solution_files:
        author, problem_id = extract_info_from_path(file_path)
        if author and problem_id:
            problems_info.append({
                'author': author,
                'problem_id': problem_id,
                'code_file': file_path,
                'language': 'java'
            })
    
    return problems_info

def select_primary_problem(problems_info):
    """여러 문제 중 기본으로 처리할 문제를 선택합니다."""
    if not problems_info:
        return None
    
    # 전략 1: 문제 번호가 가장 큰 것 (최신 문제)
    primary = max(problems_info, key=lambda x: int(x['problem_id']))
    
    print(f"🎯 기본 처리 대상: 문제 {primary['problem_id']} (작성자: {primary['author']})")
    
    return primary

def set_github_output(name, value):
    """GitHub Actions의 출력을 설정합니다."""
    output_file = os.environ.get('GITHUB_OUTPUT')
    if output_file:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"{name}={value}\n")
    print(f"📤 GITHUB_OUTPUT: {name}={value}")

def create_problems_summary(problems_info):
    """여러 문제에 대한 요약 정보를 생성합니다."""
    if len(problems_info) <= 1:
        return ""
    
    summary_lines = ["📋 **이번 PR에서 제출된 모든 문제:**"]
    for i, problem in enumerate(problems_info, 1):
        summary_lines.append(f"{i}. 문제 {problem['problem_id']} - {problem['author']}")
    
    summary_lines.append("")
    summary_lines.append(f"🎯 **현재 테스트 중:** 문제 {problems_info[0]['problem_id']}")
    summary_lines.append("💡 **참고:** 다른 문제들은 별도의 PR로 나누어 제출하는 것을 권장합니다.")
    
    return "\\n".join(summary_lines)

def main():
    pr_number = os.environ.get('PR_NUMBER')
    repo = os.environ.get('GITHUB_REPOSITORY')

    if not pr_number or not repo:
        print("❌ 환경 변수 PR_NUMBER 또는 GITHUB_REPOSITORY가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    # 1. PR에서 변경된 파일 목록 가져오기
    changed_files = get_pr_files(pr_number, repo)
    if not changed_files:
        print("❌ PR에서 변경된 파일을 가져올 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    # 2. 모든 솔루션 파일 찾기
    solution_files = find_all_solution_files(changed_files)
    
    if not solution_files:
        print("❌ '.../Main.java' 형식의 파일을 찾을 수 없습니다.", file=sys.stderr)
        # 더미 값 설정
        set_github_output('author', 'unknown')
        set_github_output('problem_id', '0000')
        set_github_output('code_file', 'dummy/Main.java')
        set_github_output('language', 'java')
        set_github_output('multiple_problems', 'false')
        set_github_output('problems_count', '0')
        set_github_output('problems_summary', '❌ 올바른 파일 구조를 찾을 수 없습니다.')
        print("⚠️ 파일 구조 오류로 인해 더미 값을 설정합니다.")
        return

    # 3. 모든 문제 정보 추출
    problems_info = extract_all_problems_info(solution_files)
    
    if not problems_info:
        print("❌ 유효한 문제 정보를 추출할 수 없습니다.", file=sys.stderr)
        # 더미 값 설정
        set_github_output('author', 'unknown')
        set_github_output('problem_id', '0000')
        set_github_output('code_file', 'dummy/Main.java')
        set_github_output('language', 'java')
        set_github_output('multiple_problems', 'false')
        set_github_output('problems_count', '0')
        set_github_output('problems_summary', '❌ 유효한 문제 정보를 찾을 수 없습니다.')
        return

    # 4. 기본 처리할 문제 선택
    primary_problem = select_primary_problem(problems_info)
    
    # 5. GitHub Actions 출력 설정
    set_github_output('author', primary_problem['author'])
    set_github_output('problem_id', primary_problem['problem_id'])
    set_github_output('code_file', primary_problem['code_file'])
    set_github_output('language', primary_problem['language'])
    
    # 6. 여러 문제 관련 정보 설정
    multiple_problems = len(problems_info) > 1
    set_github_output('multiple_problems', 'true' if multiple_problems else 'false')
    set_github_output('problems_count', str(len(problems_info)))
    
    # 7. 문제 요약 정보 생성
    problems_summary = create_problems_summary(problems_info)
    set_github_output('problems_summary', problems_summary)
    
    # 8. 전체 문제 목록을 JSON으로 저장 (필요시 사용)
    with open('all_problems.json', 'w', encoding='utf-8') as f:
        json.dump(problems_info, f, ensure_ascii=False, indent=2)
    
    # 9. 결과 출력
    if multiple_problems:
        print(f"\n🎉 정보 추출 완료! (총 {len(problems_info)}개 문제)")
        print(f"🎯 기본 처리: 문제 {primary_problem['problem_id']} ({primary_problem['author']})")
        print("📝 다른 문제들:")
        for problem in problems_info:
            if problem != primary_problem:
                print(f"   - 문제 {problem['problem_id']} ({problem['author']})")
        print("\n💡 권장사항: 향후에는 문제별로 별도의 PR을 만들어 주세요!")
    else:
        print("✅ 단일 문제 정보 추출 완료.")

if __name__ == "__main__":
    main()