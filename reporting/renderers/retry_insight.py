def build_retry_insight(attempts: list[dict]) -> list[str]:
    """生成RetryInsight文本"""
    lines = []

    failed = [a for a in attempts if a["status"] == "FAILED"]
    passed = [a for a in attempts if a["status"] == "PASSED"]

    if failed and passed:
        lines += [f"• Failed {len(failed)} times, then passed on retry", "• Likely flaky test (unstable behavior)"]
        # lines.append(
        #     f"• Failed {len(failed)} times, then passed on retry"
        # )
        # lines.append("• Likely flaky test (unstable behavior)")
    elif len(failed) == len(attempts):
        lines.append(
            f"• All {len(attempts)} attempts failed"
        )

    errors = {
        a["error"] for a in failed if a["error"]
    }
    if len(errors) == 1 and failed:
        lines.append("• Same error across failed attempts")
    elif len(errors) > 1:
        lines.append("• Error message changed between attempts")

    urls = {a["url"] for a in attempts if a["url"]}
    if len(urls) > 1:
        lines.append("• Failed at different URLs")
    return lines
