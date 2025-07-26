#!/usr/bin/env python3
"""
scripts/test_personal_notifications.py
개인별 알림 시스템 테스트 스크립트
"""

import os
import sys
from datetime import datetime
import pytz

# deadline_checker 모듈 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from deadline_checker import (
    get_repository_info,
    get_participants_from_directory,
    get_weekly_problem_count,
    send_personal_notification,
    create_personal_reminder_message,
    send_summary_notification
)

def test_environment_setup():
    """환경 설정 테스트"""
    print("🔧 환경 설정 테스트...")
    
    required_vars = ['GITHUB_TOKEN', 'GITHUB_REPOSITORY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 필수 환경변수 누락: {', '.join(missing_vars)}")
        return False
    
    print("✅ 기본 환경변수 설정 완료")
    return True

def test_participant_detection():
    """참가자 감지 테스트"""
    print("👥 참가자 감지 테스트...")
    
    participants = get_participants_from_directory()
    
    if not participants:
        print("❌ 참가자를 찾을 수 없습니다.")
        print("💡 확인사항: 현재 디렉토리에 사용자 디렉토리가 있는지 확인하세요.")
        return []
    
    print(f"✅ {len(participants)}명 참가자 발견: {', '.join(participants)}")
    return participants

def test_webhook_configuration(participants):
    """Webhook 설정 테스트"""
    print("🔗 Webhook 설정 테스트...")
    
    webhook_status = {}
    
    # 기본 채널 webhook 확인
    default_webhook = os.getenv('MATTERMOST_WEBHOOK_URL')
    if default_webhook:
        print("✅ 기본 채널 webhook 설정됨")
        webhook_status['default'] = True
    else:
        print("⚠️ 기본 채널 webhook 미설정")
        webhook_status['default'] = False
    
    # 개인별 webhook 확인
    for participant in participants:
        personal_webhook_key = f"{participant}_MATTERMOST_URL"
        personal_webhook = os.getenv(personal_webhook_key)
        
        if personal_webhook:
            print(f"✅ {participant}: 개인 webhook 설정됨")
            webhook_status[participant] = True
        else:
            print(f"⚠️ {participant}: 개인 webhook 미설정 ({personal_webhook_key})")
            webhook_status[participant] = False
    
    return webhook_status

def test_problem_counting(participants):
    """문제 카운팅 테스트"""
    print("📊 문제 카운팅 테스트...")
    
    problem_counts = {}
    
    for participant in participants:
        try:
            count = get_weekly_problem_count(participant)
            problem_counts[participant] = count
            print(f"📈 {participant}: {count}문제")
        except Exception as e:
            print(f"❌ {participant}: 카운팅 실패 - {e}")
            problem_counts[participant] = 0
    
    return problem_counts

def test_message_generation(participants, problem_counts):
    """메시지 생성 테스트"""
    print("💬 메시지 생성 테스트...")
    
    # 레포지토리 정보 가져오기
    repo_info = get_repository_info()
    
    # 다양한 시나리오 테스트
    test_scenarios = [
        ("friday_morning", "금요일 오전"),
        ("sunday_morning", "일요일 오전"),
        ("sunday_evening", "일요일 저녁"),
        ("general", "일반")
    ]
    
    messages = {}
    
    for participant in participants:
        problem_count = problem_counts.get(participant, 0)
        participant_messages = {}
        
        for reminder_type, description in test_scenarios:
            message = create_personal_reminder_message(
                participant, problem_count, reminder_type, repo_info
            )
            participant_messages[reminder_type] = message
            print(f"✅ {participant} - {description} 메시지 생성 완료")
        
        messages[participant] = participant_messages
    
    return messages

def test_dry_run_notification(participants, problem_counts, webhook_status):
    """알림 발송 시뮬레이션 (실제 발송 X)"""
    print("🧪 알림 발송 시뮬레이션...")
    
    repo_info = get_repository_info()
    reminder_type = "general"  # 테스트용
    
    # 5개 미만인 사용자들
    need_reminder_users = [
        {"username": p, "problem_count": problem_counts.get(p, 0)}
        for p in participants if problem_counts.get(p, 0) < 5
    ]
    
    print(f"🔔 알림 대상: {len(need_reminder_users)}명")
    
    for participant_info in need_reminder_users:
        username = participant_info["username"]
        problem_count = participant_info["problem_count"]
        
        # 메시지 생성
        message = create_personal_reminder_message(
            username, problem_count, reminder_type, repo_info
        )
        
        # Webhook 상태 확인
        has_personal_webhook = webhook_status.get(username, False)
        has_default_webhook = webhook_status.get('default', False)
        
        if has_personal_webhook or has_default_webhook:
            webhook_type = "개인 DM" if has_personal_webhook else "기본 채널"
            print(f"✅ {username}: {webhook_type}로 발송 가능")
        else:
            print(f"❌ {username}: 발송 불가 (webhook 없음)")
    
    return need_reminder_users

def test_actual_notification(participants, webhook_status):
    """실제 테스트 알림 발송"""
    print("📤 실제 테스트 알림 발송...")
    
    # 사용자 확인
    print("⚠️ 실제 Mattermost 알림이 발송됩니다!")
    print("계속하시겠습니까? (y/N): ", end="")
    
    if input().lower() != 'y':
        print("테스트 알림 발송을 취소했습니다.")
        return
    
    repo_info = get_repository_info()
    
    success_count = 0
    total_count = 0
    
    for participant in participants:
        if not webhook_status.get(participant, False) and not webhook_status.get('default', False):
            print(f"⏭ {participant}: Webhook 없어서 스킵")
            continue
        
        # 테스트 메시지 생성
        test_message = f"""
🧪 **개인 알림 시스템 테스트**

👋 안녕하세요, {participant}님!
🕐 **테스트 시간**: {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')} KST

✅ **테스트 결과**: 개인 알림 시스템이 정상 작동합니다!

---
💡 **참고사항**:
- 이 메시지는 시스템 테스트용입니다
- 실제 알림은 금요일 9시, 일요일 9시/21시에 발송됩니다
- 주간 5문제 이상 해결 시 목표 달성 메시지가 발송됩니다

*테스트 메시지입니다. 정상 수신되었다면 설정이 완료되었습니다! 🎉*
"""
        
        # 실제 발송
        if send_personal_notification(participant, test_message):
            success_count += 1
        total_count += 1
    
    print(f"📊 테스트 알림 결과: {success_count}/{total_count}건 성공")

def main():
    """메인 테스트 함수"""
    print("🚀 개인별 알림 시스템 테스트 시작")
    print("=" * 50)
    
    # 디버깅 모드 옵션 제공
    print("🔧 테스트 모드를 선택하세요:")
    print("1. 일반 테스트")
    print("2. 디버깅 모드 테스트 (세 가지 메시지 타입 모두)")
    choice = input("선택 (1 또는 2): ").strip()
    
    if choice == "2":
        os.environ['DEBUG_MODE'] = 'true'
        print("🧪 디버깅 모드가 활성화되었습니다!")
    else:
        os.environ.pop('DEBUG_MODE', None)
        print("📋 일반 테스트 모드입니다.")
    
    # 1. 환경 설정 테스트
    if not test_environment_setup():
        print("❌ 환경 설정 실패")
        return
    print()
    
    # 2. 참가자 감지 테스트
    participants = test_participant_detection()
    if not participants:
        print("❌ 참가자 감지 실패")
        return
    print()
    
    # 3. Webhook 설정 테스트
    webhook_status = test_webhook_configuration(participants)
    print()
    
    # 4. 문제 카운팅 테스트
    problem_counts = test_problem_counting(participants)
    print()
    
    # 5. 메시지 생성 테스트
    messages = test_message_generation(participants, problem_counts)
    print()
    
    # 6. 발송 시뮬레이션
    need_reminder_users = test_dry_run_notification(participants, problem_counts, webhook_status)
    print()
    
    # 7. 실제 테스트 알림 발송 (선택사항)
    print("🎯 전체 테스트 완료!")
    print()
    print("📤 실제 테스트 알림을 발송하시겠습니까?")
    test_actual_notification(participants, webhook_status)
    
    print()
    print("✅ 모든 테스트 완료!")
    print("💡 문제가 있다면 개인알림_설정가이드.md를 참고하세요.")

if __name__ == "__main__":
    main() 