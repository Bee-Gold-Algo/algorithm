#!/usr/bin/env python3
"""
scripts/deadline_checker.py
마감일을 체크하고 개인별 Mattermost로 알림을 보냅니다.
"""

import os
import json
import requests
import subprocess
from datetime import datetime, timedelta
import pytz
import re

def get_repository_info():
    """GitHub 레포지토리 정보 가져오기"""
    try:
        # GitHub API를 통해 레포지토리 정보 가져오기
        token = os.getenv('GITHUB_TOKEN')
        repo = os.getenv('GITHUB_REPOSITORY')  # 예: 'username/repo-name'
        
        if not token or not repo:
            print("GitHub 환경변수가 설정되지 않았습니다.")
            return None
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
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
    if os.getenv('DEBUG_MODE') == 'true':
        return "debug_all"
    
    kst = pytz.timezone('Asia/Seoul')
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
        for item in os.listdir('.'):
            if os.path.isdir(item) and item not in ['.git', '.github', 'scripts', '__pycache__']:
                participants.append(item)
        
        print(f"📁 발견된 참가자 디렉토리: {participants}")
        return participants
        
    except Exception as e:
        print(f"디렉토리에서 참가자 추출 실패: {e}")
        return []

def get_weekly_problem_count(username):
    """특정 사용자의 일주일간 해결한 문제 수 계산"""
    try:
        token = os.getenv('GITHUB_TOKEN')
        repo = os.getenv('GITHUB_REPOSITORY')
        
        if not token or not repo:
            return 0
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 일주일 전 날짜
        week_ago = datetime.now() - timedelta(days=7)
        since_date = week_ago.isoformat()
        
        # 최근 병합된 PR 조회 (해당 사용자만)
        pr_url = f"https://api.github.com/repos/{repo}/pulls?state=closed&since={since_date}&per_page=100"
        response = requests.get(pr_url, headers=headers)
        
        problem_count = 0
        if response.status_code == 200:
            prs = response.json()
            
            for pr in prs:
                # 해당 사용자가 작성하고 병합된 PR만 확인
                if pr.get('merged_at') and pr['user']['login'] == username:
                    # PR의 파일 변경사항 조회
                    files_url = pr['url'] + '/files'
                    files_response = requests.get(files_url, headers=headers)
                    
                    if files_response.status_code == 200:
                        files = files_response.json()
                        
                        # 해당 사용자 디렉토리의 문제 파일들 카운트
                        for file in files:
                            file_path = file['filename']
                            # username/문제번호/Main.java 패턴 확인
                            if file_path.startswith(f"{username}/") and file_path.endswith('/Main.java'):
                                if file['status'] in ['added', 'modified']:
                                    problem_count += 1
        
        return problem_count
        
    except Exception as e:
        print(f"주간 문제 수 계산 실패 ({username}): {e}")
        return 0

