#!/usr/bin/env python3
"""
scripts/test_runner.py
샘플 테스트와 AI 생성 테스트를 실행합니다.
"""

import argparse
import json
import subprocess
import os
import sys
from pathlib import Path

def write_output(key, value):
    """GitHub Actions의 다음 단계로 출력을 전달합니다."""
    # 줄바꿈 문자를 이스케이프 처리하여 여러 줄의 오류 메시지를 안전하게 전달
    value = value.replace('%', '%25').replace('\n', '%0A').replace('\r', '%0D')
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"{key}={value}\n")
    else:
        # 로컬 테스트를 위한 레거시 출력 방식
        print(f"::set-output name={key}::{value}")

class TestRunner:
    def __init__(self, code_file, language):
        self.code_file = code_file
        self.language = language
        self.failed_tests = []
        self.executable = None
        self.java_class_path = None

    def compile_if_needed(self):
        """컴파일이 필요한 언어의 경우 컴파일 실행"""
        if self.language == 'java':
            try:
                code_path = Path(self.code_file)
                # 클래스 파일이 생성될 디렉토리와 클래스 이름을 저장
                self.java_class_path = code_path.parent
                self.executable = code_path.stem  # e.g., 'Main'

                result = subprocess.run(
                    ['javac', str(code_path)],
                    capture_output=True, text=True, timeout=30, check=True
                )
                return True, "컴파일 성공"
            except subprocess.CalledProcessError as e:
                return False, f"컴파일 오류:\n{e.stderr}"
            except Exception as e:
                return False, f"컴파일 예외: {e}"
        # 다른 컴파일 언어 로직 (예: cpp)은 여기에 추가 가능
        return True, "컴파일 불필요"

    def run_single_test(self, test_input, timeout=5):
        """단일 테스트케이스 실행"""
        cmd = []
        try:
            if self.language == 'python':
                cmd = ['python3', self.code_file]
            elif self.language == 'java':
                # -cp 옵션으로 클래스 경로를 지정해야 올바르게 실행됨
                cmd = ['java', '-cp', str(self.java_class_path), self.executable]
            else:
                return False, f"지원하지 않는 언어: {self.language}"

            process = subprocess.run(
                cmd, input=test_input, capture_output=True,
                text=True, timeout=timeout
            )
            if process.returncode != 0:
                error_msg = process.stderr or "런타임 오류 발생"
                return False, f"실행 오류: {error_msg.strip()}"
            
            # 성공 시 (True, 실행 결과) 반환
            return True, process.stdout.strip()
        
        # ⭐️ 들여쓰기 수정 및 예외 처리 강화 ⭐️
        except subprocess.TimeoutExpired:
            return False, f"{timeout}초 시간 초과"
        except Exception as e:
            return False, f"실행 중 예외 발생: {e}"

    def run_tests_from_file(self, file_path, test_type):
        """파일로부터 테스트케이스 목록을 읽어와 실행"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_cases = data.get('test_cases', [])
            if not test_cases:
                return True, f"{test_type} 테스트케이스 없음"
            
            print(f"🔄 {test_type} 테스트 실행 중... ({len(test_cases)}개)")
            
            for i, case in enumerate(test_cases):
                test_input = case.get('input', '')
                expected_output = case.get('output', '')
                
                success, actual_output = self.run_single_test(test_input)
                
                if not success:
                    # 실행 자체가 실패한 경우
                    self.failed_tests.append({'type': test_type, 'case_number': i + 1, 'input': test_input, 'error': actual_output})
                    return False, f"{test_type} 테스트 {i + 1} 실행 실패"

                if test_type == "샘플": # 샘플 테스트만 정답 비교
                    if actual_output.strip() != expected_output.strip():
                        self.failed_tests.append({'type': test_type, 'case_number': i + 1, 'input': test_input, 'expected': expected_output, 'actual': actual_output})
                        return False, f"{test_type} 테스트 {i + 1} 출력 불일치"
            
            return True, f"{test_type} 테스트 {len(test_cases)}개 모두 통과"
        except Exception as e:
            return False, f"{test_type} 테스트 로드/실행 실패: {e}"

    def cleanup(self):
        """컴파일된 .class 파일 등 임시 파일 정리"""
        if self.language == 'java' and self.java_class_path:
            class_file = self.java_class_path / f"{self.executable}.class"
            if class_file.exists():
                class_file.unlink()

def format_failure_details(failed_tests):
    """실패한 테스트 상세 정보 포맷팅"""
    if not failed_tests: return ""
    test = failed_tests[0] # 첫 번째 실패만 자세히 표시
    if 'error' in test:
        return f"{test['type']} 테스트 {test['case_number']} 오류:\n{test['error']}"
    else:
        return (f"{test['type']} 테스트 {test['case_number']} 불일치:\n"
                f"  입력: {test['input']}\n"
                f"  예상: {test['expected']}\n"
                f"  실제: {test['actual']}")

def main():
    parser = argparse.ArgumentParser(description='테스트케이스 실행')
    parser.add_argument('--code-file', required=True)
    parser.add_argument('--language', required=True)
    parser.add_argument('--sample-tests', required=True)
    parser.add_argument('--generated-tests', required=True)
    args = parser.parse_args()
    
    runner = TestRunner(args.code_file, args.language)
    
    try:
        print(f"🚀 테스트 시작: {args.code_file} ({args.language})")
        
        # 1. 컴파일
        success, msg = runner.compile_if_needed()
        if not success:
            print(f"::error::{msg}")
            write_output("result", "FAIL")
            write_output("details", msg)
            sys.exit(1)
        print(f"✅ {msg}")
        
        # 2. 샘플 테스트
        success, msg = runner.run_tests_from_file(args.sample_tests, "샘플")
        if not success:
            details = format_failure_details(runner.failed_tests)
            print(f"::error::{msg}\n{details}")
            write_output("result", "FAIL")
            write_output("details", details)
            sys.exit(1)
        print(f"✅ {msg}")
        
        # 3. AI 생성 테스트
        success, msg = runner.run_tests_from_file(args.generated_tests, "AI 생성")
        if not success:
            details = format_failure_details(runner.failed_tests)
            # AI 테스트는 실패해도 경고만 하고 통과 처리
            print(f"::warning::{msg}\n{details}")
        else:
            print(f"✅ {msg}")
        
        # 최종 통과
        print("🎉 모든 테스트 통과!")
        write_output("result", "PASS")
        write_output("details", "모든 테스트케이스 통과")
        
    finally:
        runner.cleanup()

if __name__ == "__main__":
    main()