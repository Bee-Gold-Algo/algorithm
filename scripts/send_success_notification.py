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
    
    # PR URL 단축 (가독성 향상)
    pr_url = sys.argv[1] if len(sys.argv) > 1 else "N/A"
    pr_display = pr_url.split('/')[-1] if pr_url != "N/A" else "N/A"  # PR 번호만 추출
    
    # 메시지 구성 - 실제 줄바꿈 문자 사용
    message_parts = []
    
    # 헤더
    message_parts.append('🎉 **Test Results**')
    message_parts.append('')  # 빈 줄
    
    # 통계 정보 (더 간결하게)
    message_parts.append(f'📊 **총 {total}개 문제**')
    message_parts.append(f'✅ 완전 성공: **{passed}개**')
    if partial > 0:
        message_parts.append(f'⚠️ 부분 성공: **{partial}개**')
    if failed > 0:
        message_parts.append(f'❌ 실패: **{failed}개**')
    
    success_rate = round((passed + partial) / max(total, 1) * 100, 1)
    message_parts.append(f'📈 성공률: **{success_rate}%**')
    message_parts.append('')  # 빈 줄
    
    # 성공한 문제들 (한 줄에 3개씩 표시)
    if success_list:
        message_parts.append('**✅ 완전 성공한 문제들:**')
        # 3개씩 그룹화
        for i in range(0, len(success_list), 3):
            group = success_list[i:i+3]
            message_parts.append(' | '.join(group))
        message_parts.append('')  # 빈 줄
    
    # 부분 성공한 문제들
    if partial_list:
        message_parts.append('**⚠️ 부분 성공한 문제들:**')
        for i in range(0, len(partial_list), 3):
            group = partial_list[i:i+3]
            message_parts.append(' | '.join(group))
        message_parts.append('')  # 빈 줄
    
    # 실패한 문제들 (너무 많으면 개수만 표시)
    if failed_list:
        if len(failed_list) <= 5:
            message_parts.append('**❌ 실패한 문제들:**')
            for i in range(0, len(failed_list), 3):
                group = failed_list[i:i+3]
                message_parts.append(' | '.join(group))
        else:
            message_parts.append(f'**❌ 실패한 문제들:** {len(failed_list)}개 (자세한 내용은 PR 확인)')
        message_parts.append('')  # 빈 줄
    
    # 결론
    message_parts.append('🎯 **한 문제 이상 성공으로 PR 승인됩니다!**')
    
    # PR 링크 (짧게 표시)
    if pr_url != "N/A":
        message_parts.append(f'🔗 [PR #{pr_display} 보기]({pr_url})')
    
    # 실제 줄바꿈 문자로 조인
    message = '\n'.join(message_parts)
    
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
    
    # 디버깅용 메시지 출력
    print(f'📝 전송할 메시지 미리보기:')
    print('=' * 50)
    print(message)
    print('=' * 50)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
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
    # 오류 발생 시 스택 트레이스도 출력
    import traceback
    traceback.print_exc()