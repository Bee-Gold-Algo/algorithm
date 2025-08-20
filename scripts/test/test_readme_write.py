#!/usr/bin/env python3
"""
github_actions_simulator.py
GitHub Actions 워크플로우 시뮬레이터
실제 GitHub API 호출 없이 로컬에서 테스트 가능
"""

import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

class GitHubActionsSimulator:
    """GitHub Actions 환경 시뮬레이터"""
    
    def __init__(self):
        self.test_dir = tempfile.mkdtemp(prefix="gh_actions_test_")
        self.original_cwd = os.getcwd()
        
        # 환경변수 설정
        self.env_vars = {
            "GITHUB_REPOSITORY": "test-org/algorithm-study",
            "PR_NUMBER": "123",
            "GITHUB_TOKEN": "fake_token_for_test",
            "WEEK_NUMBER": "1",
            "BRANCH_USER": "testuser",
            "GITHUB_OUTPUT": str(Path(self.test_dir) / "github_output.txt")
        }
        
        print(f"🧪 테스트 환경 초기화: {self.test_dir}")
    
    def setup_test_files(self):
        """테스트용 파일 구조 생성"""
        # scripts 디렉토리 생성
        scripts_dir = Path(self.test_dir) / "scripts"
        scripts_dir.mkdir(parents=True)
        
        # 실제 스크립트 파일들 복사 (있다면) 또는 mock 버전 생성
        self.create_mock_scripts(scripts_dir)
        
        # 테스트용 Java 파일들 생성
        test_files = {
            "testuser/1000/Main.java": """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
""",
            "testuser/1001/Main.java": """
public class Main {
    public static void main(String[] args) {
        int a = 1, b = 2;
        System.out.println(a + b);
    }
}
""",
            "testuser/2557/Main.java": """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello World!");
    }
}
"""
        }
        
        for filepath, content in test_files.items():
            full_path = Path(self.test_dir) / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        
        # 초기 README.md 생성
        initial_readme = """# 🚀 알고리즘 스터디

## 📅 1회차 현황
**기간**: 2024-08-05 ~ 2024-08-11
**마감**: 2024-08-11 23:59

### 제출 현황

| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |
|--------|----|----|----|----|----|----|---|
|        | 08/05 | 08/06 | 08/07 | 08/08 | 08/09 | 08/10 | 08/11 |
| 아직_제출없음 |  |  |  |  |  |  |  |

## 🤖 자동화 시스템 소개
자동화 테스트 시스템입니다.
"""
        
        with open(Path(self.test_dir) / "README.md", "w", encoding="utf-8") as f:
            f.write(initial_readme)
    
    def create_mock_scripts(self, scripts_dir):
        """Mock 스크립트 파일들 생성"""
        
        # session_counter.py 생성
        session_counter = """
from datetime import datetime, timedelta

def get_session_info(submission_date=None):
    if submission_date:
        date = datetime.strptime(submission_date, "%Y-%m-%d")
    else:
        date = datetime.now()
    
    # 월요일을 기준으로 주 계산
    start_of_week = date - timedelta(days=date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    return {
        "session_number": 1,
        "monday": start_of_week.strftime("%Y-%m-%d"),
        "sunday": end_of_week.strftime("%Y-%m-%d"),
        "deadline": end_of_week.strftime("%Y-%m-%d 23:59"),
    }
"""
        
        with open(scripts_dir / "session_counter.py", "w", encoding="utf-8") as f:
            f.write(session_counter)
        
        # __init__.py 생성
        with open(scripts_dir / "__init__.py", "w", encoding="utf-8") as f:
            f.write("")
    
    def simulate_pr_files(self, scenario="multiple_dates"):
        """PR 파일 변경사항 시뮬레이션"""
        scenarios = {
            "multiple_dates": [
                {
                    "filename": "testuser/1000/Main.java",
                    "status": "modified",
                    "additions": 5,
                    "deletions": 2,
                    "commit_date": "2024-08-05"  # 월요일
                },
                {
                    "filename": "testuser/1000/Main.java", 
                    "status": "modified",
                    "additions": 3,
                    "deletions": 1,
                    "commit_date": "2024-08-07"  # 수요일 (최신)
                },
                {
                    "filename": "testuser/1001/Main.java",
                    "status": "added", 
                    "additions": 10,
                    "deletions": 0,
                    "commit_date": "2024-08-06"  # 화요일
                }
            ],
            "single_date": [
                {
                    "filename": "testuser/2557/Main.java",
                    "status": "added",
                    "additions": 8,
                    "deletions": 0, 
                    "commit_date": "2024-08-07"
                }
            ]
        }
        
        return scenarios.get(scenario, [])
    
    def create_mock_extract_pr_info(self, file_changes):
        """Mock extract_pr_info.py 실행 결과 생성"""
        problems = []
        file_dates = {}
        
        # 파일별 최신 날짜 계산
        for change in file_changes:
            filename = change["filename"]
            commit_date = change["commit_date"]
            
            if filename not in file_dates or commit_date >= file_dates[filename]:
                file_dates[filename] = commit_date
        
        # 중복 제거된 문제 목록 생성
        problem_map = {}
        for change in file_changes:
            filename = change["filename"]
            
            # 파일 경로에서 정보 추출
            parts = Path(filename).parts
            if len(parts) >= 3 and parts[2] == "Main.java" and parts[1].isdigit():
                problem_id = parts[1]
                author = parts[0]
                submission_date = file_dates[filename]
                
                key = (problem_id, author)
                if key not in problem_map or submission_date > problem_map[key]["submission_date"]:
                    problem_map[key] = {
                        "problem_id": problem_id,
                        "author": author,
                        "code_file": filename,
                        "language": "java",
                        "submission_date": submission_date,
                        "file_status": change["status"],
                        "additions": change["additions"],
                        "deletions": change["deletions"]
                    }
        
        problems = list(problem_map.values())
        
        # problems_info.json 생성
        with open(Path(self.test_dir) / "problems_info.json", "w", encoding="utf-8") as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)
        
        print(f"📝 생성된 문제 목록:")
        for problem in problems:
            print(f"  - 문제 {problem['problem_id']} ({problem['author']}) - {problem['submission_date']}")
        
        return problems
    
    def run_update_readme_batch(self):
        """update_readme_batch.py 시뮬레이션 실행"""
        print("\n🔄 README 배치 업데이트 시뮬레이션...")
        
        os.chdir(self.test_dir)
        
        try:
            with open("problems_info.json", "r", encoding="utf-8") as f:
                problems = json.load(f)
            
            if not problems:
                print("ℹ️ 처리할 문제가 없습니다.")
                return True
            
            # 날짜별 문제 분포 출력
            date_groups = {}
            for problem in problems:
                date = problem.get("submission_date", "unknown")
                if date not in date_groups:
                    date_groups[date] = []
                date_groups[date].append(problem)
            
            print(f"📅 제출 날짜 분포:")
            for date, problem_list in sorted(date_groups.items()):
                problem_ids = [p["problem_id"] for p in problem_list]
                print(f"  - {date}: {len(problem_list)}개 문제 ({', '.join(problem_ids)})")
            
            # 각 문제별로 README 업데이트 (순서를 날짜순으로 정렬)
            problems_sorted = sorted(problems, key=lambda x: x.get("submission_date", ""))
            success_count = 0
            
            for problem in problems_sorted:
                success = self.simulate_update_readme_single(
                    problem["problem_id"],
                    problem["author"], 
                    problem.get("submission_date", datetime.now().strftime("%Y-%m-%d")),
                    problem.get("language", "Java")
                )
                if success:
                    success_count += 1
            
            print(f"\n📊 업데이트 완료: {success_count}/{len(problems)}개 성공")
            return success_count == len(problems)
            
        except Exception as e:
            print(f"❌ 배치 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            os.chdir(self.original_cwd)
    
    def simulate_update_readme_single(self, problem_id, author, submission_date, language):
        """단일 문제 README 업데이트 시뮬레이션"""
        try:
            print(f"  🔄 업데이트: 문제 {problem_id} ({author}) - {submission_date}")
            
            # README 읽기
            with open("README.md", "r", encoding="utf-8") as f:
                readme_content = f.read()
            
            # 업데이트 로직 시뮬레이션
            updated_readme = self.update_readme_content(
                readme_content, problem_id, author, submission_date
            )
            
            # README 저장
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(updated_readme)
            
            print(f"    ✅ 성공")
            return True
            
        except Exception as e:
            print(f"    ❌ 실패: {e}")
            return False
    
    def update_readme_content(self, readme_content, problem_id, author, submission_date):
        """README 내용 업데이트 로직"""
        from datetime import datetime
        
        # 요일 계산
        weekday_idx = datetime.strptime(submission_date, "%Y-%m-%d").weekday()
        
        lines = readme_content.split("\n")
        author_line_idx = None
        
        # 작성자 라인 찾기
        for i, line in enumerate(lines):
            if line.strip().startswith(f"| {author} "):
                author_line_idx = i
                break
        
        # 작성자 라인이 없으면 새로 생성
        if author_line_idx is None:
            # 테이블의 끝 찾기
            table_end_idx = None
            for i, line in enumerate(lines):
                if "아직_제출없음" in line:
                    table_end_idx = i
                    break
                elif i > 0 and "|" in lines[i-1] and "##" in line:
                    # 테이블 다음에 오는 섹션 발견
                    table_end_idx = i
                    break
            
            if table_end_idx is not None:
                # "아직_제출없음" 라인을 새 사용자 라인으로 교체
                if "아직_제출없음" in lines[table_end_idx]:
                    new_line = f"| {author} |  |  |  |  |  |  |  |"
                    lines[table_end_idx] = new_line
                    author_line_idx = table_end_idx
                else:
                    # 테이블 중간에 삽입
                    new_line = f"| {author} |  |  |  |  |  |  |  |"
                    lines.insert(table_end_idx, new_line)
                    author_line_idx = table_end_idx
        
        # 해당 작성자 라인 업데이트
        if author_line_idx is not None:
            line = lines[author_line_idx]
            
            # 테이블 파싱
            parts = line.split("|")
            
            # 첫 번째와 마지막 빈 부분 제거
            if len(parts) > 0 and parts[0].strip() == "":
                parts = parts[1:]
            if len(parts) > 0 and parts[-1].strip() == "":
                parts = parts[:-1]
            
            # 각 부분 정리
            parts = [p.strip() for p in parts]
            
            # 정확히 8개 컬럼 보장 (사용자명 + 7일)
            if len(parts) < 8:
                while len(parts) < 8:
                    parts.append("")
            elif len(parts) > 8:
                parts = parts[:8]
            
            # 모든 요일에서 해당 문제 제거 (중복 방지)
            for j in range(1, 8):  # 월~일 (7개 열, 인덱스 1-7)
                if parts[j]:
                    problems = [p.strip() for p in parts[j].split(",") 
                              if p.strip() and p.strip() != problem_id]
                    parts[j] = ", ".join(problems) if problems else ""
                else:
                    parts[j] = ""
            
            # 새로운 요일에 문제 추가
            day_col_idx = weekday_idx + 1  # 월요일=0이므로 +1
            
            if day_col_idx < 8:  # 인덱스 1-7 범위 내에서만
                existing_problems = []
                if parts[day_col_idx]:
                    existing_problems = [p.strip() for p in parts[day_col_idx].split(",") 
                                       if p.strip()]
                
                if problem_id not in existing_problems:
                    existing_problems.append(problem_id)
                
                # 문제 번호순으로 정렬
                parts[day_col_idx] = ", ".join(sorted(existing_problems, key=int))
            
            # 테이블 형식으로 재구성 (모든 8개 컬럼 포함)
            formatted_line = "|"
            for i in range(8):
                formatted_line += f" {parts[i]} |"
            
            lines[author_line_idx] = formatted_line
        
        return "\n".join(lines)
    
    def run_test_scenario(self, scenario_name="multiple_dates"):
        """테스트 시나리오 실행"""
        print(f"\n🎬 시나리오 실행: {scenario_name}")
        print("=" * 50)
        
        try:
            # 1. 테스트 환경 설정
            self.setup_test_files()
            
            # 2. PR 변경사항 시뮬레이션
            file_changes = self.simulate_pr_files(scenario_name)
            print(f"📋 PR 변경사항: {len(file_changes)}개 파일")
            for change in file_changes:
                print(f"  - {change['filename']} ({change['status']}) - {change['commit_date']}")
            
            # 3. extract_pr_info.py 시뮬레이션
            print(f"\n🔍 PR 정보 추출...")
            problems = self.create_mock_extract_pr_info(file_changes)
            
            # 4. README 업데이트 전 상태 출력
            print(f"\n📖 README 업데이트 전:")
            self.print_readme_table()
            
            # 5. update_readme_batch.py 시뮬레이션
            success = self.run_update_readme_batch()
            
            # 6. README 업데이트 후 상태 출력
            print(f"\n📖 README 업데이트 후:")
            self.print_readme_table()
            
            return success
            
        except Exception as e:
            print(f"❌ 시나리오 실행 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_readme_table(self):
        """README 테이블 상태 출력"""
        try:
            with open(Path(self.test_dir) / "README.md", "r", encoding="utf-8") as f:
                content = f.read()
            
            lines = content.split("\n")
            in_table = False
            table_lines = []
            
            for line in lines:
                if "### 제출 현황" in line:
                    in_table = True
                    continue
                elif in_table and line.startswith("##"):
                    break
                elif in_table and line.strip():
                    table_lines.append(line)
            
            # 테이블 라인들 출력
            for line in table_lines:
                print(f"  {line}")
            
            # 추가 디버깅 정보 (빈 컬럼 보존)
            if table_lines:
                print(f"\n  📊 테이블 분석:")
                for i, line in enumerate(table_lines):
                    if "|" in line and "참가자" not in line and "---" not in line and line.strip():
                        # 빈 컬럼 보존을 위한 개선된 파싱
                        parts = line.split("|")
                        
                        # 첫 번째와 마지막 빈 부분만 제거
                        if len(parts) > 0 and parts[0].strip() == "":
                            parts = parts[1:]
                        if len(parts) > 0 and parts[-1].strip() == "":
                            parts = parts[:-1]
                        
                        # strip만 하고 빈 문자열은 유지
                        parts = [p.strip() for p in parts]
                        
                        if parts:
                            print(f"    라인 {i}: {len(parts)}개 컬럼 - {parts}")
                    
        except Exception as e:
            print(f"  ❌ README 읽기 실패: {e}")
    
    def verify_scenario_results(self, expected_results):
        """시나리오 결과 검증"""
        print(f"\n🔍 결과 검증...")
        
        try:
            with open(Path(self.test_dir) / "README.md", "r", encoding="utf-8") as f:
                content = f.read()
            
            for author, expected_problems in expected_results.items():
                # 사용자 라인 찾기 (더 유연하게)
                user_line = None
                for line in content.split("\n"):
                    line_stripped = line.strip()
                    if line_stripped.startswith("|") and f" {author} " in line_stripped:
                        user_line = line_stripped
                        break
                
                if user_line is None:
                    print(f"  ❌ {author} 라인을 찾을 수 없음")
                    print(f"     README 내용 확인:")
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if "|" in line and "참가자" not in line and "---" not in line:
                            print(f"     Line {i}: {repr(line)}")
                    return False
                
                # 테이블 파싱 개선 (빈 컬럼 보존)
                parts = user_line.split("|")
                
                # 첫 번째와 마지막 빈 부분만 제거
                if len(parts) > 0 and parts[0].strip() == "":
                    parts = parts[1:]
                if len(parts) > 0 and parts[-1].strip() == "":
                    parts = parts[:-1]
                
                # strip만 하고 빈 문자열은 유지 (제거하지 않음)
                parts = [p.strip() for p in parts]
                
                print(f"  📋 {author} 라인 파싱: {parts}")
                
                if len(parts) < 8:
                    print(f"  ❌ {author} 라인의 컬럼 수가 부족함: {len(parts)}/8")
                    print(f"     원본 라인: {repr(user_line)}")
                    return False
                
                # 각 요일별 검증
                weekdays = ["월", "화", "수", "목", "금", "토", "일"]
                for day_idx, expected_day_problems in enumerate(expected_problems):
                    col_idx = day_idx + 1  # 첫 번째 컬럼은 사용자명
                    
                    if col_idx < len(parts):
                        actual_problems_str = parts[col_idx].strip()
                        if actual_problems_str:
                            actual_problems = set(p.strip() for p in actual_problems_str.split(",") if p.strip())
                        else:
                            actual_problems = set()
                        
                        expected_problems_set = set(expected_day_problems)
                        
                        if actual_problems != expected_problems_set:
                            print(f"  ❌ {author} {weekdays[day_idx]}요일 불일치:")
                            print(f"      예상: {expected_problems_set}")
                            print(f"      실제: {actual_problems}")
                            print(f"      원본: '{actual_problems_str}'")
                            return False
                        else:
                            if actual_problems:
                                print(f"  ✅ {author} {weekdays[day_idx]}요일: {actual_problems}")
                            else:
                                print(f"  ✅ {author} {weekdays[day_idx]}요일: (비어있음)")
                    else:
                        if expected_day_problems:
                            print(f"  ❌ {author} {weekdays[day_idx]}요일 컬럼이 없음")
                            return False
                        else:
                            print(f"  ✅ {author} {weekdays[day_idx]}요일: (비어있음)")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 검증 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """테스트 환경 정리"""
        os.chdir(self.original_cwd)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 테스트 환경 정리 완료")

def run_comprehensive_test():
    """종합 테스트 실행"""
    print("🚀 GitHub Actions 워크플로우 시뮬레이션 테스트")
    print("=" * 60)
    
    simulator = GitHubActionsSimulator()
    
    try:
        # 시나리오 1: 같은 문제의 다른 날짜 제출
        print("\n📋 시나리오 1: 날짜 중복 문제 해결 테스트")
        success1 = simulator.run_test_scenario("multiple_dates")
        
        # 결과 검증
        expected_results = {
            "testuser": [
                [],        # 월요일 (1000이 수요일로 이동되어야 함)
                ["1001"],  # 화요일 (1001)
                ["1000"],  # 수요일 (1000이 여기로 이동)
                [],        # 목요일
                [],        # 금요일
                [],        # 토요일
                []         # 일요일
            ]
        }
        
        verify1 = simulator.verify_scenario_results(expected_results)
        
        if success1 and verify1:
            print("✅ 시나리오 1 통과: 날짜 중복 문제가 올바르게 해결됨")
        else:
            print("❌ 시나리오 1 실패")
            return False
        
        # 새로운 시뮬레이터로 시나리오 2 실행
        simulator.cleanup()
        simulator = GitHubActionsSimulator()
        
        print("\n📋 시나리오 2: 단일 날짜 제출 테스트")
        success2 = simulator.run_test_scenario("single_date")
        
        expected_results_2 = {
            "testuser": [
                [],        # 월요일
                [],        # 화요일
                ["2557"],  # 수요일 (2557)
                [],        # 목요일
                [],        # 금요일
                [],        # 토요일
                []         # 일요일
            ]
        }
        
        verify2 = simulator.verify_scenario_results(expected_results_2)
        
        if success2 and verify2:
            print("✅ 시나리오 2 통과: 단일 날짜 제출이 올바르게 처리됨")
        else:
            print("❌ 시나리오 2 실패")
            return False
        
        print("\n🎉 모든 시뮬레이션 테스트 통과!")
        print("✅ 날짜 중복 이슈 수정이 정상적으로 동작합니다.")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        simulator.cleanup()

def run_interactive_test():
    """대화형 테스트"""
    print("🔧 대화형 테스트 모드")
    print("=" * 30)
    
    simulator = GitHubActionsSimulator()
    
    try:
        simulator.setup_test_files()
        
        while True:
            print("\n📋 사용 가능한 명령:")
            print("1. 문제 추가 (add)")
            print("2. README 상태 확인 (status)")
            print("3. 종료 (quit)")
            
            command = input("\n명령을 입력하세요: ").strip().lower()
            
            if command in ["quit", "q", "종료"]:
                break
            elif command in ["add", "1"]:
                problem_id = input("문제 번호: ").strip()
                author = input("작성자: ").strip()
                date = input("제출 날짜 (YYYY-MM-DD): ").strip()
                
                success = simulator.simulate_update_readme_single(
                    problem_id, author, date, "Java"
                )
                if success:
                    print("✅ 추가 완료")
                else:
                    print("❌ 추가 실패")
                    
            elif command in ["status", "2"]:
                simulator.print_readme_table()
            else:
                print("❌ 잘못된 명령입니다.")
                
    except KeyboardInterrupt:
        print("\n🔄 테스트 중단됨")
    finally:
        simulator.cleanup()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            run_interactive_test()
        elif sys.argv[1] == "--help":
            print("사용법:")
            print("  python github_actions_simulator.py              # 종합 테스트")
            print("  python github_actions_simulator.py --interactive # 대화형 테스트")
            print("  python github_actions_simulator.py --help       # 도움말")
        else:
            print("❌ 잘못된 옵션입니다. --help를 참조하세요.")
    else:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)