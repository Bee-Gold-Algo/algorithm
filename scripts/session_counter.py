#!/usr/bin/env python3
"""
scripts/session_counter.py
회차 정보를 관리하는 스크립트 (개선된 버전)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pytz

SESSION_FILE = "session_info.json"
TIMEZONE = pytz.timezone("Asia/Seoul")


def get_kst_now():
    """한국 시간 기준 현재 시간 반환"""
    return datetime.now(TIMEZONE).replace(tzinfo=None)


def load_session_info():
    """회차 정보 로드"""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 기존 데이터 검증 및 마이그레이션
                if "created_at" not in data:
                    data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if "updated_at" not in data:
                    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if "study_start_date" not in data:
                    # 기존 start_date를 study_start_date로 마이그레이션
                    data["study_start_date"] = data.get(
                        "start_date", datetime.now().strftime("%Y-%m-%d")
                    )
                return data
        except Exception as e:
            print(f"⚠️ 회차 정보 로드 실패: {e}")
            print("🔄 기본값으로 초기화합니다.")

    # 기본값 반환 (스터디 시작일을 현재 주의 월요일로 설정)
    current_week = get_current_week_info()
    return {
        "current_session": 1,
        "study_start_date": current_week["monday"],  # 스터디 시작일
        "start_date": current_week["monday"],  # 호환성을 위해 유지
        "last_week_start": None,
        "last_week_end": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_weeks": 0,
        "metadata": {
            "timezone": "Asia/Seoul",
            "week_format": "monday_to_sunday",
            "version": "2.0",
        },
    }


def save_session_info(session_info):
    """회차 정보 저장"""
    try:
        # 업데이트 시간 갱신
        session_info["updated_at"] = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")

        # 백업 파일 생성 (기존 파일이 있는 경우)
        if os.path.exists(SESSION_FILE):
            backup_file = f"{SESSION_FILE}.backup"
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                backup_data = f.read()
            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(backup_data)

        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session_info, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 회차 정보 저장 실패: {e}")
        return False


def get_current_week_info():
    """현재 주차 정보 계산 (일요일 기준, 한국 시간)"""
    today = get_kst_now()

    # 이번 주 일요일 찾기 (오늘이 일요일이면 오늘, 아니면 다음 일요일)
    days_until_sunday = (6 - today.weekday()) % 7  # 월=0, 일=6
    if days_until_sunday == 0 and today.weekday() == 6:  # 오늘이 일요일
        current_sunday = today
    else:
        current_sunday = today + timedelta(days=days_until_sunday)

    # 이번 주 월요일 계산
    current_monday = current_sunday - timedelta(days=6)

    return {
        "monday": current_monday.strftime("%Y-%m-%d"),
        "sunday": current_sunday.strftime("%Y-%m-%d"),
        "deadline": current_sunday.strftime("%Y-%m-%d 23:59"),
    }


def get_week_info_for_date(date_str):
    """특정 날짜의 주차 정보 계산 (일요일 기준)"""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        print(f"❌ 잘못된 날짜 형식: {date_str}. YYYY-MM-DD 형식을 사용하세요.")
        raise e

    # 해당 날짜가 속한 주의 일요일 찾기
    days_until_sunday = (6 - target_date.weekday()) % 7  # 월=0, 일=6
    if days_until_sunday == 0 and target_date.weekday() == 6:  # 해당 날짜가 일
        current_sunday = target_date
    else:
        current_sunday = target_date + timedelta(days=days_until_sunday)

    # 해당 주 월요일 계산
    current_monday = current_sunday - timedelta(days=6)

    return {
        "monday": current_monday.strftime("%Y-%m-%d"),
        "sunday": current_sunday.strftime("%Y-%m-%d"),
        "deadline": current_sunday.strftime("%Y-%m-%d 23:59"),
    }


def calculate_session_number_from_start(target_date_str, study_start_date_str):
    """스터디 시작일로부터 회차 번호 계산"""
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        study_start = datetime.strptime(study_start_date_str, "%Y-%m-%d")

        # 스터디 시작일이 속한 주의 월요일 찾기
        start_week_monday = get_week_info_for_date(study_start_date_str)["monday"]
        start_monday = datetime.strptime(start_week_monday, "%Y-%m-%d")

        # 타겟 날짜가 속한 주의 월요일 찾기
        target_week_monday = get_week_info_for_date(target_date_str)["monday"]
        target_monday = datetime.strptime(target_week_monday, "%Y-%m-%d")

        # 주차 차이 계산
        weeks_diff = (target_monday - start_monday).days // 7

        # 스터디 시작 전이면 1회차로 처리
        if weeks_diff < 0:
            return 1

        return weeks_diff + 1

    except Exception as e:
        print(f"⚠️ 회차 계산 실패: {e}")
        return 1


def get_session_info(submission_date=None):
    """현재 회차 정보 반환 (개선된 버전)"""
    session_info = load_session_info()

    if submission_date:
        # 제출 날짜 기준으로 주차 계산
        target_week = get_week_info_for_date(submission_date)

        # 스터디 시작일 기준으로 정확한 회차 계산
        calculated_session = calculate_session_number_from_start(
            submission_date, session_info["study_start_date"]
        )

        # 현재 저장된 회차와 계산된 회차 비교 및 업데이트
        if calculated_session != session_info["current_session"]:
            old_session = session_info["current_session"]
            session_info["current_session"] = calculated_session
            session_info["last_week_start"] = target_week["monday"]
            session_info["last_week_end"] = target_week["sunday"]
            session_info["total_weeks"] = calculated_session - 1
            save_session_info(session_info)
            print(f"🔄 회차 업데이트: {old_session}회차 → {calculated_session}회차")

        return {
            "session_number": calculated_session,
            "monday": target_week["monday"],
            "sunday": target_week["sunday"],
            "deadline": target_week["deadline"],
        }
    else:
        # 현재 날짜 기준으로 주차 계산
        current_week = get_current_week_info()
        today_str = get_kst_now().strftime("%Y-%m-%d")

        # 스터디 시작일 기준으로 정확한 회차 계산
        calculated_session = calculate_session_number_from_start(
            today_str, session_info["study_start_date"]
        )

        # 회차 정보 업데이트
        if calculated_session != session_info["current_session"]:
            old_session = session_info["current_session"]
            session_info["current_session"] = calculated_session
            session_info["last_week_start"] = current_week["monday"]
            session_info["last_week_end"] = current_week["sunday"]
            session_info["total_weeks"] = calculated_session - 1
            save_session_info(session_info)
            print(f"🔄 회차 업데이트: {old_session}회차 → {calculated_session}회차")

        return {
            "session_number": calculated_session,
            "monday": current_week["monday"],
            "sunday": current_week["sunday"],
            "deadline": current_week["deadline"],
        }


def is_new_week_start(target_date=None):
    """새로운 주차의 시작(월요일)인지 확인"""
    if target_date is None:
        today = get_kst_now()
        target_date_str = today.strftime("%Y-%m-%d")
        is_monday = today.weekday() == 0
    else:
        target_date_str = target_date
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        is_monday = target_dt.weekday() == 0

    week_info = get_week_info_for_date(target_date_str)
    return target_date_str == week_info["monday"] and is_monday


def get_session_statistics():
    """회차 관련 통계 정보 반환"""
    session_info = load_session_info()
    current = get_session_info()

    # 스터디 진행 기간 계산
    study_start = datetime.strptime(session_info["study_start_date"], "%Y-%m-%d")
    today = get_kst_now()
    total_days = (today - study_start).days

    return {
        "current_session": current["session_number"],
        "total_weeks_completed": current["session_number"] - 1,
        "study_start_date": session_info["study_start_date"],
        "total_study_days": total_days,
        "current_week": {
            "monday": current["monday"],
            "sunday": current["sunday"],
            "deadline": current["deadline"],
        },
        "created_at": session_info.get("created_at", "Unknown"),
        "last_updated": session_info.get("updated_at", "Unknown"),
    }


def reset_session_counter(new_start_date=None):
    """회차 카운터 초기화"""
    if new_start_date is None:
        # 현재 주의 월요일을 시작일로 설정
        current_week = get_current_week_info()
        new_start_date = current_week["monday"]

    try:
        # 새로운 시작일의 주차 정보 확인
        start_week = get_week_info_for_date(new_start_date)

        session_info = {
            "current_session": 1,
            "study_start_date": new_start_date,
            "start_date": new_start_date,  # 호환성을 위해 유지
            "last_week_start": start_week["monday"],
            "last_week_end": start_week["sunday"],
            "created_at": get_kst_now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": get_kst_now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_weeks": 0,
            "metadata": {
                "timezone": "Asia/Seoul",
                "week_format": "monday_to_sunday",
                "version": "2.0",
                "reset_reason": "manual_reset",
            },
        }

        if save_session_info(session_info):
            print(f"✅ 회차 카운터가 초기화되었습니다.")
            print(f"   - 새로운 시작일: {new_start_date}")
            print(f"   - 1회차 기간: {start_week['monday']} ~ {start_week['sunday']}")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ 회차 카운터 초기화 실패: {e}")
        return False


def repair_session_data():
    """손상된 회차 데이터 복구"""
    print("🔧 회차 데이터 복구 중...")

    # 백업 파일에서 복구 시도
    backup_file = f"{SESSION_FILE}.backup"
    if os.path.exists(backup_file):
        try:
            with open(backup_file, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
            print("📁 백업 파일에서 데이터 복구 시도...")
            if save_session_info(backup_data):
                print("✅ 백업에서 복구 완료")
                return True
        except Exception as e:
            print(f"⚠️ 백업 복구 실패: {e}")

    # 완전 초기화
    print("🔄 완전 초기화 진행...")
    return reset_session_counter()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="회차 정보 관리 도구")
    parser.add_argument("--reset", action="store_true", help="회차 카운터 초기화")
    parser.add_argument("--start-date", help="스터디 시작일 설정 (YYYY-MM-DD)")
    parser.add_argument("--stats", action="store_true", help="회차 통계 정보 출력")
    parser.add_argument("--check-date", help="특정 날짜의 회차 정보 확인 (YYYY-MM-DD)")
    parser.add_argument("--repair", action="store_true", help="손상된 데이터 복구")
    parser.add_argument(
        "--is-new-week", help="특정 날짜가 새 주차 시작인지 확인 (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    try:
        if args.repair:
            repair_session_data()
        elif args.reset:
            start_date = args.start_date
            if reset_session_counter(start_date):
                print("✅ 회차 카운터 초기화 완료")
            else:
                print("❌ 회차 카운터 초기화 실패")
        elif args.stats:
            stats = get_session_statistics()
            print("📊 회차 통계 정보")
            print(f"   - 현재 회차: {stats['current_session']}회차")
            print(f"   - 완료된 주차: {stats['total_weeks_completed']}주")
            print(f"   - 스터디 시작일: {stats['study_start_date']}")
            print(f"   - 총 진행 일수: {stats['total_study_days']}일")
            print(
                f"   - 현재 주차: {stats['current_week']['monday']} ~ {stats['current_week']['sunday']}"
            )
            print(f"   - 마감: {stats['current_week']['deadline']}")
            print(f"   - 마지막 업데이트: {stats['last_updated']}")
        elif args.check_date:
            session_info = get_session_info(args.check_date)
            print(f"📅 {args.check_date}의 회차 정보")
            print(f"   - 회차: {session_info['session_number']}회차")
            print(
                f"   - 주차 기간: {session_info['monday']} ~ {session_info['sunday']}"
            )
            print(f"   - 마감: {session_info['deadline']}")
        elif args.is_new_week:
            is_new = is_new_week_start(args.is_new_week)
            week_info = get_week_info_for_date(args.is_new_week)
            print(
                f"🗓️ {args.is_new_week}: {'새로운 주차 시작일' if is_new else '새로운 주차 시작일 아님'}"
            )
            print(f"   - 해당 주 월요일: {week_info['monday']}")
        else:
            # 기본 동작: 현재 회차 정보 출력
            session_info = get_session_info()
            print(f"📅 현재 회차: {session_info['session_number']}회차")
            print(f"   - 기간: {session_info['monday']} ~ {session_info['sunday']}")
            print(f"   - 마감: {session_info['deadline']}")

            # 새로운 주차 시작인지 확인
            if is_new_week_start():
                print("🚀 오늘은 새로운 주차 시작일입니다!")

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
