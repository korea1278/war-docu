"""공통 유틸: 경로, 스토리보드 로딩, HTTP 세션."""
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
UA = "war-docu/1.0 (https://github.com/korea1278/war-docu; educational documentary)"


def ep_dirs(ep: str):
    src = ROOT / "episodes" / ep
    out = ROOT / "public" / "ep" / ep
    out.mkdir(parents=True, exist_ok=True)
    return src, out


def load_board(ep: str) -> dict:
    src, _ = ep_dirs(ep)
    return json.loads((src / "storyboard.json").read_text(encoding="utf-8"))


def line_text(line) -> str:
    return line if isinstance(line, str) else line["t"]


def line_say(line) -> str:
    return line if isinstance(line, str) else line.get("say", line["t"])


def session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return s


def log_error(msg: str):
    """오류를 저장소 logs/errors.txt 에 남김 (Actions 로그를 못 볼 때 확인용)."""
    d = ROOT / "logs"
    d.mkdir(exist_ok=True)
    with open(d / "errors.txt", "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg.replace("\n", " ")[:600] + "\n")


def retry(fn, tries=4, wait=4, label=""):
    last = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa
            last = e
            print(f"  ! {label} 실패 ({i + 1}/{tries}): {e}", file=sys.stderr)
            if "401" in str(e) or "404" in str(e) or "quota" in str(e):
                break
            time.sleep(wait * (i + 1))
    log_error(f"{label}: {last}")
    raise last


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def read_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def env(name: str, default=None, required=False):
    v = os.environ.get(name) or default
    if required and not v:
        log_error(f"환경변수 {name} 없음 (GitHub Secrets 확인)")
        sys.exit(f"환경변수 {name} 가 필요합니다 (GitHub Secrets 확인)")
    return v
