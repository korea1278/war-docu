"""썸네일 v5 주인공 누끼 (2026-11-26 · war-docu·map-of-war 공통 · docs/THUMB_STANDARD_V5.md)

PAROHO_V2["<ep>"](및 alts)에 `cut: "ep/<ep>/thumbcut/<이름>.png"`가 있으면, 그 항목의 배경(bg — 컬러 복원본이 있으면 그것)에서
주인공만 따낸 **배경과 같은 크기** 투명 PNG를 만든다 → HitThumb가 배경 위에 같은 자리로 겹쳐 흰 테두리 빛을 준다.
(ai_images.cutout은 잘라서(crop) 저장하므로 자리가 어긋나 쓰지 않는다)
모델: rembg birefnet-general-lite(MIT) → isnet → u2net, 별도 프로세스(메모리 부족으로 죽어도 다음 모델). 전부 실패하면 만들지 않음(썸네일은 누끼 없이 렌더)
이미 있으면 다시 만들지 않는다 (다시 만들려면 파일을 지우고 실행)

사용: python3 thumb_cut.py <ep>
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"


def entry_block(ep: str) -> str:
    src = (ROOT / "remotion" / "Thumbnail.tsx").read_text(encoding="utf-8")
    i = src.find("export const PAROHO_V2")
    j = src.find(f'"{ep}": {{', i)
    if i < 0 or j < 0:
        return ""
    k = src.find(f"// ALTS:{ep}", j)
    if k < 0:
        k = src.find('\n  "', j + 5)
    return src[j: k if k > 0 else j + 4000]


def shown_bg(bg: str, block: str) -> str:
    """Thumbnail.tsx v2Bg와 같은 규칙: 흑백 사진의 DDColor 컬러 복원본이 있으면 그것 (gray: true면 원본)"""
    if re.search(r"\bgray:\s*true", block):
        return bg
    parts = bg.split("/")
    cp = "/".join(parts[:2] + ["thumbcolor", "_".join(parts[2:]).rsplit(".", 1)[0] + ".jpg"])
    return cp if (PUB / cp).exists() else bg


def make_cut(src: Path, dst: Path) -> bool:
    code = ("import sys; from PIL import Image; from rembg import remove, new_session; "
            "remove(Image.open(sys.argv[1]).convert('RGB'), session=new_session(sys.argv[2])).save(sys.argv[3])")
    for model in ("birefnet-general-lite", "isnet-general-use", "u2net"):
        tmp = Path(tempfile.mkdtemp()) / "cut.png"
        try:
            r = subprocess.run([sys.executable, "-c", code, str(src), model, str(tmp)], capture_output=True, text=True, timeout=900)
        except Exception as e:  # noqa: BLE001
            print(f"  [cut] {model} 실패 {e}")
            continue
        if r.returncode == 0 and tmp.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            tmp.replace(dst)
            print(f"  [cut] {dst.relative_to(ROOT)} ← {src.relative_to(ROOT)} ({model})")
            return True
        print(f"  [cut] {model} 실패(코드 {r.returncode}) {r.stderr.strip()[-160:]}")
    return False


def main(ep: str):
    block = entry_block(ep)
    if not block:
        print(f"[cut] PAROHO_V2에 {ep} 없음 — 건너뜀")
        return
    base_bg = (re.search(r'\bbg:\s*"([^"]+)"', block) or [None, None])[1]
    # 본안과 시안(alts)마다 bg·cut 짝 — 시안에 bg가 없으면 본안 bg
    pairs = []
    for m in re.finditer(r'\bcut:\s*"([^"]+)"', block):
        seg = block[: m.start()]
        cur = seg[max(seg.rfind("{"), 0):]
        bgm = re.search(r'\bbg:\s*"([^"]+)"', cur)
        pairs.append(((bgm.group(1) if bgm else base_bg), m.group(1)))
    if not pairs:
        print(f"[cut] {ep}: cut 지정 없음 — 건너뜀")
        return
    for bg, cut in dict.fromkeys(pairs):
        dst = PUB / cut
        if dst.exists():
            print(f"  [cut] 이미 있음 {cut}")
            continue
        src = PUB / shown_bg(bg, block)
        if not src.exists():
            print(f"  [cut] 배경 파일 없음 {src}")
            continue
        make_cut(src, dst)


if __name__ == "__main__":
    main(sys.argv[1])
