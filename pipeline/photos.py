"""위키미디어 공용(Commons)에서 사료 사진 검색·다운로드.

python pipeline/photos.py yongmunsan
- 스토리보드의 visual.q (검색어) 마다 후보를 찾아 1장을 고릅니다.
- episodes/<ep>/photo_pins.json 에 {"검색어#번호": "File:정확한파일명.jpg"} 또는 {"검색어#번호": 후보순번} 으로 고정 가능.
- public/ep/<ep>/photos_review.jpg : 검색어별 후보 썸네일(번호 표시) — 사진 교체할 때 참고.
"""
import io
import re
import sys
import time

from PIL import Image, ImageDraw, ImageFont

from common import ROOT, ep_dirs, load_board, read_json, retry, session, write_json

API = "https://commons.wikimedia.org/w/api.php"
BAD = re.compile(r"(map|flag|logo|coat[_ ]of[_ ]arms|emblem|insignia|chart|diagram|stamp|seal|\.svg|\.tif|\.pdf|signature|medal|badge|poster)", re.I)
PERSON_TYPES = {"person"}


def keys_from_board(board):
    out = {}
    for sc in board["scenes"]:
        v = sc["visual"]
        if v.get("q"):
            k = f"{v['q']}#{v.get('alt', 0)}"
            out.setdefault(k, {"q": v["q"], "alt": v.get("alt", 0), "person": v["type"] in PERSON_TYPES})
    return out


def credit_ko(meta):
    txt = " ".join(str(meta.get(k, {}).get("value", "")) for k in ("Artist", "Credit", "ImageDescription"))
    for pat, ko in [
        ("Republic of Korea MND|Defense Media Agency|국방부|국방홍보원", "대한민국 국방부"), ("Marine", "미 해병대"), ("Navy", "미 해군"), ("Air Force", "미 공군"),
        ("Army", "미 육군"), ("NARA|National Archives", "미 국립문서기록관리청"),
    ]:
        if re.search(pat, txt, re.I):
            return f"출처: {ko} / Wikimedia Commons"
    return "출처: Wikimedia Commons"


def search(s, q, person):
    def call():
        r = s.get(API, params={
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 20,
            "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1920,
        }, timeout=60)
        r.raise_for_status()
        return r.json()

    data = retry(call, label=f"search {q}")
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    cands = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        title = p["title"]
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/webp"):
            continue
        if BAD.search(title):
            continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if w < 700 and h < 700:
            continue
        ratio = w / max(h, 1)
        if not person and ratio < 0.9:
            continue
        meta = ii.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        if "fair" in lic.lower():
            continue
        cands.append({
            "title": title, "url": ii.get("thumburl") or ii["url"], "w": w, "h": h,
            "license": lic, "credit": credit_ko(meta), "page": ii.get("descriptionurl"),
        })
    return cands


def file_info(s, title):
    r = s.get(API, params={
        "action": "query", "format": "json", "titles": title, "prop": "imageinfo",
        "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1920,
    }, timeout=60)
    r.raise_for_status()
    p = next(iter(r.json()["query"]["pages"].values()))
    ii = p["imageinfo"][0]
    meta = ii.get("extmetadata", {})
    return {"title": title, "url": ii.get("thumburl") or ii["url"], "w": ii["width"], "h": ii["height"],
            "license": meta.get("LicenseShortName", {}).get("value", ""), "credit": credit_ko(meta),
            "page": ii.get("descriptionurl")}


def fetch_img(s, url):
    def call():
        r = s.get(url, timeout=120)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    return retry(call, label="download")


def slug(k):
    return re.sub(r"[^a-zA-Z0-9]+", "_", k).strip("_").lower()[:60]


def main(ep):
    src, out = ep_dirs(ep)
    board = load_board(ep)
    pins = read_json(src / "photo_pins.json", {})
    pdir = out / "photos"
    pdir.mkdir(exist_ok=True)
    manifest = read_json(out / "photos.json", {})
    s = session()
    review_rows = []
    for k, info in keys_from_board(board).items():
        pin = pins.get(k)
        prev = manifest.get(k)
        fname = f"{slug(k)}.jpg"
        if prev and prev.get("pin") == pin and (pdir / fname).exists():
            continue
        print(f"PHOTO {k}")
        chosen = None
        if isinstance(pin, str):
            cands = []
            chosen = retry(lambda: file_info(s, pin), label=f"file {pin}")
        else:
            cands = search(s, info["q"], info["person"])
            time.sleep(0.5)
        if chosen:
            pass
        elif isinstance(pin, int) and pin < len(cands):
            chosen = cands[pin]
        else:
            alt = info["alt"]
            chosen = cands[alt] if len(cands) > alt else (cands[0] if cands else None)
        if cands:
            review_rows.append((k, cands[:8]))
        if not chosen:
            print(f"  ! '{info['q']}' 결과 없음 — 대체 배경 사용")
            manifest[k] = {"file": None, "cands": [], "pin": pin}
            continue
        img = fetch_img(s, chosen["url"])
        img.thumbnail((2400, 2400))
        img.save(pdir / fname, quality=90)
        manifest[k] = {"file": f"photos/{fname}", "title": chosen["title"], "credit": chosen["credit"],
                       "license": chosen["license"], "page": chosen["page"], "w": img.width, "h": img.height,
                       "pin": pin, "cands": cands[:8]}
        time.sleep(0.5)
    write_json(out / "photos.json", manifest)
    make_review(s, review_rows, out / "photos_review.jpg")
    print("사진 완료")


def make_review(s, rows, path):
    if not rows:
        return
    tw, th, cols = 240, 160, 8
    sheet = Image.new("RGB", (cols * tw + 300, len(rows) * (th + 10)), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 14)
    except Exception:
        font = ImageFont.load_default()
    for r, (k, cands) in enumerate(rows):
        y = r * (th + 10)
        d.text((5, y + 5), k[:40], fill=(255, 255, 0), font=font)
        for c, cand in enumerate(cands[:cols]):
            try:
                url = cand["url"].replace("/1920px-", "/240px-") if "/1920px-" in cand["url"] else cand["url"]
                im = fetch_img(s, url)
                im.thumbnail((tw - 4, th - 4))
                sheet.paste(im, (300 + c * tw, y))
                d.rectangle([300 + c * tw, y, 330 + c * tw, y + 18], fill=(0, 0, 0))
                d.text((304 + c * tw, y), str(c), fill=(255, 255, 255), font=font)
            except Exception:
                pass
    sheet.save(path, quality=80)


if __name__ == "__main__":
    main(sys.argv[1])
