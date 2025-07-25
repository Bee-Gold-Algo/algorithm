#!/usr/bin/env python3
"""
scripts/fallback_search.py
Gemini 검색 실패 시 대안 검색 (solved.ac API 사용)
"""

import argparse
import json
import requests
import sys

def search_problem_info(problem_id):
    """solved.ac API를 사용하여 문제 정보를 검색합니다."""
    try:
        # solved.ac API 호출
        url = f'https://solved.ac/api/v3/problem/show?problemId={problem_id}'
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # 태그 정보 추출
            tags = []
            for tag_data in data.get('tags', []):
                korean_name = None
                for display_name in tag_data.get('displayNames', []):
                    if display_name['language'] == 'ko':
                        korean_name = display_name['name']
                        break
                if korean_name:
                    tags.append(korean_name)
            
            # 문제 정보 구성
            problem_info = {
                'problem_id': problem_id,
                'title': data.get('titleKo', f'문제 {problem_id}'),
                'level': data.get('level', 'N/A'),
                'tags': tags,
                'description': f'Gemini 검색 실패로 인해 상세한 문제 설명을 가져올 수 없습니다.\nhttps://www.acmicpc.net/problem/{problem_id} 에서 직접 확인해주세요.',
                'input_format': '입력 형식을 직접 확인해주세요.',
                'output_format': '출력 형식을 직접 확인해주세요.',
                'limits': {
                    'time': '시간 제한을 직접 확인해주세요.',
                    'memory': '메모리 제한을 직접 확인해주세요.'
                },
                'hint': '',
                'samples': [],
                'source': 'solved.ac_fallback'
            }
            
            return problem_info
            
        else:
            raise Exception(f'solved.ac API 응답 오류: {response.status_code}')
            
    except Exception as e:
        print(f"⚠️ solved.ac API 검색 실패: {e}")
        
        # 최소한의 정보라도 제공
        return {
            'problem_id': problem_id,
            'title': f'문제 {problem_id}',
            'level': 'N/A',
            'tags': [],
            'description': f'API 검색 실패로 인해 문제 설명을 가져올 수 없습니다.\nhttps://www.acmicpc.net/problem/{problem_id} 에서 직접 확인해주세요.',
            'input_format': '입력 형식을 직접 확인해주세요.',
            'output_format': '출력 형식을 직접 확인해주세요.',
            'limits': {
                'time': '시간 제한을 직접 확인해주세요.',
                'memory': '메모리 제한을 직접 확인해주세요.'
            },
            'hint': '',
            'samples': [],
            'source': 'minimal_fallback'
        }

def generate_empty_sample_tests(problem_id):
    """빈 샘플 테스트 파일을 생성합니다."""
    return {
        'problem_id': problem_id,
        'test_cases': [],
        'source': 'fallback_empty'
    }

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='대안 문제 검색')
    parser.add_argument('--problem-id', required=True, help='문제 ID')
    parser.add_argument('--output', required=True, help='출력 파일명')
    args = parser.parse_args()
    
    print(f"🛠️ 대안 검색 시작: 문제 {args.problem_id}")
    
    # 문제 정보 검색
    problem_info = search_problem_info(args.problem_id)
    
    # 문제 정보 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(problem_info, f, ensure_ascii=False, indent=2)
    
    # 빈 샘플 테스트 파일 생성
    sample_tests = generate_empty_sample_tests(args.problem_id)
    sample_filename = f'sample_{args.problem_id}_tests.json'
    
    with open(sample_filename, 'w', encoding='utf-8') as f:
        json.dump(sample_tests, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 대안 검색 완료")
    print(f"   - 문제 정보: {args.output}")
    print(f"   - 샘플 테스트: {sample_filename}")
    print(f"   - 소스: {problem_info['source']}")

if __name__ == "__main__":
    main()