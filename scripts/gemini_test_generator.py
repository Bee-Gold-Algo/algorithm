#!/usr/bin/env python3
"""
scripts/gemini_test_generator.py
Gemini API를 사용해 반례 테스트케이스를 생성합니다.
"""

import argparse
import json
import re
import os
import google.generativeai as genai
from pathlib import Path

def load_problem_info(problem_info_file):
    """문제 정보 JSON 로드"""
    try:
        with open(problem_info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"문제 정보 로드 실패: {e}")
        return {}

def load_code(code_file):
    """제출된 코드 로드"""
    try:
        with open(code_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"코드 파일 로드 실패: {e}")
        return ""

def create_gemini_prompt(problem_info, code, language):
    """Gemini API용 프롬프트 생성"""
    
    samples_text = ""
    if problem_info.get('samples'):
        samples_text = "\n".join([
            f"예제 {i+1}:\n입력: {sample.get('input', '')}\n출력: {sample.get('output', '')}"
            for i, sample in enumerate(problem_info['samples'][:3])
        ])
    
    prompt = f"""
백준 온라인 저지 문제의 코드를 분석하고 반례를 찾아주세요.

【문제 정보】
- 번호: {problem_info.get('problem_id', 'Unknown')}
- 제목: {problem_info.get('title', 'Unknown')}
- 난이도: {problem_info.get('level', 0)}
- 태그: {', '.join(problem_info.get('tags', [])[:5])}

【문제 설명】
{problem_info.get('description', '(설명 없음)')}

【입력 형식】
{problem_info.get('input_format', '(설명 없음)')}

【출력 형식】
{problem_info.get('output_format', '(설명 없음)')}

【예제】
{samples_text if samples_text else '(예제 없음)'}

【제출된 코드】
언어: {language}
```{language}
{code}
```

【분석 요청】
이 코드를 면밀히 분석하여 다음과 같은 반례를 찾아주세요:
1. **경계값 테스트**: 최솟값, 최댓값, 0 등
2. **특수 케이스**: 빈 입력, 음수, 중복값 등
3. **알고리즘 오류**: 로직 실수를 유발할 수 있는 케이스

【출력 형식】
반드시 다음 JSON 형태로만 응답해주세요:
{{
  "analysis": "코드 분석 결과 (간단히)",
  "test_cases": [
    {{
      "input": "실제 테스트 입력값",
      "expected_output": "예상되는 정답",
      "test_type": "경계값|특수케이스|알고리즘오류",
      "description": "이 테스트케이스가 찾으려는 오류에 대한 설명"
    }}
  ]
}}

중요:
- 문제의 입력 형식을 정확히 따라주세요
- 최대 3개의 테스트케이스만 생성해주세요
- 실제 실행 가능한 입력값을 제공해주세요
- JSON 형식을 정확히 지켜주세요
"""
    return prompt

def parse_gemini_response(response_text):
    """Gemini 응답에서 JSON 추출 및 파싱"""
    try:
        if not response_text or not response_text.strip():
            raise ValueError("API 응답이 비어있습니다.")
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("응답에서 JSON을 찾을 수 없습니다")
            json_text = json_match.group(0)
        
        return json.loads(json_text)
    
    except Exception as e:
        print(f"Gemini 응답 파싱 실패: {e}")
        print(f"원문: {response_text[:500]}...")
        return None

def validate_test_cases(test_cases):
    """생성된 테스트케이스 검증 (None 값 처리 강화)"""
    validated = []
    if not isinstance(test_cases, list):
        print("⚠️  'test_cases' 필드가 리스트 형식이 아닙니다.")
        return []

    for i, case in enumerate(test_cases):
        try:
            if not isinstance(case, dict):
                print(f"⚠️  테스트케이스 {i+1}: 딕셔너리 형식이 아닙니다.")
                continue

            # 'input' 키가 없거나, 값이 None이거나, 문자열로 변환했을 때 비어있는 경우를 모두 처리
            test_input = case.get('input')
            if test_input is None or not str(test_input).strip():
                print(f"⚠️  테스트케이스 {i+1}: 유효한 'input' 값이 없습니다.")
                continue
            
            # expected_output은 없어도 되므로 검증 완화
            if 'expected_output' not in case:
                case['expected_output'] = "" # 기본값 설정

            validated.append(case)
            
        except Exception as e:
            print(f"⚠️  테스트케이스 {i+1} 검증 실패: {e}")
    
    return validated

def main():
    parser = argparse.ArgumentParser(description='Gemini로 테스트케이스 생성')
    parser.add_argument('--problem-id', required=True)
    parser.add_argument('--code-file', required=True)
    parser.add_argument('--language', required=True)
    parser.add_argument('--problem-info', required=True)
    args = parser.parse_args()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("::error::GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        return
    
    print(f"🤖 Gemini로 문제 {args.problem_id} 반례 생성 중...")
    
    problem_info = load_problem_info(args.problem_info)
    code = load_code(args.code_file)
    
    if not code:
        print("::error::코드를 로드할 수 없습니다.")
        return
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = create_gemini_prompt(problem_info, code, args.language)
        response = model.generate_content(prompt)
        
        response_text = response.text if hasattr(response, 'text') else ''
        parsed_response = parse_gemini_response(response_text)
        
        validated_cases = []
        analysis_text = "AI 분석 실패"
        if parsed_response and isinstance(parsed_response.get('test_cases'), list):
            validated_cases = validate_test_cases(parsed_response['test_cases'])
            analysis_text = parsed_response.get('analysis', '분석 내용 없음')

        generated_tests = {
            "problem_id": args.problem_id,
            "analysis": analysis_text,
            "test_cases": validated_cases
        }
        
        with open('generated_tests.json', 'w', encoding='utf-8') as f:
            json.dump(generated_tests, f, ensure_ascii=False, indent=2)
        
        print(f"✅ AI 테스트케이스 생성 완료: {len(validated_cases)}개")
        for i, case in enumerate(validated_cases):
            print(f"  {i+1}. {case.get('test_type', 'Unknown')}: {case.get('description', '')[:50]}...")
    
    except Exception as e:
        print(f"::error::Gemini API 호출 실패: {e}")
        with open('generated_tests.json', 'w', encoding='utf-8') as f:
            json.dump({"problem_id": args.problem_id, "analysis": f"API 오류: {str(e)}", "test_cases": []}, f)

if __name__ == "__main__":
    main()
