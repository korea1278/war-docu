"""사진 화질 개선 + 2.5D 입체 레이어 (2026-11-24 · 무료 오픈소스, 추가 비용 0원)

  python enhance.py <ep>

1) Real-ESRGAN (realesr-general-x4v3, BSD-3) — 작고 흐린 사료 사진을 선명하게 키움
   - 긴 변이 1600px 미만인 사진(photos/)만. 원본은 그대로 두고 public/fx/<ep>/ 에 따로 저장
   - torch 없이 onnxruntime으로 돌리려고, 공식 .pth 가중치를 이 스크립트가 직접 ONNX로 바꿔 씀
2) Depth Anything V2 **Small** (Apache-2.0 — Base/Large는 비상업 라이선스라 쓰면 안 됨)
   - 사진·재연 그림의 앞뒤 거리(깊이 지도)를 계산 → Remotion KenBurns가 픽셀마다 깊이만큼 다르게 밀어
     가까운 사람·물체가 배경보다 더 움직이는 '입체로 움직이는 사진'(2.5D 패럴랙스)을 만듦
3) 결과 목록 public/fx/<ep>/fx.json → timeline.py가 장면에 hd·depth를 붙임
   - public/fx/는 .gitignore (저장소 용량 보호) — Actions 캐시로 재사용, 캐시가 없으면 다시 계산(무료)
   - 어떤 단계든 실패하면 그 그림만 건너뜀 → 영상은 예전 방식(켄번즈)으로 그대로 렌더됨

보드 옵션: "fx": false (전부 끔) · "parallax": false (입체만 끔) · "upscale": false (화질 개선만 끔)
장면 옵션: visual.parallax = false (그 장면만 입체 끔)
"""
import hashlib
import io
import json
import pickle
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / ".cache" / "models"  # public 밖 (번들에 복사되지 않게)
VER = 1  # 처리 방식을 바꾸면 올림 → 전부 다시 계산

ESR_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth"
DEPTH_URL = "https://github.com/fabio-sim/Depth-Anything-ONNX/releases/download/v2.0.0/depth_anything_v2_vits_dynamic.onnx"

UPSCALE_BELOW = 1600   # 긴 변이 이보다 작으면 화질 개선
OUT_LONG = 2400        # 화질 개선 결과 긴 변 (1920 화면 + 켄번즈 확대 여유)


def log(*a):
    print("[enhance]", *a, flush=True)


def fetch(url, dst):
    if dst.exists() and dst.stat().st_size > 1000:
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    log("모델 받기:", url.rsplit("/", 1)[-1])
    tmp = dst.with_suffix(".part")
    for i in range(4):
        try:
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(dst)
            return dst
        except Exception as e:  # noqa: BLE001
            log("  재시도", i + 1, e)
            time.sleep(5 * (i + 1))
    raise RuntimeError("모델 다운로드 실패: " + url)


# ---------------------------------------------------------------- Real-ESRGAN (.pth → ONNX, torch 없이)
def _load_pth(path):
    """torch 없이 .pth(zip+pickle) 텐서를 numpy로 읽기."""
    z = zipfile.ZipFile(path)
    pre = z.namelist()[0].split("/")[0]
    DT = {"FloatStorage": np.float32, "HalfStorage": np.float16, "DoubleStorage": np.float64}

    class Store:
        def __init__(self, name):
            self.name = name

    def rebuild(storage, offset, size, stride, *_a):
        arr = storage
        n = int(np.prod(size)) if size else 1
        flat = arr[offset: offset + max(n, 1) * 4]
        if not size:
            return flat[:1].reshape(())
        itemstrides = [s * arr.itemsize for s in stride]
        return np.lib.stride_tricks.as_strided(arr[offset:], shape=tuple(size), strides=tuple(itemstrides)).copy()

    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if name == "_rebuild_tensor_v2":
                return rebuild
            if name.endswith("Storage"):
                return name
            if mod == "collections" and name == "OrderedDict":
                import collections
                return collections.OrderedDict
            if name == "_rebuild_parameter":
                return lambda data, *a: data
            return super().find_class(mod, name)

        def persistent_load(self, pid):
            _, kind, key, _loc, _n = pid
            raw = z.read(f"{pre}/data/{key}")
            return np.frombuffer(raw, dtype=DT.get(kind, np.float32))

    return U(io.BytesIO(z.read(f"{pre}/data.pkl"))).load()


