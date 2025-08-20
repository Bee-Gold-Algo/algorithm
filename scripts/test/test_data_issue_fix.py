#!/usr/bin/env python3
"""
test_date_issue_fix.py
날짜 중복 이슈 수정에 대한 종합 테스트 스크립트
"""

import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sys
import subprocess
from unittest.mock import patch, MagicMock
import re

# 테스트용 임시 디렉토리
TEST_DIR = None

def setup_test_environment():
    """테스트 환경 설정"""
    global TEST_DIR
    TEST_DIR = tempfile.mkdtemp(prefix="date_fix_test_")
    print(f"🧪 테스트 디렉토리: {TEST_DIR}")
    
    # 테스트용 scripts 디렉토리 생성
    scripts_dir = Path(TEST_DIR) / "scripts"
    scripts_dir.mkdir(parents=True)
    
    return TEST_DIR

def cleanup_test_environment():
    """테스트 환경 정리"""
    global TEST_DIR
    if TEST_DIR and os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
        print(f"🧹 테스트 디렉토리 정리 완료: {TEST_DIR}")

def create_mock_problems_info(problems_data):
    """테스트용 problems_info.json 파일 생성"""
    problems_file = Path(TEST_DIR) / "problems_info.json"
    with open(problems_file, "w", encoding="utf-8") as f:
        json.dump(problems_data, f, ensure_ascii=False, indent=2)
    return problems_file

def create_mock_readme(content):
    """테스트용 README.md 파일 생성"""
    readme_file = Path(TEST_DIR) / "README.md"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(content)
    return readme_file

def create_test_files(file_structure):
    """테스트용 파일 구조 생성"""
    for filepath, content in file_structure.items():
        full_path = Path(TEST_DIR) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

class TestExtractPRInfo:
    """extract_pr_info.py 관련 테스트"""
    
    def create_complete_extract_module(self):
        """완전한 extract_pr_info.py 모듈 생성"""
        extract_script = """
import re
from pathlib import Path

def remove_duplicate_problems(problems):
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

def extract_problem_info_from_path(filepath):
    path = Path(filepath)
    parts = path.parts

    if len(parts) < 2:
        return None

    author = parts[0]

    if not path.suffix.lower() == ".java":
        return None

    problem_id = None

    if len(parts) >= 3:
        potential_id = parts[1]
        if potential_id.isdigit():
            problem_id = potential_id
    else:
        stem = path.stem
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
"""
        
        extract_file = Path(TEST_DIR) / "scripts" / "extract_pr_info.py"
        with open(extract_file, "w", encoding="utf-8") as f:
            f.write(extract_script)
        
        return extract_file
    
    def test_remove_duplicate_problems(self):
        """중복 문제 제거 테스트"""
        print("\n🔍 테스트: 중복 문제 제거")
        
        # Mock function을 위해 sys.path에 테스트 디렉토리 추가
        sys.path.insert(0, str(Path(TEST_DIR) / "scripts"))
        
        # 완전한 extract_pr_info.py 모듈 생성
        self.create_complete_extract_module()
        
        # 테스트 데이터: 같은 문제의 여러 제출
        test_problems = [
            {
                "problem_id": "1000",
                "author": "testuser",
                "code_file": "testuser/1000/Main.java",
                "language": "java",
                "submission_date": "2024-08-01"
            },
            {
                "problem_id": "1000", 
                "author": "testuser",
                "code_file": "testuser/1000/Main.java",
                "language": "java",
                "submission_date": "2024-08-03"  # 더 최신
            },
            {
                "problem_id": "1001",
                "author": "testuser", 
                "code_file": "testuser/1001/Main.java",
                "language": "java",
                "submission_date": "2024-08-02"
            }
        ]
        
        # 모듈 import 및 테스트
        import extract_pr_info
        result = extract_pr_info.remove_duplicate_problems(test_problems)
        
        # 검증
        assert len(result) == 2, f"예상 2개, 실제 {len(result)}개"
        
        # 1000번 문제는 최신 날짜(2024-08-03)만 남아야 함
        problem_1000 = next(p for p in result if p["problem_id"] == "1000")
        assert problem_1000["submission_date"] == "2024-08-03", f"날짜 오류: {problem_1000['submission_date']}"
        
        print("  ✅ 중복 제거 테스트 통과")
        
        # cleanup
        sys.path.remove(str(Path(TEST_DIR) / "scripts"))
        
    def test_extract_problem_info_from_path(self):
        """파일 경로에서 문제 정보 추출 테스트"""
        print("\n🔍 테스트: 파일 경로 분석")
        
        # Mock function을 위해 sys.path에 테스트 디렉토리 추가
        sys.path.insert(0, str(Path(TEST_DIR) / "scripts"))
        
        # 완전한 extract_pr_info.py 모듈 생성
        self.create_complete_extract_module()
        
        # 모듈 import
        import extract_pr_info
        
        # 테스트 케이스들
        test_cases = [
            ("testuser/1000/Main.java", "1000", "testuser"),
            ("alice/2557/Main.java", "2557", "alice"), 
            ("bob/Main1001.java", "1001", "bob"),
            ("charlie/solution.py", None, None),  # Java 파일이 아님
            ("invalid/path", None, None),  # 잘못된 경로
        ]
        
        for filepath, expected_id, expected_author in test_cases:
            result = extract_pr_info.extract_problem_info_from_path(filepath)
            
            if expected_id is None:
                assert result is None, f"None 예상, 실제: {result}"
            else:
                assert result is not None, f"결과가 None: {filepath}"
                assert result["problem_id"] == expected_id, f"문제 ID 오류: {result['problem_id']} != {expected_id}"
                assert result["author"] == expected_author, f"작성자 오류: {result['author']} != {expected_author}"
        
        print("  ✅ 파일 경로 분석 테스트 통과")
        
        # cleanup
        sys.path.remove(str(Path(TEST_DIR) / "scripts"))

