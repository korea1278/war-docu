"""OpenAI 이미지 생성 (재연 일러스트).

python pipeline/ai_images.py yongmunsan
환경변수: OPENAI_API_KEY, OPENAI_IMAGE_MODEL(기본 gpt-image-1), OPENAI_IMAGE_QUALITY(기본 high)
"""
import base64
import hashlib
import io
import sys

from PIL import Image

from common import ep_dirs, env, load_board, read_json, retry, session, write_json


def main(ep):
    key = env("OPENAI_API_KEY", required=True)
    model = env("OPENAI_IMAGE_MODEL") or "gpt-image-1"
    quality = env("OPENAI_IMAGE_QUALITY") or "high"
    board = load_board(ep)
    _, out = ep_dirs(ep)
    d = out / "ai"
    d.mkdir(exist_ok=True)
    man = read_json(out / "ai.json", {})
    used = {sc["visual"]["img"] for sc in board["scenes"] if sc["visual"]["type"] == "ai"}
    for sc in board["scenes"]:
        for it in sc["visual"].get("items", []) if sc["visual"]["type"] == "teaser" else []:
            used.add(it["img"])
    s = session()
    for name in sorted(used):
        prompt = board["ai_images"][name]
        sig = hashlib.sha1(f"{model}|{quality}|{prompt}".encode()).hexdigest()[:12]
        p = d / f"{name}.jpg"
        if man.get(name) == sig and p.exists():
            continue
        print(f"AI IMG {name}")

        def call():
            r = s.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {key}"},
                json={"model": model, "prompt": prompt, "size": "1536x1024", "quality": quality, "n": 1},
                timeout=300,
            )
            if r.status_code >= 400:
                raise RuntimeError(f"{r.status_code} {r.text[:300]}")
            return r.json()

        data = retry(call, tries=3, wait=8, label=f"image {name}")
        img = Image.open(io.BytesIO(base64.b64decode(data["data"][0]["b64_json"]))).convert("RGB")
        img.save(p, quality=92)
        man[name] = sig
        write_json(out / "ai.json", man)
    print("AI 이미지 완료")


if __name__ == "__main__":
    main(sys.argv[1])
