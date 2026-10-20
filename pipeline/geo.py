"""지도 데이터 생성: SRTM 기반 음영기복(hillshade) 래스터 + OSM 하천·호수.

python pipeline/geo.py
결과: public/geo/rasters.json, public/geo/*.webp, public/geo/water.json
한 번 만들면 저장소에 커밋되어 재사용됩니다(한반도 중부 기준).
"""
import io
import math
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image

from common import ROOT, retry, session, write_json

sys.setrecursionlimit(1000000)
OUT = ROOT / "public" / "geo"
TILE = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"

# (이름, [서, 남, 동, 북], 줌, 과장계수, 가장자리 페더)
RASTERS = [
    ("korea", [122.5, 32.0, 132.5, 44.0], 8, 3.2, 0),
    ("central", [125.9, 36.9, 129.2, 39.0], 11, 1.7, 48),
    ("detail", [127.2, 37.38, 128.2, 38.32], 12, 1.35, 64),
    # EP02 낙동강·대구 권역
    ("south", [127.6, 34.9, 129.7, 36.8], 11, 1.7, 48),
    ("south_detail", [128.2, 35.82, 128.9, 36.3], 12, 1.35, 64),
    ("dabu_zoom", [128.42, 35.97, 128.72, 36.16], 13, 1.15, 64),
    # EP03 철원·백마고지 권역
    ("cheorwon", [126.95, 38.08, 127.62, 38.5], 12, 1.35, 64),
    ("baengma_zoom", [127.11, 38.235, 127.3, 38.36], 13, 1.15, 64),
]


def lon2x(lon, z):
    return (lon + 180) / 360 * 2 ** z


def lat2y(lat, z):
    r = math.radians(lat)
    return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** z


def x2lon(x, z):
    return x / 2 ** z * 360 - 180


def y2lat(y, z):
    n = math.pi - 2 * math.pi * y / 2 ** z
    return math.degrees(math.atan(math.sinh(n)))


def fetch_tile(s, z, x, y):
    def call():
        r = s.get(TILE.format(z=z, x=x, y=y), timeout=60)
        r.raise_for_status()
        a = np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB"), dtype=np.float64)
        return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    return retry(call, label=f"tile {z}/{x}/{y}")


def hillshade(elev, z, lat0, lat1, exag):
    h, w = elev.shape
    lats = np.linspace(lat1, lat0, h)[:, None]
    res = 156543.03392 * np.cos(np.radians(lats)) / 2 ** z
    e = np.where(elev < -50, 0, elev)
    dy, dx = np.gradient(e)
    dx = dx / res * exag
    dy = dy / res * exag
    slope = np.arctan(np.hypot(dx, dy))
    aspect = np.arctan2(dy, -dx)

    def shade(az_deg, alt_deg):
        az = math.radians(360 - az_deg + 90)
        zen = math.radians(90 - alt_deg)
        return np.clip(np.cos(zen) * np.cos(slope) + np.sin(zen) * np.sin(slope) * np.cos(az - aspect), 0, 1)

    hs = 0.6 * shade(315, 45) + 0.2 * shade(270, 45) + 0.2 * shade(0, 45)
    flat = math.cos(math.radians(45))
    v = np.clip(0.93 + 1.15 * (hs - flat), 0.30, 1.0)
    return v


def build_raster(s, name, bbox, z, exag, feather):
    w, so, e, n = bbox
    x0, x1 = int(lon2x(w, z)), int(lon2x(e, z))
    y0, y1 = int(lat2y(n, z)), int(lat2y(so, z))
    tiles = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
    print(f"RASTER {name}: z{z} {len(tiles)} tiles")
    with ThreadPoolExecutor(16) as ex:
        arrs = list(ex.map(lambda t: fetch_tile(s, z, *t), tiles))
    cols = x1 - x0 + 1
    rows = [np.hstack(arrs[r * cols:(r + 1) * cols]) for r in range(y1 - y0 + 1)]
    elev = np.vstack(rows)
    lon_w, lon_e = x2lon(x0, z), x2lon(x1 + 1, z)
    lat_n, lat_s = y2lat(y0, z), y2lat(y1 + 1, z)
    v = hillshade(elev, z, lat_s, lat_n, exag)
    rgb = np.stack([v * 247, v * 248, v * 250], -1).astype(np.uint8)
    img = Image.fromarray(rgb, "RGB")
    if feather:
        h, w_ = v.shape
        yy = np.minimum(np.arange(h), np.arange(h)[::-1])[:, None]
        xx = np.minimum(np.arange(w_), np.arange(w_)[::-1])[None, :]
        a = np.clip(np.minimum(yy, xx) / feather, 0, 1)
        img.putalpha(Image.fromarray((a * 255).astype(np.uint8), "L"))
    img.save(OUT / f"{name}.webp", quality=88, method=4)
    return {"name": name, "file": f"geo/{name}.webp", "west": lon_w, "east": lon_e, "north": lat_n, "south": lat_s,
            "w": img.width, "h": img.height}


# ---------------- 하천 / 호수 (OpenStreetMap Overpass) ----------------
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
            "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
WBOX = (34.9, 126.3, 38.75, 129.6)


def overpass(s, q):
    last = None
    for url in OVERPASS:
        try:
            r = s.post(url, data={"data": q}, timeout=300)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa
            last = e
            print(f"  ! overpass {url}: {e}")
    raise last


