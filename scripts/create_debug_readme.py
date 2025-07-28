#!/usr/bin/env python3
"""
scripts/create_debug_readme.py
GitHub Actions에서 사용할 디버그용 README 생성 스크립트
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path


def get_session_info_from_env():
    """환경변수에서 회차 정보 가져오기"""
    return {
        "session_number": os.environ.get("SESSION_NUMBER", "999"),
        "today": os.environ.get("TODAY", datetime.now().strftime("%Y-%m-%d")),
        "week_start": os.environ.get("WEEK_START", "Unknown"),
        "week_end": os.environ.get("WEEK_END", "Unknown"),
        "deadline": os.environ.get("DEADLINE", "Unknown"),
        "has_session_counter": os.environ.get("HAS_SESSION_COUNTER", "false").lower()
        == "true",
        "total_weeks": os.environ.get("TOTAL_WEEKS", "0"),
        "total_days": os.environ.get("TOTAL_DAYS", "0"),
    }


def create_debug_readme_content(session_info, debug_mode=False):
    """디버그용 README 컨텐츠 생성"""

    # 현재 시간
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")

    # GitHub 정보
    github_event = os.environ.get("GITHUB_EVENT_NAME", "unknown")
    github_actor = os.environ.get("GITHUB_ACTOR", "Unknown")
    github_repo = os.environ.get("GITHUB_REPOSITORY", "Unknown/Unknown")

    # 디버그 정보 섹션
    debug_section = ""
    if debug_mode:
        debug_section = f"""
### 🐛 디버그 정보
- **실행 시간**: {current_time}
- **회차**: {session_info['session_number']}회차
- **오늘**: {session_info['today']}
- **주차**: {session_info['week_start']} ~ {session_info['week_end']}
- **트리거**: {github_event}
- **실행자**: {github_actor}
- **Session Counter**: {'사용 가능' if session_info['has_session_counter'] else '사용 불가'}
- **완료 주차**: {session_info['total_weeks']}주
- **총 진행일**: {session_info['total_days']}일

⚠️ **주의**: 이것은 5분마다 실행되는 디버그 모드입니다.
"""

    # 주간 날짜 계산 (간단 버전)
    try:
        from datetime import datetime, timedelta

        monday = datetime.strptime(session_info["week_start"], "%Y-%m-%d")
        week_dates = []
        for i in range(7):
            date = monday + timedelta(days=i)
            week_dates.append(date.strftime("%m/%d"))
    except:
        week_dates = ["01/01", "01/02", "01/03", "01/04", "01/05", "01/06", "01/07"]

    # 모드에 따른 제목
    if debug_mode:
        title_suffix = " (Debug Mode)"
        mode_indicator = "🐛 "
    else:
        title_suffix = ""
        mode_indicator = ""

    content = f"""# 🚀 알고리즘 스터디{title_suffix}

## 📅 {mode_indicator}{session_info['session_number']}회차 현황
**기간**: {session_info['week_start']} ~ {session_info['week_end']}  
**마감**: {session_info['deadline']}

### 제출 현황

| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |
|--------|----|----|----|----|----|----|---|
|        | {week_dates[0]} | {week_dates[1]} | {week_dates[2]} | {week_dates[3]} | {week_dates[4]} | {week_dates[5]} | {week_dates[6]} |
| debug_user | 1000 | 1001 | 1002 |  |  |  |  |

## 🤖 자동화 시스템 소개

