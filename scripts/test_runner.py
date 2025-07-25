#!/usr/bin/env python3
"""
scripts/test_runner.py
향상된 테스트 실행 및 상세 결과 제공
"""

import argparse
import json
import subprocess
import sys
import os
import tempfile
import time
from pathlib import Path

class TestResult:
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

def compare_outputs(expected, actual):
    """출력을 비교합니다."""
    expected_norm = normalize_output(expected)
    actual_norm = normalize_output(actual)
    
    return expected_norm == actual_norm

def run_single_test(class_name, test_case, test_type, test_index):
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
    
    # 출력 비교
    if compare_outputs(expected_output, actual_output):
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

def run_test_suite(class_name, test_cases, test_type):
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
        test_result = run_single_test(class_name, test_case, test_type, i)
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

def generate_detailed_report(result, code_file):
    """상세한 테스트 리포트를 생성합니다."""
    total_tests = result.sample_tests['total'] + result.generated_tests['total']
    total_passed = result.sample_tests['passed'] + result.generated_tests['passed']
    
    report = []
    report.append(f"📋 테스트 결과 상세 리포트")
    report.append(f"=" * 50)
    report.append(f"파일: {code_file}")
    report.append(f"컴파일: {'성공' if result.compilation_success else '실패'}")
    
    if not result.compilation_success:
        report.append(f"컴파일 오류: {result.compilation_error}")
        return '\n'.join(report)
    
    report.append(f"전체 테스트: {total_passed}/{total_tests} 통과")
    report.append(f"샘플 테스트: {result.sample_tests['passed']}/{result.sample_tests['total']} 통과")
    report.append(f"생성 테스트: {result.generated_tests['passed']}/{result.generated_tests['total']} 통과")
    report.append(f"전체 결과: {result.overall_result}")
    
    # 실패한 테스트케이스 상세 정보
    failed_tests = []
    
    for detail in result.sample_tests['details']:
        if not detail['passed']:
            failed_tests.append(f"샘플 - {detail['description']}: {detail['error']}")
    
    for detail in result.generated_tests['details']:
        if not detail['passed']:
            failed_tests.append(f"생성 - {detail['description']}: {detail['error']}")
    
    if failed_tests:
        report.append(f"\n❌ 실패한 테스트케이스:")
        for i, fail in enumerate(failed_tests[:5], 1):  # 최대 5개까지만
            report.append(f"  {i}. {fail}")
        if len(failed_tests) > 5:
            report.append(f"  ... 외 {len(failed_tests) - 5}개 더")
    
    # 오류 메시지
    if result.error_messages:
        report.append(f"\n🚨 오류 메시지:")
        for i, error in enumerate(result.error_messages[:3], 1):  # 최대 3개까지만
            report.append(f"  {i}. {error}")
    
    return '\n'.join(report)

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='향상된 테스트 실행기')
    parser.add_argument('--code-file', required=True, help='테스트할 코드 파일')
    parser.add_argument('--language', required=True, help='프로그래밍 언어')
    parser.add_argument('--sample-tests', required=True, help='샘플 테스트 파일')
    parser.add_argument('--generated-tests', required=True, help='생성된 테스트 파일')
    args = parser.parse_args()
    
    print(f"🚀 테스트 실행 시작: {args.code_file}")
    
    result = TestResult()
    
    # 현재는 Java만 지원
    if args.language.lower() != 'java':
        print(f"❌ 지원하지 않는 언어: {args.language}")
        result.error_messages.append(f"지원하지 않는 언어: {args.language}")
        sys.exit(1)
    
    # 코드 파일 존재 확인
    if not os.path.exists(args.code_file):
        print(f"❌ 코드 파일을 찾을 수 없습니다: {args.code_file}")
        result.error_messages.append(f"코드 파일 없음: {args.code_file}")
        sys.exit(1)
    
    # Java 코드 컴파일
    compilation_success, compilation_error = compile_java_code(args.code_file)
    result.compilation_success = compilation_success
    result.compilation_error = compilation_error
    
    if not compilation_success:
        result.error_messages.append(f"컴파일 실패: {compilation_error}")
        result.overall_result = "COMPILATION_ERROR"
        
        # 상세 리포트 출력
        report = generate_detailed_report(result, args.code_file)
        print(f"\n{report}")
        
        # GitHub Actions Output 설정
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
                f.write(f"result=FAIL\n")
                f.write(f"details={compilation_error}\n")
        
        sys.exit(1)
    
    # 클래스 이름 추출 (파일명에서 .java 제거)
    class_name = Path(args.code_file).stem
    
    try:
        # 테스트케이스 로드
        sample_test_cases = load_test_cases(args.sample_tests)
        generated_test_cases = load_test_cases(args.generated_tests)
        
        # 샘플 테스트 실행
        result.sample_tests = run_test_suite(class_name, sample_test_cases, "샘플")
        
        # 생성된 테스트 실행
        result.generated_tests = run_test_suite(class_name, generated_test_cases, "생성")
        
        # 전체 결과 판정
        sample_all_passed = (result.sample_tests['total'] > 0 and 
                           result.sample_tests['failed'] == 0)
        
        generated_any_passed = result.generated_tests['passed'] > 0
        
        if sample_all_passed:
            if generated_any_passed or result.generated_tests['total'] == 0:
                result.overall_result = "PASS"
            else:
                result.overall_result = "PARTIAL_PASS"  # 샘플은 통과했지만 생성 테스트 실패
        elif result.sample_tests['passed'] > 0:
            result.overall_result = "PARTIAL_PASS"  # 샘플 일부 통과
        else:
            result.overall_result = "FAIL"  # 샘플 테스트 모두 실패
        
        # 상세 리포트 생성 및 출력
        report = generate_detailed_report(result, args.code_file)
        print(f"\n{report}")
        
        # GitHub Actions Output 설정
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
                f.write(f"result={result.overall_result}\n")
                
                # 실패 시 상세 정보 제공
                if result.overall_result in ["FAIL", "PARTIAL_PASS"]:
                    details = []
                    if result.sample_tests['failed'] > 0:
                        details.append(f"샘플 테스트 {result.sample_tests['failed']}개 실패")
                    if result.generated_tests['failed'] > 0:
                        details.append(f"생성 테스트 {result.generated_tests['failed']}개 실패")
                    if result.error_messages:
                        details.extend(result.error_messages[:2])
                    
                    details_str = " | ".join(details)
                    f.write(f"details={details_str}\n")
                else:
                    f.write(f"details=모든 테스트 통과\n")
        
        # 성공 조건: PASS 또는 PARTIAL_PASS
        success = result.overall_result in ["PASS", "PARTIAL_PASS"]
        sys.exit(0 if success else 1)
        
    except Exception as e:
        error_msg = f"테스트 실행 중 오류: {str(e)}"
        print(f"❌ {error_msg}")
        result.error_messages.append(error_msg)
        result.overall_result = "ERROR"
        
        # GitHub Actions Output 설정
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
                f.write(f"result=FAIL\n")
                f.write(f"details={error_msg}\n")
        
        sys.exit(1)
    
    finally:
        # 컴파일된 .class 파일 정리
        try:
            class_file = Path(args.code_file).with_suffix('.class')
            if class_file.exists():
                class_file.unlink()
                print(f"🧹 정리 완료: {class_file}")
        except Exception as e:
            print(f"⚠️ 파일 정리 실패: {e}")

if __name__ == "__main__":
    main()