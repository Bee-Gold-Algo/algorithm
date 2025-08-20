#!/usr/bin/env python3
"""
scripts/update_readme_batch.py
각 문제의 실제 제출 날짜를 사용하여 README 업데이트
"""

import json
import subprocess
import sys
from datetime import datetime


def main():
    try:
        with open("problems_info.json", "r", encoding="utf-8") as f:
            all_problems_in_pr = json.load(f)

        if not all_problems_in_pr:
            print("ℹ️ 처리할 문제가 없습니다.")
            return

        print(f"✅ README 업데이트 대상: {len(all_problems_in_pr)}개 문제")

        # 날짜별로 문제들 그룹화하여 로깅
        date_groups = {}
        for problem in all_problems_in_pr:
            submission_date = problem.get("submission_date", datetime.now().strftime("%Y-%m-%d"))
            if submission_date not in date_groups:
                date_groups[submission_date] = []
            date_groups[submission_date].append(problem)

        print(f"📅 제출 날짜 분포:")
        for date, problems in sorted(date_groups.items()):
            problem_ids = [p["problem_id"] for p in problems]
            print(f"  - {date}: {len(problems)}개 문제 ({', '.join(problem_ids)})")

        # 각 문제별로 README 업데이트 실행
        success_count = 0
        failure_count = 0

        for problem in all_problems_in_pr:
            problem_id = problem["problem_id"]
            author = problem["author"]
            submission_date = problem.get("submission_date", datetime.now().strftime("%Y-%m-%d"))
            language = problem.get("language", "Java")

            print(f"\n🔄 처리 중: 문제 {problem_id} ({author}) - {submission_date}")

            cmd = [
                "python",
                "scripts/update_readme.py",
                "--problem-id",
                problem_id,
                "--author",
                author,
                "--submission-date",
                submission_date,
                "--language",
                language,
            ]

            try:
                result = subprocess.run(
                    cmd, 
                    check=True, 
                    timeout=30,
                    capture_output=True,
                    text=True
                )
                
                print(f"  ✅ 성공: 문제 {problem_id} README 업데이트 완료")
                if result.stdout:
                    print(f"     출력: {result.stdout.strip()}")
                success_count += 1
                
            except subprocess.CalledProcessError as e:
                print(f"  ❌ 실패: 문제 {problem_id} README 업데이트 실패")
                print(f"     오류 코드: {e.returncode}")
                if e.stdout:
                    print(f"     출력: {e.stdout.strip()}")
                if e.stderr:
                    print(f"     에러: {e.stderr.strip()}")
                failure_count += 1
                
            except subprocess.TimeoutExpired:
                print(f"  ⏰ 시간초과: 문제 {problem_id} README 업데이트 시간초과")
                failure_count += 1
                
            except Exception as e:
                print(f"  ⚠️ 예외: 문제 {problem_id} README 업데이트 중 예외 발생: {e}")
                failure_count += 1

        # 최종 요약
        print(f"\n📊 README 업데이트 완료")
        print(f"=" * 40)
        print(f"총 처리 문제: {len(all_problems_in_pr)}개")
        print(f"성공: {success_count}개")
        print(f"실패: {failure_count}개")

        if failure_count > 0:
            print(f"⚠️ {failure_count}개 문제의 README 업데이트가 실패했습니다.")
            # 실패가 있어도 워크플로우는 계속 진행 (README 업데이트 실패가 PR 승인을 막지 않도록)
        else:
            print("🎉 모든 문제의 README 업데이트가 성공했습니다!")

    except FileNotFoundError:
        print("ℹ️ problems_info.json 파일이 없어 README 업데이트를 건너뜁니다.")
        
    except json.JSONDecodeError as e:
        print(f"❌ problems_info.json 파싱 오류: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ README 업데이트 중 예상치 못한 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()