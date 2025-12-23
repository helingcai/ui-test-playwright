import zipfile

import base64
from playwright.sync_api import sync_playwright
from pathlib import Path
import pytest, shutil, json, allure
from scripts.save_login_state import save_login_state


# ================== Session Fixtures ==================
@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    """浏览器只启动一次"""
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    print("🔥 browser started", id(browser))
    browser.close()


@pytest.fixture(scope="session", autouse=True)
def clean_screenshot():
    """测试session启动前，清空artifacts、videos、tracing、allure-results"""
    for path in ["artifacts", "videos", "tracing", "allure-results", "storage"]:
        p = Path(path)
        if p.exists():
            shutil.rmtree(p)  # 删除目录 p 及其包含的所有文件和子目录。
        p.mkdir()


@pytest.fixture(scope="session", autouse=True)
def ensure_login_state(request):
    """
     确保 login.json 存在且有效
    """
    login_file = Path("storage/login.json")

    if not login_file.exists() or login_file.stat().st_size == 0:
        print("🔐 login.json不存在或无效，重新生成")
        save_login_state()
    else:
        print("✅ login.json已存在且有效，跳过生成")


# ================== Function Fixtures ==================
@pytest.fixture(scope="function")
def context(browser, request):
    """
    每个测试方法一个全新 context
    - 登录态隔离 都基于 login.json
    - 视频 + tracing 每个 attempt 单独目录
    """
    attempt = getattr(request.node, "execution_count", 1)
    attempt_dir = f"attempt_{attempt}"
    record_video_dir = Path("videos") / attempt_dir
    record_tracing_dir = Path("tracing") / attempt_dir
    record_video_dir.mkdir(parents=True, exist_ok=True)
    record_tracing_dir.mkdir(parents=True, exist_ok=True)

    need_login = request.node.get_closest_marker("need_login") is not None

    context = browser.new_context(
        storage_state="storage/login.json" if need_login else None,
        record_video_dir=str(record_video_dir),
        # Playwright只知道videos/，不会关系artifacts，video文件只有在context.close()后才会真正落盘
        record_video_size={"width": 1280, "height": 720},
        no_viewport=True)

    #  ======== 手动开启tracing ========
    #  为啥手动开启：
    #  因为Playwright不会自动帮你管理tracing文件
    # 你需要 start→stop→ 指定zip路径
    context.tracing.start(
        name=attempt_dir,
        screenshots=True,
        snapshots=True,
        sources=True)

    yield context

    #  ======== teardown阶段:(video、trace即将生成；page已close) ========
    trace_path = record_tracing_dir / "trace.zip"
    try:
        context.tracing.stop(path=trace_path)  # stop tracing，trace.zip 在这里真正生成
    finally:
        context.close()  # 一定要先close：释放video文件句柄、video真正写入磁盘

    #  ======== 执行成功用例删除video、trace ========
    failed = getattr(request.node, "_failed", False)
    if not failed:
        shutil.rmtree(record_video_dir, ignore_errors=True)
        shutil.rmtree(record_tracing_dir, ignore_errors=True)
        return

    #  ======== 执行失败用例移动video、trace到artifacts目录 ========
    module = request.node.module.__name__.split(".")[-1]
    cls = request.node.cls.__name__ if request.node.cls else "no_class"
    name = request.node.name

    target_dir = Path("artifacts") / module / cls / name / attempt_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    # 移动视频
    for video_file in record_video_dir.glob("*.webm"):
        shutil.move(str(video_file), target_dir / video_file.name)
    # 移动 trace
    if trace_path.exists():
        shutil.move(str(trace_path), target_dir / "trace.zip")

    #  ======== 捕获执行失败的video、trace ========
    # ❤️重要：video和trace捕获为什么要放在teardown阶段：
    # 因为pytest_runtest_makereport hook触发早于context fixture teardown，hook阶段video和trace文件尚未生成，此时捕获会失败
    # 所以video和trace捕获动作要放在teardown阶段

    # Attach 视频（精确文件）
    for video in target_dir.glob("*.webm"):
        allure.attach.file(
            video,
            name="📎 Video (used by Failure Panel)",
            attachment_type=allure.attachment_type.WEBM
        )

    # Attach trace
    trace = target_dir / "trace.zip"
    if trace.exists():
        allure.attach.file(
            trace,
            name="📎 Playwright-Trace.zip (used by Failure Panel)"
        )
    attach_failure_panel(target_dir, attempt)