def simplify(pts, tol):
    """Douglas-Peucker (반복 버전)."""
    n = len(pts)
    if n < 3:
        return list(pts)
    P = np.array(pts, dtype=float)
    keep = np.zeros(n, bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        i0, i1 = stack.pop()
        if i1 - i0 < 2:
            continue
        a, b = P[i0], P[i1]
        ab = b - a
        L = math.hypot(*ab)
        seg = P[i0 + 1:i1]
        if L == 0:
            d = np.hypot(*(seg - a).T)
        else:
            d = np.abs(ab[0] * (seg[:, 1] - a[1]) - ab[1] * (seg[:, 0] - a[0])) / L
        k = int(np.argmax(d))
        if d[k] > tol:
            m = i0 + 1 + k
            keep[m] = True
            stack += [(i0, m), (m, i1)]
    return [tuple(p) for p in P[keep].tolist()]


def ring_area_km2(r):
    if len(r) < 3:
        return 0
    lat = math.radians(sum(p[1] for p in r) / len(r))
    kx, ky = 111.32 * math.cos(lat), 110.57
    s = 0
    for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]):
        s += x1 * kx * y2 * ky - x2 * kx * y1 * ky
    return abs(s) / 2


def join_ways(ways):
    ways = [list(w) for w in ways if len(w) > 1]
    rings = []
    while ways:
        cur = ways.pop(0)
        changed = True
        while changed and cur[0] != cur[-1]:
            changed = False
            for i, w in enumerate(ways):
                if w[0] == cur[-1]:
                    cur += w[1:]
                elif w[-1] == cur[-1]:
                    cur += w[::-1][1:]
                elif w[-1] == cur[0]:
                    cur = w + cur[1:]
                elif w[0] == cur[0]:
                    cur = w[::-1] + cur[1:]
                else:
                    continue
                ways.pop(i)
                changed = True
                break
        rings.append(cur)
    return rings


def build_water(s):
    s_, w_, n_, e_ = WBOX
    bb = f"({s_},{w_},{n_},{e_})"
    q = f"""[out:json][timeout:600][maxsize:1073741824];
(
 way["natural"="water"]{bb};
 relation["natural"="water"]{bb};
 way["waterway"="riverbank"]{bb};
);
out geom;"""
    print("WATER polygons…")
    data = overpass(s, q)
    lakes = []
    for el in data["elements"]:
        if el["type"] == "way" and "geometry" in el:
            pts = [(round(g["lon"], 5), round(g["lat"], 5)) for g in el["geometry"]]
            rings = [pts]
        elif el["type"] == "relation":
            outers = [[(round(g["lon"], 5), round(g["lat"], 5)) for g in m.get("geometry", [])]
                      for m in el.get("members", []) if m.get("role") == "outer"]
            rings = join_ways(outers)
        else:
            continue
        for r in rings:
            if ring_area_km2(r) < 0.4:
                continue
            lakes.append([list(p) for p in simplify([tuple(p) for p in r], 0.00025)])
    q2 = f"""[out:json][timeout:240];
way["waterway"="river"]{bb};
out geom;"""
    print("WATER rivers…")
    data2 = overpass(s, q2)
    by = {}
    for el in data2["elements"]:
        if "geometry" not in el:
            continue
        nm = el.get("tags", {}).get("name", "")
        pts = [(round(g["lon"], 5), round(g["lat"], 5)) for g in el["geometry"]]
        by.setdefault(nm or f"_{el['id']}", []).append(pts)
    rivers = []
    for nm, segs in by.items():
        length = 0
        for sg in segs:
            for (x1, y1), (x2, y2) in zip(sg, sg[1:]):
                length += math.hypot((x2 - x1) * 88.5, (y2 - y1) * 110.6)
        if length < 30:
            continue
        rivers.append({"len": round(length), "name": nm, "lines": [[list(p) for p in simplify(sg, 0.0003)] for sg in segs]})
    write_json(OUT / "water.json", {"bbox": list(WBOX), "lakes": lakes, "rivers": rivers})
    print(f"  호수/하천면 {len(lakes)}개, 하천선 {len(rivers)}개")


def main(what="all"):
    OUT.mkdir(parents=True, exist_ok=True)
    s = session()
    if what in ("all", "terrain", "auto"):
        # 이미 만든 래스터는 재사용, 새로 추가된 권역만 생성
        import json as _j
        old = {m["name"]: m for m in (_j.loads((OUT / "rasters.json").read_text()) if (OUT / "rasters.json").exists() else [])}
        meta = [old[r[0]] if r[0] in old and (OUT / f"{r[0]}.webp").exists() else build_raster(s, *r) for r in RASTERS]
        write_json(OUT / "rasters.json", meta)
    if what == "auto":  # 하천 데이터 범위가 바뀌었을 때만 다시 받기
        import json as _j
        w = _j.loads((OUT / "water.json").read_text()) if (OUT / "water.json").exists() else {}
        what = "water" if w.get("bbox") != list(WBOX) else "none"
    if what in ("all", "water"):
        try:
            build_water(s)
        except Exception as e:
            print(f"  ! 하천 데이터 실패(지도에서 생략): {e}")
            write_json(OUT / "water.json", {"lakes": [], "rivers": []})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
