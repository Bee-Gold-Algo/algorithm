#!/usr/bin/env python3
"""
tests/test_weekly_counter.py
주간 문제 카운트 기능을 테스트하는 코드
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytz
import json

# test 디렉토리에서 상위 디렉토리의 scripts 모듈을 import 할 수 있도록 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))  # test 디렉토리
parent_dir = os.path.dirname(current_dir)  # 프로젝트 루트
scripts_dir = os.path.join(parent_dir, 'scripts')  # scripts 디렉토리
sys.path.insert(0, parent_dir)  # 프로젝트 루트를 sys.path에 추가

try:
    # deadline_checker.py가 프로젝트 루트에 있으므로 직접 import
    from deadline_checker import (
        get_current_week_range,
        get_weekly_problem_count_by_commit_time,
        get_weekly_problem_count_alternative,
        get_participants_from_directory
    )
    print(f"✅ deadline_checker.py 모듈 로드 성공 (프로젝트 루트)")
except ImportError as e:
    print(f"❌ deadline_checker.py를 찾을 수 없습니다: {e}")
    print(f"📁 현재 디렉토리: {current_dir}")
    print(f"📁 상위 디렉토리: {parent_dir}")
    print(f"📄 deadline_checker.py 존재 (루트): {os.path.exists(os.path.join(parent_dir, 'deadline_checker.py'))}")
    print(f"📄 deadline_checker.py 존재 (scripts): {os.path.exists(os.path.join(scripts_dir, 'deadline_checker.py'))}")
    print("💡 deadline_checker.py 파일이 프로젝트 루트에 있는지 확인해주세요.")
    sys.exit(1)

class TestWeeklyCounter(unittest.TestCase):
    """주간 문제 카운트 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.kst = pytz.timezone("Asia/Seoul")
        
        # 테스트용 환경변수 설정
        os.environ["GITHUB_TOKEN"] = "test_token"
        os.environ["GITHUB_REPOSITORY"] = "test_user/test_repo"
    
    def test_current_week_range(self):
        """주간 범위 계산 테스트"""
        print("\n🧪 주간 범위 계산 테스트")
        
        week_start, week_end = get_current_week_range()
        
        # 주간 범위가 올바른지 확인
        self.assertEqual(week_start.weekday(), 0)  # 월요일 = 0
        self.assertEqual(week_start.hour, 0)
        self.assertEqual(week_start.minute, 0)
        self.assertEqual(week_start.second, 0)
        
        self.assertEqual(week_end.weekday(), 6)  # 일요일 = 6
        self.assertEqual(week_end.hour, 23)
        self.assertEqual(week_end.minute, 59)
        self.assertEqual(week_end.second, 59)
        
        print(f"✅ 주간 범위: {week_start.strftime('%Y-%m-%d %H:%M')} ~ {week_end.strftime('%Y-%m-%d %H:%M')}")
    
    def create_mock_commit_data(self, username, commit_dates, problem_numbers):
        """테스트용 커밋 데이터 생성"""
        commits = []
        for i, (commit_date, problem_num) in enumerate(zip(commit_dates, problem_numbers)):
            commit = {
                "sha": f"commit_{i}",
                "commit": {
                    "author": {
                        "date": commit_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }
                },
                "author": {
                    "login": username
                }
            }
            commits.append(commit)
        return commits
    
    def create_mock_directory_structure(self, username, problem_numbers):
        """테스트용 디렉토리 구조 생성"""
        contents = []
        for problem_num in problem_numbers:
            contents.append({
                "name": str(problem_num),
                "type": "dir"
            })
        return contents
    
    @patch('requests.get')
    def test_weekly_problem_count_this_week_commits(self, mock_get):
        """이번 주 커밋이 있는 경우 테스트"""
        print("\n🧪 이번 주 커밋 카운트 테스트")
        
        username = "test_user"
        week_start, week_end = get_current_week_range()
        
        # 이번 주 커밋 데이터 (화요일, 목요일)
        tuesday = week_start + timedelta(days=1, hours=10)  # 화요일 10시
        thursday = week_start + timedelta(days=3, hours=15)  # 목요일 15시
        
        commit_dates = [tuesday, thursday]
        problem_numbers = [1001, 1002]
        
        # Mock 설정
        mock_responses = []
        
        # 1. 디렉토리 구조 응답
        directory_response = MagicMock()
        directory_response.status_code = 200
        directory_response.json.return_value = self.create_mock_directory_structure(username, problem_numbers)
        mock_responses.append(directory_response)
        
        # 2. 각 문제별 커밋 히스토리 응답
        for i, (commit_date, problem_num) in enumerate(zip(commit_dates, problem_numbers)):
            commit_response = MagicMock()
            commit_response.status_code = 200
            commit_response.json.return_value = self.create_mock_commit_data(username, [commit_date], [problem_num])
            mock_responses.append(commit_response)
        
        mock_get.side_effect = mock_responses
        
        # 테스트 실행
        count = get_weekly_problem_count_by_commit_time(username)
        
        self.assertEqual(count, 2)
        print(f"✅ 이번 주 커밋 2개 정상 카운트: {count}개")
    
    @patch('requests.get')
    def test_weekly_problem_count_last_week_commits(self, mock_get):
        """지난 주 커밋은 카운트되지 않는 경우 테스트"""
        print("\n🧪 지난 주 커밋 제외 테스트")
        
        username = "test_user"
        week_start, week_end = get_current_week_range()
        
        # 지난 주 커밋 데이터
        last_week = week_start - timedelta(days=3)  # 지난 주 금요일
        
        commit_dates = [last_week]
        problem_numbers = [1001]
        
        # Mock 설정
        mock_responses = []
        
        # 1. 디렉토리 구조 응답
        directory_response = MagicMock()
        directory_response.status_code = 200
        directory_response.json.return_value = self.create_mock_directory_structure(username, problem_numbers)
        mock_responses.append(directory_response)
        
        # 2. 커밋 히스토리 응답 (지난 주 커밋)
        commit_response = MagicMock()
        commit_response.status_code = 200
        commit_response.json.return_value = self.create_mock_commit_data(username, commit_dates, problem_numbers)
        mock_responses.append(commit_response)
        
        mock_get.side_effect = mock_responses
        
        # 테스트 실행
        count = get_weekly_problem_count_by_commit_time(username)
        
        self.assertEqual(count, 0)
        print(f"✅ 지난 주 커밋 제외 확인: {count}개")
    
    @patch('requests.get')
    def test_weekly_problem_count_mixed_commits(self, mock_get):
        """이번 주와 지난 주 커밋이 섞여있는 경우 테스트"""
        print("\n🧪 이번 주/지난 주 커밋 혼합 테스트")
        
        username = "test_user"
        week_start, week_end = get_current_week_range()
        
        # 이번 주 커밋 2개, 지난 주 커밋 1개
        this_week_tuesday = week_start + timedelta(days=1, hours=14)
        this_week_friday = week_start + timedelta(days=4, hours=16)
        last_week_thursday = week_start - timedelta(days=4)
        
        # Mock 설정 - 각 문제별로 별도 응답
        mock_responses = []
        
        # 1. 디렉토리 구조 응답
        directory_response = MagicMock()
        directory_response.status_code = 200
        directory_response.json.return_value = self.create_mock_directory_structure(username, [1001, 1002, 1003])
        mock_responses.append(directory_response)
        
        # 2. 각 문제별 커밋 히스토리
        # 문제 1001 - 이번 주 커밋
        commit_1001 = MagicMock()
        commit_1001.status_code = 200
        commit_1001.json.return_value = self.create_mock_commit_data(username, [this_week_tuesday], [1001])
        mock_responses.append(commit_1001)
        
        # 문제 1002 - 이번 주 커밋
        commit_1002 = MagicMock()
        commit_1002.status_code = 200
        commit_1002.json.return_value = self.create_mock_commit_data(username, [this_week_friday], [1002])
        mock_responses.append(commit_1002)
        
        # 문제 1003 - 지난 주 커밋
        commit_1003 = MagicMock()
        commit_1003.status_code = 200
        commit_1003.json.return_value = self.create_mock_commit_data(username, [last_week_thursday], [1003])
        mock_responses.append(commit_1003)
        
        mock_get.side_effect = mock_responses
        
        # 테스트 실행
        count = get_weekly_problem_count_by_commit_time(username)
        
        self.assertEqual(count, 2)
        print(f"✅ 혼합 커밋에서 이번 주만 카운트: {count}개")
    
    @patch('requests.get')
    def test_weekly_problem_count_no_commits(self, mock_get):
        """커밋이 없는 경우 테스트"""
        print("\n🧪 커밋 없음 테스트")
        
        username = "test_user"
        
        # Mock 설정
        directory_response = MagicMock()
        directory_response.status_code = 200
        directory_response.json.return_value = self.create_mock_directory_structure(username, [1001])
        
        commit_response = MagicMock()
        commit_response.status_code = 200
        commit_response.json.return_value = []  # 커밋 없음
        
        mock_get.side_effect = [directory_response, commit_response]
        
        # 테스트 실행
        count = get_weekly_problem_count_by_commit_time(username)
        
        self.assertEqual(count, 0)
        print(f"✅ 커밋 없는 경우 확인: {count}개")
    
    def test_edge_cases(self):
        """경계 조건 테스트"""
        print("\n🧪 경계 조건 테스트")
        
        week_start, week_end = get_current_week_range()
        
        # 월요일 00:00:00 정확히
        exactly_start = week_start
        print(f"📅 주간 시작 시간: {exactly_start}")
        
        # 일요일 23:59:59 정확히
        exactly_end = week_end
        print(f"📅 주간 종료 시간: {exactly_end}")
        
        # 시간 차이 확인
        duration = exactly_end - exactly_start
        expected_duration = timedelta(days=7) - timedelta(seconds=1)
        
        self.assertAlmostEqual(duration.total_seconds(), expected_duration.total_seconds(), delta=1)
        print(f"✅ 주간 지속시간: {duration}")


