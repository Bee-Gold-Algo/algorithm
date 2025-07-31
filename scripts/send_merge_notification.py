#!/usr/bin/env python3
"""
PR 머지 완료 알림을 Mattermost로 전송하는 스크립트
"""

import sys
import requests
import json
from datetime import datetime
import pytz

def send_merge_notification(pr_url, user, week_number, webhook_url):
    """머지 완료 알림 전송"""
    
    # 한국 시간대 설정
    kst = pytz.timezone('Asia/Seoul')
    current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S KST')
    
    # problems_info.json에서 제출된 문제 정보 가져오기
    problems_count = 0
    problems_list = []
    
    try:
        with open('problems_info.json', 'r', encoding='utf-8') as f:
            problems_data = json.load(f)
            problems_count = problems_data.get('total_count', 0)
            problems_list = [p['problem_number'] for p in problems_data.get('problems', [])]
    except FileNotFoundError:
        print("ℹ️ problems_info.json 파일을 찾을 수 없습니다.")
    
    # 메시지 구성
    if week_number == "owner":
        title = f"🎉 저장소 소유자 솔루션 머지 완료!"
        week_text = "Owner"
    else:
        title = f"🎉 Week {week_number} 솔루션 머지 완료!"
        week_text = f"Week {week_number}"
    
    fields = [
        {
            "title": "👤 제출자",
            "value": user,
            "short": True
        },
        {
            "title": "📅 주차",
            "value": week_text,
            "short": True
        },
        {
            "title": "📊 제출 문제 수",
            "value": f"{problems_count}개",
            "short": True
        },
        {
            "title": "⏰ 머지 시간",
            "value": current_time,
            "short": True
        }
    ]
    
    # 제출된 문제 목록 추가
    if problems_list:
        problems_text = ", ".join(problems_list)
        if len(problems_text) > 200:  # 너무 길면 축약
            problems_text = problems_text[:200] + "..."
        
        fields.append({
            "title": "📋 제출된 문제",
            "value": problems_text,
            "short": False
        })
    
    # Mattermost 메시지 구성
    message = {
        "username": "Algorithm Study Bot",
        "icon_emoji": ":white_check_mark:",
        "attachments": [
            {
                "color": "#36a64f",  # 초록색
                "title": title,
                "title_link": pr_url,
                "fields": fields,
                "footer": "Algorithm Study Automation",
                "ts": int(datetime.now().timestamp())
            }
        ]
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ {user}님에게 머지 완료 알림을 전송했습니다.")
        else:
            print(f"❌ 알림 전송 실패: HTTP {response.status_code}")
            print(f"응답: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 알림 전송 중 오류 발생: {e}")

def main():
    if len(sys.argv) != 5:
        print("사용법: python send_merge_notification.py <PR_URL> <USER> <WEEK_NUMBER> <WEBHOOK_URL>")
        sys.exit(1)
    
    pr_url = sys.argv[1]
    user = sys.argv[2]
    week_number = sys.argv[3]
    webhook_url = sys.argv[4]
    
    if week_number == "owner":
        print(f"📤 저장소 소유자({user})님에게 머지 완료 알림을 전송합니다...")
    else:
        print(f"📤 {user}님에게 Week {week_number} 머지 완료 알림을 전송합니다...")
    
    send_merge_notification(pr_url, user, week_number, webhook_url)

if __name__ == "__main__":
    main()