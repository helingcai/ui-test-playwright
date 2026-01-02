# # 所在目录：reporting/renderers/failure_panel.py
# import base64, json
# from pathlib import Path
# from reporting.utils.template_loader import load_template
#
#
# def render_failure_panel(base_dir: Path, attempt: int) -> str:
#     # 加载html模板
#     template_failure_panel = load_template("failure_panel.html")
#     template_trace_block = load_template("trace_block.html")
#
#     page_url = (base_dir / "url.txt").read_text(encoding="utf-8")
#
#     screenshot = base_dir / "failure.png"
#     screenshot_base64 = ""
#     if screenshot.exists():
#         screenshot_base64 = base64.b64encode(
#             screenshot.read_bytes()
#         ).decode("utf-8")
#
#     console_errors = json.loads((base_dir / "console_errors.json").read_text(encoding="utf-8"))
#     console_pretty = json.dumps(console_errors, indent=2, ensure_ascii=False)
#
#     # trace_block = (render_trace_open_block())
#
#     return (template_failure_panel.replace("{{attempt}}", str(attempt))
#             .replace("{{page_url}}", str(page_url))
#             .replace("{{console_pretty}}", str(console_pretty))
#             .replace("{{screenshot_base64}}", str(screenshot_base64))
#             .replace("{{trace_block}}", str(template_trace_block)))