@pytest.fixture(scope="function")
def page(context):
    """每个测试方法一个新 page"""
    page = context.new_page()
    console_error = []  # 这是内存中的list，所有console.error都会被收集

    # 捕获console errors, page.on("console")是浏览器级别监听,不会因为跳转丢失
    page.on(
        "console",
        lambda msg: console_error.append({
            "type": msg.type,
            "text": msg.text,
            "location": str(msg.location)
        }) if msg.type == "error" else None
    )
    page._console_errors = console_error  # 挂到page上，方便hook里取
    yield page
    page.close()


# ================== Pytest Hook：失败处理 ==================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试失败时自动保存：
    - 截图
    - URL
    - Console errors
    """
    outcome = yield
    rep = outcome.get_result()

    # 只处理 call 阶段失败
    if rep.when != "call" or not rep.failed:
        return

    page = item.funcargs.get("page")
    if not page:
        return

    # artifacts 目录结构
    module_name = item.module.__name__.split(".")[-1]
    class_name = item.cls.__name__ if item.cls else "no_class"
    test_name = item.name
    attempt = getattr(item, "execution_count", 1)
    attempt_dir = f"attempt_{attempt}"

    base_dir = Path("artifacts") / module_name / class_name / test_name / attempt_dir
    base_dir.mkdir(parents=True, exist_ok=True)

    # 生成失败用例截图
    page.screenshot(path=base_dir / "failure.png", full_page=True)

    # 生成失败用例URL文件
    (base_dir / "url.txt").write_text(page.url, encoding="utf-8")

    # 生成失败用例Console errors文件
    (base_dir / "console_errors.json").write_text(
        json.dumps(getattr(page, "_console_errors", []), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # 标记失败（跨fixture通信的关键，告诉 context： 👉 这是一次失败执行）
    item._failed = True

    # # ========= Allure Attach =========
    # # Attach 失败用例截图
    # screenshot = base_dir / "failure.png"
    # if screenshot.exists():
    #     allure.attach.file(
    #         screenshot,
    #         name="Failure-Screenshot",
    #         attachment_type=allure.attachment_type.PNG
    #     )

    # # Attach 失败用例页面url
    # url = base_dir / "url.txt"
    # if url.exists():
    #     allure.attach(
    #         url.read_text(encoding="utf-8"),
    #         name="Page-Url",
    #         attachment_type=allure.attachment_type.TEXT
    #     )

    # # Attach 失败用例控制台报错
    # console = base_dir / "console_errors.json"
    # if console.exists():
    #     allure.attach.file(
    #         console,
    #         name="Console-Errors",
    #         attachment_type=allure.attachment_type.JSON
    #     )


def render_trace_open_block(trace_path: Path)->str:
    """生成打开trace.zip的命令模板（三端通吃）"""
    # project_root = Path.cwd()

    # # 生成相对路径（Allure 中更稳定）
    # try:
    #     rel_trace = trace_path.relative_to(project_root)
    # except ValueError:
    #     rel_trace = trace_path  # 兜底

    # rel_posix = rel_trace.as_posix()
    # rel_win = str(rel_trace)

    # windows_powershell = f'cd {project_root}; npx playwright show-trace {rel_posix}'
    # windows_cmd = f'cd /d {project_root} && npx playwright show-trace {rel_win}'
    # macos_linux = f'cd {project_root} && npx playwright show-trace {rel_posix}'
    # <!-- Hidden command holders -->
    #   <textarea id="ps" style="display:none;">{windows_powershell}</textarea>
    #   <textarea id="cmd" style="display:none;">{windows_cmd}</textarea>
    #   <textarea id="unix" style="display:none;">{macos_linux}</textarea>
    
    return f"""
    <details>
      <summary><b>🧭 Playwright Trace</b></summary>
      <p class="hint">
        1️⃣ Click<b>📎 Playwright-Trace.zip (used by Failure Panel)</b><br/>
        2️⃣ Download <b>Playwright-Trace.zip</b><br/>
        3️⃣ Run in terminal:
      </p>
      <textarea id="trace-cmd" style="display:none;">npx playwright show-trace Playwright-Trace.zip</textarea>
      <button data-label="📋 Copy show-trace Command" onclick="copyCmd(this,'trace-cmd')">
        📋 Copy show-trace Command
      </button>
      <script type="text/javascript">
        function copyCmd(button,id) {{
          const el = document.getElementById(id);

          el.style.display = 'block';
          el.select();
          document.execCommand('copy');
          el.style.display = 'none';

          // 修改按钮状态
          const original = button.getAttribute('data-label');
          button.innerText = '✅ Copied';
          button.disabled = true;

          // 2 秒后恢复
          setTimeout(() => {{
          button.innerText = original;
          button.disabled = false;}}, 2000);
        }}
      </script>
    </details>
    """

def attach_failure_panel(base_dir: Path, attempt: int):
    page_url = (base_dir / "url.txt").read_text(encoding="utf-8")
    console_errors = json.loads((base_dir / "console_errors.json").read_text(encoding="utf-8"))

    screenshot = base_dir / "failure.png"
    video = next(base_dir.glob("*.webm"), None)
    trace = base_dir / "trace.zip"

    # ===== Screenshot → base64 =====
    screenshot_base64 = ""
    if screenshot.exists():
        screenshot_base64 = base64.b64encode(
            screenshot.read_bytes()
        ).decode("utf-8")

    # ===== Console pretty =====
    console_pretty = json.dumps(console_errors, indent=2, ensure_ascii=False)

    # ===== Trace block =====
    trace_block = (
        render_trace_open_block(trace)
        if trace.exists()
        else "<i>Trace not available</i>"
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{ font-family: Arial, sans-serif; }}
      h2 {{ color: #b00020; }}
      .section {{ margin-bottom: 20px; }}
      details {{ margin-left: 10px; }}
      pre {{ background: #f6f8fa; padding: 10px; }}
      img {{ max-width: 100%; border: 1px solid #ccc; }}
      .hint {{ color: #666; font-size: 12px; }}
    </style>
    </head>
    <body>

    <h2>❌ Failure Panel (Attempt {attempt})</h2>
    <p class="hint">
    This panel aggregates all failure information.<br/>
    Other attachments are raw data and normally do not need to be opened.
    </p>

    <div class="section">
      <details>
        <summary><b>📍 Page URL</b></summary>
        <pre>{page_url}</pre>
      </details>
    </div>

    <div class="section">
      <details>
        <summary><b>❌ Console Errors</b></summary>
        <pre>{console_pretty}</pre>
      </details>
    </div>

    <div class="section">
      <details>
        <summary><b>📸 Screenshot</b></summary>
        <img src="data:image/png;base64,{screenshot_base64}" />
      </details>
    </div>

    <div class="section">
      <details>
        <summary><b>🎥 Video</b></summary>
        <p class="hint">
          See attachment: <b>📎 Video (used by Failure Panel)</b>
        </p>
      </details>
    </div>

    <div class="section">
        {trace_block}
    </div>

    </body>
    </html>
    """
    allure.attach(
        html,
        name=f"Failure Panel (Attempt {attempt})",
        attachment_type=allure.attachment_type.HTML
    )