### 🔧 주요 기능
- **자동 테스트**: 샘플 테스트케이스 + AI 생성 반례 테스트
- **스마트 채점**: 부분 점수 지원 (샘플만/생성 테스트만 통과)
- **개인 알림**: Mattermost 개인 DM으로 결과 통知
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
MATTERMOST_WEBHOOK_URL=your_default_channel_webhook  # 기본 채널용
본인깃허브아이디_MATTERMOST_URL=your_personal_webhook  # 개인 DM용 (필수)
```

**📱 개인 알림 설정**: 주간 5문제 미달 시 개인 DM 알림을 받으려면 반드시 개인 webhook URL을 설정하세요. 
자세한 설정 방법은 `docs/개인알림_설정가이드.md`를 참고하세요.

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
1. **브랜치 생성**: `git checkout -b week-N-solutions`  
2. **코드 작성**: 위 구조대로 파일 배치
3. **PR 생성**: main 브랜치로 Pull Request
4. **자동 테스트**: GitHub Actions에서 자동 실행
5. **결과 확인**: 개인 DM + PR 댓글로 결과 통知
6. **자동 병합**: 테스트 통과 시 자동 README 업데이트 후 병합

### 🎯 테스트 기준
- **완전 성공**: 샘플 + 생성 테스트 모두 통과
- **부분 성공**: 샘플 또는 생성 테스트 중 하나만 통과  
- **실패**: 모든 테스트 실패
- **PR 승인**: 한 문제 이상 성공 시 자동 승인

### 🚨 주의사항
- Java 11 환경에서 테스트됩니다
- 파일명은 반드시 `Main.java`로 통일
- 패키지 선언 없이 작성해주세요
- 무한루프나 과도한 메모리 사용 시 타임아웃됩니다

### 📞 문의사항
- GitHub Issues 또는 Mattermost 채널에서 문의
- 버그 리포트나 개선 제안 환영합니다!{debug_section}

---
*Auto-updated by GitHub Actions 🤖{" (Debug Mode)" if debug_mode else ""}*
"""

    return content


def try_advanced_readme():
    """고급 README 생성 시도 (scripts가 있는 경우)"""
    try:
        # session_counter와 weekly_reset이 있는지 확인
        session_counter_exists = Path("scripts/session_counter.py").exists()
        weekly_reset_exists = Path("scripts/weekly_reset.py").exists()

        if session_counter_exists and weekly_reset_exists:
            print("📝 고급 README 업데이트 시도...")

            # weekly_reset.py 실행
            import subprocess

            result = subprocess.run(
                [sys.executable, "scripts/weekly_reset.py", "--force", "--verbose"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print("✅ 고급 README 생성 성공")
                return True
            else:
                print(f"⚠️ 고급 README 생성 실패: {result.stderr}")
                return False
        else:
            print("ℹ️ 필요한 scripts 파일이 없음, 기본 README 사용")
            return False

    except Exception as e:
        print(f"⚠️ 고급 README 생성 중 오류: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="디버그용 README 생성")
    parser.add_argument(
        "--debug-mode", action="store_true", help="디버그 모드 (상세 정보 포함)"
    )
    parser.add_argument(
        "--try-advanced", action="store_true", help="고급 README 생성 시도"
    )
    parser.add_argument("--output", default="README.md", help="출력 파일명")

    args = parser.parse_args()

    try:
        # 환경변수에서 회차 정보 가져오기
        session_info = get_session_info_from_env()

        print(f"📝 README 생성 중... (디버그 모드: {args.debug_mode})")
        print(f"   - 회차: {session_info['session_number']}회차")
        print(f"   - 기간: {session_info['week_start']} ~ {session_info['week_end']}")

        # 고급 README 시도 (옵션)
        advanced_success = False
        if args.try_advanced:
            advanced_success = try_advanced_readme()

        # 고급 생성이 실패했거나 시도하지 않은 경우 기본 README 생성
        if not advanced_success:
            print("📝 기본 README 생성 중...")

            # 디버그용 README 컨텐츠 생성
            readme_content = create_debug_readme_content(session_info, args.debug_mode)

            # 파일에 저장
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(readme_content)

            print(f"✅ 기본 README 생성 완료: {args.output}")

        # 생성된 파일 정보 출력
        readme_path = Path(args.output)
        if readme_path.exists():
            line_count = len(readme_path.read_text(encoding="utf-8").splitlines())
            file_size = readme_path.stat().st_size
            print(f"📊 생성된 README 정보:")
            print(f"   - 파일: {args.output}")
            print(f"   - 라인 수: {line_count}")
            print(f"   - 파일 크기: {file_size} bytes")

    except Exception as e:
        print(f"❌ README 생성 실패: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
