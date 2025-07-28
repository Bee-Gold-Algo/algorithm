#!/usr/bin/env python3
"""
scripts/update_readme_batch.py
"""

import json
import subprocess
import sys
from datetime import datetime

try:
    with open("problems_info.json", "r", encoding="utf-8") as f:
        all_problems_in_pr = json.load(f)

    if all_problems_in_pr:
        print(
            f"✅ README 업데이트 대상: {len(all_problems_in_pr)}개 문제 (테스트 결과 무관)"
        )

    for problem in all_problems_in_pr:
        problem_id = problem["problem_id"]
        author = problem["author"]

        cmd = [
            "python",
            "scripts/update_readme.py",
            "--problem-id",
            problem_id,
            "--author",
            author,
            "--submission-date",
            datetime.now().strftime("%Y-%m-%d"),
            "--language",
            "Java",
        ]

        try:
            subprocess.run(cmd, check=True, timeout=30)
            print(f"  - 문제 {problem_id} README 업데이트 완료")
        except Exception as e:
            print(f"  - ⚠️ 문제 {problem_id} README 업데이트 실패: {e}")

except FileNotFoundError:
    print("ℹ️ problems_info.json 파일이 없어 README 업데이트를 건너뜁니다.")
except Exception as e:
    print(f"❌ README 업데이트 중 오류: {e}")
    sys.exit(1)
