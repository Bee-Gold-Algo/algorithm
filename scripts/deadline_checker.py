#!/usr/bin/env python3
"""
scripts/deadline_checker.py
마감일을 체크하고 개인별 Mattermost로 알림을 보냅니다.
해당 주차(월요일~일요일)에 커밋된 문제만 카운트합니다.
"""

import os
import json
import requests
import subprocess
from datetime import datetime, timedelta
import pytz
import re


def get_current_week_range():
    """현재 주차의 시작(월요일 00:00)과 끝(일요일 23:59) 시간 반환 (KST 기준)"""
    kst = pytz.timezone("Asia/Seoul")
    now = datetime.now(kst)
    
    # 현재 주의 월요일 00:00:00 구하기
    days_since_monday = now.weekday()  # 0=월요일, 6=일요일
    week_start = now - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 현재 주의 일요일 23:59:59 구하기
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    return week_start, week_end


def get_repository_info():
    """GitHub 레포지토리 정보 가져오기"""
    try:
        # GitHub API를 통해 레포지토리 정보 가져오기
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPOSITORY")  # 예: 'username/repo-name'

        if not token or not repo:
            print("GitHub 환경변수가 설정되지 않았습니다.")
            return None

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # 레포지토리 기본 정보
        repo_url = f"https://api.github.com/repos/{repo}"
        response = requests.get(repo_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"GitHub API 오류: {response.status_code}")
            return None

    except Exception as e:
        print(f"레포지토리 정보 조회 실패: {e}")
        return None


def get_current_reminder_type():
    """현재 시간에 따른 알림 타입 결정"""
    # 디버깅 모드: 모든 메시지 타입 테스트
    if os.getenv("DEBUG_MODE") == "true":
        return "debug_all"

    kst = pytz.timezone("Asia/Seoul")
    now = datetime.now(kst)

    # 금요일 오전 9시 알림
    if now.weekday() == 4 and 8 <= now.hour < 10:  # 금요일, 8-10시 사이
        return "friday_morning"
    # 일요일 오전 9시 알림
    elif now.weekday() == 6 and 8 <= now.hour < 10:  # 일요일, 8-10시 사이
        return "sunday_morning"
    # 일요일 오후 9시 알림
    elif now.weekday() == 6 and 20 <= now.hour < 22:  # 일요일, 20-22시 사이
        return "sunday_evening"
    else:
        return "general"


def get_participants_from_directory():
    """디렉토리 구조에서 참가자 목록 추출"""
    participants = []
    try:
        # 현재 디렉토리의 모든 하위 디렉토리 검사
        for item in os.listdir("."):
            if os.path.isdir(item) and item not in [
                ".git",
                ".github",
                "scripts",
                "__pycache__",
                ".cursor",
                "docs",
            ]:
                participants.append(item)

        print(f"📁 발견된 참가자 디렉토리: {participants}")
        return participants

    except Exception as e:
        print(f"디렉토리에서 참가자 추출 실패: {e}")
        return []


