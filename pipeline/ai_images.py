"""재연 일러스트·썸네일 배경 이미지 생성.

python pipeline/ai_images.py yongmunsan [--thumb]

이미지 엔진 (환경변수 IMAGE_PROVIDER, 기본 auto):
  auto        → GEMINI_API_KEY 있으면 gemini, 아니면 Cloudflare 키가 있으면 cloudflare, 없으면 pollinations
  gemini      → Google Gemini 2.5 Flash Image (Nano Banana). Google AI Pro 구독의 월 $10 Cloud 크레딧으로 결제
                GEMINI_API_KEY (Cloud Billing 연결된 프로젝트의 키), GEMINI_IMAGE_MODEL(기본 gemini-2.5-flash-image)
  cloudflare  → Cloudflare Workers AI FLUX.1 schnell (무료 하루 1만 뉴런 ≈ 그림 150장 이상)
                CF_ACCOUNT_ID, CF_API_TOKEN 필요
  pollinations→ Pollinations.ai FLUX (가입·키 없이 무료, 15초에 1장). POLLINATIONS_TOKEN 있으면 사용
  openai      → OpenAI gpt-image-1 (유료). OPENAI_API_KEY, OPENAI_IMAGE_MODEL, OPENAI_IMAGE_QUALITY

이미 만든 그림은 프롬프트가 같으면 엔진과 상관없이 그대로 재사용한다 (서명 공식 고정).
"""
import base64
import hashlib
import io
import sys
import time
import urllib.parse

from PIL import Image

from common import ep_dirs, env, load_board, read_json, retry, session, write_json

W, H = 1536, 1024


def fit(img):
    """3:2 (1536x1024)로 가운데 잘라 맞춤."""
    img = img.convert("RGB")
    w, h = img.size
    if abs(w / h - W / H) > 0.01:
        if w / h > W / H:
            nw = int(h * W / H)
            img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w * H / W)
            top = int((h - nh) * 0.4)  # 위쪽(하늘·얼굴) 조금 더 남김
            img = img.crop((0, top, w, top + nh))
    return img.resize((W, H), Image.LANCZOS)


def gen_openai(s, prompt):
    key = env("OPENAI_API_KEY", required=True)
    r = s.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": env("OPENAI_IMAGE_MODEL") or "gpt-image-1", "prompt": prompt, "size": "1536x1024",
              "quality": env("OPENAI_IMAGE_QUALITY") or "high", "n": 1},
        timeout=300,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code} {r.text[:300]}")
    return Image.open(io.BytesIO(base64.b64decode(r.json()["data"][0]["b64_json"])))


def gen_gemini(s, prompt):
    key = env("GEMINI_API_KEY", required=True)
    model = env("GEMINI_IMAGE_MODEL") or "gemini-2.5-flash-image"
    r = s.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": key},
        json={"contents": [{"parts": [{"text": prompt}]}],
              "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "3:2"}}},
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


def gen_cloudflare(s, prompt):
    acc, tok = env("CF_ACCOUNT_ID", required=True), env("CF_API_TOKEN", required=True)
    r = s.post(
        f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        headers={"Authorization": f"Bearer {tok}"},
        json={"prompt": prompt[:2000], "steps": 8},
        timeout=180,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code} {r.text[:300]}")
    return Image.open(io.BytesIO(base64.b64decode(r.json()["result"]["image"])))


def gen_pollinations(s, prompt, seed):
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:1800], safe="")
    q = {"width": W, "height": H, "model": "flux", "nologo": "true", "enhance": "false", "seed": seed}
    hdr = {}
    if env("POLLINATIONS_TOKEN"):
        hdr["Authorization"] = f"Bearer {env('POLLINATIONS_TOKEN')}"
    r = s.get(url, params=q, headers=hdr, timeout=300)
    if r.status_code >= 400 or not r.headers.get("content-type", "").startswith("image"):
        raise RuntimeError(f"{r.status_code} {r.headers.get('content-type')} {r.text[:200]}")
    time.sleep(16)  # 무료 등급 속도 제한 (15초에 1장)
    return Image.open(io.BytesIO(r.content))


