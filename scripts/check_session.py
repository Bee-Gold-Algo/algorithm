#!/usr/bin/env python3
"""
scripts/check_session.py
GitHub Actions에서 사용할 회차 정보 체크 스크립트
"""

import os
import sys
from datetime import datetime, timedelta


def main():
    """회차 정보 체크 및 환경변수 출력"""
    try:
        # session_counter 모듈 import 시도
        try:
            from session_counter import (
                is_new_week_start,
                get_session_info,
                get_session_statistics,
            )

            has_session_counter = True
        except ImportError:
            print(
                "⚠️ session_counter 모듈을 찾을 수 없습니다. 기본값을 사용합니다.",
                file=sys.stderr,
            )
            has_session_counter = False

        # 현재 날짜
        today = datetime.now().strftime("%Y-%m-%d")

        if has_session_counter:
            try:
                # 정상적인 회차 정보 조회
                session_info = get_session_info()
                is_new = is_new_week_start(today)

                # 디버그 모드에서는 강제로 새 주차로 설정
                debug_mode = os.environ.get("DEBUG_MODE", "false").lower() == "true"
                if debug_mode:
                    is_new = True
                    print("🐛 디버그 모드: 강제로 새 주차로 설정", file=sys.stderr)

                # 환경변수 형태로 출력
                print(f"IS_NEW_WEEK={str(is_new).lower()}")
                print(f"SESSION_NUMBER={session_info['session_number']}")
                print(f"TODAY={today}")
                print(f"WEEK_START={session_info['monday']}")
                print(f"WEEK_END={session_info['sunday']}")
                print(f"DEADLINE={session_info['deadline']}")
                print(f"HAS_SESSION_COUNTER=true")

                # 통계 정보도 가져오기 (선택적)
                try:
                    stats = get_session_statistics()
                    print(f"TOTAL_WEEKS={stats['total_weeks_completed']}")
                    print(f"TOTAL_DAYS={stats['total_study_days']}")
                    print(f"STUDY_START={stats['study_start_date']}")
                except Exception as e:
                    print(f"⚠️ 통계 정보 조회 실패: {e}", file=sys.stderr)

                if is_new:
                    print("✅ 새로운 주차 시작일입니다!", file=sys.stderr)
                else:
                    print("ℹ️ 새로운 주차 시작일이 아닙니다.", file=sys.stderr)

            except Exception as e:
                print(f"❌ 회차 정보 조회 실패: {e}", file=sys.stderr)
                raise

        else:
            # session_counter가 없을 때의 폴백 로직
            print("🔄 기본값으로 회차 정보 생성 중...", file=sys.stderr)

            today_dt = datetime.now()
            week_end = today_dt + timedelta(days=6)

            # 디버그 모드나 강제 실행인 경우
            force_reset = os.environ.get("FORCE_RESET", "false").lower() == "true"
            debug_mode = os.environ.get("DEBUG_MODE", "false").lower() == "true"

            print(f"IS_NEW_WEEK={str(force_reset or debug_mode).lower()}")
            print(f"SESSION_NUMBER=999")  # 디버그용 회차 번호
            print(f"TODAY={today}")
            print(f"WEEK_START={today}")
            print(f"WEEK_END={week_end.strftime('%Y-%m-%d')}")
            print(f"DEADLINE={week_end.strftime('%Y-%m-%d 23:59')}")
            print(f"HAS_SESSION_COUNTER=false")
            print(f"TOTAL_WEEKS=0")
            print(f"TOTAL_DAYS=0")
            print(f"STUDY_START={today}")

    except Exception as e:
        print(f"❌ 치명적 오류: {e}", file=sys.stderr)
        # 최소한의 환경변수라도 출력
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"IS_NEW_WEEK=false")
        print(f"SESSION_NUMBER=1")
        print(f"TODAY={today}")
        print(f"WEEK_START={today}")
        print(f"WEEK_END={today}")
        print(f"DEADLINE={today} 23:59")
        print(f"HAS_SESSION_COUNTER=false")
        print(f"ERROR=true")
        sys.exit(1)


if __name__ == "__main__":
    main()
