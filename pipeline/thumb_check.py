"""썸네일 점검 시트 (2026-11-26 · war-docu·map-of-war 공통 · docs/THUMB_STANDARD_V5.md)

렌더한 썸네일 시안(thumbnails/<ep>_ko_A.png, _A2, _A3 …)을 한 장에 모아 세 가지 보기로 나란히 보여 준다
  1. 원본 (640px)
  2. TV 보기 — **50% 테스트**: 위쪽 절반만 보이고 아래는 TV 화면처럼 가려짐. 여기서 '무슨 영상인지·궁금한지'가 보여야 함
  3. 휴대폰 작은 크기 (홈 피드 약 360px · 추천 목록 약 168px) — 글자가 읽히는지, 주인공이 먼저 보이는지
→ thumbnails/<ep>_check.jpg (Actions thumb 모드가 자동 생성·커밋)

사용: python3 thumb_check.py <ep>
"""
import glob
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "public" / "fonts" / "Pretendard-Black.woff2"


def font(size):
    try:
        return ImageFont.truetype(str(FONT), size)  # 저장소 글꼴 (러너에 한글 글꼴이 없어도 됨)
    except Exception:  # noqa: BLE001
        pass
    for p in ("/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main(ep):
    files = sorted(glob.glob(str(ROOT / "thumbnails" / f"{ep}_ko_A*.png")), key=lambda p: int(re.search(r"_A(\d*)\.png$", p).group(1) or 1))
    if not files:
        print(f"[check] {ep}: 썸네일 없음")
        return
    W, PAD, ROWH = 640, 24, 360 + 60
    sheet = Image.new("RGB", (PAD + W + PAD + W + PAD + 360 + PAD + 168 + PAD, PAD + ROWH * len(files) + 40), "#16181c")
    d = ImageDraw.Draw(sheet)
    f1, f2 = font(26), font(18)
    heads = [("원본", PAD), ("TV 보기 (50% 테스트)", PAD * 2 + W), ("휴대폰 홈", PAD * 3 + W * 2), ("추천 목록", PAD * 4 + W * 2 + 360)]
    for t, x in heads:
        d.text((x, 8), t, fill="#f4c430", font=f1)
    for r, fp in enumerate(files):
        y = 50 + r * ROWH
        im = Image.open(fp).convert("RGB")
        a = im.resize((W, 360), Image.LANCZOS)
        sheet.paste(a, (PAD, y))
        # TV 보기: 위 절반만 보이고 아래는 TV 화면처럼 가려짐 (제목은 리모컨 '아래'를 눌러야 보임)
        tv = a.copy()
        td = ImageDraw.Draw(tv)
        td.rectangle([0, 180, W, 360], fill="#0f0f0f")
        td.rounded_rectangle([20, 200, 420, 222], 6, fill="#2a2a2a")
        td.rounded_rectangle([20, 236, 300, 254], 6, fill="#222")
        td.text((20, 290), "▼ 아래쪽은 TV에서 안 보임", fill="#777", font=f2)
        sheet.paste(tv, (PAD * 2 + W, y))
        sheet.paste(im.resize((360, 202), Image.LANCZOS), (PAD * 3 + W * 2, y))
        sheet.paste(im.resize((168, 94), Image.LANCZOS), (PAD * 4 + W * 2 + 360, y))
        d.text((PAD, y + 366), Path(fp).name, fill="#cfd5dc", font=f2)
    out = ROOT / "thumbnails" / f"{ep}_check.jpg"
    sheet.save(out, quality=88)
    print(f"[check] {out.relative_to(ROOT)} — 시안 {len(files)}개")


if __name__ == "__main__":
    main(sys.argv[1])