def get_weekly_problem_count_by_commit_time(username):
    """GitHub API를 사용하여 이번 주에 커밋된 문제 수 계산"""
    try:
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPOSITORY")

        if not token or not repo:
            return 0

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # 이번 주 범위 계산 (월요일 00:00 ~ 일요일 23:59)
        week_start, week_end = get_current_week_range()
        
        print(f"📅 {username} 이번 주 범위: {week_start.strftime('%Y-%m-%d %H:%M')} ~ {week_end.strftime('%Y-%m-%d %H:%M')} KST")

        # 1. 해당 사용자 디렉토리의 모든 Java 파일 가져오기
        contents_url = f"https://api.github.com/repos/{repo}/contents/{username}"
        response = requests.get(contents_url, headers=headers)
        
        if response.status_code != 200:
            print(f"📁 {username} 디렉토리를 찾을 수 없습니다.")
            return 0

        problem_count = 0
        processed_problems = set()  # 중복 방지
        solved_problems = []  # 해결한 문제 번호 저장
        
        contents = response.json()
        for item in contents:
            if item["type"] == "dir":  # 문제 번호 디렉토리
                problem_dir = item["name"]
                
                # 문제 번호인지 확인 (숫자로만 구성)
                if not problem_dir.isdigit():
                    continue
                
                # Main.java 파일 경로
                main_java_path = f"{username}/{problem_dir}/Main.java"
                
                # 2. 해당 파일의 커밋 히스토리 조회 (이번 주 범위)
                commits_url = f"https://api.github.com/repos/{repo}/commits"
                commits_params = {
                    "path": main_java_path,
                    "since": week_start.isoformat(),
                    "until": week_end.isoformat(),
                    "per_page": 100
                }
                
                commits_response = requests.get(commits_url, headers=headers, params=commits_params)
                
                if commits_response.status_code == 200:
                    commits = commits_response.json()
                    
                    # 3. 이번 주에 커밋이 있는지 확인
                    for commit in commits:
                        commit_date_str = commit["commit"]["author"]["date"]
                        commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
                        commit_date_kst = commit_date.astimezone(pytz.timezone("Asia/Seoul"))
                        
                        # 커밋 작성자가 해당 사용자인지 확인
                        commit_author = commit.get("author", {})
                        if commit_author and commit_author.get("login") == username:
                            # 이번 주 범위 내 커밋인지 확인
                            if week_start <= commit_date_kst <= week_end:
                                if problem_dir not in processed_problems:
                                    processed_problems.add(problem_dir)
                                    solved_problems.append(problem_dir)
                                    problem_count += 1
                                    print(f"  ✅ 문제 {problem_dir}: {commit_date_kst.strftime('%Y-%m-%d %H:%M')} KST")
                                break  # 해당 문제의 첫 번째 유효 커밋만 카운트
                                
        solved_problems.sort(key=int)  # 문제 번호 순으로 정렬
        print(f"📊 {username}: 이번 주 해결한 문제 {problem_count}개 - {solved_problems}")
        return problem_count

    except Exception as e:
        print(f"GitHub API 기반 주간 문제 수 계산 실패 ({username}): {e}")
        import traceback
        traceback.print_exc()
        return 0


