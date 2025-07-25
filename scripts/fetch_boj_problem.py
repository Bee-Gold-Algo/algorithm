#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
Gemini API의 웹 검색 기능을 활용하여 백준 문제 정보를 수집합니다.
기존 크롤링 방식에서 Gemini API 웹 검색 방식으로 변경됨.
"""

import argparse
import json
import requests
import google.generativeai as genai
import os
import time

def get_solved_ac_info(problem_id):
    """solved.ac API에서 문제의 기본 정보(제목, 레벨, 태그)를 가져옵니다."""
    print("\n📡 solved.ac API에서 정보 조회 중...")
    try:
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            # 한국어 태그 이름을 우선적으로 찾아서 추출합니다.
            tags = []
            for tag_data in data.get("tags", []):
                korean_name = next((d['name'] for d in tag_data.get('displayNames', []) if d['language'] == 'ko'), None)
                if korean_name:
                    tags.append(korean_name)
            
            print(f"  ✅ solved.ac 정보: {data.get('titleKo', '')}, 레벨: {data.get('level', 0)}")
            return {
                "title": data.get("titleKo", f"문제 {problem_id}"),
                "level": data.get("level", "N/A"),
                "tags": tags
            }
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ solved.ac API 호출 오류: {e}")
    except json.JSONDecodeError:
        print("  ⚠️ solved.ac API 응답이 올바른 JSON 형식이 아닙니다.")
    
    # API 호출 실패 시 기본 정보를 반환합니다.
    return {
        "title": f"문제 {problem_id}",
        "level": "N/A",
        "tags": []
    }

def setup_gemini_api():
    """Gemini API를 설정합니다."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    genai.configure(api_key=api_key)
    print("🔑 Gemini API 설정 완료")
    return genai.GenerativeModel('gemini-2.5-flash')

def get_boj_problem_with_gemini(model, problem_id):
    """Gemini API의 웹 검색 기능을 사용하여 백준 문제 정보를 수집합니다."""
    print(f"\n🤖 Gemini API로 문제 {problem_id} 정보 검색 중...")
    
    prompt = f"""
백준 온라인 저지(BOJ) 문제 {problem_id}번에 대한 정보를 검색하여 다음 항목들을 JSON 형식으로 정리해주세요:

1. 문제 설명 (problem_description)
2. 입력 형식 (input_format) 
3. 출력 형식 (output_format)
4. 제한사항 (limits) - 시간 제한, 메모리 제한 등
5. 예제 입출력 (sample_tests) - 배열 형태로, 각각 input과 output 필드 포함
6. 힌트 (hint) - 있는 경우만

검색할 URL: https://www.acmicpc.net/problem/{problem_id}

응답은 반드시 다음과 같은 JSON 형식으로만 해주세요:
{{
    "problem_description": "문제 설명 내용",
    "input_format": "입력 형식 설명",
    "output_format": "출력 형식 설명", 
    "limits": "제한사항 정보",
    "sample_tests": [
        {{"input": "예제 입력 1", "output": "예제 출력 1"}},
        {{"input": "예제 입력 2", "output": "예제 출력 2"}}
    ],
    "hint": "힌트 내용 (있는 경우)"
}}

만약 해당 문제를 찾을 수 없으면 "error": "문제를 찾을 수 없습니다" 형태로 응답해주세요.
"""

    try:
        # Gemini API에서 웹 검색 기능 활성화
        response = model.generate_content(
            prompt,
            tools=['google_search_retrieval'],
            generation_config={
                'temperature': 0.1,  # 일관된 결과를 위해 낮은 temperature 사용
                'max_output_tokens': 8192
            }
        )
        
        print("  ✅ Gemini API 응답 수신 완료")
        return response.text
        
    except Exception as e:
        print(f"  ❌ Gemini API 호출 중 오류 발생: {e}")
        return None

def parse_gemini_response(response_text):
    """Gemini 응답에서 JSON 데이터를 추출합니다."""
    print("  🔍 Gemini 응답 파싱 중...")
    
    if not response_text:
        return None
    
    try:
        # JSON 블록 찾기 (```json ... ``` 형태)
        import re
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
                return None
        
        # JSON 파싱
        problem_data = json.loads(json_text)
        
        # 오류 확인
        if 'error' in problem_data:
            print(f"  ❌ 문제 정보 수집 실패: {problem_data['error']}")
            return None
        
        # 필수 필드 확인
        required_fields = ['problem_description', 'sample_tests']
        for field in required_fields:
            if field not in problem_data or not problem_data[field]:
                print(f"  ⚠️ 필수 필드 '{field}'가 누락되었습니다.")
                return None
        
        print("  ✅ JSON 파싱 완료")
        return problem_data
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 파싱 오류: {e}")
        print(f"  📄 원본 응답: {response_text[:500]}...")
        return None

