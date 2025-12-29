import allure
from .attempt_view import render_attempt_chain, render_attempt_tabs
from .retry_insight import build_retry_insight
from .attempt_diff import calculate_attempt_diff
from reporting.utils.template_loader import load_template, load_js, load_css


def attach_attempt_summary(attempts: list[dict]):
    template = load_template("attempt_summary.html")
    js = load_js("attempt_summary.js")
    css = load_css("attempt_summary.css")

    attempt_chain = render_attempt_chain(attempts)
    retry_insight = build_retry_insight(attempts)
    retry_insight_html = "<ul>" + "".join(
        f"<li>{line}</li>" for line in retry_insight
    ) + "</ul>" if retry_insight else ""

    tabs, cards = render_attempt_tabs(attempts)
    attempt_diff = calculate_attempt_diff(attempts)

    last_failed = max(
        (a["attempt"] for a in attempts if a["status"] == "FAILED"),
        default=attempts[-1]["attempt"]
    )

    html = (template.replace("{{css}}", str(css))
            .replace("{{js}}", str(js))
            .replace("{{tabs}}", str(tabs))
            .replace("{{cards}}",str(cards))
            .replace("{{attempt_diff}}", str(attempt_diff))
            .replace("{{last_failed}}", str(last_failed))
            .replace("{{attempt_chain}}",str(attempt_chain))
            .replace("{{retry_insight_html}}",str(retry_insight_html)))
    allure.attach(
        html,
        name=" Attempt Summary",
        attachment_type=allure.attachment_type.HTML
    )
