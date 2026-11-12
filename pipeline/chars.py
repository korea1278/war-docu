"""화면 업그레이드 2단계 ① 고정 캐릭터 라이브러리 (2026-11-12 사용자 확정).

정장 차림 볼(countryball) 캐릭터 — 플랫 2D, 투명 누끼 PNG.
한 번 만들어 모든 편에서 재사용한다 (stage 화면의 chars[].c = "<나라>_<포즈>").

python pipeline/chars.py            # 없는 것만 생성
python pipeline/chars.py kr_point   # 지정한 것만 다시 생성
결과: public/chars/<나라>_<포즈>.png (누끼), public/chars/raw/*.png (원본), public/chars/chars.json (서명)
그림 엔진: Gemini 2.5 Flash Image (GEMINI_API_KEY) — 장당 약 55원
"""
import base64
import hashlib
import io
import sys

from PIL import Image

from common import ROOT, env, read_json, retry, session, write_json

OUT = ROOT / "public" / "chars"

COUNTRIES = {
    "kr": "South Korea — the ball is painted exactly as the Taegukgi flag: pure white with a red-over-blue taeguk circle in the middle and four black trigram bars at the corners",
    "us": "United States — the ball is painted as the American flag: red and white horizontal stripes with a blue canton of white stars on the upper left",
    "cn": "People's Republic of China — the ball is painted as the Chinese flag: bright red with one large yellow star and four small yellow stars on the upper left",
    "nk": "North Korea — the ball is painted as the North Korean flag: blue top and bottom bands, thin white lines, a wide red middle band with a red star inside a white circle",
    "uk": "United Kingdom — the ball is painted as the Union Jack: dark blue with white and red crosses and diagonals",
    "su": "Soviet Union — the ball is painted as the Soviet flag: plain red with a small yellow hammer and sickle and a yellow-outlined star on the upper left",
    "un": "United Nations — the ball is painted as the UN flag: light sky blue with a white world map emblem surrounded by white olive branches",
}

POSES = {
    "idle": "standing upright calmly with arms relaxed at the sides, calm confident eyes",
    "plead": "pleading desperately with both small hands clasped together in front, eyes looking up, worried",
    "shrug": "shrugging with both small hands raised to the sides palms up, eyes half-closed, puzzled",
    "salute": "giving a crisp military salute with the right hand at the brow, serious determined eyes",
    "point": "pointing firmly to the right side of the frame with one arm fully extended, determined eyes",
    "shock": "shocked, both small hands raised beside the body, eyes wide open, a small open mouth",
}

PROMPT = (
    "Flat 2D vector cartoon illustration of exactly ONE countryball (polandball style) character. "
    "The character is a perfectly round ball representing {country}. "
    "Countryball eyes: two simple white oval eyes with thin black outlines, no pupils. "
    "The ball wears a small dark navy business suit jacket, white shirt collar and a red necktie on its lower half, "
    "with tiny black stick arms and short legs with black shoes. Pose: {pose}. "
    "Full body visible, centered, filling about 75% of the frame height. "
    "Thick clean black outlines, flat solid colors, no gradients, no cast shadow, no ground. "
    "Isolated on a plain pure white background. Absolutely no text, no letters, no speech bubbles, no extra characters."
)


def gen(s, prompt):
    key = env("GEMINI_API_KEY", required=True)
    model = env("GEMINI_IMAGE_MODEL") or "gemini-2.5-flash-image"
    r = s.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": key},
        json={"contents": [{"parts": [{"text": prompt}]}],
              "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}},
        timeout=300,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code} {r.text[:300]}")
    for c in r.json().get("candidates", []):
        for part in c.get("content", {}).get("parts", []):
            data = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if data:
                return Image.open(io.BytesIO(base64.b64decode(data)))
    raise RuntimeError(f"그림 없음: {r.text[:300]}")


def cut(img):
    """rembg isnet 누끼 → 여백 잘라 높이 900px 이내로."""
    img = img.convert("RGB")
    try:
        from rembg import new_session, remove
        global _RS
        try:
            _RS
        except NameError:
            _RS = new_session("isnet-general-use")
        out = remove(img, session=_RS)
    except Exception as e:  # noqa: BLE001
        print(f"  rembg 실패({e}) → 흰 배경 알파")
        from PIL import ImageFilter, ImageOps
        g = ImageOps.grayscale(img)
        a = g.point(lambda v: 255 if v < 232 else int((255 - v) * 255 / 23))
        out = img.copy()
        out.putalpha(a.filter(ImageFilter.GaussianBlur(1)))
    bbox = out.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    if bbox:
        out = out.crop(bbox)
    if out.height > 900:
        out = out.resize((round(out.width * 900 / out.height), 900), Image.LANCZOS)
    return out


def main(only):
    (OUT / "raw").mkdir(parents=True, exist_ok=True)
    man = read_json(OUT / "chars.json", {})
    s = session()
    made = 0
    for c, cdesc in COUNTRIES.items():
        for p, pdesc in POSES.items():
            k = f"{c}_{p}"
            prompt = PROMPT.format(country=cdesc, pose=pdesc)
            sig = hashlib.sha1(prompt.encode()).hexdigest()[:12]
            dst = OUT / f"{k}.png"
            if only and k not in only:
                continue
            if not only and man.get(k) == sig and dst.exists():
                continue
            print(f"CHAR {k}")
            img = retry(lambda: gen(s, prompt), tries=4, wait=20, label=f"char {k}")
            img.convert("RGB").save(OUT / "raw" / f"{k}.jpg", quality=92)
            cut(img).save(dst, optimize=True)
            man[k] = sig
            write_json(OUT / "chars.json", man)
            made += 1
    print(f"캐릭터 완료 — 새로 만든 것 {made}장")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