def esr_onnx():
    out = MODELS / "realesr-general-x4v3.onnx"
    if out.exists():
        return out
    import onnx
    from onnx import TensorProto, helper, numpy_helper

    sd = _load_pth(fetch(ESR_URL, MODELS / "realesr-general-x4v3.pth"))
    sd = sd.get("params_ema") or sd.get("params") or sd
    idx = sorted({int(k.split(".")[1]) for k in sd if k.startswith("body.")})
    nodes, inits, cur = [], [], "x"
    for i in idx:
        w = np.asarray(sd[f"body.{i}.weight"], dtype=np.float32)
        nm = f"b{i}"
        if w.ndim == 4:  # Conv
            b = np.asarray(sd[f"body.{i}.bias"], dtype=np.float32)
            inits += [numpy_helper.from_array(w, nm + "w"), numpy_helper.from_array(b, nm + "b")]
            nodes.append(helper.make_node("Conv", [cur, nm + "w", nm + "b"], [nm], pads=[1, 1, 1, 1], kernel_shape=[3, 3]))
        else:  # PReLU (채널별)
            inits.append(numpy_helper.from_array(w.reshape(-1, 1, 1), nm + "s"))
            nodes.append(helper.make_node("PRelu", [cur, nm + "s"], [nm]))
        cur = nm
    nodes.append(helper.make_node("DepthToSpace", [cur], ["ps"], blocksize=4, mode="CRD"))
    inits.append(numpy_helper.from_array(np.array([1, 1, 4, 4], dtype=np.float32), "sc"))
    nodes.append(helper.make_node("Resize", ["x", "", "sc"], ["base"], mode="nearest"))
    nodes.append(helper.make_node("Add", ["ps", "base"], ["y"]))
    g = helper.make_graph(nodes, "srvgg", [helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 3, None, None])],
                          [helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 3, None, None])], inits)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 13)])
    m.ir_version = 8
    onnx.checker.check_model(m)
    onnx.save(m, out)
    log("Real-ESRGAN ONNX 변환 완료")
    return out


_SESS = {}


def sess(name, path):
    if name not in _SESS:
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        _SESS[name] = ort.InferenceSession(str(path), so, providers=["CPUExecutionProvider"])
    return _SESS[name]


def upscale(img: Image.Image) -> Image.Image:
    """4배 화질 개선 (타일 처리) → 긴 변 OUT_LONG로 맞춤."""
    s = sess("esr", esr_onnx())
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    H, W, _ = rgb.shape
    T, P = 192, 12
    out = np.zeros((H * 4, W * 4, 3), dtype=np.float32)
    for y in range(0, H, T):
        for x in range(0, W, T):
            y0, x0 = max(0, y - P), max(0, x - P)
            y1, x1 = min(H, y + T + P), min(W, x + T + P)
            tile = rgb[y0:y1, x0:x1].transpose(2, 0, 1)[None]
            r = s.run(None, {"x": np.ascontiguousarray(tile)})[0][0].transpose(1, 2, 0)
            oy, ox = (y - y0) * 4, (x - x0) * 4
            th, tw = (min(y + T, H) - y) * 4, (min(x + T, W) - x) * 4
            out[y * 4: y * 4 + th, x * 4: x * 4 + tw] = r[oy: oy + th, ox: ox + tw]
    big = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))
    k = OUT_LONG / max(big.size)
    if k < 1:
        big = big.resize((round(big.width * k), round(big.height * k)), Image.LANCZOS)
    # 원본이 흑백이면 흑백 유지 (색 번짐 방지)
    if _is_gray(img):
        big = big.convert("L").convert("RGB")
    return big


def _is_gray(img):
    a = np.asarray(img.convert("RGB").resize((96, 96)), dtype=np.int16)
    return float(np.abs(a[..., 0] - a[..., 1]).mean() + np.abs(a[..., 1] - a[..., 2]).mean()) < 6


