import json
import subprocess
import os
import tempfile
import sys

try:
    with open("test_results_summary.json", "r", encoding="utf-8") as f:
        results = json.load(f)

    total = results.get("total_problems", 0)
    passed = results.get("passed_problems", 0)
    partial = results.get("partial_passed_problems", 0)
    failed = results.get("failed_problems", 0)
    error = results.get("error_problems", 0)

    # 실패 상세 정보
    failure_details = []
    for detail in results.get("details", []):
        if detail["result"] not in ["PASS", "PARTIAL_PASS"]:
            problem_id = detail["problem_id"]
            author = detail["author"]
            errors = detail.get("errors", [])

            error_summary = errors[0] if errors else "알 수 없는 오류"
            if len(error_summary) > 100:
                error_summary = error_summary[:100] + "..."

            failure_details.append(f"**{problem_id}** ({author}): {error_summary}")

    # PR URL 단축
    pr_url = sys.argv[1] if len(sys.argv) > 1 else "N/A"
    pr_display = pr_url.split("/")[-1] if pr_url != "N/A" else "N/A"

    # 메시지 구성 (send_success_notification.py와 유사한 형식)
    message_parts = [
        "❌ **Test Result**",
        "",
        f"📊 **총 {total}개 문제**",
        f"✅ 완전 성공: **{passed}개**",
        f"⚠️ 부분 성공: **{partial}개**",
        f"❌ 실패: **{failed + error}개**",
        "",
    ]

    if failure_details:
        message_parts.append("**❌ 실패 상세:**")
        message_parts.extend(failure_details[:5])  # 최대 5개까지만
        if len(failure_details) > 5:
            message_parts.append(
                f"... 외 {len(failure_details) - 5}개 더 (자세한 내용은 PR 확인)"
            )
        message_parts.append("")

    message_parts.append("💪 코드를 수정한 후 다시 푸시해주세요!")

    if pr_url != "N/A":
        message_parts.append(f"🔗 [PR #{pr_display} 보기]({pr_url})")

    # [수정] 실제 줄바꿈 문자를 사용하도록 변경
    message = "\n".join(message_parts)

    # MatterMost 알림 전송
    payload = {"username": "BOJ-Bot", "icon_emoji": ":x:", "text": message}

    # PR 작성자 정보 가져오기 (두 번째 인자)
    pr_author = sys.argv[2] if len(sys.argv) > 2 else None

    # 개인 웹훅 URL 가져오기 (세 번째 인자, 우선순위 1)
    personal_webhook_url = (
        sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "" else None
    )

    webhook_url = None
    if personal_webhook_url:
        webhook_url = personal_webhook_url
        print(f"📩 개인 DM으로 알림 전송: {pr_author}")
    elif pr_author:
        # 환경변수에서 개인 웹훅 URL 시도 (우선순위 2)
        personal_webhook_key = f"{pr_author.upper()}_MATTERMOST_URL"
        webhook_url = os.environ.get(personal_webhook_key)

        if webhook_url:
            print(f"📩 환경변수에서 개인 DM으로 알림 전송: {pr_author}")
        else:
            print(f"❌ {personal_webhook_key} 환경변수가 설정되지 않았습니다.")
            sys.exit(0)

    if not webhook_url:
        print("❌ 사용 가능한 개인 웹훅 URL이 없습니다.")
        sys.exit(0)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        payload_file = f.name

    subprocess.run(
        [
            "curl",
            "-X",
            "POST",
            "-H",
            "Content-Type: application/json",
            "-d",
            f"@{payload_file}",
            webhook_url,
            "--fail",
            "--silent",
            "--show-error",
        ],
        check=True,
    )

    os.unlink(payload_file)
    print("✅ 실패 알림 전송 완료")

except Exception as e:
    print(f"❌ 알림 전송 실패: {e}")
