#!/usr/bin/env python3
"""
scripts/test_runner.py
향상된 테스트 실행 및 상세 결과 제공
"""

import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path

def load_problems_info():
    """PR에서 추출된 문제 정보를 로드합니다."""
    try:
        with open('problems_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ problems_info.json 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"❌ 문제 정보 로드 실패: {e}")
        return []

def run_single_problem_test(problem_info):
    """단일 문제에 대한 테스트를 실행합니다."""
    problem_id = problem_info['problem_id']
    code_file = problem_info['code_file']
    author = problem_info['author']
    language = problem_info.get('language', 'java')
    
    print(f"\n🧪 문제 {problem_id} 테스트 시작 (작성자: {author})")
    
    result = {
        'problem_id': problem_id,
        'author': author,
        'code_file': code_file,
        'language': language,
        'result': 'FAIL',
        'search_success': False,
        'sample_tests': {'total': 0, 'passed': 0, 'failed': 0},
        'generated_tests': {'total': 0, 'passed': 0, 'failed': 0},
        'errors': []
    }
    
    try:
        # 1. Gemini로 문제 검색
        print(f"🔍 문제 {problem_id} 정보 검색 중...")
        search_result = subprocess.run([
            'python', 'scripts/gemini_problem_search.py',
            '--problem-id', problem_id,
            '--output', f'problem_{problem_id}_info.json'
        ], capture_output=True, text=True, timeout=60)
        
        if search_result.returncode == 0:
            result['search_success'] = True
            print(f"✅ 문제 {problem_id} 검색 성공")
        else:
            print(f"⚠️ 문제 {problem_id} 검색 실패, 대안 처리...")
            result['errors'].append("Gemini 검색 실패")
            
            # 대안 처리: solved.ac API 사용
            subprocess.run([
                'python', 'scripts/fallback_search.py',
                '--problem-id', problem_id,
                '--output', f'problem_{problem_id}_info.json'
            ], timeout=30)
        
        # 2. 테스트케이스 생성
        print(f"🤖 문제 {problem_id} 테스트케이스 생성 중...")
        test_gen_result = subprocess.run([
            'python', 'scripts/gemini_test_generator.py',
            '--problem-id', problem_id,
            '--code-file', code_file,
            '--language', language,
            '--problem-info', f'problem_{problem_id}_info.json',
            '--output', f'tests_{problem_id}.json'
        ], capture_output=True, text=True, timeout=120)
        
        if test_gen_result.returncode != 0:
            result['errors'].append("테스트케이스 생성 실패")
        
        # 3. 테스트 실행
        print(f"🚀 문제 {problem_id} 테스트 실행 중...")
        test_result = subprocess.run([
            'python', 'scripts/test_runner.py',
            '--code-file', code_file,
            '--language', language,
            '--sample-tests', f'sample_{problem_id}_tests.json',
            '--generated-tests', f'tests_{problem_id}.json'
        ], capture_output=True, text=True, timeout=180)
        
        # 테스트 결과 처리
        if test_result.returncode == 0:
            result['result'] = 'PASS'
        elif 'PARTIAL_PASS' in test_result.stdout:
            result['result'] = 'PARTIAL_PASS'
        else:
            result['result'] = 'FAIL'
            if test_result.stderr:
                result['errors'].append(test_result.stderr[:200])
        
        # 상세 결과 파싱 (가능한 경우)
        try:
            if os.path.exists(f'test_result_{problem_id}.json'):
                with open(f'test_result_{problem_id}.json', 'r', encoding='utf-8') as f:
                    detailed = json.load(f)
                    result['sample_tests'] = detailed.get('sample_tests', result['sample_tests'])
                    result['generated_tests'] = detailed.get('generated_tests', result['generated_tests'])
        except:
            pass
        
        print(f"📊 문제 {problem_id} 결과: {result['result']}")
        
    except subprocess.TimeoutExpired:
        result['errors'].append("테스트 시간 초과")
        result['result'] = 'ERROR'
    except Exception as e:
        result['errors'].append(f"실행 중 오류: {str(e)}")
        result['result'] = 'ERROR'
    
    return result

def generate_summary(results):
    """테스트 결과 요약을 생성합니다."""
    total_problems = len(results)
    passed_problems = len([r for r in results if r['result'] == 'PASS'])
    partial_passed = len([r for r in results if r['result'] == 'PARTIAL_PASS'])
    failed_problems = len([r for r in results if r['result'] in ['FAIL', 'ERROR']])
    
    # 전체 성공 조건: 최소 1개 문제가 PASS 또는 PARTIAL_PASS
    overall_success = (passed_problems + partial_passed) > 0
    
    summary = {
        'overall_success': overall_success,
        'total_problems': total_problems,
        'passed_problems': passed_problems,
        'partial_passed_problems': partial_passed,
        'failed_problems': failed_problems,
        'error_problems': len([r for r in results if r['result'] == 'ERROR']),
        'details': results
    }
    
    return summary

def main():
    """메인 실행 함수"""
    print("🚀 다중 문제 테스트 시작...")
    
    # 문제 정보 로드
    problems = load_problems_info()
    
    if not problems:
        print("❌ 처리할 문제가 없습니다.")
        sys.exit(1)
    
    print(f"📋 총 {len(problems)}개 문제 처리 예정")
    
    # 각 문제별 테스트 실행
    results = []
    for problem in problems:
        try:
            result = run_single_problem_test(problem)
            results.append(result)
        except Exception as e:
            print(f"❌ 문제 {problem.get('problem_id', 'unknown')} 처리 중 오류: {e}")
            results.append({
                'problem_id': problem.get('problem_id', 'unknown'),
                'author': problem.get('author', 'unknown'),
                'result': 'ERROR',
                'search_success': False,
                'errors': [str(e)]
            })
    
    # 결과 요약 생성
    summary = generate_summary(results)
    
    # 결과 저장
    with open('test_results_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"\n📊 전체 테스트 결과")
    print(f"=" * 50)
    print(f"전체 문제: {summary['total_problems']}개")
    print(f"완전 성공: {summary['passed_problems']}개")
    print(f"부분 성공: {summary['partial_passed_problems']}개")
    print(f"실패: {summary['failed_problems']}개")
    print(f"오류: {summary['error_problems']}개")
    print(f"전체 결과: {'성공' if summary['overall_success'] else '실패'}")
    
    # GitHub Actions 출력 설정
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write(f"overall_result={'PASS' if summary['overall_success'] else 'FAIL'}\n")
            f.write(f"total_problems={summary['total_problems']}\n")
            f.write(f"passed_problems={summary['passed_problems']}\n")
            f.write(f"partial_passed_problems={summary['partial_passed_problems']}\n")
            f.write(f"failed_problems={summary['failed_problems']}\n")
    
    # 성공 조건에 따른 종료 코드
    sys.exit(0 if summary['overall_success'] else 1)

if __name__ == "__main__":
    main()