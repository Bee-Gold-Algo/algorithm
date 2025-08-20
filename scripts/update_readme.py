import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# session_counter 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_readme():
    """기존 README.md 로드 또는 초기 템플릿 생성"""
    readme_path = Path("README.md")
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return create_initial_readme()


def get_week_info(submission_date=None):
    """현재 회차 정보 계산"""
    try:
        from session_counter import get_session_info

        return get_session_info(submission_date)
    except ImportError:
        print("⚠️ session_counter 모듈을 찾을 수 없어 기본값을 사용합니다.")
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return {
            "session_number": 1,
            "monday": start_of_week.strftime("%Y-%m-%d"),
            "sunday": end_of_week.strftime("%Y-%m-%d"),
            "deadline": end_of_week.strftime("%Y-%m-%d 23:59"),
        }


def create_initial_readme():
    """초기 README.md 템플릿 생성"""
    week_info = get_week_info()
    table = create_participant_table({}, week_info)  # 빈 참가자 목록으로 테이블 생성
    static_info = create_static_info_section()

    readme_content = f"""# 🚀 알고리즘 스터디

## 📅 {week_info['session_number']}회차 현황
**기간**: {week_info['monday']} ~ {week_info['sunday']}
**마감**: {week_info['deadline']}

### 제출 현황

{table}
{static_info}
"""
    return update_footer(readme_content)


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


def parse_current_week_stats(readme_content, current_week_info):
    """README에서 현재 주차의 제출 현황을 파싱"""
    stats = {"participants": {}}
    week_pattern = rf"## 📅 {current_week_info['session_number']}회차 현황"
    if not re.search(week_pattern, readme_content):
        return {"participants": {}, "need_reset": True}

    table_content_match = re.search(
        r"### 제출 현황\n\n(.*?)(\n##|$)", readme_content, re.DOTALL
    )
    if not table_content_match:
        return stats

    table_content = table_content_match.group(1)
    lines = table_content.strip().split("\n")

    for line in lines:
        if (
            line.startswith("|")
            and not line.startswith("| 참가자")
            and not line.startswith("|---")
            and "아직_제출없음" not in line
        ):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 8 and parts[0]:
                participant = parts[0]
                weekdays = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]
                participant_data = {day: [] for day in weekdays}
                for i, day in enumerate(weekdays):
                    if i + 1 < len(parts) and parts[i + 1]:
                        problems = [
                            p.strip()
                            for p in parts[i + 1].replace("...", "").split(",")
                            if p.strip().isdigit()
                        ]
                        participant_data[day] = problems
                stats["participants"][participant] = participant_data
    return stats


def get_weekday_from_date(date_str):
    """날짜 문자열에서 요일 인덱스 반환 (월=0, 일=6)"""
    return datetime.strptime(date_str, "%Y-%m-%d").weekday()


def create_participant_table(participants, week_info):
    """참가자 현황 테이블 마크다운 생성"""
    monday = datetime.strptime(week_info["monday"], "%Y-%m-%d")
    week_dates = [(monday + timedelta(days=i)).strftime("%m/%d") for i in range(7)]

    header = f"""| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |
|--------|----|----|----|----|----|----|---|
|        | {week_dates[0]} | {week_dates[1]} | {week_dates[2]} | {week_dates[3]} | {week_dates[4]} | {week_dates[5]} | {week_dates[6]} |"""

    rows = []
    if not participants:
        rows.append("| 아직_제출없음 |  |  |  |  |  |  |  |")
    else:
        weekdays = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for name in sorted(participants.keys()):
            data = participants[name]
            row_parts = [name]
            for day in weekdays:
                problems = sorted(data.get(day, []), key=int)
                if not problems:
                    row_parts.append("")
                elif len(problems) > 3:
                    row_parts.append(", ".join(problems[:3]) + "...")
                else:
                    row_parts.append(", ".join(problems))
            rows.append("| " + " | ".join(row_parts) + " |")

    return header + "\n" + "\n".join(rows)


