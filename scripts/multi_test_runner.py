#!/usr/bin/env python3
"""
scripts/multi_test_runner.py
다중 문제 테스트 실행 및 결과 통합 (기존 test_runner.py 기능 포함)
"""

import json
import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

class TestResult:
    """단일 문제의 테스트 결과를 저장하는 클래스"""
    def __init__(self):
        self.sample_tests = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        self.generated_tests = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
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
        # 컴파일 명령어 실행
        result = subprocess.run(
            ['javac', code_file],
            capture_output=True,
            text=True,
            timeout=30
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

def run_java_program(class_name, input_data, timeout=5):
    """Java 프로그램을 실행하고 결과를 반환합니다."""
    try:
        start_time = time.time()
        
        process = subprocess.run(
            ['java', class_name],
            input=input_data,
            capture_output=True,
            text=True,
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
    
    # 공백 정리 및 줄바꿈 정규화
    lines = output.strip().split('\n')
    normalized_lines = [line.strip() for line in lines]
    return '\n'.join(normalized_lines)

def compare_outputs(expected, actual, problem_id=None):
    """출력을 비교합니다. 부동소수점 문제는 특별 처리합니다."""
    expected_norm = normalize_output(expected)
    actual_norm = normalize_output(actual)
    
    # 정확한 문자열 비교 먼저 시도
    if expected_norm == actual_norm:
        return True
    
    # 부동소수점 비교가 필요한 문제들 (A/B 등)
    float_problems = ['1008', '1003', '10869', '2914']  # 확장 가능
    
    if problem_id in float_problems:
        try:
            expected_float = float(expected_norm)
            actual_float = float(actual_norm)
            
            # 상대 오차 또는 절대 오차가 1e-9 이하면 정답
            abs_diff = abs(expected_float - actual_float)
            rel_diff = abs_diff / max(abs(expected_float), 1e-10)
            
            if abs_diff < 1e-9 or rel_diff < 1e-9:
                return True
        except ValueError:
            # 부동소수점 변환 실패 시 원래 문자열 비교 결과 유지
            pass
    
    return False

def run_single_test(class_name, test_case, test_type, test_index, problem_id=None):
    """단일 테스트케이스를 실행합니다."""
    input_data = test_case.get('input', '')
    expected_output = test_case.get('output', '')
    description = test_case.get('description', f'{test_type} 테스트 {test_index + 1}')
    
    print(f"  🧪 {description}")
    print(f"     입력: {repr(input_data)}")
    print(f"     예상: {repr(expected_output)}")
    
    # 프로그램 실행
    success, actual_output, exec_time, error_msg = run_java_program(class_name, input_data)
    
    if not success:
        print(f"     ❌ 실행 실패: {error_msg}")
        return {
            'passed': False,
            'input': input_data,
            'expected': expected_output,
            'actual': '',
            'error': error_msg,
            'execution_time': exec_time,
            'description': description
        }
    
    print(f"     실제: {repr(actual_output)}")
    print(f"     시간: {exec_time:.3f}초")
    
    # 출력 비교 (문제 ID 포함)
    if compare_outputs(expected_output, actual_output, problem_id):
        print(f"     ✅ 통과")
        return {
            'passed': True,
            'input': input_data,
            'expected': expected_output,
            'actual': actual_output,
            'error': '',
            'execution_time': exec_time,
            'description': description
        }
    else:
        print(f"     ❌ 실패 - 출력 불일치")
        return {
            'passed': False,
            'input': input_data,
            'expected': expected_output,
            'actual': actual_output,
            'error': '출력 불일치',
            'execution_time': exec_time,
            'description': description
        }

def run_test_suite(class_name, test_cases, test_type, problem_id=None):
    """테스트 스위트를 실행합니다."""
    print(f"\n📋 {test_type} 테스트 실행 ({len(test_cases)}개)")
    
    results = {
        'total': len(test_cases),
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    if not test_cases:
        print(f"  ⚠️ {test_type} 테스트케이스가 없습니다.")
        return results
    
    for i, test_case in enumerate(test_cases):
        test_result = run_single_test(class_name, test_case, test_type, i, problem_id)
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
        return []
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
        return []
    except Exception as e:
        print(f"❌ 문제 정보 로드 실패: {e}")
        return []

def search_problem_with_fetch_boj(problem_id):
    """fetch_boj_problem.py를 사용하여 문제를 검색합니다."""
    print(f"🔍 fetch_boj_problem.py로 문제 {problem_id} 검색 중...")
    
    try:
        # fetch_boj_problem.py 실행
        result = subprocess.run([
            'python', 'scripts/fetch_boj_problem.py',
            '--problem-id', problem_id,
            '--output', f'problem_{problem_id}_info.json'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ 문제 {problem_id} 검색 성공")
            return True, ""
        else:
            error_msg = result.stderr or result.stdout or "검색 실패"
            print(f"⚠️ 문제 {problem_id} 검색 실패: {error_msg}")
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        print(f"⚠️ 문제 {problem_id} 검색 시간 초과")
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
        # gemini_test_generator.py 실행
        result = subprocess.run([
            'python', 'scripts/gemini_test_generator.py',
            '--problem-id', problem_id,
            '--code-file', code_file,
            '--language', language,
            '--problem-info', f'problem_{problem_id}_info.json',
            '--output', f'tests_{problem_id}.json'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ 문제 {problem_id} 테스트케이스 생성 성공")
            return True, ""
        else:
            error_msg = result.stderr or result.stdout or "테스트 생성 실패"
            print(f"⚠️ 문제 {problem_id} 테스트케이스 생성 실패: {error_msg}")
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        print(f"⚠️ 문제 {problem_id} 테스트 생성 시간 초과")
        return False, "테스트 생성 시간 초과"
    except Exception as e:
        print(f"⚠️ 문제 {problem_id} 테스트 생성 중 오류: {e}")
        return False, str(e)

def create_fallback_files(problem_id):
    """검색 실패 시 대안 파일들을 생성합니다."""
    print(f"🛠️ 문제 {problem_id} 대안 파일 생성 중...")
    
    problem_info = {
        'problem_id': problem_id,
        'title': f'문제 {problem_id}',
        'level': 'N/A',
        'tags': [],
        'description': f'문제 정보를 가져올 수 없습니다. https://www.acmicpc.net/problem/{problem_id} 에서 직접 확인해주세요.',
        'input_format': '입력 형식을 직접 확인해주세요.',
        'output_format': '출력 형식을 직접 확인해주세요.',
        'limits': {
            'time': '시간 제한을 직접 확인해주세요.',
            'memory': '메모리 제한을 직접 확인해주세요.'
        },
        'hint': '',
        'samples': [],
        'source': 'fallback'
    }
    
    with open(f'problem_{problem_id}_info.json', 'w', encoding='utf-8') as f:
        json.dump(problem_info, f, ensure_ascii=False, indent=2)
    
    # 빈 샘플 테스트 파일 생성
    sample_tests = {
        'problem_id': problem_id,
        'test_cases': [],
        'source': 'fallback_empty'
    }
    
    with open(f'sample_{problem_id}_tests.json', 'w', encoding='utf-8') as f:
        json.dump(sample_tests, f, ensure_ascii=False, indent=2)
    
    # 빈 생성 테스트 파일 생성
    with open(f'tests_{problem_id}.json', 'w', encoding='utf-8') as f:
        json.dump(sample_tests, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 문제 {problem_id} 기본 대안 파일 생성 완료")

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
        # 1. 코드 파일 존재 확인
        if not os.path.exists(code_file):
            result['errors'].append(f"코드 파일 없음: {code_file}")
            result['result'] = 'ERROR'
            return result
        
        # 2. Java 코드 컴파일
        compilation_success, compilation_error = compile_java_code(code_file)
        if not compilation_success:
            result['errors'].append(f"컴파일 실패: {compilation_error}")
            result['result'] = 'COMPILATION_ERROR'
            return result
        
        # 클래스 이름 추출
        class_name = Path(code_file).stem
        
        try:
            # 3. 문제 정보 검색
            search_success, search_error = search_problem_with_fetch_boj(problem_id)
            result['search_success'] = search_success
            
            if not search_success:
                result['errors'].append(f"문제 검색 실패: {search_error}")
                print(f"⚠️ 문제 검색 실패, 대안 처리 진행...")
                create_fallback_files(problem_id)
            
            # 필수 파일들이 존재하는지 확인하고 없으면 생성
            required_files = {
                f'problem_{problem_id}_info.json': 'problem_info',
                f'sample_{problem_id}_tests.json': 'sample_tests'
            }
            
            for file_path, file_type in required_files.items():
                if not Path(file_path).exists():
                    print(f"⚠️ {file_type} 파일 없음: {file_path}, 대안 파일 생성")
                    create_fallback_files(problem_id)
                    break
            
            # 4. 테스트케이스 생성 (Gemini) - 실패해도 계속 진행
            test_gen_success, test_gen_error = generate_tests_with_gemini(problem_info)
            if not test_gen_success:
                result['errors'].append(f"테스트 생성 실패: {test_gen_error}")
                if not Path(f'tests_{problem_id}.json').exists():
                    empty_tests = {
                        'problem_id': problem_id,
                        'test_cases': [],
                        'source': 'generation_failed'
                    }
                    with open(f'tests_{problem_id}.json', 'w', encoding='utf-8') as f:
                        json.dump(empty_tests, f, ensure_ascii=False, indent=2)
            
            # 5. 테스트케이스 로드 및 실행
            sample_test_cases = load_test_cases(f'sample_{problem_id}_tests.json')
            generated_test_cases = load_test_cases(f'tests_{problem_id}.json')
            
            print(f"📋 로드된 테스트케이스:")
            print(f"   샘플: {len(sample_test_cases)}개")
            print(f"   생성: {len(generated_test_cases)}개")
            
            # 샘플 테스트 실행
            test_result = TestResult()
            test_result.sample_tests = run_test_suite(class_name, sample_test_cases, "샘플", problem_id)
            test_result.generated_tests = run_test_suite(class_name, generated_test_cases, "생성", problem_id)
            
            # 결과 판정 개선
            total_sample_tests = test_result.sample_tests['total']
            total_generated_tests = test_result.generated_tests['total']
            sample_passed = test_result.sample_tests['passed']
            generated_passed = test_result.generated_tests['passed']
            
            print(f"📊 테스트 상세:")
            print(f"   샘플 테스트: {sample_passed}/{total_sample_tests} 통과")
            print(f"   생성 테스트: {generated_passed}/{total_generated_tests} 통과")
            
            # 결과 판정 로직
            if total_sample_tests == 0 and total_generated_tests == 0:
                # 테스트케이스가 아예 없는 경우 - 컴파일만 성공하면 부분 성공
                result['result'] = "PARTIAL_PASS"
                result['errors'].append("테스트케이스 없음 - 컴파일만 확인됨")
                print(f"⚠️ 테스트케이스 없음, 컴파일 성공으로 부분 성공 처리")
            elif total_sample_tests > 0:
                # 샘플 테스트가 있는 경우
                sample_all_passed = test_result.sample_tests['failed'] == 0
                
                if sample_all_passed:
                    if total_generated_tests == 0 or generated_passed > 0:
                        result['result'] = "PASS"
                        print(f"✅ 샘플 테스트 모두 통과!")
                    else:
                        result['result'] = "PARTIAL_PASS"
                        print(f"⚠️ 샘플은 통과했지만 생성 테스트 실패")
                elif sample_passed > 0:
                    result['result'] = "PARTIAL_PASS"
                    print(f"⚠️ 샘플 테스트 일부 통과 ({sample_passed}/{total_sample_tests})")
                else:
                    result['result'] = "FAIL"
                    print(f"❌ 샘플 테스트 모두 실패")
            else:
                # 샘플 테스트는 없고 생성 테스트만 있는 경우
                if generated_passed > 0:
                    result['result'] = "PARTIAL_PASS"
                    print(f"⚠️ 생성 테스트만 일부 통과 ({generated_passed}/{total_generated_tests})")
                else:
                    result['result'] = "FAIL"
                    print(f"❌ 생성 테스트 모두 실패")
            
            # 상세 결과 저장
            result['sample_tests'] = test_result.sample_tests
            result['generated_tests'] = test_result.generated_tests
            
            print(f"📊 문제 {problem_id} 최종 결과: {result['result']}")
            
        finally:
            # 컴파일된 .class 파일 정리
            try:
                class_file = Path(code_file).with_suffix('.class')
                if class_file.exists():
                    class_file.unlink()
                    print(f"🧹 정리 완료: {class_file}")
            except Exception as e:
                print(f"⚠️ 파일 정리 실패: {e}")
        
    except Exception as e:
        result['errors'].append(f"실행 중 오류: {str(e)}")
        result['result'] = 'ERROR'
        print(f"❌ 문제 {problem_id} 처리 중 오류: {e}")
    
    return result

def generate_summary(results):
    """테스트 결과 요약을 생성합니다."""
    total_problems = len(results)
    passed_problems = len([r for r in results if r['result'] == 'PASS'])
    partial_passed = len([r for r in results if r['result'] == 'PARTIAL_PASS'])
    failed_problems = len([r for r in results if r['result'] in ['FAIL', 'COMPILATION_ERROR']])
    error_problems = len([r for r in results if r['result'] == 'ERROR'])
    
    # 전체 성공 조건: 최소 1개 문제가 PASS 또는 PARTIAL_PASS
    overall_success = (passed_problems + partial_passed) > 0
    
    summary = {
        'overall_success': overall_success,
        'total_problems': total_problems,
        'passed_problems': passed_problems,
        'partial_passed_problems': partial_passed,
        'failed_problems': failed_problems,
        'error_problems': error_problems,
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
    for problem in problems:
        print(f"  - 문제 {problem['problem_id']} ({problem['author']}) - {problem['code_file']}")
    
    # 각 문제별 테스트 실행
    results = []
    for i, problem in enumerate(problems, 1):
        print(f"\n🔄 진행률: {i}/{len(problems)}")
        try:
            result = run_single_problem_test(problem)
            results.append(result)
        except Exception as e:
            print(f"❌ 문제 {problem.get('problem_id', 'unknown')} 처리 중 오류: {e}")
            results.append({
                'problem_id': problem.get('problem_id', 'unknown'),
                'author': problem.get('author', 'unknown'),
                'code_file': problem.get('code_file', 'unknown'),
                'language': problem.get('language', 'java'),
                'result': 'ERROR',
                'search_success': False,
                'sample_tests': {'total': 0, 'passed': 0, 'failed': 0},
                'generated_tests': {'total': 0, 'passed': 0, 'failed': 0},
                'errors': [str(e)]
            })
    
    # 결과 요약 생성
    summary = generate_summary(results)
    
    # 결과 저장
    with open('test_results_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"\n{'='*60}")
    print(f"📊 전체 테스트 결과 요약")
    print(f"{'='*60}")
    print(f"전체 문제: {summary['total_problems']}개")
    print(f"완전 성공: {summary['passed_problems']}개")
    print(f"부분 성공: {summary['partial_passed_problems']}개")
    print(f"실패: {summary['failed_problems']}개")
    print(f"오류: {summary['error_problems']}개")
    print(f"전체 결과: {'🎉 성공' if summary['overall_success'] else '❌ 실패'}")
    
    # 각 문제별 간단 요약
    print(f"\n📝 문제별 결과:")
    for result in results:
        status_emoji = {
            'PASS': '✅',
            'PARTIAL_PASS': '⚠️',
            'FAIL': '❌',
            'ERROR': '💥',
            'COMPILATION_ERROR': '🔧'
        }.get(result['result'], '❓')
        
        print(f"  {status_emoji} 문제 {result['problem_id']} ({result['author']}): {result['result']}")
        if result['errors']:
            print(f"      └─ {result['errors'][0]}")
    
    # GitHub Actions 출력 설정
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write(f"overall_result={'PASS' if summary['overall_success'] else 'FAIL'}\n")
            f.write(f"total_problems={summary['total_problems']}\n")
            f.write(f"passed_problems={summary['passed_problems']}\n")
            f.write(f"partial_passed_problems={summary['partial_passed_problems']}\n")
            f.write(f"failed_problems={summary['failed_problems']}\n")
            f.write(f"error_problems={summary['error_problems']}\n")
    
    # 성공 조건에 따른 종료 코드
    exit_code = 0 if summary['overall_success'] else 1
    print(f"\n🏁 테스트 완료 (종료 코드: {exit_code})")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()