# 시스템 아키텍처 패턴

## 핵심 아키텍처

```
GitHub Repository
├── .github/workflows/boj-automation.yaml (GitHub Actions 워크플로우)
├── scripts/
│   ├── deadline_checker.py (개인별 알림 시스템)
│   ├── multi_test_runner.py (자동 테스트)
│   └── update_readme.py (README 업데이트)
└── {username}/
    └── {problem_id}/
        └── Main.java
```

## 주요 시스템 패턴

### 1. 이벤트 기반 자동화

- **PR 이벤트**: 자동 테스트 및 검증
- **Schedule 이벤트**: 정기 알림 (cron 기반)

### 2. 다중 알림 채널

- **개인 DM**: `{USERNAME}_MATTERMOST_URL` 환경변수
- **공통 채널**: `MATTERMOST_WEBHOOK_URL` 환경변수
- **Fallback**: 개인 webhook 없을 시 공통 채널 사용

### 3. 시간 기반 알림 분기

```python
def get_current_reminder_type():
    - friday_morning: 금요일 8-10시
    - sunday_morning: 일요일 8-10시
    - sunday_evening: 일요일 20-22시
    - general: 기타 시간대
```

### 4. 문제 해결 카운팅 로직

- GitHub API 활용: 최근 1주일 병합된 PR 분석
- 파일 패턴 매칭: `{username}/{problem_id}/Main.java`
- 파일 상태 확인: 'added' 또는 'modified'

### 5. 환경변수 패턴

```
GITHUB_TOKEN: GitHub API 인증
GEMINI_API_KEY: AI 테스트 생성
MATTERMOST_WEBHOOK_URL: 기본 채널
{USERNAME}_MATTERMOST_URL: 개인별 채널
```

## 핵심 컴포넌트

### deadline_checker.py 주요 함수

1. `get_participants_from_directory()`: 디렉토리 기반 참가자 추출
2. `get_weekly_problem_count()`: 개인별 주간 문제 해결 수 계산
3. `send_personal_notification()`: 개인별 webhook 알림
4. `create_personal_reminder_message()`: 시간대별 맞춤 메시지
5. `send_summary_notification()`: 전체 요약 알림

### 에러 처리 패턴

- API 호출 실패 시 기본값 반환
- Webhook 실패 시 대체 채널 사용
- 개인 webhook 없을 시 공통 채널 fallback

## 확장성 고려사항

- 새로운 참가자 추가 시 디렉토리만 생성하면 자동 인식
- 새로운 알림 시간대 추가 가능 (cron + 함수 수정)
- 다양한 메시징 플랫폼 지원 가능 (webhook 패턴 활용)
