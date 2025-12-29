from reporting.utils.template_loader import load_template

def calculate_attempt_diff(attempts: list[dict]):
    """ 计算多个 attempts 之间的差异
    :param attempts: 一个包含所有 attempts 信息的列表
    :return: diff_summary: 一个包含 attempts 差异分析的文本"""
    template_attempt_diff = load_template("attempt_diff.html")
    diff_summary = []

    # 错误信息差异
    error_summary = "🛑 Error Differences"
    error_diff = compare_field(attempts, 'error')
    if error_diff:
        diff_summary.append(template_attempt_diff.replace("{{summary}}",error_summary).replace("{{content}}",error_diff))
        # f"""
        #                 <details>
        #                   <summary class="attempt-diff-summary">🛑 Error Differences</summary>
        #                   <pre>{error_diff}</pre>
        #                 </details>
        #                 """

    # 页面 URL 差异
    url_summary = "🌍 URL Differences"
    url_diff = compare_field(attempts, 'url')
    if url_diff:
        diff_summary.append(template_attempt_diff.replace("{{summary}}", url_summary).replace("{{content}}", url_diff))
        # diff_summary.append(f"""
        #        <details>
        #          <summary class="attempt-diff-summary">🌍 URL Differences</summary>
        #          <pre>{url_diff}</pre>
        #        </details>
        #        """)

    # 持续时间差异
    duration_summary = "🕣 Duration Differences"
    duration_diff = compare_field(attempts, 'duration')
    if duration_diff:
        diff_summary.append(template_attempt_diff.replace("{{summary}}", duration_summary).replace("{{content}}", duration_diff))
        # diff_summary.append(f"""
        #         <details>
        #           <summary class="attempt-diff-summary">🕣 Duration Differences</summary>
        #           <pre>{duration_diff}</pre>
        #         </details>
        #         """)

    # 附件差异（截图、视频、trace）
    attachments_summary = "📎 Attachment Differences"
    attachments_diff = compare_attachments(attempts)
    if attachments_diff:
        diff_summary.append(
            template_attempt_diff.replace("{{summary}}", attachments_summary).replace("{{content}}", attachments_diff))
        # diff_summary.append(f"""
        #         <details>
        #           <summary class="attempt-diff-summary">📎 Attachment Differences</summary>
        #           <pre>{attachments_diff}</pre>
        #         </details>
        #         """)

    return "".join(diff_summary)

def compare_field(attempts: list[dict], field: str):
    """ 比较同一字段在不同 attempts 中的差异
    :param attempts: 一个包含所有 attempts 信息的列表
    :param field: 需要比较的字段（例如 error, url, duration）
    :return: 差异文本，如果没有差异则返回空字符串 """
    field_values = [attempt.get(field) for attempt in attempts]
    unique_values = set(field_values)

    return "\n".join(map(str, unique_values)) if len(unique_values) > 1 else ""


def compare_attachments(attempts: list[dict]):
    """ 比较所有尝试中生成的附件差异（如截图、视频、trace）
    :param attempts: 一个包含所有 attempts 信息的列表
    :return: 差异文本，如果没有差异则返回空字符串 """
    attachment_diff = []

    for field in ['has_screenshot', 'has_video', 'has_trace']:
        field_values = [attempt.get(field) for attempt in attempts]
        unique_values = set(field_values)

        if len(unique_values) > 1:
            attachment_diff.append(f"{field} difference: {', '.join(map(str, unique_values))}")

    return ", ".join(attachment_diff) if attachment_diff else ""