# ---------------------------------------------------------------- Depth Anything V2 Small → 앞/뒤 레이어
def depth_map(img: Image.Image) -> np.ndarray:
    s = sess("depth", fetch(DEPTH_URL, MODELS / "depth_anything_v2_vits_dynamic.onnx"))
    W, H = img.size
    k = 518 / max(W, H)
    w, h = max(14, round(W * k / 14) * 14), max(14, round(H * k / 14) * 14)
    x = np.asarray(img.convert("RGB").resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    d = s.run(None, {"image": x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    d = np.asarray(Image.fromarray(d.astype(np.float32)).resize((W, H), Image.BILINEAR))
    lo, hi = np.percentile(d, 2), np.percentile(d, 98)
    return np.clip((d - lo) / max(1e-6, hi - lo), 0, 1)  # 1 = 가까움


def make_depth(img: Image.Image, out_path: Path):
    """깊이 지도 PNG (흑백, 밝을수록 가까움). 평평한 사진(문서·지도 사진 등)은 None → 입체 생략.
    Remotion이 이 지도로 픽셀마다 다른 양만큼 밀어서(깊이 와핑) 카메라가 움직이는 듯한 입체감을 만듦 —
    잘라 붙이는 방식과 달리 빈 구멍·번진 자국이 생기지 않음."""
    import cv2

    d = depth_map(img.convert("RGB"))
    spread = float(np.percentile(d, 90) - np.percentile(d, 10))
    if spread < 0.35 or float(d.std()) < 0.12:
        return None
    H, W = d.shape
    k = 768 / max(W, H)
    small = cv2.resize(d.astype(np.float32), (max(8, round(W * k)), max(8, round(H * k))), interpolation=cv2.INTER_AREA)
    # 가까운 물체의 윤곽을 살짝 넓혀(최댓값 필터) 늘어나는 자리가 물체가 아니라 배경 쪽에 생기게 → 부드럽게
    small = cv2.dilate(small, np.ones((5, 5), np.uint8))
    small = cv2.GaussianBlur(small, (0, 0), 2.2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((np.clip(small, 0, 1) * 255 + 0.5).astype(np.uint8), "L").save(out_path, optimize=True)
    return {"spread": round(spread, 3)}


# ---------------------------------------------------------------- main
def sha(p: Path):
    return hashlib.sha1(p.read_bytes()).hexdigest()[:16]


def main(ep):
    board_p = ROOT / "episodes" / ep / "storyboard.json"
    board = json.loads(board_p.read_text(encoding="utf-8")) if board_p.exists() else {}
    if board.get("fx") is False:
        log("보드 fx=false → 건너뜀")
        return
    do_up = board.get("upscale", True) is not False
    do_par = board.get("parallax", True) is not False
    ep = board.get("assets_ep") or ep  # 다국어판(_en)은 원본 에피소드 재료를 씀
    src_dir = ROOT / "public" / "ep" / ep
    out_dir = ROOT / "public" / "fx" / ep
    man_p = out_dir / "fx.json"
    man = json.loads(man_p.read_text(encoding="utf-8")) if man_p.exists() else {}
    if man.get("_v") != VER:
        man = {"_v": VER}
    files = sorted((src_dir / "photos").glob("*.jpg")) + sorted((src_dir / "ai").glob("*.jpg"))
    files = [f for f in files if not f.name.startswith("thumb")]
    t0, n_up, n_par = time.time(), 0, 0
    for f in files:
        rel = f.relative_to(ROOT / "public").as_posix()  # ep/<ep>/photos/x.jpg
        h = sha(f)
        ent = man.get(rel)
        if ent and ent.get("sha") == h and ent.get("up_ok") == do_up and ent.get("par_ok") == do_par:
            continue
        ent = {"sha": h, "up_ok": do_up, "par_ok": do_par}
        stem = f"{f.parent.name}_{f.stem}"
        try:
            img = Image.open(f)
            img.load()
            img = img.convert("RGB")
            if do_up and f.parent.name == "photos" and max(img.size) < UPSCALE_BELOW and min(img.size) >= 120:
                t = time.time()
                img = upscale(img)
                hd = out_dir / f"{stem}.hd.jpg"
                img.save(hd, quality=90)
                ent["hd"] = f"fx/{ep}/{hd.name}"
                n_up += 1
                log(f"화질 개선 {rel} → {img.size[0]}x{img.size[1]} ({time.time() - t:.0f}초)")
            if do_par:
                dp = out_dir / f"{stem}.depth.png"
                info = make_depth(img, dp)
                if info:
                    ent["depth"] = f"fx/{ep}/{dp.name}"
                    ent.update(info)
                    n_par += 1
        except Exception as e:  # noqa: BLE001 — 한 장 실패는 건너뜀 (예전 방식으로 렌더)
            log("실패(건너뜀):", rel, repr(e)[:200])
            ent["err"] = repr(e)[:200]
        man[rel] = ent
        out_dir.mkdir(parents=True, exist_ok=True)
        man_p.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"완료: 새로 화질 개선 {n_up}장 · 깊이 지도 {n_par}장 · {time.time() - t0:.0f}초")


if __name__ == "__main__":
    main(sys.argv[1])
