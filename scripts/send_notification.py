#!/usr/bin/env python3
"""
scripts/send_notification.py
GitHub Actions에서 사용할 알림 전송 스크립트
"""

import os
import sys
import requests
import argparse
from datetime import datetime


def get_session_info():
    """회차 정보 가져오기"""
    try:
        from session_counter import get_session_info, get_session_statistics

        return get_session_info(), get_session_statistics()
    except ImportError:
        # 환경변수에서 정보 가져오기
        return {
            "session_number": os.environ.get("SESSION_NUMBER", "1"),
            "monday": os.environ.get("WEEK_START", "Unknown"),
            "sunday": os.environ.get("WEEK_END", "Unknown"),
            "deadline": os.environ.get("DEADLINE", "Unknown"),
        }, {
            "total_weeks_completed": int(os.environ.get("TOTAL_WEEKS", "0")),
            "total_study_days": int(os.environ.get("TOTAL_DAYS", "0")),
        }


def send_mattermost_notification(webhook_url, message, user_name="Unknown"):
    """Mattermost로 알림 전송"""
    try:
        response = requests.post(webhook_url, json={"text": message}, timeout=10)
        if response.status_code == 200:
            print(f"✅ {user_name} 알림 전송 성공")
            return True
        else:
            print(f"❌ {user_name} 알림 전송 실패: HTTP {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"⏰ {user_name} 알림 전송 타임아웃")
        return False
    except Exception as e:
        print(f"❌ {user_name} 알림 전송 오류: {e}")
        return False


def create_message(session_info, stats, force_reset=False, debug_mode=False):
    """알림 메시지 생성"""

    # 헤더 결정
    if debug_mode:
        header = "🐛 **DEBUG: README 자동 업데이트 테스트**"
        emoji = "🧪"
    elif force_reset:
        header = "🔧 **README 강제 초기화 완료!**"
        emoji = "🔧"
    else:
        header = f"🚀 **새로운 {session_info['session_number']}회차가 시작되었습니다!**"
        emoji = "🚀"

    # 트리거 정보
    trigger = os.environ.get("GITHUB_EVENT_NAME", "unknown")
    actor = os.environ.get("GITHUB_ACTOR", "Unknown")

    if force_reset:
        trigger_info = f"👤 실행자: {actor}"
    else:
        trigger_info = "🤖 자동 트리거"

    # 특별 메시지 (디버그 모드)
    special_msg = ""
    if debug_mode:
        special_msg = "\n⚠️ **이것은 5분마다 실행되는 디버그 테스트입니다.**"

    # Repository 정보
    repo = os.environ.get("GITHUB_REPOSITORY", "Unknown/Unknown")

    message = f"""{header}

📅 **기간**: {session_info['monday']} ~ {session_info['sunday']}
⏰ **마감**: {session_info['deadline']}
📊 **진행**: {stats['total_weeks_completed']}주 완료 → {session_info['session_number']}회차 시작
📈 **총 일수**: {stats['total_study_days']}일
{trigger_info}
🕐 **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}{special_msg}

{emoji} 이번 주도 열심히 문제를 풀어보세요!
🔗 **Repository**: https://github.com/{repo}
📝 **README**: https://github.com/{repo}#readme"""

    return message


def main():
    parser = argparse.ArgumentParser(description="Mattermost 알림 전송")
    parser.add_argument("--force-reset", action="store_true", help="강제 리셋 메시지")
    parser.add_argument("--debug-mode", action="store_true", help="디버그 모드 메시지")
    parser.add_argument(
        "--dry-run", action="store_true", help="실제 전송하지 않고 메시지만 출력"
    )

    args = parser.parse_args()

    try:
        # 회차 정보 가져오기
        session_info, stats = get_session_info()

        # 메시지 생성
        message = create_message(
            session_info,
            stats,
            force_reset=args.force_reset,
            debug_mode=args.debug_mode,
        )

        if args.dry_run:
            print("📝 생성된 메시지:")
            print("=" * 50)
            print(message)
            print("=" * 50)
            return

        # Webhook URL 수집
        webhook_configs = []

        # 환경변수에서 webhook URL들 찾기
        for key, value in os.environ.items():
            if key.endswith("_MATTERMOST_URL") and value:
                # YEOMIN4242_MATTERMOST_URL -> yeomin4242
                user_name = key.replace("_MATTERMOST_URL", "").lower()
                webhook_configs.append((user_name, value))

        if not webhook_configs:
            print("⚠️ 설정된 Mattermost webhook URL이 없습니다.")
            print("   GitHub Secrets에서 다음과 같은 형식으로 설정하세요:")
            print("   - YEOMIN4242_MATTERMOST_URL")
            print("   - USERNAME_MATTERMOST_URL")
            return

        # 알림 전송 실행
        success_count = 0
        total_count = len(webhook_configs)

        print(f"📢 {total_count}개 채널로 알림 전송 중...")

        for user_name, webhook_url in webhook_configs:
            if send_mattermost_notification(webhook_url, message, user_name):
                success_count += 1

        print(f"📊 알림 전송 완료: {success_count}/{total_count} 성공")

        if success_count == 0:
            print("❌ 모든 알림 전송이 실패했습니다.")
            sys.exit(1)
        elif success_count < total_count:
            print("⚠️ 일부 알림 전송이 실패했습니다.")
        else:
            print("✅ 모든 알림이 성공적으로 전송되었습니다.")

    except Exception as e:
        print(f"❌ 알림 전송 중 치명적 오류: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
