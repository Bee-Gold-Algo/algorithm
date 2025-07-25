#!/usr/bin/env python3
"""
scripts/gemini_test_generator.py
최신 Gemini 2.5-flash API를 사용하여 백준 문제의 반례 테스트케이스를 생성합니다.
"""

import argparse
import json
import os
import sys

def setup_gemini_client():
    """최신 Gemini API 클라이언트를 설정합니다."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    try:
        from google import genai
        from google.genai import types
        
        # 클라이언트 설정 (공식 문서 방식)
        client = genai.Client(api_key=api_key)
        
        print("🔑 최신 Gemini 2.5-flash API 클라이언트 설정 완료")
        return client, types
        
    except ImportError as e:
        print(f"❌ google-genai 라이브러리가 필요합니다: {e}")
        print("   pip install google-genai")
        raise
    except Exception as e:
        print(f"❌ Gemini 클라이언트 설정 실패: {e}")
        raise

def generate_test_cases(client, types, problem_info, code_content, language):
    """최신 Gemini 2.5-flash API를 사용하여 테스트케이스를 생성합니다."""
    
    print(f"🤖 Gemini 2.5-flash로 {language} 코드의 반례 테스트케이스 생성 중...")
    
    # 샘플 테스트케이스 정보 포함
    sample_info = ""
    if problem_info.get('samples'):
        sample_info = f"\n**기존 샘플 테스트케이스:**\n{json.dumps(problem_info.get('samples'), ensure_ascii=False, indent=2)}"
    
    prompt = f"""
다음은 백준 온라인 저지 문제입니다:

**문제 설명:**
{problem_info.get('description', 'N/A')}

**입력 형식:**
{problem_info.get('input_format', 'N/A')}

**출력 형식:**
{problem_info.get('output_format', 'N/A')}

**제한사항:**
{problem_info.get('limits', 'N/A')}
{sample_info}

**제출된 코드 ({language}):**
```{language.lower()}
{code_content}
```

이 코드가 틀릴 수 있는 반례 테스트케이스를 생성해주세요.
특히 다음과 같은 경우들을 고려해주세요:

1. **경계값 테스트**: 최소값, 최대값, 0, 음수, 빈 입력
2. **일반적인 실수 패턴**: 
   - 오버플로우/언더플로우
   - 배열 인덱스 오류
   - 반복문 조건 실수
   - 자료형 변환 오류
   - 예외 처리 부족
3. **특수 케이스**: 
   - 단일 원소
   - 모든 원소가 같은 경우
   - 정렬된/역정렬된 입력
   - 중복값 처리

가능하면 5-8개의 다양한 테스트케이스를 생성해주세요.

