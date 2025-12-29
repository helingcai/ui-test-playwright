from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_template(name: str) -> str:
    path = BASE_DIR / "templates" / name
    return path.read_text(encoding="utf-8")

def load_css(name: str) -> str:
    path = BASE_DIR / "styles" / name
    return path.read_text(encoding="utf-8")

def load_js(name: str) -> str:
    path = BASE_DIR / "scripts" / name
    return path.read_text(encoding="utf-8")
