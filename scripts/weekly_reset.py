#!/usr/bin/env python3
"""
scripts/weekly_reset.py
주간 README 초기화 스크립트 - 월요일 오전 0시에 새로운 회차로 리셋
"""

import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
import pytz

# session_counter 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from session_counter import get_session_info, is_new_week_start
except ImportError:
    print("⚠️ session_counter 모듈을 찾을 수 없습니다.")
    sys.exit(1)


def is_monday_reset_time():
    """월요일 오전 0시-2시 사이인지 확인 (KST 기준)"""
    kst = pytz.timezone("Asia/Seoul")
    now = datetime.now(kst)
    
    # 월요일(weekday=0)이고 0시-2시 사이
    return now.weekday() == 0 and 0 <= now.hour < 2


def load_readme():
    """현재 README.md 파일 로드"""
    readme_path = Path("README.md")
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def create_new_week_table(week_info):
    """새로운 주차 테이블 생성"""
    monday = datetime.strptime(week_info["monday"], "%Y-%m-%d")
    week_dates = [(monday + timedelta(days=i)).strftime("%m/%d") for i in range(7)]

    header = f"""| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |
|--------|----|----|----|----|----|----|---|
|        | {week_dates[0]} | {week_dates[1]} | {week_dates[2]} | {week_dates[3]} | {week_dates[4]} | {week_dates[5]} | {week_dates[6]} |
| 아직_제출없음 |  |  |  |  |  |  |  |"""

    return header


def create_static_info_section():
    """정적 정보 섹션 생성"""
    return """
## 🤖 자동화 시스템 소개

### 🔧 주요 기능
- **자동 테스트**: 샘플 테스트케이스 + AI 생성 반례 테스트
- **스마트 채점**: 부분 점수 지원 (샘플만/생성 테스트만 통과)
- **개인 알림**: Mattermost 개인 DM으로 결과 알림
- **자동 README 업데이트**: 제출 현황 실시간 반영

### 🧠 사용 기술
- **AI 모델**: Google Gemini 2.5-flash
- **테스트 생성**: 문제 분석 → 반례 자동 생성
- **플랫폼**: GitHub Actions + Python
- **개인 알림**: 사용자별 주간 현황 체크 + 맞춤 알림

### 📝 사용 방법

#### 1. Repository 설정
```bash
# 1. 이 Repository Fork
# 2. 본인 디렉토리 생성: 본인깃허브아이디/문제번호/Main.java
# 3. 코드 작성 후 PR 생성
```

#### 2. 필요한 Secrets 설정
Repository Settings → Secrets and variables → Actions에서 다음 설정:

```
GEMINI_API_KEY=your_gemini_api_key
본인깃허브아이디_MATTERMOST_URL=your_personal_webhook  # 개인 DM용 (필수)
```

**📱 개인 알림 설정**: 주간 5문제 미달 시 개인 DM 알림을 받으려면 반드시 개인 webhook URL을 설정하세요. 

#### 3. 디렉토리 구조
```
본인깃허브아이디/
├── 1000/
│   └── Main.java
├── 1001/
│   └── Main.java
└── 2557/
    └── Main.java
```

#### 4. PR 제출 과정
1. **브랜치 생성**: `git checkout -b week-N-<githubId>`  
2. **코드 작성**: 위 구조대로 파일 배치
3. **PR 생성**: main 브랜치로 Pull Request
4. **자동 테스트**: GitHub Actions에서 자동 실행
5. **결과 확인**: 개인 DM + PR 댓글로 결과 알림
6. **자동 병합**: 테스트 통과 시 자동 README 업데이트 후 병합

### 🎯 테스트 기준
- **완전 성공**: 샘플 + 생성 테스트 모두 통과
- **부분 성공**: 샘플 또는 생성 테스트 중 하나만 통과  
- **실패**: 모든 테스트 실패
- **PR 승인**: 문제 정답 여부와 상관없이 모두 승인

### 🚨 주의사항
- Java 11 환경에서 테스트됩니다
- 파일명은 반드시 `Main.java`로 통일
- 패키지 선언 없이 작성해주세요
- 무한루프나 과도한 메모리 사용 시 타임아웃됩니다

### 📞 문의사항
- GitHub Issues 또는 Mattermost 채널에서 문의
- 버그 리포트나 개선 제안 환영합니다!
"""


def update_footer(readme_content):
    """기존 푸터를 제거하고 새로운 푸터를 추가합니다."""
    # 기존 푸터 제거 (정규식 사용)
    cleaned_content = re.sub(
        r"\n---\n\*Auto-updated by GitHub Actions 🤖.*",
        "",
        readme_content,
        flags=re.DOTALL,
    )

    # 새로운 푸터 추가
    new_footer = "\n\n---\n*Auto-updated by GitHub Actions 🤖 (Weekly Reset)*"
    return cleaned_content.rstrip() + new_footer


def reset_weekly_readme():
    """README.md를 새로운 주차로 초기화"""
    try:
        # 현재 회차 정보 가져오기
        week_info = get_session_info()
        
        print(f"🔄 주간 README 초기화 시작...")
        print(f"   - 회차: {week_info['session_number']}회차")
        print(f"   - 기간: {week_info['monday']} ~ {week_info['sunday']}")
        print(f"   - 마감: {week_info['deadline']}")

        # 새로운 테이블 생성
        new_table = create_new_week_table(week_info)
        static_info = create_static_info_section()

        # 새로운 README 내용 생성
        new_readme_content = f"""# 🚀 알고리즘 스터디

## 📅 {week_info['session_number']}회차 현황
**기간**: {week_info['monday']} ~ {week_info['sunday']}

**마감**: {week_info['deadline']}

### 제출 현황

{new_table}
{static_info}
"""

        # 푸터 추가
        new_readme_content = update_footer(new_readme_content)

        # README.md 파일 업데이트
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme_content)

        print("✅ README.md 주간 초기화 완료!")
        return True

    except Exception as e:
        print(f"❌ README.md 주간 초기화 실패: {e}")
        return False


def should_perform_reset():
    """리셋을 수행해야 하는지 확인"""
    # 강제 모드 체크
    if os.getenv("FORCE_WEEKLY_RESET") == "true":
        print("🔧 강제 모드: 주간 리셋을 강제로 실행합니다.")
        return True
    
    # 월요일 새벽 시간 체크
    if not is_monday_reset_time():
        kst = pytz.timezone("Asia/Seoul")
        now = datetime.now(kst)
        print(f"⏰ 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')} KST")
        print("⚠️ 월요일 오전 0-2시가 아니므로 리셋을 건너뜁니다.")
        return False
    
    # 새로운 주차 시작인지 체크
    if not is_new_week_start():
        print("⚠️ 새로운 주차 시작일이 아니므로 리셋을 건너뜁니다.")
        return False
    
    return True


def main():
    """메인 실행 함수"""
    print("🤖 주간 README 초기화 스크립트 시작...")
    
    # 디버깅 정보 출력
    kst = pytz.timezone("Asia/Seoul")
    now = datetime.now(kst)
    print(f"🕐 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')} KST")
    print(f"📅 요일: {['월', '화', '수', '목', '금', '토', '일'][now.weekday()]}")
    
    # 리셋 조건 확인
    if not should_perform_reset():
        print("🚫 리셋 조건을 만족하지 않아 종료합니다.")
        return
    
    print("✅ 리셋 조건을 만족합니다. 주간 초기화를 진행합니다.")
    
    # README 초기화 실행
    if reset_weekly_readme():
        print("🎉 주간 README 초기화가 성공적으로 완료되었습니다!")
    else:
        print("❌ 주간 README 초기화에 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
