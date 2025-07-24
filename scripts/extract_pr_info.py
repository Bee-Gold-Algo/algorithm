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
        return

def find_solution_file(files):
    """파일 목록에서 Main.java 파일을 찾습니다."""
    for file_path in files:
        if file_path.endswith('/Main.java'):
            print(f"🎯 솔루션 파일 발견: {file_path}")
            return file_path
    return None

def extract_info_from_path(file_path):
    """파일 경로에서 작성자와 문제 번호를 추출합니다."""
    # 정규식 패턴: <작성자>/<문제번호>/Main.java
    match = re.search(r'^([^/]+)/(\d+)/Main\.java$', file_path)
    if match:
        author, problem_id = match.groups()
        print(f"👤 작성자: {author}, 🔢 문제 번호: {problem_id}")
        return author, problem_id
    print(f"⚠️ 경로 패턴 매칭 실패: {file_path}", file=sys.stderr)
    return None, None

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

    changed_files = get_pr_files(pr_number, repo)
    if not changed_files:
        print("❌ PR에서 변경된 파일을 가져올 수 없습니다.", file=sys.stderr)
        sys.exit(1) # 실패 처리

    main_file = find_solution_file(changed_files)
    
    if not main_file:
        print("❌ '.../Main.java' 형식의 파일을 찾을 수 없습니다.", file=sys.stderr)
        author, problem_id, code_file, language = "unknown", "0000", "dummy/Main.java", "java"
    else:
        author, problem_id = extract_info_from_path(main_file)
        if not author or not problem_id:
            author, problem_id = "unknown", "0000"
        code_file = main_file
        language = "java"

    set_github_output('author', author)
    set_github_output('problem_id', problem_id)
    set_github_output('code_file', code_file)
    set_github_output('language', language)

    if author == "unknown" or problem_id == "0000":
        print("⚠️ 파일 구조 오류로 인해 더미 값을 설정합니다. 후속 작업을 건너뜁니다.")
    else:
        print("✅ 정보 추출 완료.")

if __name__ == "__main__":
    main()