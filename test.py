python -c "
import json
import subprocess
import sys
from datetime import datetime

try:
    with open('test_results_summary.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    successful_problems = []
    for detail in results.get('details', []):
        if detail['result'] in ['PASS', 'PARTIAL_PASS']:
            successful_problems.append(detail)
    
    print(f'README 업데이트 대상: {len(successful_problems)}개 문제')
    
    # --- [수정된 부분 시작] ---
    for problem in successful_problems:
        # f-string에 사용될 값을 미리 변수에 할당
        problem_id = problem['problem_id']
        author = problem['author']
        
        cmd = [
            'python', 'scripts/update_readme.py',
            '--problem-id', problem_id,
            '--author', author,
            '--submission-date', datetime.now().strftime('%Y-%m-%d'),
            '--language', 'Java'
        ]
        
        try:
            subprocess.run(cmd, check=True, timeout=30)
            # f-string 안에서는 간단한 변수만 사용
            print(f'✅ 문제 {problem_id} README 업데이트 완료')
        except Exception as e:
            print(f'⚠️ 문제 {problem_id} README 업데이트 실패: {e}')
    # --- [수정된 부분 끝] ---
            
except Exception as e:
    print(f'❌ README 업데이트 중 오류: {e}')
    sys.exit(1)
"