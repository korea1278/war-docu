"""장면별 미리보기 스틸 → 콘택트 시트 (렌더 전 점검용).

python pipeline/preview.py yongmunsan [번들폴더]
결과: previews/<ep>/sheet_1.jpg ... (장면 6개씩 2열)
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import ROOT


def main(ep, bundle):
    tl = json.loads((ROOT / "public" / "ep" / ep / "timeline.json").read_text(encoding="utf-8"))
    out = ROOT / "previews" / ep
    out.mkdir(parents=True, exist_ok=True)
    tmp = ROOT / "out" / "stills"
    tmp.mkdir(parents=True, exist_ok=True)
    jobs = []
    for sc in tl["scenes"]:
        f = int((sc["start"] + sc["dur"] * 0.8) * tl["fps"])
        jobs.append((sc["id"], f))

    def still(job):
        sid, f = job
        p = tmp / f"{sid}.jpg"
        subprocess.run(["npx", "remotion", "still", bundle, "Documentary", str(p), f"--frame={f}", "--image-format=jpeg",
                        "--scale=0.5", "--log=error", f'--props={{"ep":"{ep}"}}'], cwd=ROOT, check=False)
        return sid, p

    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(still, jobs))
    try:
        font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 28)
    except Exception:
        font = ImageFont.load_default()
    per = 8
    for k in range(0, len(res), per):
        chunk = res[k:k + per]
        sheet = Image.new("RGB", (1920, 540 * ((len(chunk) + 1) // 2)), (0, 0, 0))
        d = ImageDraw.Draw(sheet)
        for i, (sid, p) in enumerate(chunk):
            x, y = (i % 2) * 960, (i // 2) * 540
            if p.exists():
                sheet.paste(Image.open(p).convert("RGB").resize((960, 540)), (x, y))
            d.rectangle([x, y, x + 90, y + 40], fill=(255, 220, 0))
            d.text((x + 8, y + 2), sid, fill=(0, 0, 0), font=font)
        sheet.save(out / f"sheet_{k // per + 1}.jpg", quality=72)
    print("미리보기 완료:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "remotion/index.ts")