def main(ep, thumb=False):
    prov = (env("IMAGE_PROVIDER") or "auto").lower()
    if prov == "auto":
        prov = ("gemini" if env("GEMINI_API_KEY") else
                "cloudflare" if env("CF_ACCOUNT_ID") and env("CF_API_TOKEN") else "pollinations")
    board = load_board(ep)
    if board.get("assets_ep"):
        print(f"AI 이미지: {board['assets_ep']} 에피소드 것을 재사용")
        return
    _, out = ep_dirs(ep)
    d = out / "ai"
    d.mkdir(exist_ok=True)
    man = read_json(out / "ai.json", {})
    used = {v["img"] for sc in board["scenes"] for v in [sc["visual"], *sc.get("visuals", [])] if v["type"] == "ai"}
    for sc in board["scenes"]:
        for it in sc["visual"].get("items", []) if sc["visual"]["type"] == "teaser" else []:
            used.add(it["img"])
    used |= {k for k in board.get("ai_images", {}) if k.startswith("thumb_")}  # 썸네일 전용 그림
    s = session()
    print(f"이미지 엔진: {prov}")
    for name in sorted(used):
        prompt = board["ai_images"][name]
        # 서명은 예전 공식 그대로 (엔진을 바꿔도 이미 만든 그림을 다시 그리지 않도록)
        sig = hashlib.sha1(f"gpt-image-1|high|{prompt}".encode()).hexdigest()[:12]
        p = d / f"{name}.jpg"
        if man.get(name) == sig and p.exists():
            continue
        if name.startswith("thumb_") and p.exists() and not thumb:
            continue  # 썸네일 배경은 thumb 모드에서만 다시 그림 (영상 렌더 중 과금·실패 방지)
        print(f"AI IMG {name} ({prov})")
        seed = int(sig[:6], 16)
        if prov == "openai":
            call = lambda: gen_openai(s, prompt)  # noqa: E731
        elif prov == "gemini":
            call = lambda: gen_gemini(s, prompt)  # noqa: E731
        elif prov == "cloudflare":
            call = lambda: gen_cloudflare(s, prompt)  # noqa: E731
        else:
            call = lambda: gen_pollinations(s, prompt, seed)  # noqa: E731
        img = retry(call, tries=4, wait=20, label=f"image {name}")
        fit(img).save(p, quality=92)
        man[name] = sig
        write_json(out / "ai.json", man)
    # 실존 인물(EP11 맥아더 등)은 AI로 그리지 않고 공개 사진(위키미디어, 미 정부 저작물)을 받아 누끼 — 스토리보드 "thumb_photo"
    tp = board.get("thumb_photo")
    if tp and (thumb or not (d / "thumb_subject.png").exists()):
        from photos import fetch_img, file_info
        info = retry(lambda: file_info(s, tp), label=f"thumb photo {tp}")
        fetch_img(s, info["url"]).save(d / "thumb_subject.jpg", quality=95)
        man["thumb_subject"] = f"photo:{tp}"
        write_json(out / "ai.json", man)
        print(f"  썸네일 인물 사진: {tp} ({info.get('license')})")
        cutout(d / "thumb_subject.jpg", d / "thumb_subject.png")
    elif "thumb_subject" in used and (thumb or not (d / "thumb_subject.png").exists()):
        cutout(d / "thumb_subject.jpg", d / "thumb_subject.png")
    print("AI 이미지 완료")


def cutout(src, dst):
    """썸네일 표준 Layer 3: 인물 누끼(배경 제거) PNG. rembg가 있으면 사용, 없거나 실패하면 흰 배경 기준 알파로 대체."""
    from PIL import ImageFilter, ImageOps
    img = Image.open(src).convert("RGB")
    try:
        from rembg import remove
        out = remove(img)
        print("  누끼: rembg")
    except Exception as e:  # noqa: BLE001
        print(f"  누끼: rembg 사용 불가({e}) → 흰 배경 알파로 대체")
        g = ImageOps.grayscale(img)
        a = g.point(lambda v: 255 if v < 225 else int((255 - v) * 255 / 30))
        a = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(2))
        out = img.copy()
        out.putalpha(a)
    bbox = out.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    if bbox:
        out = out.crop(bbox)
    out.save(dst)


if __name__ == "__main__":
    main(sys.argv[1], thumb="--thumb" in sys.argv)
