"""자막 노출 검사 — [자막 렌더링 무결성 원칙] (CLAUDE.md)

python pipeline/check_subs.py <ep> <번들폴더>
- timeline.json의 모든 장면에서, 나레이션 줄마다 첫 자막 청크의 가운데 시점을 실제로 렌더(스틸)한다
- 화면 하단에 자막 박스(초록 테두리 #22594a)가 보이는지 픽셀로 확인
- 하나라도 안 보이면 장면 id·시각을 출력하고 exit 1 → 본 렌더링(MP4)을 막는다
결과: logs/subs_check_<ep>.txt
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

from common import ROOT, log_error

BORDER = (0x22, 0x59, 0x4A)  # theme.ts C.subBorder
SCALE = 0.5
MIN_PIX = 150  # 0.5배 스틸에서 테두리 픽셀 최소 개수 (정상 자막은 수천 개)


def border_pixels(p: Path) -> int:
    im = Image.open(p).convert("RGB")
    w, h = im.size
    band = im.crop((0, int(h * 0.72), w, h))  # 자막 자리 (하단 28%)
    px = band.tobytes()
    n = 0
    for i in range(0, len(px), 3):
        if abs(px[i] - BORDER[0]) < 22 and abs(px[i + 1] - BORDER[1]) < 22 and abs(px[i + 2] - BORDER[2]) < 22:
            n += 1
    return n


def main(ep, bundle):
    tl = json.loads((ROOT / "public" / "ep" / ep / "timeline.json").read_text(encoding="utf-8"))
    fps = tl["fps"]
    tmp = ROOT / "out" / "subs_check"
    tmp.mkdir(parents=True, exist_ok=True)
    jobs = []
    for sc in tl["scenes"]:
        for li, ln in enumerate(sc["lines"]):
            ch = [c for c in ln.get("chunks", []) if c["end"] - c["start"] >= 0.3]
            if not ch:
                jobs.append((sc["id"], li, sc["visual"]["type"], None))  # 자막 청크 자체가 없음 = 실패
                continue
            c = ch[0]
            t = sc["start"] + (c["start"] + c["end"]) / 2
            jobs.append((sc["id"], li, sc["visual"]["type"], int(round(t * fps))))

    def run(job):
        sid, li, ty, f = job
        if f is None:
            return job, -1
        p = tmp / f"{sid}_{li}.png"
        p.unlink(missing_ok=True)
        cmd = ["npx", "remotion", "still", bundle, "Documentary", str(p), f"--frame={f}", "--image-format=png",
               f"--scale={SCALE}", "--log=error", f'--props={{"ep":"{ep}"}}']
        if os.environ.get("REMOTION_BROWSER"):  # 세션 안에서 돌릴 때 (Actions는 기본 브라우저)
            cmd.append(f"--browser-executable={os.environ['REMOTION_BROWSER']}")
        r = subprocess.run(cmd, cwd=ROOT, check=False, capture_output=True, text=True)
        if not p.exists():
            print(f"  스틸 실패 {sid}[{li}]: {(r.stderr or r.stdout).strip()[-300:]}")
            return job, -2
        return job, border_pixels(p)

    with ThreadPoolExecutor(2) as ex:
        res = list(ex.map(run, jobs))
    bad = [(j, n) for j, n in res if n < MIN_PIX]
    lines = [f"{j[0]}[{j[1]}] {j[2]:<10} frame {j[3]}  테두리 {n}px  {'OK' if n >= MIN_PIX else '자막 안 보임'}" for j, n in res]
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / f"subs_check_{ep}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"자막 노출 검사 {ep}: {len(res) - len(bad)}/{len(res)} 통과")
    if bad:
        for j, n in bad:
            msg = f"{ep}: 자막 안 보임 — {j[0]} {j[1] + 1}번째 줄 ({j[2]}, frame {j[3]}, 테두리 {n}px)"
            print("  ! " + msg)
            log_error(msg)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1], str(Path(sys.argv[2]).resolve()))