def get_weekly_problem_count_alternative(username):
    """Git 로그를 사용하여 이번 주에 커밋된 문제 수 계산"""
    try:
        # 이번 주 범위 계산 (월요일 00:00 ~ 일요일 23:59)
        week_start, week_end = get_current_week_range()
        
        print(f"📅 {username} Git 로그 검색 범위: {week_start.strftime('%Y-%m-%d %H:%M')} ~ {week_end.strftime('%Y-%m-%d %H:%M')} KST")
        
        # Git 로그 명령어로 이번 주 커밋 조회
        git_command = [
            "git", "log",
            "--since", week_start.strftime("%Y-%m-%d %H:%M:%S"),
            "--until", week_end.strftime("%Y-%m-%d %H:%M:%S"),
            "--author", username,
            "--name-only",
            "--pretty=format:%H|%ad|%an",
            "--date=iso",
            f"-- {username}/*/Main.java"
        ]
        
        result = subprocess.run(git_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Git 명령어 실행 실패: {result.stderr}")
            return 0
        
        # 커밋 로그 파싱
        lines = result.stdout.strip().split('\n')
        processed_problems = set()
        solved_problems = []
        
        current_commit = None
        for line in lines:
            if '|' in line:  # 커밋 정보 라인
                parts = line.split('|')
                if len(parts) >= 3:
                    commit_hash = parts[0]
                    commit_date_str = parts[1]
                    author_name = parts[2]
                    current_commit = commit_hash
                    
                    # 커밋 시간이 이번 주 범위 내인지 다시 한번 확인
                    try:
                        commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
                        commit_date_kst = commit_date.astimezone(pytz.timezone("Asia/Seoul"))
                        if not (week_start <= commit_date_kst <= week_end):
                            current_commit = None
                            continue
                        print(f"  📅 유효한 커밋: {commit_date_kst.strftime('%Y-%m-%d %H:%M')} KST")
                    except:
                        current_commit = None
                        continue
                        
            elif line.strip() and current_commit:  # 파일 경로 라인
                # username/문제번호/Main.java 패턴 확인
                if line.startswith(f"{username}/") and line.endswith("/Main.java"):
                    path_parts = line.split('/')
                    if len(path_parts) >= 3:
                        problem_dir = path_parts[1]
                        if problem_dir.isdigit() and problem_dir not in processed_problems:
                            processed_problems.add(problem_dir)
                            solved_problems.append(problem_dir)
        
        solved_problems.sort(key=int)  # 문제 번호 순으로 정렬
        problem_count = len(processed_problems)
        print(f"📊 {username}: 이번 주 해결한 문제 {problem_count}개 - {solved_problems}")
        return problem_count
        
    except Exception as e:
        print(f"Git 로그 기반 주간 문제 수 계산 실패 ({username}): {e}")
        return 0


def get_weekly_problem_count(username):
    """사용자의 이번 주 해결한 문제 수 계산 (커밋 시간 기준)"""
    print(f"\n🔍 {username}의 이번 주 문제 수 계산 중...")
    
    # 먼저 GitHub API 방식 시도
    count_api = get_weekly_problem_count_by_commit_time(username)
    
    # GitHub API가 실패하거나 0개면 Git 로그 방식 시도
    if count_api == 0:
        print(f"🔄 {username}: GitHub API 방식에서 0개 또는 실패, Git 로그 방식으로 재시도")
        count_git = get_weekly_problem_count_alternative(username)
        return count_git
    
    return count_api


def send_personal_notification(username, message):
    """사용자별 개인 webhook으로 알림 전송"""
    # 개인 webhook URL 패턴: {USERNAME}_MATTERMOST_URL (대문자)
    personal_webhook_key = f"{username.upper()}_MATTERMOST_URL"
    personal_webhook_url = os.getenv(personal_webhook_key)

    if not personal_webhook_url:
        print(f"❌ {username}의 개인 webhook이 설정되지 않음 ({personal_webhook_key})")
        return False

    payload = {
        "text": message,
        "username": "Algorithm Study Bot",
        "icon_emoji": ":robot_face:",
    }

    try:
        response = requests.post(personal_webhook_url, json=payload)
        if response.status_code == 200:
            print(f"✅ {username}에게 개인 알림 전송 성공")
            return True
        else:
            print(f"❌ {username}에게 개인 알림 전송 실패: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ {username}에게 개인 알림 전송 예외: {e}")
        return False


def create_personal_reminder_message(username, problem_count, reminder_type, repo_info):
    """개인별 알림 메시지 생성"""
    kst = pytz.timezone("Asia/Seoul")
    now = datetime.now(kst)
    week_start, week_end = get_current_week_range()

    repo_name = (
        repo_info.get("name", "Algorithm Study") if repo_info else "Algorithm Study"
    )
    repo_url = repo_info.get("html_url", "") if repo_info else ""

    # 알림 타입별 메시지 구성
    if reminder_type == "friday_morning":
        urgency = "📅 **주간 중간 체크**"
        time_context = "금요일 오전"
        deadline_msg = "이번 주 일요일 23:59까지"
    elif reminder_type == "sunday_morning":
        urgency = "⏰ **마감일 당일**"
        time_context = "일요일 오전"
        deadline_msg = "오늘 23:59까지"
    elif reminder_type == "sunday_evening":
        urgency = "🚨 **마감 임박**"
        time_context = "일요일 저녁"
        deadline_msg = "오늘 23:59까지 (약 3시간 남음)"
    else:
        urgency = "📢 **알림**"
        time_context = "정기"
        deadline_msg = "이번 주 일요일 23:59까지"

    message = f"""
{urgency} @{username}님께 개인 알림

👋 안녕하세요, {username}님!
🕐 **알림 시간**: {time_context} ({now.strftime('%H:%M')})
🏠 **스터디**: [{repo_name}]({repo_url})

📊 **이번 주 현황** ({week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')}):
- **해결한 문제**: {problem_count}개
- **목표**: 5개 이상  
- **부족한 문제**: {max(0, 5 - problem_count)}개

"""

    if problem_count >= 5:
        message += """
🎉 **축하합니다!** 이번 주 목표를 달성하셨네요! 👏
계속해서 꾸준히 참여해주세요! 🚀
"""
    else:
        remaining = 5 - problem_count
        if reminder_type == "friday_morning":
            message += f"""
💪 **화이팅!** 아직 주말이 남았습니다!
📝 **남은 문제**: {remaining}개
⏰ **마감**: {deadline_msg}

주말을 활용해서 목표를 달성해보세요! 🎯
"""
        elif reminder_type == "sunday_morning":
            message += f"""
⏰ **마감일입니다!** 하루가 남았어요!
📝 **남은 문제**: {remaining}개  
⏰ **마감**: {deadline_msg}

하루 안에 충분히 가능합니다! 화이팅! 💪
"""
        elif reminder_type == "sunday_evening":
            message += f"""
🚨 **마감 임박!** 시간이 얼마 남지 않았습니다!
📝 **남은 문제**: {remaining}개
⏰ **마감**: {deadline_msg}

지금이라도 시작하면 됩니다! 마지막 스퍼트! 🏃‍♂️
"""
        else:
            message += f"""
📝 **남은 문제**: {remaining}개
⏰ **마감**: {deadline_msg}

꾸준히 참여해주세요! 💪
"""

    message += f"""
---
📋 **제출 방법**:
1. `{username}/문제번호/Main.java` 형태로 파일 생성
2. Pull Request로 제출
3. 자동 테스트 후 병합

💡 **참고**:
- 이번 주 (월요일 00:00 ~ 일요일 23:59) 커밋만 카운트됩니다
- 한 번에 여러 문제를 PR로 제출해도 됩니다
- 부분 점수도 인정되니 도전해보세요!
- 궁금한 점은 언제든 문의해주세요

*이 메시지는 자동으로 전송되었습니다. ({time_context} 알림)*
*문제 수는 이번 주 ({week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')}) 커밋 시간을 기준으로 계산됩니다.*
"""

    return message


def send_summary_notification(participants_status, reminder_type, repo_info):
    """전체 요약 알림을 모든 참가자에게 개인 DM으로 전송"""
    # 모든 참가자에게 개인 DM으로 요약 전송
    success_count = 0
    total_participants = len(participants_status)

    for participant in participants_status:
        username = participant["username"]
        webhook_key = f"{username.upper()}_MATTERMOST_URL"
        webhook_url = os.getenv(webhook_key)

        if not webhook_url:
            print(f"⚠️ {username}의 개인 webhook이 설정되지 않음 ({webhook_key})")
            continue

        kst = pytz.timezone("Asia/Seoul")
        now = datetime.now(kst)
        week_start, week_end = get_current_week_range()

        repo_name = (
            repo_info.get("name", "Algorithm Study") if repo_info else "Algorithm Study"
        )

        # 통계 계산
        total_participants = len(participants_status)
        achieved_goal = len([p for p in participants_status if p["problem_count"] >= 5])
        need_reminder = len([p for p in participants_status if p["problem_count"] < 5])

        # 알림 타입별 제목
        if reminder_type == "friday_morning":
            title = "📅 **주간 중간 체크 요약** (금요일 오전)"
        elif reminder_type == "sunday_morning":
            title = "⏰ **마감일 당일 요약** (일요일 오전)"
        elif reminder_type == "sunday_evening":
            title = "🚨 **마감 임박 요약** (일요일 저녁)"
        else:
            title = "📊 **스터디 현황 요약**"

        message = f"""
{title}

🏠 **스터디**: {repo_name}
🕐 **체크 시간**: {now.strftime('%Y-%m-%d %H:%M')} KST
📅 **이번 주**: {week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')}

📊 **전체 현황** (이번 주 커밋 기준):
- **전체 참가자**: {total_participants}명
- **목표 달성**: {achieved_goal}명 (5개 이상)
- **알림 대상**: {need_reminder}명 (5개 미만)

"""

        if participants_status:
            message += "👥 **참가자별 현황**:\n"
            for participant in participants_status:
                status_emoji = "✅" if participant["problem_count"] >= 5 else "⚠️"
                message += f"- {status_emoji} **{participant['username']}**: {participant['problem_count']}문제\n"

            message += "\n"

        if need_reminder > 0:
            need_reminder_users = [
                p["username"] for p in participants_status if p["problem_count"] < 5
            ]
            message += f"🔔 **개인 알림 발송 대상**: {', '.join(need_reminder_users)}\n\n"

        message += f"""
---
💡 **참고사항**:
- 마감: 매주 일요일 23:59 KST
- 목표: 주당 5문제 이상 해결
- 계산 기준: 이번 주 ({week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')}) 커밋 시간

*이 메시지는 자동으로 전송되었습니다.*
"""

        payload = {
            "text": message,
            "username": "Algorithm Study Bot",
            "icon_emoji": ":chart_with_upwards_trend:",
        }

        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                success_count += 1
                print(f"✅ {username}에게 요약 알림 전송 성공")
            else:
                print(f"❌ {username}에게 요약 알림 전송 실패: {response.status_code}")

        except Exception as e:
            print(f"❌ {username}에게 요약 알림 전송 예외: {e}")

    print(f"✅ 전체 요약 알림 전송 완료: {success_count}/{total_participants}명")
    return success_count > 0


def main():
    """메인 실행 함수"""
    is_debug_mode = os.getenv("DEBUG_MODE") == "true"
    kst = pytz.timezone("Asia/Seoul")
    now = datetime.now(kst)
    week_start, week_end = get_current_week_range()
    
    print(f"🤖 주간 문제 해결 현황 체크 및 개인 알림 시작... {'(디버깅 모드)' if is_debug_mode else ''}")
    print(f"📅 이번 주 범위: {week_start.strftime('%Y-%m-%d %H:%M')} ~ {week_end.strftime('%Y-%m-%d %H:%M')} KST")
    print(f"🕐 현재 시간: {now.strftime('%Y-%m-%d %H:%M')} KST")

    # 1. 레포지토리 정보 가져오기
    repo_info = get_repository_info()
    if not repo_info:
        print("❌ 레포지토리 정보를 가져올 수 없습니다.")
        return

    print(f"📁 레포지토리: {repo_info.get('name', 'Unknown')}")

    # 2. 현재 알림 타입 결정
    reminder_type = get_current_reminder_type()
    print(f"⏰ 알림 타입: {reminder_type}")

    # 3. 참가자 목록 가져오기 (디렉토리 기반)
    participants = get_participants_from_directory()
    if not participants:
        print("❌ 참가자 목록을 찾을 수 없습니다.")
        return

    print(f"👥 참가자 수: {len(participants)}명")
    print(f"👥 참가자: {', '.join(participants)}")

    # 4. 각 참가자별 이번 주 문제 해결 수 체크
    participants_status = []
    for username in participants:
        problem_count = get_weekly_problem_count(username)
        participants_status.append(
            {"username": username, "problem_count": problem_count}
        )

    # 결과 요약 출력
    print(f"\n📊 이번 주 ({week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')}) 결과 요약:")
    for participant in participants_status:
        username = participant["username"]
        count = participant["problem_count"]
        status = "✅" if count >= 5 else "⚠️"
        print(f"  {status} {username}: {count}문제")

    # 5. 5개 미만인 사용자들에게 개인 알림 발송
    need_reminder_users = [p for p in participants_status if p["problem_count"] < 5]
    print(f"\n🔔 개인 알림 필요: {len(need_reminder_users)}명")

    if is_debug_mode and reminder_type == "debug_all":
        # 디버깅 모드: 세 가지 메시지 타입을 모두 테스트
        message_types = [
            ("friday_morning", "금요일 오전"),
            ("sunday_morning", "일요일 오전"),
            ("sunday_evening", "일요일 저녁"),
        ]

        total_success = 0
        total_sent = 0

        for msg_type, description in message_types:
            print(f"\n🧪 [{description}] 메시지 타입 테스트 중...")

            for participant in need_reminder_users:
                username = participant["username"]
                problem_count = participant["problem_count"]

                # 디버깅용 메시지에 타입 표시 추가
                message = create_personal_reminder_message(
                    username, problem_count, msg_type, repo_info
                )
                debug_message = f"🧪 **[{description} 메시지 테스트]**\n\n{message}\n\n---\n*이것은 디버깅 모드 테스트 메시지입니다.*"

                if send_personal_notification(username, debug_message):
                    total_success += 1
                total_sent += 1

                # 메시지 간 간격 (API 제한 방지)
                import time
                time.sleep(2)

        print(f"✅ 디버깅 모드 알림 성공: {total_success}/{total_sent}건")

        # 디버깅 모드 전체 요약
        debug_summary_message = f"""
🧪 **디버깅 모드 실행 완료**

🕐 **실행 시간**: {now.strftime('%Y-%m-%d %H:%M:%S')} KST
📅 **이번 주**: {week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')}
📊 **테스트 결과**: {len(message_types)}가지 메시지 타입 × {len(need_reminder_users)}명 = {total_sent}건 발송

📝 **테스트된 메시지 타입**:
- 금요일 오전: 주간 중간 체크
- 일요일 오전: 마감일 당일 알림  
- 일요일 저녁: 마감 임박 긴급 알림

🎯 **알림 대상**: {', '.join([p['username'] for p in need_reminder_users])} ({len(need_reminder_users)}명)
📅 **계산 기준**: 이번 주 커밋 시간 ({week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')})

---
*디버깅 모드에서 모든 메시지 타입을 테스트했습니다.*
"""

        # 디버깅 모드에서는 첫 번째 참가자에게만 요약 전송
        if participants_status:
            first_participant = participants_status[0]
            username = first_participant["username"]
            webhook_key = f"{username.upper()}_MATTERMOST_URL"
            webhook_url = os.getenv(webhook_key)

            if webhook_url:
                payload = {
                    "text": debug_summary_message,
                    "username": "Algorithm Study Debug Bot",
                    "icon_emoji": ":bug:",
                }
                requests.post(webhook_url, json=payload)
                print(f"✅ 디버깅 모드 요약 알림 전송 완료 ({username})")
            else:
                print(f"⚠️ 디버깅 모드 요약 전송 실패: {webhook_key} 설정되지 않음")

    else:
        # 일반 모드: 기존 로직
        success_count = 0
        for participant in need_reminder_users:
            username = participant["username"]
            problem_count = participant["problem_count"]

            message = create_personal_reminder_message(
                username, problem_count, reminder_type, repo_info
            )

            if send_personal_notification(username, message):
                success_count += 1

        print(f"✅ 개인 알림 성공: {success_count}/{len(need_reminder_users)}건")

        # 6. 전체 요약을 기본 채널로 전송
        if send_summary_notification(participants_status, reminder_type, repo_info):
            print("✅ 전체 요약 알림 전송 완료")

    print("🎯 주간 문제 체크 및 알림 완료!")


if __name__ == "__main__":
    main()