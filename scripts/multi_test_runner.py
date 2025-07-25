#!/usr/bin/env python3
"""
scripts/multi_test_runner.py
다중 문제 테스트 실행 및 결과 통합 (기존 test_runner.py 기능 포함)
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path

class TestResult:
    """단일 문제의 테스트 결과를 저장하는 클래스"""
    def __init__(self):
        self.sample_tests = {
            'total': 0, 'passed': 0, 'failed': 0, 'details': []
        }
        self.generated_tests = {
            'total': 0, 'passed': 0, 'failed': 0, 'details': []
        }
        self.compilation_success = False
        self.compilation_error = ""
        self.overall_result = "FAIL"
        self.error_messages = []
        self.execution_time = 0

def compile_java_code(code_file):
    """Java 코드를 컴파일합니다."""
    print(f"⚙️ Java 코드 컴파일 중: {code_file}")
    try:
        result = subprocess.run(
            ['javac', '-encoding', 'UTF-8', code_file],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("✅ 컴파일 성공")
            return True, ""
        else:
            error_msg = result.stderr or result.stdout or "알 수 없는 컴파일 오류"
            print(f"❌ 컴파일 실패: {error_msg}")
            return False, error_msg
    except subprocess.TimeoutExpired:
        error_msg = "컴파일 시간 초과 (30초)"
        print(f"❌ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"컴파일 중 오류: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def run_java_program(code_dir, class_name, input_data, timeout=5):
    """Java 프로그램을 실행하고 결과를 반환합니다."""
    try:
        start_time = time.time()
        # ✨ [수정] -cp 옵션으로 클래스 경로를 지정하여 ClassNotFoundException 해결
        process = subprocess.run(
            ['java', '-cp', code_dir, class_name],
            input=input_data,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=timeout
        )
        execution_time = time.time() - start_time
        
        if process.returncode == 0:
            return True, process.stdout.strip(), execution_time, ""
        else:
            error_msg = process.stderr or "프로그램 실행 오류"
            return False, "", execution_time, error_msg
    except subprocess.TimeoutExpired:
        return False, "", timeout, f"실행 시간 초과 ({timeout}초)"
    except Exception as e:
        return False, "", 0, f"실행 중 오류: {str(e)}"

def normalize_output(output):
    """출력을 정규화합니다."""
    if not output:
        return ""
    lines = output.strip().split('\n')
    normalized_lines = [line.strip() for line in lines]
    return '\n'.join(normalized_lines)

def compare_outputs(expected, actual, problem_id=None):
    """출력을 비교합니다."""
    expected_norm = normalize_output(expected)
    actual_norm = normalize_output(actual)
    return expected_norm == actual_norm

def run_single_test(code_dir, class_name, test_case, test_type, test_index, problem_id=None):
    """단일 테스트케이스를 실행합니다."""
    input_data = test_case.get('input', '')
    expected_output = test_case.get('output', '')
    description = test_case.get('description', f'{test_type} 테스트 {test_index + 1}')
    
    print(f"  🧪 {description}")
    print(f"     입력: {repr(input_data)}")
    print(f"     예상: {repr(expected_output)}")
    
    # ✨ [수정] 코드 디렉토리를 run_java_program에 전달
    success, actual_output, exec_time, error_msg = run_java_program(code_dir, class_name, input_data)
    
    result_detail = {
        'input': input_data, 'expected': expected_output, 
        'actual': actual_output, 'error': error_msg,
        'execution_time': exec_time, 'description': description
    }
    
    if not success:
        print(f"     ❌ 실행 실패: {error_msg.strip()}")
        result_detail['passed'] = False
        return result_detail
    
    print(f"     실제: {repr(actual_output)}")
    print(f"     시간: {exec_time:.3f}초")
    
    if compare_outputs(expected_output, actual_output, problem_id):
        print(f"     ✅ 통과")
        result_detail['passed'] = True
    else:
        print(f"     ❌ 실패 - 출력 불일치")
        result_detail['passed'] = False
        result_detail['error'] = '출력 불일치'
        
    return result_detail

def run_test_suite(code_dir, class_name, test_cases, test_type, problem_id=None):
    """테스트 스위트를 실행합니다."""
    print(f"\n📋 {test_type} 테스트 실행 ({len(test_cases)}개)")
    results = {'total': len(test_cases), 'passed': 0, 'failed': 0, 'details': []}
    
    if not test_cases:
        print(f"  ⚠️ {test_type} 테스트케이스가 없습니다.")
        return results
    
    for i, test_case in enumerate(test_cases):
        # ✨ [수정] 코드 디렉토리를 run_single_test에 전달
        test_result = run_single_test(code_dir, class_name, test_case, test_type, i, problem_id)
        results['details'].append(test_result)
        if test_result['passed']:
            results['passed'] += 1
        else:
            results['failed'] += 1
            
    print(f"📊 {test_type} 테스트 결과: {results['passed']}/{results['total']} 통과")
    return results

def load_test_cases(file_path):
    """테스트케이스 파일을 로드합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('test_cases', [])
    except FileNotFoundError:
        print(f"⚠️ 테스트 파일 없음: {file_path}")
    except Exception as e:
        print(f"❌ 테스트 파일 로드 실패 ({file_path}): {e}")
    return []

