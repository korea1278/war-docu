"""사진 후보 대량 수집(스카우트) → previews/scout/*.jpg 번호 시트 + catalog.json
사람(또는 Claude)이 시트를 보고 photo_pins.json 에 파일명을 고정하는 용도.

python pipeline/scout.py
"""
import json
import sys
import time

from PIL import Image, ImageDraw, ImageFont

from common import ROOT, write_json, session
from photos import BAD, API, credit_ko, fetch_img

QUERIES = [
    "Korean War 1951 infantry", "Korean War ROK Army", "Republic of Korea Army soldiers Korean War", "ROK troops 1951",
    "South Korean soldiers 1950", "Korean War hill", "Korean War machine gun", "Korean War foxhole", "Korean War trench",
    "Korean War artillery 1951", "155mm howitzer Korea", "105mm howitzer Korea", "Korean War artillery night",
    "Chinese People's Volunteer Army", "Chinese prisoners Korea", "Chinese POW Korean War", "Chinese Communist troops Korea",
    "Korean War May 1951", "Operation Killer Korea", "Operation Ripper", "Korean War tank 1951", "Korean War refugees 1951",
    "Korean War mountains", "Hwachon Dam", "Hwachon reservoir", "Chang Do-young", "장도영", "Syngman Rhee", "이승만",
    "파로호", "Paroho", "Hwacheon lake", "화천호", "용문산", "Yongmunsan", "Yongmun mountain", "용문산 전투", "화천댐",
    "국군 제6사단", "Korean War soldier portrait", "Korean War wounded soldiers", "Korean War advance north",
    "Korean War Marines 1951", "Korean War US Army 1951 Korea hill", "Korean War pursuit", "Korean War captured Chinese",
    "Korean War night", "Korean War flare", "6.25 전쟁 국군", "한국전쟁 국군", "한국전쟁 중공군", "Korean War memorial Gyeonggi",
]


def run(ep=None):
    s = session()
    queries = QUERIES
    if ep and (ROOT / "episodes" / ep / "scout_queries.json").exists():
        queries = json.loads((ROOT / "episodes" / ep / "scout_queries.json").read_text(encoding="utf-8"))
    seen, cat = set(), []
    for q in queries:
        try:
            r = s.get(API, params={
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 14,
                "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 320,
            }, timeout=60)
            pages = sorted((r.json().get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
        except Exception as e:
            print("!", q, e)
            continue
        for p in pages:
            t = p["title"]
            ii = (p.get("imageinfo") or [{}])[0]
            if t in seen or BAD.search(t) or ii.get("mime") not in ("image/jpeg", "image/png"):
                continue
            if max(ii.get("width", 0), ii.get("height", 0)) < 700:
                continue
            seen.add(t)
            meta = ii.get("extmetadata", {})
            desc = meta.get("ImageDescription", {}).get("value", "")
            cat.append({"id": len(cat), "q": q, "title": t, "thumb": ii.get("thumburl"), "w": ii["width"], "h": ii["height"],
                        "license": meta.get("LicenseShortName", {}).get("value", ""), "credit": credit_ko(meta),
                        "desc": desc[:200]})
        time.sleep(0.3)
    out = ROOT / "previews" / (f"scout_{ep}" if ep else "scout")
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "catalog.json", cat)
    try:
        font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 20)
    except Exception:
        font = ImageFont.load_default()
    tw, th, cols, per = 320, 220, 6, 48
    for k in range(0, len(cat), per):
        chunk = cat[k:k + per]
        sheet = Image.new("RGB", (cols * tw, ((len(chunk) + cols - 1) // cols) * th), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        for i, c in enumerate(chunk):
            x, y = (i % cols) * tw, (i // cols) * th
            try:
                im = fetch_img(s, c["thumb"])
                im.thumbnail((tw - 6, th - 6))
                sheet.paste(im, (x + 3, y + 3))
            except Exception:
                pass
            d.rectangle([x, y, x + 54, y + 26], fill=(255, 220, 0))
            d.text((x + 4, y + 1), str(c["id"]), fill=(0, 0, 0), font=font)
        sheet.save(out / f"scout_{k // per + 1}.jpg", quality=78)
    print("후보", len(cat))


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "pipeline"))
    run(sys.argv[1] if len(sys.argv) > 1 else None)
