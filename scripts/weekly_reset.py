#!/usr/bin/env python3
"""
scripts/weekly_reset.py
매주 월요일 새로운 회차로 README.md를 초기화합니다. (개선된 버전)
"""

import argparse
from datetime import datetime
from pathlib import Path
import sys
import os


def main():
    """새로운 주차 시작 시 README.md 초기화"""
    try:
        # session_counter 모듈 경로 추가
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        sys.path.insert(0, parent_dir)
        sys.path.insert(0, script_dir)

        from session_counter import (
            get_session_info,
            is_new_week_start,
            get_session_statistics,
        )

        # 오늘이 새로운 주차 시작일인지 확인
        today = datetime.now().strftime("%Y-%m-%d")
        if not is_new_week_start(today):
            print(f"ℹ️ 오늘({today})은 새로운 주차 시작일이 아닙니다.")
            if not args.force:
                print("   --force 옵션을 사용하여 강제 실행할 수 있습니다.")
                return
            else:
                print("   --force 옵션으로 강제 실행합니다.")

        # 현재 회차 정보 가져오기
        current_session = get_session_info()
        print(f"🔄 새로운 {current_session['session_number']}회차 시작!")
        print(f"📅 기간: {current_session['monday']} ~ {current_session['sunday']}")
        print(f"⏰ 마감: {current_session['deadline']}")

        # update_readme.py의 함수들을 import
        try:
            from update_readme import create_initial_readme, update_last_updated
        except ImportError:
            print("❌ update_readme.py 모듈을 찾을 수 없습니다.")
            print("   scripts/update_readme.py 파일이 존재하는지 확인하세요.")
            sys.exit(1)

        # 기존 README 백업 (필요시)
        readme_path = Path("README.md")
        if readme_path.exists() and not args.no_backup:
            backup_path = Path(
                f'README_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            )
            try:
                with open(readme_path, "r", encoding="utf-8") as src:
                    with open(backup_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                print(f"📁 기존 README 백업 완료: {backup_path}")
            except Exception as e:
                print(f"⚠️ README 백업 실패: {e}")

        # 새로운 README 생성
        print("📝 새로운 README.md 생성 중...")
        new_readme = create_initial_readme()
        new_readme = update_last_updated(new_readme)

        # README.md 파일에 저장
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_readme)

        print("✅ README.md가 새로운 주차로 초기화되었습니다!")

        # 통계 정보 출력
        if args.verbose:
            stats = get_session_statistics()
            print(f"\n📊 스터디 진행 현황:")
            print(f"   - 현재 회차: {stats['current_session']}회차")
            print(f"   - 완료된 주차: {stats['total_weeks_completed']}주")
            print(f"   - 총 진행 일수: {stats['total_study_days']}일")
            print(f"   - 스터디 시작일: {stats['study_start_date']}")

        return True

    except ImportError as e:
        print(f"❌ 필요한 모듈을 찾을 수 없습니다: {e}")
        print("   다음을 확인하세요:")
        print("   1. scripts/session_counter.py 파일 존재")
        print("   2. scripts/update_readme.py 파일 존재")
        print("   3. 파일 권한 및 Python 경로")
        sys.exit(1)
    except Exception as e:
        print(f"❌ README 초기화 실패: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="새로운 주차로 README.md 초기화")
    parser.add_argument(
        "--force", action="store_true", help="새로운 주차가 아니어도 강제로 초기화 실행"
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="기존 README 백업하지 않음"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 정보 출력")

    args = parser.parse_args()

    try:
        success = main()
        if success:
            print(
                f"\n🎉 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}에 주차 초기화 완료!"
            )
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예기치 않은 오류: {e}")
        sys.exit(1)