def load_problems_info():
    """PR에서 추출된 문제 정보를 로드합니다."""
    try:
        with open('problems_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ problems_info.json 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 문제 정보 로드 실패: {e}")
    return []

def search_problem_with_fetch_boj(problem_id):
    """fetch_boj_problem.py를 사용하여 문제를 검색합니다."""
    print(f"🔍 fetch_boj_problem.py로 문제 {problem_id} 검색 중...")
    try:
        # ✨ [수정] 타임아웃을 180초로 늘려 안정성 확보
        result = subprocess.run([
            'python', 'scripts/fetch_boj_problem.py',
            '--problem-id', problem_id,
            '--output', f'problem_{problem_id}_info.json'
        ], capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print(f"✅ 문제 {problem_id} 검색 성공")
            return True, ""
        else:
            error_msg = result.stderr or result.stdout or "알 수 없는 검색 실패"
            print(f"⚠️ 문제 {problem_id} 검색 실패: {error_msg.strip()}")
            return False, error_msg.strip()
    except subprocess.TimeoutExpired:
        print(f"⚠️ 문제 {problem_id} 검색 시간 초과 (180초)")
        return False, "검색 시간 초과"
    except Exception as e:
        print(f"⚠️ 문제 {problem_id} 검색 중 오류: {e}")
        return False, str(e)

def generate_tests_with_gemini(problem_info):
    """Gemini API를 사용하여 테스트케이스를 생성합니다."""
    problem_id = problem_info['problem_id']
    code_file = problem_info['code_file']
    language = problem_info.get('language', 'java')
    
    print(f"🤖 Gemini로 문제 {problem_id} 테스트케이스 생성 중...")
    try:
        result = subprocess.run([
            'python', 'scripts/gemini_test_generator.py',
            '--problem-id', problem_id, '--code-file', code_file,
            '--language', language, '--problem-info', f'problem_{problem_id}_info.json',
            '--output', f'tests_{problem_id}.json'
        ], capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print(f"✅ 문제 {problem_id} 테스트케이스 생성 성공")
            return True, ""
        else:
            error_msg = result.stderr or result.stdout or "테스트 생성 실패"
            print(f"⚠️ 문제 {problem_id} 테스트케이스 생성 실패: {error_msg.strip()}")
            return False, error_msg.strip()
    except subprocess.TimeoutExpired:
        print(f"⚠️ 문제 {problem_id} 테스트 생성 시간 초과")
        return False, "테스트 생성 시간 초과"
    except Exception as e:
        print(f"⚠️ 문제 {problem_id} 테스트 생성 중 오류: {e}")
        return False, str(e)

def run_single_problem_test(problem_info):
    """단일 문제에 대한 전체 테스트를 실행합니다."""
    problem_id = problem_info['problem_id']
    code_file = problem_info['code_file']
    author = problem_info['author']
    language = problem_info.get('language', 'java')
    
    print(f"\n{'='*60}")
    print(f"🧪 문제 {problem_id} 테스트 시작 (작성자: {author})")
    print(f"{'='*60}")
    
    result = {
        'problem_id': problem_id, 'author': author, 'code_file': code_file,
        'language': language, 'result': 'FAIL', 'search_success': False,
        'sample_tests': {'total': 0, 'passed': 0, 'failed': 0},
        'generated_tests': {'total': 0, 'passed': 0, 'failed': 0},
        'errors': []
    }
    
    try:
        if not os.path.exists(code_file):
            result['errors'].append(f"코드 파일 없음: {code_file}")
            result['result'] = 'ERROR'
            return result

        compilation_success, compilation_error = compile_java_code(code_file)
        if not compilation_success:
            result['errors'].append(f"컴파일 실패: {compilation_error}")
            result['result'] = 'COMPILATION_ERROR'
            return result
        
        # ✨ [수정] Java 클래스 경로와 이름을 올바르게 설정
        code_path = Path(code_file)
        code_dir = str(code_path.parent)
        class_name = code_path.stem
        
        try:
            # ✨ [수정] 검색 실패 시 대안 처리 로직 제거, 실패 시 즉시 에러로 반환
            search_success, search_error = search_problem_with_fetch_boj(problem_id)
            result['search_success'] = search_success
            if not search_success:
                result['errors'].append(f"문제 검색 실패: {search_error}")
                result['result'] = 'ERROR'
                return result

            test_gen_success, test_gen_error = generate_tests_with_gemini(problem_info)
            if not test_gen_success:
                result['errors'].append(f"테스트 생성 실패: {test_gen_error}")
                # 테스트 생성 실패는 치명적이지 않으므로 계속 진행 (샘플 테스트는 가능)
            
            sample_tests_path = f'sample_{problem_id}_tests.json'
            generated_tests_path = f'tests_{problem_id}.json'
            
            sample_test_cases = load_test_cases(sample_tests_path)
            generated_test_cases = load_test_cases(generated_tests_path)
            
            print(f"📋 로드된 테스트케이스: 샘플 {len(sample_test_cases)}개, 생성 {len(generated_test_cases)}개")
            
            # ✨ [수정] 테스트 실행 함수에 코드 디렉토리 전달
            test_result_obj = TestResult()
            test_result_obj.sample_tests = run_test_suite(code_dir, class_name, sample_test_cases, "샘플", problem_id)
            test_result_obj.generated_tests = run_test_suite(code_dir, class_name, generated_test_cases, "생성", problem_id)
            
            s_total, s_passed = test_result_obj.sample_tests['total'], test_result_obj.sample_tests['passed']
            g_total, g_passed = test_result_obj.generated_tests['total'], test_result_obj.generated_tests['passed']

            print(f"📊 테스트 상세: 샘플 {s_passed}/{s_total} 통과, 생성 {g_passed}/{g_total} 통과")

            if s_total == 0 and g_total == 0:
                result['result'] = "PARTIAL_PASS" # 컴파일만 성공
                result['errors'].append("테스트케이스 없음 - 컴파일만 확인됨")
            elif s_total > 0 and s_passed == s_total:
                result['result'] = "PASS"
            elif s_passed > 0 or g_passed > 0:
                result['result'] = "PARTIAL_PASS"
            else:
                result['result'] = "FAIL"
            
            result['sample_tests'] = test_result_obj.sample_tests
            result['generated_tests'] = test_result_obj.generated_tests
            
            print(f"📊 문제 {problem_id} 최종 결과: {result['result']}")
            
        finally:
            class_file = Path(code_file).with_suffix('.class')
            if class_file.exists():
                class_file.unlink()
                print(f"🧹 정리 완료: {class_file}")
    
    except Exception as e:
        result['errors'].append(f"실행 중 치명적 오류: {str(e)}")
        result['result'] = 'ERROR'
        import traceback
        print(f"❌ 문제 {problem_id} 처리 중 치명적 오류: {e}\n{traceback.format_exc()}")
        
    return result

# generate_summary와 main 함수는 기존 코드와 동일하게 사용합니다.
def generate_summary(results):
    """테스트 결과 요약을 생성합니다."""
    total = len(results)
    passed = len([r for r in results if r['result'] == 'PASS'])
    partial = len([r for r in results if r['result'] == 'PARTIAL_PASS'])
    failed = len([r for r in results if r['result'] in ['FAIL', 'COMPILATION_ERROR']])
    error = len([r for r in results if r['result'] == 'ERROR'])
    
    overall_success = (passed + partial) > 0
    
    return {
        'overall_success': overall_success, 'total_problems': total,
        'passed_problems': passed, 'partial_passed_problems': partial,
        'failed_problems': failed, 'error_problems': error,
        'details': results
    }

def main():
    """메인 실행 함수"""
    print("🚀 다중 문제 테스트 시작...")
    problems = load_problems_info()
    
    if not problems:
        print("❌ 처리할 문제가 없습니다.")
        sys.exit(1)
    
    print(f"📋 총 {len(problems)}개 문제 처리 예정")
    for p in problems:
        print(f"  - 문제 {p['problem_id']} ({p['author']}) - {p['code_file']}")
    
    results = []
    for i, problem in enumerate(problems, 1):
        print(f"\n🔄 진행률: {i}/{len(problems)}")
        try:
            results.append(run_single_problem_test(problem))
        except Exception as e:
            print(f"❌ 문제 {problem.get('problem_id', 'unknown')} 처리 중 최상위 오류: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'problem_id': problem.get('problem_id', 'unknown'),
                'author': problem.get('author', 'unknown'),
                'result': 'ERROR', 'errors': [str(e)]
            })
    
    summary = generate_summary(results)
    with open('test_results_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"📊 전체 테스트 결과 요약")
    print(f"{'='*60}")
    print(f"전체 문제: {summary['total_problems']}개")
    print(f"✅ 완전 성공: {summary['passed_problems']}개")
    print(f"⚠️ 부분 성공: {summary['partial_passed_problems']}개")
    print(f"❌ 실패: {summary['failed_problems']}개")
    print(f"💥 오류: {summary['error_problems']}개")
    print(f"전체 결과: {'🎉 성공' if summary['overall_success'] else '❌ 실패'}")
    
    print(f"\n📝 문제별 결과:")
    for res in results:
        status = {
            'PASS': '✅', 'PARTIAL_PASS': '⚠️', 'FAIL': '❌', 
            'ERROR': '💥', 'COMPILATION_ERROR': '🔧'
        }.get(res['result'], '❓')
        print(f"  {status} 문제 {res['problem_id']} ({res['author']}): {res['result']}")
        if res.get('errors'):
            print(f"      └─ {res['errors'][0]}")
    
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            for key, value in summary.items():
                if isinstance(value, (int, bool)):
                    f.write(f"{key}={str(value).lower() if isinstance(value, bool) else value}\n")
            f.write(f"overall_result={'PASS' if summary['overall_success'] else 'FAIL'}\n")

    exit_code = 0 if summary['overall_success'] else 1
    print(f"\n🏁 테스트 완료 (종료 코드: {exit_code})")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()