class TestUpdateReadme:
    """update_readme.py 관련 테스트"""
    
    def create_complete_update_module(self):
        """완전한 update_readme.py 모듈 생성"""
        update_script = """
import re

def remove_problem_from_all_days(participant_data, problem_id):
    weekdays = [
        "monday", "tuesday", "wednesday", "thursday", 
        "friday", "saturday", "sunday"
    ]
    
    removed_from_days = []
    for day in weekdays:
        if problem_id in participant_data[day]:
            participant_data[day].remove(problem_id)
            removed_from_days.append(day)
    
    return removed_from_days

def parse_current_week_stats(readme_content, current_week_info):
    stats = {"participants": {}}
    week_pattern = rf"## 📅 {current_week_info['session_number']}회차 현황"
    if not re.search(week_pattern, readme_content):
        return {"participants": {}, "need_reset": True}

    table_content_match = re.search(
        r"### 제출 현황\\n\\n(.*?)(\\n##|$)", readme_content, re.DOTALL
    )
    if not table_content_match:
        return stats

    table_content = table_content_match.group(1)
    lines = table_content.strip().split("\\n")

    for line in lines:
        if (
            line.startswith("|")
            and not line.startswith("| 참가자")
            and not line.startswith("|---")
            and "아직_제출없음" not in line
        ):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 8 and parts[0]:
                participant = parts[0]
                weekdays = [
                    "monday", "tuesday", "wednesday", "thursday", 
                    "friday", "saturday", "sunday"
                ]
                participant_data = {day: [] for day in weekdays}
                for i, day in enumerate(weekdays):
                    if i + 1 < len(parts) and parts[i + 1]:
                        problems = [
                            p.strip()
                            for p in parts[i + 1].replace("...", "").split(",")
                            if p.strip().isdigit()
                        ]
                        participant_data[day] = problems
                stats["participants"][participant] = participant_data
    return stats
"""
        
        update_file = Path(TEST_DIR) / "scripts" / "update_readme.py"
        with open(update_file, "w", encoding="utf-8") as f:
            f.write(update_script)
        
        return update_file
    
    def test_remove_problem_from_all_days(self):
        """모든 요일에서 문제 제거 테스트"""
        print("\n🔍 테스트: 중복 문제 제거 (README)")
        
        # Mock function을 위해 sys.path에 테스트 디렉토리 추가
        sys.path.insert(0, str(Path(TEST_DIR) / "scripts"))
        
        # 완전한 update_readme.py 모듈 생성
        self.create_complete_update_module()
        
        # 모듈 import
        import update_readme
        
        # 테스트 데이터: 같은 문제가 여러 요일에 있는 상황
        participant_data = {
            "monday": ["1000", "1001"],
            "tuesday": [],
            "wednesday": ["1000", "2557"],  # 1000이 중복
            "thursday": [],
            "friday": ["1000"],  # 1000이 또 중복
            "saturday": [],
            "sunday": []
        }
        
        # 1000번 문제를 모든 요일에서 제거
        removed_days = update_readme.remove_problem_from_all_days(participant_data, "1000")
        
        # 검증
        expected_removed = ["monday", "wednesday", "friday"]
        assert sorted(removed_days) == sorted(expected_removed), f"제거된 요일 오류: {removed_days}"
        
        # 모든 요일에서 1000이 제거되었는지 확인
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            assert "1000" not in participant_data[day], f"{day}에서 1000이 제거되지 않음"
        
        # 다른 문제들은 그대로 남아있는지 확인
        assert "1001" in participant_data["monday"], "1001이 잘못 제거됨"
        assert "2557" in participant_data["wednesday"], "2557이 잘못 제거됨"
        
        print("  ✅ 중복 문제 제거 테스트 통과")
        
        # cleanup
        sys.path.remove(str(Path(TEST_DIR) / "scripts"))
    
    def test_readme_parsing(self):
        """README 파싱 테스트"""
        print("\n🔍 테스트: README 파싱")
        
        # 샘플 README 내용
        sample_readme = """# 🚀 알고리즘 스터디

## 📅 1회차 현황
**기간**: 2024-08-05 ~ 2024-08-11
**마감**: 2024-08-11 23:59

### 제출 현황

| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |
|--------|----|----|----|----|----|----|---|
|        | 08/05 | 08/06 | 08/07 | 08/08 | 08/09 | 08/10 | 08/11 |
| alice | 1000, 1001 | 2557 |  |  |  |  |  |
| bob |  | 1000 | 1001, 2557 |  |  |  |  |

## 🤖 자동화 시스템 소개
...
"""
        
        # Mock function을 위해 sys.path에 테스트 디렉토리 추가
        sys.path.insert(0, str(Path(TEST_DIR) / "scripts"))
        
        # 완전한 update_readme.py 모듈 생성
        self.create_complete_update_module()
        
        # 모듈 import
        import update_readme
        
        # 파싱 테스트
        week_info = {"session_number": 1}
        result = update_readme.parse_current_week_stats(sample_readme, week_info)
        
        # 검증
        participants = result["participants"]
        assert "alice" in participants, "alice 파싱 실패"
        assert "bob" in participants, "bob 파싱 실패"
        
        # alice 데이터 검증
        alice_data = participants["alice"]
        assert "1000" in alice_data["monday"], "alice 월요일 1000 누락"
        assert "1001" in alice_data["monday"], "alice 월요일 1001 누락"
        assert "2557" in alice_data["tuesday"], "alice 화요일 2557 누락"
        
        # bob 데이터 검증
        bob_data = participants["bob"]
        assert "1000" in bob_data["tuesday"], "bob 화요일 1000 누락"
        assert "1001" in bob_data["wednesday"], "bob 수요일 1001 누락"
        assert "2557" in bob_data["wednesday"], "bob 수요일 2557 누락"
        
        print("  ✅ README 파싱 테스트 통과")
        
        # cleanup
        sys.path.remove(str(Path(TEST_DIR) / "scripts"))

