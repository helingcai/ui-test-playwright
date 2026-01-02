# # 所在目录：reporting/renderers/attempt_view.py
# from pathlib import Path
# from .failure_panel import render_failure_panel
# from reporting.utils.template_loader import load_template
#
#
# def render_attempt_chain(attempts: list[dict]) -> str:
#     template_chain = load_template('attempt_view_chain.html')
#     statuses = [a["status"] for a in attempts]
#     unique = set(statuses)
#
#     # 全部同状态（比如全失败）
#     if len(unique) == 1:
#         status = statuses[0]
#         return (f'<div class="attempt-chain muted">'
#                 f'🔁 Attempts: {"passed" if status == "PASSED" else str(len(attempts)) + "failures"}'
#                 f'</div>')
#
#     # 有状态变化（重要）
#     badges = []
#     for a in attempts:
#         cls = "failed" if a["status"] == "FAILED" else "passed"
#         icon = "❌" if a["status"] == "FAILED" else "✅"
#         badges.append(
#             f'<span class="attempt-badge {cls}">Attempt {a["attempt"]} {icon}</span>')
#     chain = '<span class="arrow">→</span>'.join(badges)
#
#     return template_chain.replace("{{chain}}", str(chain))
#
#
# def render_attempt_tabs(attempts):
#     template_tabs = load_template("attempt_view_tabs.html")
#     template_cards = load_template("attempt_view_cards.html")
#     tabs = ""
#     cards = ""
#
#     for i, a in enumerate(attempts):
#         active = "active" if i == len(attempts) - 1 else ""
#         aid = a["attempt"]
#         failure_panel_html = render_failure_panel(Path(a["base_dir"]), aid) if a["status"] == "FAILED" else ""
#
#         tabs += template_tabs.replace("{{aid}}", str(aid)).replace("{{active}}", str(active))
#
#         failure_panel = (
#             f'<button type="button" onclick="togglePanel({aid});return false;" class="panel-btn">🖲️ View Failure Panel (Attempt {aid})</button>'
#             if a['status'] == 'FAILED' else ''
#         )
#         cards += (template_cards.replace("{{aid}}", str(aid))
#                   .replace("{{active}}", str(active))
#                   .replace("{{status_icon}}", "❌ FAILED" if a['status'] == 'FAILED' else "✅ PASSED")
#                   .replace("{{duration}}", str(a.get('duration', '-')))
#                   .replace("{{error}}", str(a.get('error', '-')))
#                   .replace("{{url}}", str(a.get('url', '-')))
#                   .replace("{{screenshot}}", "✔️" if a['has_screenshot'] else "❌")
#                   .replace("{{video}}", "✔️" if a['has_video'] else "❌")
#                   .replace("{{trace}}", "✔️" if a['has_trace'] else "❌")
#                   .replace("{{view_failure_panel}}", failure_panel)
#                   .replace("{{failure_panel_html}}", str(failure_panel_html)))
#     return tabs, cards
