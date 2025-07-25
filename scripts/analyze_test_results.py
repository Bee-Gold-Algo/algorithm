import json
import os

with open('test_results_summary.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

overall_success = results.get('overall_success', False)
total_problems = results.get('total_problems', 0)
passed_problems = results.get('passed_problems', 0)
partial_passed = results.get('partial_passed_problems', 0)
failed_problems = results.get('failed_problems', 0)

# GitHub Actions Output 설정
with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
    f.write(f'overall_result={"PASS" if overall_success else "FAIL"}\n')
    f.write(f'total_problems={total_problems}\n')
    f.write(f'passed_problems={passed_problems}\n')
    f.write(f'partial_passed_problems={partial_passed}\n')
    f.write(f'failed_problems={failed_problems}\n')
    f.write(f'success_rate={round((passed_problems + partial_passed) / max(total_problems, 1) * 100, 1)}\n')

print(f'전체 결과: {"성공" if overall_success else "실패"}')
print(f'성공/부분성공: {passed_problems + partial_passed}/{total_problems}') 