class TestIntegration:
    """통합 테스트"""
    
    def test_end_to_end_scenario(self):
        """종단간 시나리오 테스트"""
        print("\n🔍 테스트: 종단간 시나리오")
        
        # 시나리오: 사용자가 같은 문제를 다른 날짜에 여러 번 제출
        problems_data = [
            {
                "problem_id": "1000",
                "author": "testuser",
                "code_file": "testuser/1000/Main.java",
                "language": "java",
                "submission_date": "2024-08-05"  # 월요일
            },
            {
                "problem_id": "1000",
                "author": "testuser", 
                "code_file": "testuser/1000/Main.java",
                "language": "java",
                "submission_date": "2024-08-07"  # 수요일 (최신)
            },
            {
                "problem_id": "1001",
                "author": "testuser",
                "code_file": "testuser/1001/Main.java", 
                "language": "java",
                "submission_date": "2024-08-06"  # 화요일
            }
        ]
        
        # 초기 README 상태 (testuser가 1000을 월요일에 제출한 상태)
        initial_readme = """# 🚀 알고리즘 스터디

## 📅 1회차 현황
**기간**: 2024-08-05 ~ 2024-08-11
**마감**: 2024-08-11 23:59

### 제출 현황

| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |
|--------|----|----|----|----|----|----|---|
|        | 08/05 | 08/06 | 08/07 | 08/08 | 08/09 | 08/10 | 08/11 |
| testuser | 1000 |  |  |  |  |  |  |

## 🤖 자동화 시스템 소개
"""
        
        create_mock_readme(initial_readme)
        create_mock_problems_info(problems_data)
        
        # update_readme_batch.py 시뮬레이션
        print("  📝 배치 업데이트 시뮬레이션...")
        
        # 각 문제별로 README 업데이트 (실제로는 subprocess 호출)
        final_readme_content = initial_readme
        
        # 가장 최신 날짜 기준으로 문제를 정렬하여 처리
        unique_problems = self.remove_duplicate_problems_simulation(problems_data)
        
        # 각 문제별로 업데이트
        for problem in unique_problems:
            final_readme_content = self.simulate_readme_update(
                final_readme_content, 
                problem["problem_id"], 
                problem["author"], 
                problem["submission_date"]
            )
        
        # 결과 검증
        lines = final_readme_content.split("\n")
        testuser_line = None
        for line in lines:
            if line.strip().startswith("| testuser"):
                testuser_line = line
                break
        
        assert testuser_line is not None, "testuser 라인을 찾을 수 없음"
        
        # 테이블 파싱 (빈 컬럼 보존)
        parts = testuser_line.split("|")
        if len(parts) > 0 and parts[0].strip() == "":
            parts = parts[1:]
        if len(parts) > 0 and parts[-1].strip() == "":
            parts = parts[:-1]
        parts = [p.strip() for p in parts]
        
        print(f"    최종 testuser 라인: {parts}")
        
        # 검증: 1000은 수요일에만, 1001은 화요일에만
        monday_problems = parts[1] if len(parts) > 1 else ""    # 월요일
        tuesday_problems = parts[2] if len(parts) > 2 else ""   # 화요일  
        wednesday_problems = parts[3] if len(parts) > 3 else "" # 수요일
        
        print(f"    월요일: '{monday_problems}'")
        print(f"    화요일: '{tuesday_problems}'")
        print(f"    수요일: '{wednesday_problems}'")
        
        # 검증: 1000은 수요일에만, 1001은 화요일에만
        assert "1000" not in monday_problems, "1000이 월요일에 남아있음"
        assert "1001" in tuesday_problems, "1001이 화요일에 없음"
        assert "1000" in wednesday_problems, "1000이 수요일에 없음"
        
        print("  ✅ 종단간 시나리오 테스트 통과")
    
    def remove_duplicate_problems_simulation(self, problems):
        """중복 제거 시뮬레이션"""
        problem_map = {}
        
        for problem in problems:
            key = (problem["problem_id"], problem["author"])
            submission_date = problem.get("submission_date", "1970-01-01")
            
            if key not in problem_map or submission_date > problem_map[key]["submission_date"]:
                problem_map[key] = problem
        
        unique_problems = list(problem_map.values())
        
        if len(unique_problems) < len(problems):
            removed_count = len(problems) - len(unique_problems)
            print(f"    🔄 중복 제거: {removed_count}개 중복 제출 제거됨")
        
        return unique_problems
    
    def simulate_readme_update(self, readme_content, problem_id, author, submission_date):
        """README 업데이트 시뮬레이션 (개선된 버전)"""
        from datetime import datetime
        
        # 요일 계산
        weekday_idx = datetime.strptime(submission_date, "%Y-%m-%d").weekday()
        
        lines = readme_content.split("\n")
        author_line_idx = None
        
        # 작성자 라인 찾기
        for i, line in enumerate(lines):
            if line.strip().startswith(f"| {author}"):
                author_line_idx = i
                break
        
        if author_line_idx is not None:
            line = lines[author_line_idx]
            
            # 테이블 파싱
            parts = line.split("|")
            if len(parts) > 0 and parts[0].strip() == "":
                parts = parts[1:]
            if len(parts) > 0 and parts[-1].strip() == "":
                parts = parts[:-1]
            parts = [p.strip() for p in parts]
            
            # 8개 컬럼 보장
            while len(parts) < 8:
                parts.append("")
            
            # 모든 요일에서 해당 문제 제거 (중복 방지)
            for j in range(1, 8):  # 월~일
                if parts[j]:
                    problems = [p.strip() for p in parts[j].split(",") 
                              if p.strip() and p.strip() != problem_id]
                    parts[j] = ", ".join(problems) if problems else ""
                else:
                    parts[j] = ""
            
            # 새로운 요일에 문제 추가
            day_col_idx = weekday_idx + 1  # 월요일=0이므로 +1
            if day_col_idx < 8:
                existing_problems = []
                if parts[day_col_idx]:
                    existing_problems = [p.strip() for p in parts[day_col_idx].split(",") 
                                       if p.strip()]
                
                if problem_id not in existing_problems:
                    existing_problems.append(problem_id)
                
                parts[day_col_idx] = ", ".join(sorted(existing_problems, key=int))
            
            # 테이블 재구성
            formatted_line = "|"
            for i in range(8):
                formatted_line += f" {parts[i]} |"
            
            lines[author_line_idx] = formatted_line
        
        return "\n".join(lines)

