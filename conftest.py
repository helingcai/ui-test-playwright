import time
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
    # print("🔥 browser started", id(browser))
    browser.close()


@pytest.fixture(scope="session", autouse=True)
def clean_screenshot():
    clean_directories()


@pytest.fixture(scope="session", autouse=True)
def ensure_login_state(request):
    ensure_login_state_exists()


# ================== Function Fixtures ==================
@pytest.fixture(scope="function")
def context(browser, request):
    """每个测试方法一个全新 context"""
    attempt = getattr(request.node, "execution_count", 1)
    request.node._current_attempt = attempt  # 🔒 锁定本次 context 对应的 attempt（关键）

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
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080})

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

    #  ======== teardown阶段：video、trace即将生成，page已close========
    trace_path = record_tracing_dir / "trace.zip"
    try:
        context.tracing.stop(path=trace_path)  # stop tracing，trace.zip 在这里真正生成
    finally:
        context.close()  # 一定要先close：释放video文件句柄、video真正写入磁盘

    # 执行成功用例删除video、trace
    failed = getattr(request.node, "_failed", False)
    if not failed:
        shutil.rmtree(record_video_dir, ignore_errors=True)
        shutil.rmtree(record_tracing_dir, ignore_errors=True)
        return

    #  执行失败用例移动video、trace到artifacts目录
    module = request.node.module.__name__.split(".")[-1]
    cls = request.node.cls.__name__ if request.node.cls else "no_class"
    name = request.node.name

    target_dir = get_attempt_dir(module, cls, name, attempt)  # 构建artifacts目录
    move_artifacts(record_video_dir, trace_path, target_dir)  # 移动video、trace到artifacts

    # 更新_attempts信息
    attempts = getattr(request.node, "_attempts", [])
    attempt = request.node._current_attempt  # 🔑 用 setup 阶段锁定的 attempt
    current = next(
        a for a in attempts
        if a["attempt"] == attempt
    )
    current.update({  # current 不是一个拷贝，它就是 _attempts[-1] 的引用
        "has_screenshot": (target_dir / "failure.png").exists(),
        "has_video": any(target_dir.glob("*.webm")),
        "has_trace": (target_dir / "trace.zip").exists(),
        "url": (target_dir / "url.txt").read_text(encoding="utf-8")
        if (target_dir / "url.txt").exists() else None,
        "base_dir": str(target_dir)
    })

    # 捕获执行失败的video、trace
    attach_artifacts_to_allure(target_dir)

    # 只在最后一次 attempt attach Attempt Summary
    max_attempts = getattr(request.node.config.option, "reruns", 0) + 1
    # if attempt == max_attempts:
    #     attach_attempt_summary(attempts)


@pytest.fixture(scope="function")
def page(context):
    """每个测试方法一个新 page"""
    page = context.new_page()

    # ------------浏览器控制台报错----------
    console_error = []
    page.on(  # page.on() 是Playwright 浏览器事件的 API，它只能监听浏览器事件，比如 console、dialog、response 等。
        "console",
        lambda msg: console_error.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }) if msg.type == "error" else None
    )
    page._console_errors = console_error  # 挂到page上，方便hook里取
    yield page
    page.close()


# ================== Pytest Hook：失败处理 ==================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动保存：截图、URL、Console errors"""
    start = time.time()  # 测试用例开始执行时间
    outcome = yield
    rep = outcome.get_result()
    duration = round(time.time() - start, 2)

    # 只处理 call 阶段
    if rep.when != "call":
        return

    if not hasattr(item, "_attempts"):
        item._attempts = []

    attempt = len(item._attempts) + 1

    item._attempts.append({
        "attempt": attempt,
        "status": "FAILED" if rep.failed else "PASSED",
        "duration": duration,
        "error": str(rep.longrepr) if rep.failed else ""
    })

    if not rep.failed:
        return

    # ========= UI 项目的职责 =========
    page = item.funcargs.get("page")
    if not page:
        return

    # 保存 Python 端的断言错误到 page
    page._test_error = str(rep.longrepr) if rep.failed else ""

    item._failed = True

    # 收集失败数据
    # attempt = getattr(item, "execution_count", 1)
    # record_failed_attempt(item, attempt, "FAILED" if rep.failed else "PASSED", duration,
    #                       str(rep.longrepr) if rep.failed else "")

    # 构建artifacts 目录,报错错误证据
    module_name = item.module.__name__.split(".")[-1]
    class_name = item.cls.__name__ if item.cls else "no_class"
    test_name = item.name
    attempt_dir = f"attempt_{attempt}"
    base_dir = Path("artifacts") / module_name / class_name / test_name / attempt_dir
    base_dir.mkdir(parents=True, exist_ok=True)

    save_failure_artifacts(page, base_dir)


# ================== Utility Functions ==================
def clean_directories(paths=None):
    """清理 session 启动前的目录"""
    if paths is None:
        paths = ["artifacts", "videos", "tracing", "allure-results", "storage"]
    for path in paths:
        p = Path(path)
        if p.exists():
            shutil.rmtree(p)
        p.mkdir()


def ensure_login_state_exists(path="storage/login.json"):
    """确保 login.json 存在且有效"""
    login_file = Path(path)
    if not login_file.exists() or login_file.stat().st_size == 0:
        print("🔐 login.json不存在或无效，重新生成")
        save_login_state()
    else:
        print("✅ login.json已存在且有效，跳过生成")


def get_attempt_dir(module, cls, test_name, attempt):
    """构建 attempt artifacts 目录"""
    attempt_dir = f"attempt_{attempt}"
    target_dir = Path("artifacts") / module / cls / test_name / attempt_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def save_failure_artifacts(page, base_dir):
    """保存失败截图、URL、console errors"""
    page.screenshot(path=base_dir / "failure.png", full_page=True)  # 生成失败用例截图

    (base_dir / "url.txt").write_text(page.url, encoding="utf-8")  # 生成失败用例URL文件

    console_errors = getattr(page, "_console_errors", [])
    (base_dir / "browser_console_errors.json").write_text(  # 生成失败用例Console errors文件
        json.dumps(console_errors, indent=2, ensure_ascii=False), encoding="utf-8")

    error_file = base_dir / "test_failure_errors.txt"
    if getattr(page, "_test_error", None):
        (error_file).write_text(page._test_error, encoding="utf-8")


def move_artifacts(src_video_dir, src_trace, dst_dir):
    """移动视频和trace到目标目录"""
    for video_file in src_video_dir.glob("*.webm"):
        shutil.move(str(video_file), dst_dir / video_file.name)
    if src_trace.exists():
        shutil.move(str(src_trace), dst_dir / "trace.zip")


def attach_artifacts_to_allure(target_dir):
    """将 video / trace 附件到 Allure"""
    for video in target_dir.glob("*.webm"):
        allure.attach.file(video, name="📎 Video",
                           attachment_type=allure.attachment_type.WEBM)
    trace = target_dir / "trace.zip"
    if trace.exists():
        allure.attach.file(trace, name="Playwright-Trace.zip")


def record_failed_attempt(item, attempt, status, duration, error=""):
    """记录一次失败的 attempt"""
    if not hasattr(item, "_attempts"):
        item._attempts = []
    item._attempts.append({
        "attempt": attempt,
        "status": status,
        "duration": duration,
        "error": error,
        "url": None  # 稍后在 teardown 补
    })