class TestGitLogCounter(unittest.TestCase):
    """Git 로그 기반 카운터 테스트"""
    
    @patch('subprocess.run')
    def test_git_log_parsing(self, mock_run):
        """Git 로그 파싱 테스트"""
        print("\n🧪 Git 로그 파싱 테스트")
        
        username = "test_user"
        week_start, week_end = get_current_week_range()
        
        # Mock Git 로그 출력
        tuesday = week_start + timedelta(days=1, hours=10)
        friday = week_start + timedelta(days=4, hours=15)
        
        mock_git_output = f"""abc123|{tuesday.isoformat()}|{username}
{username}/1001/Main.java

def456|{friday.isoformat()}|{username}
{username}/1002/Main.java

"""
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_git_output
        mock_run.return_value = mock_result
        
        # 테스트 실행
        count = get_weekly_problem_count_alternative(username)
        
        self.assertEqual(count, 2)
        print(f"✅ Git 로그 파싱 성공: {count}개")


def run_manual_test():
    """실제 레포지토리에서 수동 테스트"""
    print("\n🔧 실제 데이터 수동 테스트")
    print("=" * 50)
    
    # 현재 주간 범위 출력
    week_start, week_end = get_current_week_range()
    print(f"📅 이번 주 범위: {week_start.strftime('%Y-%m-%d %H:%M')} ~ {week_end.strftime('%Y-%m-%d %H:%M')} KST")
    
    # 참가자 목록 가져오기
    try:
        participants = get_participants_from_directory()
        print(f"👥 발견된 참가자: {participants}")
        
        if participants:
            # 첫 번째 참가자로 테스트
            test_user = participants[0]
            print(f"\n🔍 {test_user} 테스트 중...")
            
            # GitHub API 방식 테스트
            if os.getenv("GITHUB_TOKEN") and os.getenv("GITHUB_REPOSITORY"):
                try:
                    count_api = get_weekly_problem_count_by_commit_time(test_user)
                    print(f"📊 GitHub API 결과: {count_api}개")
                except Exception as e:
                    print(f"❌ GitHub API 테스트 실패: {e}")
            else:
                print("⚠️ GitHub 환경변수가 설정되지 않아 API 테스트를 건너뜁니다.")
            
            # Git 로그 방식 테스트
            try:
                count_git = get_weekly_problem_count_alternative(test_user)
                print(f"📊 Git 로그 결과: {count_git}개")
            except Exception as e:
                print(f"❌ Git 로그 테스트 실패: {e}")
        
        else:
            print("⚠️ 참가자 디렉토리를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 수동 테스트 실패: {e}")


def main():
    """테스트 메인 함수"""
    print("🧪 주간 문제 카운트 테스트 시작")
    print("=" * 60)
    
    # 단위 테스트 실행
    print("\n📋 단위 테스트 실행")
    unittest.main(argv=[''], exit=False, verbosity=0)
    
    # 수동 테스트 실행
    run_manual_test()
    
    print("\n✅ 모든 테스트 완료!")


if __name__ == "__main__":
    main()