def convert_to_standard_format(gemini_data):
    """Gemini 응답을 표준 형식으로 변환합니다."""
    print("  🔄 데이터 형식 변환 중...")
    
    standard_format = {}
    
    # 필드 매핑
    field_mapping = {
        'problem_description': 'description',
        'input_format': 'input_format', 
        'output_format': 'output_format',
        'limits': 'limits',
        'hint': 'hint'
    }
    
    for gemini_field, standard_field in field_mapping.items():
        if gemini_field in gemini_data and gemini_data[gemini_field]:
            standard_format[standard_field] = gemini_data[gemini_field]
    
    # 예제 테스트케이스 변환
    if 'sample_tests' in gemini_data and gemini_data['sample_tests']:
        samples = []
        for test in gemini_data['sample_tests']:
            if isinstance(test, dict) and 'input' in test and 'output' in test:
                samples.append({
                    'input': str(test['input']).strip(),
                    'output': str(test['output']).strip()
                })
        standard_format['samples'] = samples
    else:
        standard_format['samples'] = []
    
    print("  ✅ 데이터 형식 변환 완료")
    return standard_format

def get_boj_problem_info_gemini(problem_id, max_retries=3):
    """Gemini API를 사용하여 백준 문제 정보를 수집합니다."""
    print(f"\n🎯 문제 {problem_id} 정보 수집 시작 (Gemini 웹 검색)")
    
    try:
        model = setup_gemini_api()
    except ValueError as e:
        print(f"❌ Gemini API 설정 실패: {e}")
        return None
    
    for attempt in range(1, max_retries + 1):
        print(f"\n  🔄 시도 {attempt}/{max_retries}")
        
        # Gemini로 검색 및 정보 수집
        response_text = get_boj_problem_with_gemini(model, problem_id)
        if not response_text:
            print(f"  ⚠️ 시도 {attempt} 실패")
            if attempt < max_retries:
                time.sleep(2)
            continue
        
        # 응답 파싱
        problem_data = parse_gemini_response(response_text)
        if not problem_data:
            print(f"  ⚠️ 시도 {attempt} 파싱 실패")
            if attempt < max_retries:
                time.sleep(2)
            continue
        
        # 표준 형식으로 변환
        standard_data = convert_to_standard_format(problem_data)
        
        if standard_data and standard_data.get('description'):
            print("  🎉 문제 정보 수집 성공!")
            return standard_data
        
        print(f"  ⚠️ 시도 {attempt} - 유효한 데이터 없음")
        if attempt < max_retries:
            time.sleep(2)
    
    print("💥 모든 시도 실패")
    return None

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Gemini API 웹 검색을 활용한 백준 문제 정보 수집')
    parser.add_argument('--problem-id', required=True, help='수집할 백준 문제의 번호')
    args = parser.parse_args()

    problem_id = args.problem_id
    
    # GEMINI_API_KEY 환경변수 확인
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY 환경변수를 설정해주세요.")
        print("   export GEMINI_API_KEY='your_api_key_here'")
        exit(1)
    
    # solved.ac API로 기본 정보 수집
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # Gemini API로 상세 정보 수집
    boj_details = get_boj_problem_info_gemini(problem_id)

    if not boj_details:
        print(f"\n❌ 문제 {problem_id} 정보 수집 최종 실패")
        exit(1)

    # 최종 정보 조합
    complete_info = { 
        "problem_id": problem_id, 
        **solved_ac_info, 
        **boj_details 
    }

    try:
        # 문제 정보 저장
        with open('problem_info.json', 'w', encoding='utf-8') as f:
            json.dump(complete_info, f, ensure_ascii=False, indent=2)
        
        # 예제 테스트케이스 저장
        sample_tests = { 
            "problem_id": problem_id, 
            "test_cases": complete_info.get('samples', []) 
        }
        with open('sample_tests.json', 'w', encoding='utf-8') as f:
            json.dump(sample_tests, f, ensure_ascii=False, indent=2)

        print("\n" + "="*60)
        print("🎉 Gemini API 웹 검색 방식 정보 수집 완료!")
        print(f"  📝 제목: {complete_info['title']} (레벨: {complete_info['level']})")
        print(f"  🏷️ 태그: {', '.join(complete_info.get('tags', []))}")
        print(f"  📊 추출된 예제: {len(complete_info.get('samples', []))}개")
        print(f"  📄 문제 설명 길이: {len(complete_info.get('description', ''))}자")
        print("  💾 저장된 파일: problem_info.json, sample_tests.json")
        print("="*60)

    except IOError as e:
        print(f"\n❌ 파일 저장 중 오류가 발생했습니다: {e}")
        exit(1)

if __name__ == "__main__":
    main()