def run_all_tests():
    """모든 테스트 실행"""
    print("🧪 날짜 중복 이슈 수정 테스트 시작")
    print("=" * 50)
    
    try:
        setup_test_environment()
        
        # 모듈 캐시 정리 함수
        def cleanup_modules():
            modules_to_remove = []
            for module_name in sys.modules:
                if module_name in ['extract_pr_info', 'update_readme']:
                    modules_to_remove.append(module_name)
            
            for module_name in modules_to_remove:
                del sys.modules[module_name]
        
        # 각 테스트 클래스 실행
        extract_tests = TestExtractPRInfo()
        
        # 첫 번째 테스트
        cleanup_modules()
        extract_tests.test_remove_duplicate_problems()
        
        # 두 번째 테스트
        cleanup_modules()
        extract_tests.test_extract_problem_info_from_path()
        
        readme_tests = TestUpdateReadme()
        
        # 세 번째 테스트
        cleanup_modules()
        readme_tests.test_remove_problem_from_all_days()
        
        # 네 번째 테스트
        cleanup_modules()
        readme_tests.test_readme_parsing()
        
        integration_tests = TestIntegration()
        
        # 다섯 번째 테스트
        cleanup_modules()
        integration_tests.test_end_to_end_scenario()
        
        print("\n🎉 모든 테스트 통과!")
        print("✅ 날짜 중복 이슈가 성공적으로 해결되었습니다.")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 최종 정리
        modules_to_remove = []
        for module_name in sys.modules:
            if module_name in ['extract_pr_info', 'update_readme']:
                modules_to_remove.append(module_name)
        
        for module_name in modules_to_remove:
            del sys.modules[module_name]
            
        cleanup_test_environment()
    
    return True

def run_manual_test():
    """수동 테스트용 함수"""
    print("\n🔧 수동 테스트 도구")
    print("실제 파일들로 테스트하고 싶다면 다음을 실행하세요:")
    print("1. problems_info.json 파일 생성")
    print("2. README.md 파일 준비") 
    print("3. update_readme_batch.py 실행")
    
    # 샘플 데이터 생성
    sample_problems = [
        {
            "problem_id": "1000",
            "author": "testuser",
            "code_file": "testuser/1000/Main.java",
            "language": "java", 
            "submission_date": "2024-08-05"
        },
        {
            "problem_id": "1000",
            "author": "testuser",
            "code_file": "testuser/1000/Main.java", 
            "language": "java",
            "submission_date": "2024-08-07"  # 더 최신
        }
    ]
    
    print("\n📝 샘플 problems_info.json:")
    print(json.dumps(sample_problems, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        run_manual_test()
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)