def send_personal_notification(username, message):
    """사용자별 개인 webhook으로 알림 전송"""
    # 개인 webhook URL 패턴: {USERNAME}_MATTERMOST_URL
    personal_webhook_key = f"{username}_MATTERMOST_URL"
    personal_webhook_url = os.getenv(personal_webhook_key)
    
    # 개인 webhook이 없으면 기본 채널 사용
    if not personal_webhook_url:
        print(f"⚠️ {username}의 개인 webhook이 설정되지 않음, 기본 채널 사용")
        personal_webhook_url = os.getenv('MATTERMOST_WEBHOOK_URL')
    
    if not personal_webhook_url:
        print(f"❌ {username}에게 보낼 webhook URL이 없습니다.")
        return False
    
    payload = {
        "text": message,
        "username": "Algorithm Study Bot",
        "icon_emoji": ":robot_face:"
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
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    
    repo_name = repo_info.get('name', 'Algorithm Study') if repo_info else 'Algorithm Study'
    repo_url = repo_info.get('html_url', '') if repo_info else ''
    
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

📊 **이번 주 현황**:
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
- 한 번에 여러 문제를 PR로 제출해도 됩니다
- 부분 점수도 인정되니 도전해보세요!
- 궁금한 점은 언제든 문의해주세요

*이 메시지는 자동으로 전송되었습니다. ({time_context} 알림)*
"""
    
    return message

def send_summary_notification(participants_status, reminder_type, repo_info):
    """전체 요약 알림을 기본 채널로 전송"""
    webhook_url = os.getenv('MATTERMOST_WEBHOOK_URL')
    
    if not webhook_url:
        print("기본 채널 webhook URL이 설정되지 않았습니다.")
        return False
    
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    
    repo_name = repo_info.get('name', 'Algorithm Study') if repo_info else 'Algorithm Study'
    
    # 통계 계산
    total_participants = len(participants_status)
    achieved_goal = len([p for p in participants_status if p['problem_count'] >= 5])
    need_reminder = len([p for p in participants_status if p['problem_count'] < 5])
    
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

📊 **전체 현황**:
- **전체 참가자**: {total_participants}명
- **목표 달성**: {achieved_goal}명 (5개 이상)
- **알림 대상**: {need_reminder}명 (5개 미만)

"""
    
    if participants_status:
        message += "👥 **참가자별 현황**:\n"
        for participant in participants_status:
            status_emoji = "✅" if participant['problem_count'] >= 5 else "⚠️"
            message += f"- {status_emoji} **{participant['username']}**: {participant['problem_count']}문제\n"
        
        message += "\n"
    
    if need_reminder > 0:
        need_reminder_users = [p['username'] for p in participants_status if p['problem_count'] < 5]
        message += f"🔔 **개인 알림 발송 대상**: {', '.join(need_reminder_users)}\n\n"
    
    message += """
---
💡 **참고사항**:
- 개인별 상세 알림은 각자 DM으로 발송되었습니다
- 마감: 매주 일요일 23:59 KST
- 목표: 주당 5문제 이상 해결

*이 메시지는 자동으로 전송되었습니다.*
"""
    
    payload = {
        "text": message,
        "username": "Algorithm Study Bot",
        "icon_emoji": ":chart_with_upwards_trend:"
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ 전체 요약 알림 전송 성공")
            return True
        else:
            print(f"❌ 전체 요약 알림 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 전체 요약 알림 전송 예외: {e}")
        return False

def main():
    """메인 실행 함수"""
    is_debug_mode = os.getenv('DEBUG_MODE') == 'true'
    print(f"🤖 주간 문제 해결 현황 체크 및 개인 알림 시작... {'(디버깅 모드)' if is_debug_mode else ''}")
    
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
    
    # 4. 각 참가자별 주간 문제 해결 수 체크
    participants_status = []
    for username in participants:
        problem_count = get_weekly_problem_count(username)
        participants_status.append({
            'username': username,
            'problem_count': problem_count
        })
        print(f"📊 {username}: {problem_count}문제")
    
    # 5. 5개 미만인 사용자들에게 개인 알림 발송
    need_reminder_users = [p for p in participants_status if p['problem_count'] < 5]
    print(f"🔔 개인 알림 필요: {len(need_reminder_users)}명")
    
    if is_debug_mode and reminder_type == "debug_all":
        # 디버깅 모드: 세 가지 메시지 타입을 모두 테스트
        message_types = [
            ("friday_morning", "금요일 오전"),
            ("sunday_morning", "일요일 오전"), 
            ("sunday_evening", "일요일 저녁")
        ]
        
        total_success = 0
        total_sent = 0
        
        for msg_type, description in message_types:
            print(f"\n🧪 [{description}] 메시지 타입 테스트 중...")
            
            for participant in need_reminder_users:
                username = participant['username']
                problem_count = participant['problem_count']
                
                # 디버깅용 메시지에 타입 표시 추가
                message = create_personal_reminder_message(username, problem_count, msg_type, repo_info)
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

🕐 **실행 시간**: {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')} KST
📊 **테스트 결과**: {len(message_types)}가지 메시지 타입 × {len(need_reminder_users)}명 = {total_sent}건 발송

📝 **테스트된 메시지 타입**:
- 금요일 오전: 주간 중간 체크
- 일요일 오전: 마감일 당일 알림  
- 일요일 저녁: 마감 임박 긴급 알림

🎯 **알림 대상**: {', '.join([p['username'] for p in need_reminder_users])} ({len(need_reminder_users)}명)

---
*디버깅 모드에서 모든 메시지 타입을 테스트했습니다.*
"""
        
        # 전체 요약을 기본 채널로 전송
        webhook_url = os.getenv('MATTERMOST_WEBHOOK_URL')
        if webhook_url:
            payload = {
                "text": debug_summary_message,
                "username": "Algorithm Study Debug Bot",
                "icon_emoji": ":bug:"
            }
            requests.post(webhook_url, json=payload)
            print("✅ 디버깅 모드 전체 요약 알림 전송 완료")
    
    else:
        # 일반 모드: 기존 로직
        success_count = 0
        for participant in need_reminder_users:
            username = participant['username']
            problem_count = participant['problem_count']
            
            message = create_personal_reminder_message(username, problem_count, reminder_type, repo_info)
            
            if send_personal_notification(username, message):
                success_count += 1
        
        print(f"✅ 개인 알림 성공: {success_count}/{len(need_reminder_users)}건")
        
        # 6. 전체 요약을 기본 채널로 전송
        if send_summary_notification(participants_status, reminder_type, repo_info):
            print("✅ 전체 요약 알림 전송 완료")
    
    print("🎯 주간 문제 체크 및 알림 완료!")

if __name__ == "__main__":
    main()