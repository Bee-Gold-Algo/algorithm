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
    error = results.get('error_problems', 0)
    
    # 실패 상세 정보
    failure_details = []
    for detail in results.get('details', []):
        if detail['result'] in ['FAIL', 'ERROR']:
            problem_id = detail['problem_id']
            author = detail['author']
            errors = detail.get('errors', [])
            
            error_summary = errors[0] if errors else '알 수 없는 오류'
            if len(error_summary) > 100:
                error_summary = error_summary[:100] + '...'
            
            failure_details.append(f'**{problem_id}** ({author}): {error_summary}')
    
    # 메시지 구성
    message_parts = [
        '❌ **Multiple Problems Test Failed**',
        f'**Total**: {total}개 | **Success**: {passed}개 | **Partial**: {partial}개 | **Failed**: {failed}개 | **Error**: {error}개',
        f'**PR**: {sys.argv[1] if len(sys.argv) > 1 else "N/A"}'
    ]
    
    if failure_details:
        message_parts.append('**실패 상세:**')
        message_parts.extend(failure_details[:5])  # 최대 5개까지만
        if len(failure_details) > 5:
            message_parts.append(f'... 외 {len(failure_details) - 5}개 더')
    
    message_parts.append('💪 코드를 수정한 후 다시 푸시해주세요!')
    
    message = '\\n\\n'.join(message_parts)
    
    # MatterMost 알림 전송
    payload = {
        'username': 'BOJ-Bot',
        'icon_emoji': ':x:',
        'text': message
    }
    
    webhook_url = os.environ.get('MATTERMOST_WEBHOOK_URL')
    if not webhook_url:
        print('⚠️ MATTERMOST_WEBHOOK_URL이 설정되지 않았습니다.')
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
    print('✅ 실패 알림 전송 완료')
    
except Exception as e:
    print(f'❌ 알림 전송 실패: {e}') 