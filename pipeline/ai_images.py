"""재연 일러스트·썸네일 배경 이미지 생성.

python pipeline/ai_images.py yongmunsan [--thumb]

이미지 엔진 (환경변수 IMAGE_PROVIDER, 기본 auto):
  auto        → (2026-11-18 사용자 결정: Gemini 충전 중단) Cloudflare 키가 있으면 cloudflare, 없으면 pollinations.
                Gemini는 IMAGE_PROVIDER=gemini 로 직접 지정할 때만 쓴다
  gemini      → Google Gemini 2.5 Flash Image (Nano Banana). Google AI Pro 구독의 월 $10 Cloud 크레딧으로 결제
                GEMINI_API_KEY (Cloud Billing 연결된 프로젝트의 키), GEMINI_IMAGE_MODEL(기본 gemini-2.5-flash-image)
  cloudflare  → Cloudflare Workers AI FLUX.1 schnell (무료 하루 1만 뉴런, UTC 0시=한국 오전 9시 초기화)
                1024x1024 4단계 = 4조각x4.8 + 4단계x9.6 ≈ 58뉴런/장 → 하루 약 170장 (war-docu·map-of-war 공용 계정)
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

from common import ep_dirs, env, load_board, log_error, read_json, retry, session, write_json

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


CF_ACC = {}


def cf_account(s, tok):
    """CF_ACCOUNT_ID가 비어 있으면 토큰으로 계정 목록을 조회해 첫 계정을 쓴다 (2026-11-18 · 계정 ID 비밀값을 못 찾은 경우 대비)"""
    if env("CF_ACCOUNT_ID"):
        return env("CF_ACCOUNT_ID")
    if "id" not in CF_ACC:
        r = s.get("https://api.cloudflare.com/client/v4/accounts", headers={"Authorization": f"Bearer {tok}"}, timeout=60)
        res = (r.json() or {}).get("result") or [] if r.status_code < 400 else []
        if not res:
            raise RuntimeError(f"403 CF_ACCOUNT_ID 비어 있음 + 토큰으로 계정 조회 불가 ({r.status_code} {r.text[:150]})")
        CF_ACC["id"] = res[0]["id"]
        print(f"  Cloudflare 계정 자동 확인: {res[0].get('name', '')} (계정 {len(res)}개 중 첫 번째)")
    return CF_ACC["id"]


def gen_cloudflare(s, prompt, seed=0):
    tok = env("CF_API_TOKEN", required=True)
    acc = cf_account(s, tok)
    r = s.post(
        f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        headers={"Authorization": f"Bearer {tok}"},
        json={"prompt": prompt[:2000], "steps": int(env("CF_STEPS") or 4)},  # seed는 Cloudflare가 받지 않음(400)
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


def no_credit(e) -> bool:
    """크레딧·한도 소진 (다시 시도해도 안 되는 오류) — 2026-11-18 EP01 본 렌더가 Gemini 402로 통째로 실패한 뒤 추가"""
    t = str(e)
    return any(k in t for k in ("402", "429", "RESOURCE_EXHAUSTED", "insufficient_quota", "credits are depleted", "billing", "quota", "401", "403",
                                "allocation", "4006", "neurons"))  # Cloudflare 하루 무료 한도 소진 포함


def placeholder():
    """그림을 끝내 못 만들었을 때 렌더가 멈추지 않도록 쓰는 어두운 자리 표시 그림 (logs/errors.txt에 반드시 기록)"""
    img = Image.new("RGB", (W, H), (24, 22, 20))
    px = img.load()
    for y in range(H):
        for x in range(0, W, 4):
            v = int(24 + 18 * (1 - abs(y - H / 2) / (H / 2)))
            for k in range(4):
                if x + k < W:
                    px[x + k, y] = (v, v - 2, v - 4)
    return img


def main(ep, thumb=False):
    prov = (env("IMAGE_PROVIDER") or "auto").lower()
    if prov == "auto":
        prov = "cloudflare" if env("CF_API_TOKEN") else "pollinations"  # 계정 ID는 비어 있어도 토큰으로 자동 조회
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
    DEAD = {"credit": False}
    NEW = {"n": 0}
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
            call = lambda: gen_cloudflare(s, prompt, seed)  # noqa: E731
        else:
            call = lambda: gen_pollinations(s, prompt, seed)  # noqa: E731
        # 크레딧 소진이면 같은 엔진을 4번 다시 부르지 않고 곧바로 대체 경로로 (렌더 전체가 멈추지 않게)
        img, err = None, None
        if not DEAD["credit"]:
            try:
                img = call()
            except Exception as e:  # noqa: BLE001
                err = e
                if no_credit(e):
                    DEAD["credit"] = True
                    log_error(f"{ep}: 이미지 엔진 {prov} 크레딧·권한 문제({str(e)[:120]}) → 이번 실행은 대체 경로 사용")
                else:
                    try:
                        img = retry(call, tries=3, wait=20, label=f"image {name}")
                    except Exception as e2:  # noqa: BLE001
                        err = e2
        if img is None:
            if p.exists():
                # 예전 그림이 있으면 그대로 쓰고 서명은 그대로 둔다 (크레딧이 돌아오면 다음 실행 때 다시 그림)
                log_error(f"{ep}: 그림 {name} 새로 그리기 실패 → 기존 그림 유지 ({str(err)[:100]})")
                continue
            if prov != "pollinations":
                try:
                    img = retry(lambda: gen_pollinations(s, prompt, seed), tries=3, wait=20, label=f"image {name} (pollinations 대체)")
                    log_error(f"{ep}: 그림 {name} → {prov} 실패로 무료 pollinations 그림으로 대체 (확인 필요)")
                except Exception as e3:  # noqa: BLE001
                    err = e3
            if img is None:
                placeholder().save(p, quality=92)
                log_error(f"{ep}: ⚠ 그림 {name} 생성 실패 → 어두운 자리 표시 그림으로 렌더 계속 (업로드 전 교체 필요): {str(err)[:120]}")
                continue
            fit(img).save(p, quality=92)
            continue  # 대체 그림은 서명을 남기지 않음 → 원래 엔진이 살아나면 다시 그림
        fit(img).save(p, quality=92)
        man[name] = sig
        NEW["n"] += 1
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
    if NEW["n"]:
        msg = f"{ep}: 새 그림 {NEW['n']}장 ({prov})"
        if prov == "cloudflare":
            msg += f" · 약 {NEW['n'] * 58}뉴런 사용 (하루 무료 1만, 두 저장소 공용)"
        log_error(msg)
    print("AI 이미지 완료")


def cutout(src, dst):
    """썸네일 표준 Layer 3: 인물 누끼(배경 제거) PNG. rembg가 있으면 사용, 없거나 실패하면 흰 배경 기준 알파로 대체."""
    from PIL import ImageFilter, ImageOps
    img = Image.open(src).convert("RGB")
    out = None
    # 2026-11-24: BiRefNet(MIT, 머리카락·군모 테두리까지 깔끔) 우선 → 실패하면 예전 isnet → 흰 배경 알파
    # BiRefNet은 메모리를 6GB 넘게 씀(Actions 러너 16GB는 충분) — 메모리 부족으로 강제 종료돼도
    # 이 스크립트가 같이 죽지 않게 별도 프로세스에서 돌린다
    import subprocess
    import tempfile
    from pathlib import Path
    for model in ("birefnet-general-lite", "isnet-general-use", "u2net"):
        tmp = Path(tempfile.mkdtemp()) / "cut.png"
        code = ("import sys; from PIL import Image; from rembg import remove, new_session; "
                "remove(Image.open(sys.argv[1]).convert('RGB'), session=new_session(sys.argv[2])).save(sys.argv[3])")
        try:
            r = subprocess.run([sys.executable, "-c", code, str(src), model, str(tmp)], capture_output=True, text=True, timeout=900)
            if r.returncode == 0 and tmp.exists():
                out = Image.open(tmp).convert("RGBA")
                print(f"  누끼: rembg {model}")
                break
            print(f"  누끼: {model} 실패(코드 {r.returncode}) {r.stderr.strip()[-160:]}")
        except Exception as e:  # noqa: BLE001
            print(f"  누끼: {model} 실패({str(e)[:120]})")
    if out is None:
        print("  누끼: rembg 사용 불가 → 흰 배경 알파로 대체")
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
