import json
import subprocess
import os
import tempfile
import sys

try:
    with open('test_results_summary.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    total = results.get('total_problems', 0)
    passed = results.get('passed_problems', 0)
    partial = results.get('partial_passed_problems', 0)
    failed = results.get('failed_problems', 0)
    
    # 성공한 문제들 목록
    success_list = []
    partial_list = []
    failed_list = []
    
    for detail in results.get('details', []):
        problem_id = detail['problem_id']
        author = detail['author']
        result = detail['result']
        
        if result == 'PASS':
            success_list.append(f'**{problem_id}** ({author})')
        elif result == 'PARTIAL_PASS':
            partial_list.append(f'**{problem_id}** ({author})')
        else:
            failed_list.append(f'**{problem_id}** ({author})')
    
    # 메시지 구성
    message_parts = [
        '🎉 **Multiple Problems Test Results**',
        f'**Total**: {total}개 | **Success**: {passed}개 | **Partial**: {partial}개 | **Failed**: {failed}개',
        f'**Success Rate**: {round((passed + partial) / max(total, 1) * 100, 1)}%',
        f'**PR**: {sys.argv[1] if len(sys.argv) > 1 else "N/A"}'
    ]
    
    if success_list:
        message_parts.append(f'**✅ 완전 성공**: {" | ".join(success_list)}')
    
    if partial_list:
        message_parts.append(f'**⚠️ 부분 성공**: {" | ".join(partial_list)}')
    
    if failed_list:
        message_parts.append(f'**❌ 실패**: {" | ".join(failed_list)}')
    
    message_parts.append('🎯 한 문제 이상 성공으로 PR 승인됩니다!')
    
    message = '\\n\\n'.join(message_parts)
    
    # MatterMost 알림 전송
    payload = {
        'username': 'BOJ-Bot',
        'icon_emoji': ':white_check_mark:',
        'text': message
    }
    
        # PR 작성자 정보 가져오기 (두 번째 인자)
    pr_author = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 개인 웹훅 URL 가져오기 (세 번째 인자, 우선순위 1)
    personal_webhook_url = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '' else None
    
    webhook_url = None
    if personal_webhook_url:
        webhook_url = personal_webhook_url
        print(f'📩 개인 DM으로 알림 전송: {pr_author}')
    elif pr_author:
        # 환경변수에서 개인 웹훅 URL 시도 (백업, 우선순위 2)
        personal_webhook_key = f"{pr_author.upper()}_MATTERMOST_URL"
        webhook_url = os.environ.get(personal_webhook_key)
        
        if webhook_url:
            print(f'📩 환경변수에서 개인 DM으로 알림 전송: {pr_author}')
        else:
            print(f'⚠️ {personal_webhook_key} 환경변수가 설정되지 않았습니다. 기본 채널로 전송합니다.')
    
    # 개인 웹훅이 없으면 기본 채널 웹훅 사용 (우선순위 3)
    if not webhook_url:
        webhook_url = os.environ.get('MATTERMOST_WEBHOOK_URL')
        print('📢 기본 채널로 알림 전송')
    
    if not webhook_url:
        print('❌ 사용 가능한 MATTERMOST 웹훅 URL이 없습니다.')
        sys.exit(0)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(payload, f)
        payload_file = f.name
    
    subprocess.run([
        'curl', '-X', 'POST',
        '-H', 'Content-Type: application/json',
        '-d', f'@{payload_file}',
        webhook_url,
        '--fail', '--silent', '--show-error'
    ], check=True)
    
    os.unlink(payload_file)
    print('✅ 성공 알림 전송 완료')
    
except Exception as e:
    print(f'❌ 알림 전송 실패: {e}') 