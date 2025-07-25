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
    
    if successful_problems:
        print(f'✅ README 업데이트 대상: {len(successful_problems)}개 문제')
    
    for problem in successful_problems:
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
            print(f'  - 문제 {problem_id} README 업데이트 완료')
        except Exception as e:
            print(f'  - ⚠️ 문제 {problem_id} README 업데이트 실패: {e}')
            
except FileNotFoundError:
    print('ℹ️ test_results_summary.json 파일이 없어 README 업데이트를 건너뜁니다.')
except Exception as e:
    print(f'❌ README 업데이트 중 오류: {e}')
    sys.exit(1) 