응답은 다음 JSON 형식으로만 해주세요:
{{
    "test_cases": [
        {{
            "input": "테스트 입력", 
            "output": "예상 출력", 
            "description": "이 테스트케이스가 검증하는 내용"
        }}
    ]
}}
"""

    try:
        # 생성 설정 구성 (공식 문서 방식)
        config = types.GenerateContentConfig(
            temperature=0.7,  # 창의적인 테스트케이스 생성을 위해 약간 높게 설정
            max_output_tokens=4096
        )
        
        print("  🔧 API 요청 실행 중...")
        
        # 요청 실행 (공식 문서 방식)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        
        print("  ✅ Gemini 2.5-flash 응답 수신 완료")
        
        # 응답 텍스트 추출 (공식 문서 방식)
        if hasattr(response, 'text') and response.text:
            print(f"  ✅ 응답 텍스트 추출 완료: {len(response.text)}자")
            return response.text
        else:
            print("  ❌ 응답에서 텍스트를 찾을 수 없습니다.")
            return None
        
    except Exception as e:
        print(f"  ❌ 테스트케이스 생성 중 오류 발생: {e}")
        import traceback
        print(f"  🔍 상세 오류: {traceback.format_exc()}")
        return None

def parse_test_cases(response_text):
    """생성된 응답에서 테스트케이스를 파싱합니다."""
    print("  🔍 테스트케이스 응답 파싱 중...")
    
    if not response_text:
        return []
    
    try:
        import re
        
        # JSON 블록 찾기 (```json ... ``` 형태)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            # JSON 블록이 없으면 전체 텍스트에서 JSON 찾기
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                print("  ⚠️ JSON 형식을 찾을 수 없습니다.")
                print(f"  📄 원본 응답: {response_text[:500]}...")
                return []
        
        # JSON 파싱
        data = json.loads(json_text)
        
        if 'test_cases' in data and isinstance(data['test_cases'], list):
            test_cases = data['test_cases']
            
            # 테스트케이스 유효성 검증
            valid_cases = []
            for i, test in enumerate(test_cases):
                if isinstance(test, dict) and 'input' in test and 'output' in test:
                    # 기본값 설정
                    clean_test = {
                        'input': str(test['input']).strip(),
                        'output': str(test['output']).strip(),
                        'description': test.get('description', f'테스트케이스 {i+1}')
                    }
                    valid_cases.append(clean_test)
                else:
                    print(f"  ⚠️ 테스트케이스 {i+1} 형식 오류, 건너뜀")
            
            print(f"  ✅ {len(valid_cases)}개의 유효한 테스트케이스 파싱 완료")
            return valid_cases
        else:
            print("  ⚠️ test_cases 필드를 찾을 수 없거나 배열이 아닙니다.")
            return []
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 파싱 오류: {e}")
        print(f"  📄 원본 응답: {response_text[:500]}...")
        return []
    except Exception as e:
        print(f"  ❌ 테스트케이스 파싱 중 예상치 못한 오류: {e}")
        return []

def validate_test_cases(test_cases, problem_info):
    """생성된 테스트케이스의 품질을 검증합니다."""
    print("  🔍 테스트케이스 품질 검증 중...")
    
    if not test_cases:
        print("  ⚠️ 생성된 테스트케이스가 없습니다.")
        return test_cases
    
    # 기본 검증
    validated_cases = []
    for i, test in enumerate(test_cases):
        try:
            # 입력과 출력이 모두 있는지 확인
            if not test.get('input') or not test.get('output'):
                print(f"  ⚠️ 테스트케이스 {i+1}: 입력 또는 출력이 비어있음")
                continue
            
            # 입력과 출력이 너무 길지 않은지 확인 (1MB 제한)
            if len(test['input']) > 1000000 or len(test['output']) > 1000000:
                print(f"  ⚠️ 테스트케이스 {i+1}: 데이터가 너무 큼")
                continue
            
            validated_cases.append(test)
            
        except Exception as e:
            print(f"  ⚠️ 테스트케이스 {i+1} 검증 중 오류: {e}")
            continue
    
    print(f"  ✅ {len(validated_cases)}개의 테스트케이스가 검증을 통과했습니다.")
    return validated_cases

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Gemini 2.5-flash API를 사용한 반례 테스트케이스 생성')
    parser.add_argument('--problem-id', required=True, help='문제 번호')
    parser.add_argument('--code-file', required=True, help='코드 파일 경로')
    parser.add_argument('--language', required=True, help='프로그래밍 언어')
    parser.add_argument('--problem-info', required=True, help='문제 정보 JSON 파일 경로')
    args = parser.parse_args()

    print(f"\n🎯 문제 {args.problem_id}의 반례 테스트케이스 생성 시작")
    
    # GEMINI_API_KEY 환경변수 확인
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY 환경변수를 설정해주세요.")
        print("   export GEMINI_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    # 문제 정보 로드
    try:
        with open(args.problem_info, 'r', encoding='utf-8') as f:
            problem_info = json.load(f)
        print(f"✅ 문제 정보 로드 완료: {problem_info.get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ 문제 정보 파일 로드 실패: {e}")
        sys.exit(1)
    
    # 코드 파일 로드
    try:
        with open(args.code_file, 'r', encoding='utf-8') as f:
            code_content = f.read()
        print(f"✅ 코드 파일 로드 완료: {len(code_content)}자")
    except Exception as e:
        print(f"❌ 코드 파일 로드 실패: {e}")
        sys.exit(1)
    
    try:
        # Gemini 클라이언트 설정
        client, types = setup_gemini_client()
        
        # 테스트케이스 생성
        response_text = generate_test_cases(client, types, problem_info, code_content, args.language)
        
        if not response_text:
            print("❌ 테스트케이스 생성 실패")
            sys.exit(1)
        
        # 테스트케이스 파싱
        test_cases = parse_test_cases(response_text)
        
        # 테스트케이스 품질 검증
        validated_cases = validate_test_cases(test_cases, problem_info)
        
        if not validated_cases:
            print("⚠️ 생성된 유효한 테스트케이스가 없습니다.")
            validated_cases = []
        
        # 결과 저장
        result = {
            "problem_id": args.problem_id,
            "test_cases": validated_cases,
            "generated_by": "gemini-2.5-flash",
            "language": args.language,
            "total_generated": len(validated_cases)
        }
        
        with open('generated_tests.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print("🎉 테스트케이스 생성 완료!")
        print(f"  📊 생성된 테스트케이스: {len(validated_cases)}개")
        print(f"  💾 저장된 파일: generated_tests.json")
        print(f"  🤖 생성 모델: Gemini 2.5-flash")
        
        # 생성된 테스트케이스 요약 출력
        if validated_cases:
            print(f"\n📋 생성된 테스트케이스 요약:")
            for i, test in enumerate(validated_cases[:3], 1):  # 처음 3개만 출력
                description = test.get('description', '설명 없음')
                print(f"  {i}. {description}")
            if len(validated_cases) > 3:
                print(f"  ... (총 {len(validated_cases)}개)")
        
        print("="*50)
        
    except Exception as e:
        print(f"❌ 테스트케이스 생성 과정에서 오류 발생: {e}")
        import traceback
        print(f"🔍 상세 오류:\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()