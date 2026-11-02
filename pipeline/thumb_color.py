"""'선 넘는 지도' 스타일 썸네일용 컬러 지형 만들기 (2026-11-02)

흑백 음영 지형 래스터(public/geo/<name>.webp)를 초록·황록 컬러 지형 + 짙은 남색 바다로 칠해
public/geo/thumbc/<name>.webp 로 저장한다. (좌표 범위는 원본과 같으므로 rasters.json 그대로 사용)

  python3 pipeline/thumb_color.py south korea dosol_zoom yanggu
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), "..", "public", "geo")

# 음영 밝기(0=그늘 ~ 1=햇빛) → 지형 색 (레퍼런스: 짙은 숲 초록 → 선명한 초록 → 밝은 황록)
STOPS = [
    (0.00, (14, 30, 14)),
    (0.35, (38, 78, 30)),
    (0.62, (66, 124, 38)),
    (0.82, (124, 164, 56)),
    (1.00, (196, 204, 100)),
]
SEA = np.array([10, 30, 58], float)


def ramp(s: np.ndarray) -> np.ndarray:
    out = np.zeros(s.shape + (3,), float)
    for (a, ca), (b, cb) in zip(STOPS, STOPS[1:]):
        m = (s >= a) & (s <= b)
        t = ((s - a) / (b - a))[m][:, None]
        out[m] = np.array(ca) * (1 - t) + np.array(cb) * t
    return out


def colorize(name: str) -> str:
    src = os.path.join(ROOT, f"{name}.webp")
    im = Image.open(src).convert("RGBA")
    arr = np.array(im).astype(float)
    rgb, a = arr[..., :3], arr[..., 3:4] / 255.0
    rgb = rgb * a + 255 * (1 - a)  # 흰 바탕 위 합성 (영상 지도와 같은 모습)
    r, g, b = (arr[..., i] for i in range(3))
    # 바다 = 원본에서 정확히 (229,231,233) ±3 인 평평한 회색 → 작은 육지 얼룩 제거(열고 닫기)
    sea = (np.abs(r - 229) <= 3) & (np.abs(g - 231) <= 3) & (np.abs(b - 233) <= 3)
    mk = Image.fromarray((sea * 255).astype(np.uint8))
    mk = mk.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    mk = mk.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    sea = np.array(mk.filter(ImageFilter.GaussianBlur(1.5))).astype(float)[..., None] / 255.0
    gray = rgb.mean(axis=2) / 255.0
    # 대비를 키워 산줄기가 도드라지게
    s = np.clip((gray - 0.42) / 0.58, 0, 1) ** 1.15
    land = ramp(s)
    out = land * (1 - sea) + SEA * sea
    # 래스터 가장자리(투명 → 흰 테두리)가 노란 선으로 보이지 않게 안쪽 픽셀로 채움
    e = 18
    out[:e] = out[e]
    out[-e:] = out[-e - 1]
    out[:, :e] = out[:, e : e + 1]
    out[:, -e:] = out[:, -e - 1 : -e]
    dst_dir = os.path.join(ROOT, "thumbc")
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, f"{name}.webp")
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst, quality=82, method=6)
    return dst


if __name__ == "__main__":
    for n in sys.argv[1:]:
        print(colorize(n))