def remove_problem_from_all_days(participant_data, problem_id):
    """참가자의 모든 요일에서 특정 문제를 제거합니다."""
    weekdays = [
        "monday",
        "tuesday", 
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    
    removed_from_days = []
    for day in weekdays:
        if problem_id in participant_data[day]:
            participant_data[day].remove(problem_id)
            removed_from_days.append(day)
    
    return removed_from_days


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
    new_footer = "\n\n---\n*Auto-updated by GitHub Actions 🤖 (PR 브랜치에서 main 브랜치 데이터 반영)*"
    return cleaned_content.rstrip() + new_footer


def main():
    parser = argparse.ArgumentParser(description="README.md 업데이트")
    parser.add_argument("--problem-id", required=True, help="문제 번호")
    parser.add_argument("--author", required=True, help="제출자")
    parser.add_argument("--submission-date", required=True, help="제출 날짜 (YYYY-MM-DD)")
    parser.add_argument("--language", required=True, help="프로그래밍 언어")
    args = parser.parse_args()

    try:
        # 입력 검증
        submission_date = datetime.strptime(args.submission_date, "%Y-%m-%d")
        print(f"🔄 README 업데이트 시작: {args.author} - 문제 {args.problem_id} ({args.submission_date})")
        
    except ValueError:
        print(f"❌ 잘못된 날짜 형식: {args.submission_date}. YYYY-MM-DD 형식이어야 합니다.")
        sys.exit(1)

    readme_content = load_readme()
    current_week = get_week_info(args.submission_date)

    # 현재 README 파싱
    stats = parse_current_week_stats(readme_content, current_week)
    participants = stats.get("participants", {})

    # 새 제출 정보 추가/업데이트
    weekday_name = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ][get_weekday_from_date(args.submission_date)]
    
    participant_data = participants.get(
        args.author,
        {
            day: []
            for day in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
        },
    )

    # 중복 제거: 기존의 모든 날짜에서 이 문제를 제거
    removed_from_days = remove_problem_from_all_days(participant_data, args.problem_id)
    if removed_from_days:
        print(f"  🔄 문제 {args.problem_id} 기존 제출 제거됨: {', '.join(removed_from_days)}")

    # 새로운 날짜에 문제 추가
    if args.problem_id not in participant_data[weekday_name]:
        participant_data[weekday_name].append(args.problem_id)
        print(f"  ✅ 문제 {args.problem_id}를 {weekday_name}에 추가")
    else:
        print(f"  ℹ️ 문제 {args.problem_id}가 이미 {weekday_name}에 존재함")

    participants[args.author] = participant_data

    # 새 테이블 생성
    new_table = create_participant_table(participants, current_week)

    # README 내용에서 테이블 부분만 교체
    # 주차 정보가 다르면 전체 README 재생성
    week_pattern = rf"## 📅 {current_week['session_number']}회차 현황"
    if not re.search(week_pattern, readme_content):
        print(f"  🔄 새로운 주차({current_week['session_number']})로 README 전체 재생성")
        static_info = create_static_info_section()
        new_readme = f"""# 🚀 알고리즘 스터디

## 📅 {current_week['session_number']}회차 현황
**기간**: {current_week['monday']} ~ {current_week['sunday']}
**마감**: {current_week['deadline']}

### 제출 현황

{new_table}
{static_info}
"""
    else:
        # 기존 주차의 테이블만 업데이트
        new_readme = re.sub(
            r"(### 제출 현황\n\n)(.*?)(\n##|$)",
            f"\\1{new_table}\\3",
            readme_content,
            flags=re.DOTALL,
        )

    # 푸터 업데이트
    new_readme = update_footer(new_readme)

    # README 파일 저장
    try:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme)
        print(f"✅ README.md 업데이트 완료: {args.author} - 문제 {args.problem_id} ({args.submission_date})")
        
    except Exception as e:
        print(f"❌ README.md 저장 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()