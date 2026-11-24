# EP33 진동리·마산 서북산 혈전 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 연출 스타일 v2 + 화면 업그레이드 2단계 + 롱폼 표준 + 캐릭터 반복 방지 + 초반 후킹 표준 · 그림: 재사용 + 새 그림 Cloudflare 무료
import collections
import hashlib
import json
import pathlib
import re
import shutil

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
EP = HERE.name
raw = (HERE / "script.md").read_text(encoding="utf-8")
ACTS = []
for a in raw.split("\n## ")[1:]:
    body = [l for l in a.split("\n")[1:] if l and not l.startswith((">", "#"))]
    ACTS.append([s for l in body for s in re.split(r"(?<=[.?])\s+", l.strip()) if s])

# 자막 숫자 표기 (사용자 지시: 롱폼 자막 숫자는 숫자로) — 긴 것부터 (부분 문자열 겹침 주의)
SUBS = [
    ("천구백오십년 팔월 칠일", "1950년 8월 7일"), ("천구백오십년 칠월 말", "1950년 7월 말"), ("천구백오십년 구월 일일", "1950년 9월 1일"),
    ("천구백구십사년", "1994년"), ("천구백구십오년 십일월", "1995년 11월"),
    ("팔월 이십구일", "8월 29일"), ("팔월 이십오일", "8월 25일"), ("팔월 이십삼일", "8월 23일"), ("팔월 십팔일", "8월 18일"), ("팔월 십사일", "8월 14일"),
    ("팔월 십이일", "8월 12일"), ("팔월 십일일", "8월 11일"), ("팔월 칠일", "8월 7일"), ("팔월 육일", "8월 6일"), ("팔월 삼일", "8월 3일"),
    ("구월 십구일", "9월 19일"), ("구월 십팔일", "9월 18일"), ("구월 십오일", "9월 15일"), ("구월 칠일", "9월 7일"),
    ("칠월 하순", "7월 하순"), ("칠월 말", "7월 말"), ("팔월 초", "8월 초"), ("팔월 말", "8월 말"), ("팔월 중순", "8월 중순"), ("구월 중순", "9월 중순"),
    ("섭씨 사십 도", "섭씨 40도"), ("이십여 킬로미터", "20여 km"), ("사오십 킬로미터", "40~50km"), ("이백 킬로미터", "200km"), ("십여 킬로미터", "10여 km"), ("일 킬로미터", "1km"),
    ("칠백삼십구 미터", "739m"), ("삼백사십이 고지", "342고지"),
    ("열 명 가운데 여덟 명", "10명 가운데 8명"), ("열 명 중 두 명", "10명 중 2명"), ("칠십오 명에서 백 명", "75~100명"), ("백팔십여 명", "180여 명"), ("스물세 명", "23명"),
    ("삼사천 명", "3,000~4,000명"), ("사천여 명", "4,000여 명"), ("삼천여 명", "3,000여 명"), ("천여 명", "1,000여 명"), ("이천 명", "2,000명"), ("쉰일곱 명", "57명"),
    ("만 명 안팎", "1만 명 안팎"), ("약 이만 명", "약 2만 명"), ("백 명이 넘었습니다", "100명이 넘었습니다"),
    ("이백여 대", "200여 대"), ("백여 대", "100여 대"), ("스물여섯 대", "26대"), ("여덟 문", "8문"), ("여섯 문", "6문"), ("여섯 배", "6배"),
    ("열아홉 번", "19번"), ("스무 번", "20번"), ("사십오 일", "45일"), ("새벽 네 시", "새벽 4시"), ("일곱 살", "7살"), ("별 세 개", "별 3개"),
    ("세 개 연대", "3개 연대"), ("포병 한 개 중대", "포병 1개 중대"), ("한 개 중대", "1개 중대"), ("한 개 대대", "1개 대대"), ("한 개 사단", "1개 사단"), ("삼대가", "3대가"),
    ("이달의 육이오 전쟁영웅", "이달의 6·25 전쟁영웅"),
    ("제오백오십오포병대대", "제555포병대대"), ("제구십포병대대", "제90포병대대"), ("제일임시해병여단", "제1임시해병여단"), ("제오연대전투단", "제5연대전투단"),
    ("제이십오사단", "제25사단"), ("제이십칠연대", "제27연대"), ("제삼십오연대", "제35연대"), ("제이십사연대", "제24연대"),
    ("제육사단", "제6사단"), ("제칠사단", "제7사단"), ("제팔군", "제8군"),
]


def L(say):
    t = say
    for a, b in SUBS:
        t = t.replace(a, b)
    return {"t": t, "say": say} if t != say else say


S = []
CUR = {"act": 0, "i": 0}
NUM = {"n": 0}
PINS = {}


def take(n):
    a = ACTS[CUR["act"]]
    out = a[CUR["i"]:CUR["i"] + n]
    assert len(out) == n, (CUR, n, len(a))
    CUR["i"] += n
    return [L(x) for x in out]


def next_act():
    assert CUR["i"] == len(ACTS[CUR["act"]]), ("남은 문장", CUR, ACTS[CUR["act"]][CUR["i"]:])
    CUR["act"] += 1
    CUR["i"] = 0


def nid():
    return f"s{NUM['n'] + 1:03d}"


def sc(n, visual, **kw):
    i = nid()
    NUM["n"] += 1
    d = {"id": i, "lines": take(n), "visual": visual}
    d.update(kw)
    S.append(d)


def m(fr, to=None, items=None, **kw):
    v = {"type": "map", "from": fr, "to": to or fr, "items": items or []}
    v.update(kw)
    return v


def ai(img, kb="in", pops=None):
    v = {"type": "ai", "img": img, "kb": kb}
    if pops:
        v["pops"] = pops
    return v


# ---------- 화면 업그레이드 2단계 헬퍼 ----------
def C(c, x, h=480, on=None, at=None, flip=False, y=0.9, face=None, prop=None, anim=None):
    d = {"c": c, "x": x, "y": y, "h": h}
    if on:
        d["on"] = on
    else:
        d["at"] = at or 0
    if flip:
        d["flip"] = True
    if face:
        d["face"] = face
    if prop:
        d["prop"] = prop
    if anim:
        d["anim"] = anim
    return d


def pop(kind, x, y, text=None, on=None, at=None, **kw):
    d = {"kind": kind, "x": x, "y": y}
    if text:
        d["text"] = text
    if on:
        d["on"] = on
    else:
        d["at"] = at if at is not None else 0.2
    d.update(kw)
    return d


def stage(chars, pops=None, title=None):
    v = {"type": "stage", "chars": chars, "pops": pops or []}
    if title:
        v["title"] = title
    return v


FILL = {"410": "#f1e4c6", "408": "#e8b6a5", "392": "#e6d9bd", "156": "#dcc9a3"}


def flat(center, span, pins=None, routes=None, labels=None, title=None, pops=None, zoomTo=0.92):
    v = {"type": "flatmap", "center": center, "span": span, "fill": FILL, "pins": pins or [], "routes": routes or [], "labels": labels or [], "zoomTo": zoomTo}
    if title:
        v["title"] = title
    if pops:
        v["pops"] = pops
    return v


def fpin(ll, text, on=None, at=None, flag=None, side="below", color=None):
    d = {"ll": ll, "text": text, "side": side}
    if on:
        d["on"] = on
    else:
        d["at"] = at or 0
    if flag:
        d["flag"] = flag
    if color:
        d["color"] = color
    return d


def route(a, b, label=None, on=None, at=None, bend=0.2, color=None, dash=False, dur=1.4):
    d = {"from": a, "to": b, "bend": bend, "dur": dur}
    if label:
        d["label"] = label
    if on:
        d["on"] = on
    else:
        d["at"] = at or 0
    if color:
        d["color"] = color
    if dash:
        d["dash"] = True
    return d


def reasons(title, items):
    return {"type": "reasons", "title": title, "items": items}


def checklist(title, items):
    return {"type": "checklist", "title": title, "items": items}


def doc(head, rows, stamp="軍 秘", org="국군 제7연대", note="재구성 · 내용 요약"):
    return {"type": "document", "org": org, "head": head, "rows": rows, "stamp": stamp, "note": note}


def text(big, style="yellow", sub=None):
    v = {"type": "text", "big": big, "style": style}
    if sub:
        v.update(sub=sub, subAt=0.4)
    return v


def black(a, b=None):
    v = {"type": "black", "text": a}
    if b:
        v.update(accent=b, accentAt=0.5)
    return v


def cmp(lt, lb, rt, rb, lc="blue", rc="red"):
    return {"type": "compare", "left": {"title": lt, "big": lb, "icon": "none", "color": lc}, "right": {"title": rt, "big": rb, "icon": "none", "color": rc, "at": 0.6}}


def bars(note, items):
    return {"type": "bars", "note": note, "items": items}


def troops(n, keep=None, keepAt=None, side="us", cols=8, title=None, labels=None, vs=None, march=False):
    v = {"type": "troops", "n": n, "cols": cols, "side": side}
    if keep is not None:
        v.update(keep=keep, keepAt=keepAt)
    if title:
        v["title"] = title
    if labels:
        v["labels"] = labels
    if vs:
        v["vs"] = vs
    if march:
        v["march"] = True
    return v


# 사진: 다른 에피소드 스카우트 catalog.json 설명으로 내용·날짜를 확인한 파일만 (미 육군·미 해군·NARA 공개 자료)
PH = json.loads((HERE / "photo_keys.json").read_text(encoding="utf-8"))


def pin(key):
    sid = nid()
    PINS[f"{sid}-photo#0"] = PH[key]["file"]
    return f"{sid}-photo"


def ph(key, pos=None, marks=None):
    v = {"type": "photo", "kb": "in", "q": pin(key)}
    if PH[key].get("tag"):
        v["tag"] = PH[key]["tag"]
    if pos:
        v["pos"] = pos
    if marks:
        v["marks"] = marks
    return v


def plabel(key):
    return PH[key]["label"]


DRAMA = "재연 일러스트"




# 좌표는 개략 (서북산·필봉·전투산·342고지·봉암리는 미군 기록과 현재 지형 기준 근사 — 화면에 '위치 개략' 표기)
P = {
    "seoul": [126.978, 37.566, "서울"], "incheon": [126.63, 37.46, "인천"], "daejeon": [127.385, 36.35, "대전"], "gwangju": [126.85, 35.16, "광주"],
    "hadong": [127.751, 35.067, "하동"], "jinju": [128.085, 35.18, "진주"], "sacheon": [128.094, 35.077, "사천"], "goseong": [128.322, 34.973, "고성"],
    "chindong": [128.483, 35.108, "진동리"], "masan": [128.572, 35.197, "마산"], "busan": [129.04, 35.18, "부산"], "daegu": [128.6, 35.87, "대구"],
    "sangju": [128.16, 36.41, "상주"], "pohang": [129.36, 36.03, "포항"], "haman": [128.406, 35.272, "함안"], "bulge": [128.45, 35.5, "낙동강 돌출부"],
    "seobuk": [128.385, 35.195, "서북산"], "pilbong": [128.386, 35.193, "필봉"], "battle": [128.371, 35.205, "전투산"], "h342": [128.445, 35.118, "342고지"],
    "pongam": [128.27, 35.15, "봉암리"], "namgang": [128.37, 35.335, "남강"],
}
V = {
    "korea": {"center": [127.7, 36.2], "span": 8.2}, "peri": {"center": [128.45, 35.85], "span": 4.0}, "coast": {"center": [128.33, 35.15], "span": 0.9},
    "east": {"center": [128.78, 35.2], "span": 0.9}, "tfk": {"center": [128.3, 35.16], "span": 0.7}, "chindong": {"center": [128.47, 35.13], "span": 0.22},
    "gulch": {"center": [128.27, 35.155], "span": 0.2}, "sobuk": {"center": [128.4, 35.21], "span": 0.26}, "peak": {"center": [128.378, 35.2], "span": 0.12},
    "haman": {"center": [128.39, 35.25], "span": 0.3},
}
NK6 = [[126.98, 37.5], [126.95, 36.8], [127.1, 36.0], [126.9, 35.4], [127.3, 35.0], [127.751, 35.067], [128.085, 35.18]]
MAIN_NK = [[127.0, 37.4], [127.4, 36.6], [127.9, 36.2], [128.3, 35.95]]
JIN_MASAN = [[128.085, 35.18], [128.3, 35.21], [128.5, 35.2]]
SANGJU_MASAN = [[128.16, 36.41], [128.4, 36.0], [128.5, 35.6], [128.56, 35.25]]
PERI = [[129.45, 36.25], [128.95, 36.35], [128.5, 36.2], [128.37, 36.0], [128.42, 35.6], [128.45, 35.38], [128.4, 35.25], [128.43, 35.15], [128.48, 35.1]]
COL_N = [[128.56, 35.22], [128.45, 35.3], [128.33, 35.3], [128.2, 35.24]]
COL_C = [[128.483, 35.108], [128.38, 35.13], [128.27, 35.15], [128.15, 35.17]]
COL_S = [[128.483, 35.108], [128.4, 35.03], [128.322, 34.973], [128.2, 35.0], [128.094, 35.077]]
BACK_S = [[128.15, 35.05], [128.32, 34.98], [128.45, 35.07]]
GULCH_ATK = [[[128.27, 35.19], [128.27, 35.158]], [[128.225, 35.155], [128.263, 35.152]], [[128.295, 35.12], [128.275, 35.146]]]
NK_BATTLE = [[128.33, 35.215], [128.367, 35.206]]
US_RETAKE = [[128.415, 35.2], [128.376, 35.205]]
LINE35 = [[128.3, 35.33], [128.42, 35.335], [128.5, 35.36]]
LINE24 = [[128.355, 35.245], [128.371, 35.205], [128.386, 35.193]]
LINE5 = [[128.386, 35.193], [128.42, 35.15], [128.47, 35.115]]
ROAD = [[128.406, 35.272], [128.43, 35.2], [128.46, 35.15], [128.483, 35.108]]
NK7 = [[128.33, 35.37], [128.38, 35.3], [128.403, 35.276]]
COUNTER27 = [[128.48, 35.275], [128.412, 35.273]]
NK_OUT = [[128.37, 35.2], [128.25, 35.19], [128.1, 35.18]]
INCH = [[125.6, 37.2], [126.6, 37.45]]
OFF = [[[128.5, 36.25], [128.55, 35.97]], [[128.28, 35.52], [128.42, 35.5]], [[129.3, 36.35], [129.35, 36.08]], [[128.2, 35.22], [128.37, 35.22]]]
H342_RING = [[128.44, 35.125], [128.452, 35.112], [128.437, 35.11]]
DROP = [[128.6, 35.05], [128.445, 35.118]]

LOCK = lambda p, at=0.3, text=None, color=None, on=None: dict({"k": "lock", "p": p, "text": text or P[p][2]}, **({"on": on} if on else {"at": at}), **({"color": color} if color else {}))
badge = lambda p, t, c="#111", at=0.3, dy=-70, on=None: dict({"k": "badge", "p": p, "text": t, "color": c, "dy": dy}, **({"on": on} if on else {"at": at}))
red_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "red", "width": w}, **({"on": on} if on else {"at": at}))
blue_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "blue", "width": w}, **({"on": on} if on else {"at": at}))
dash_r = lambda path, at=0.2: {"k": "arrow", "path": path, "color": "red", "dash": True, "at": at}
dash_b = lambda path, at=0.2: {"k": "arrow", "path": path, "color": "blue", "dash": True, "at": at}
mark = lambda p, color="red", at=0, text=None, on=None: dict({"k": "marker", "p": p, "color": color}, **({"text": text} if text else {}), **({"on": on} if on else {"at": at}))
unit = lambda p, t, color="red", at=0.1, pulse=False, on=None: dict({"k": "unit", "p": p, "text": t, "color": color}, **({"on": on} if on else {"at": at}), **({"pulse": True} if pulse else {}))
clash = lambda p, at=0.3, size=1.0: {"k": "clash", "p": p, "at": at, "period": 0.9, "size": size}
shock = lambda pts, at=0.2, period=0.7: {"k": "shock", "pts": pts, "at": at, "period": period}
swarm = lambda path, at=0.1, n=120, width=None: dict({"k": "swarm", "path": path, "at": at, "n": n}, **({"width": width} if width else {}))
line = lambda path, at=0.1, color="#ffd400", on=None: dict({"k": "line", "path": path, "color": color, "glow": True}, **({"on": on} if on else {"at": at}))
radar = lambda p, at=0.2, size=1.0, color="blue", text=None: dict({"k": "radar", "p": p, "at": at, "size": size, "color": color}, **({"text": text} if text else {}))
plane = lambda path, at=0.1, n=1, dur=2.5, size=1.0, color=None: dict({"k": "plane", "path": path, "at": at, "n": n, "dur": dur, "size": size, "trail": True}, **({"color": color} if color else {}))
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]
SW = lambda at=0: [{"id": "whoosh", "at": at}]
FAR = lambda at=0.1: [{"id": "artillery_far", "at": at}]
PING = lambda at=0.6: [{"id": "ping", "at": at}]
WIND = lambda at=0: [{"id": "wind", "at": at}]
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))
QUESTION = "부산 턱밑까지 온 북한군 최정예 사단은\n왜 이 바위산 하나를 넘지 못했나"
RED = "#c9242c"
SB = lambda *items, tilt=34, **kw: m("sobuk", "sobuk", [mark("seobuk", "red", 0)] + list(items), tilt=tilt, **kw)
PK = lambda *items, tilt=40, **kw: m("peak", "peak", [mark("battle", "red", 0), mark("pilbong", "red", 0)] + list(items), tilt=tilt, **kw)
CD = lambda *items, tilt=34, **kw: m("chindong", "chindong", [mark("h342", "red", 0)] + list(items), tilt=tilt, **kw)
GU = lambda *items, tilt=36, **kw: m("gulch", "gulch", [mark("pongam", "red", 0)] + list(items), tilt=tilt, **kw)
CO = lambda *items, tilt=22, **kw: m("coast", "coast", [mark("masan", "blue", 0), mark("jinju", "red", 0)] + list(items), tilt=tilt, **kw)
TF = lambda *items, tilt=24, **kw: m("tfk", "tfk", [mark("chindong", "blue", 0), mark("seobuk", "red", 0)] + list(items), tilt=tilt, **kw)
PR = lambda *items, tilt=14, **kw: m("peri", "peri", [line(PERI, 0, "#7fd3ff")] + list(items), tilt=tilt, **kw)
HM = lambda *items, tilt=30, **kw: m("haman", "haman", [mark("haman", "blue", 0)] + list(items), tilt=tilt, **kw)
DEF3 = lambda at=0: [line(LINE35, at, "#7fd3ff"), line(LINE24, at, "#7fd3ff"), line(LINE5, at, "#7fd3ff")]

# ===== 콜드 오프닝 (초반 후킹 표준: 절정 → 수치 HUD 누적 → 통념 X → 핵심 질문 카드 → 타이틀) =====
sc(1, ai("hill342_peak"), label=DRAMA, hook={"hud": [HUD("1950. 8. 7", "진동리 서쪽 고지", "미군 기록 342고지", count=False)]}, sfx=WIND(0.2))
sc(1, ai("summer_heat"), label=DRAMA, hook={"hud": [HUD("40℃+", "한낮 기온", "미군 기록 화씨 112도", color="#FF3B3B", count=False, on="사십")]})
sc(1, CD(LOCK("h342", 0.3, "포위된 미군 1개 중대", RED), hud=True), sfx=PING(0.4))
sc(1, CD(swarm(H342_RING, 0.1, 90, 0.15), unit("h342", "미군 1개 중대", "blue", 0.2, True)), callouts=low("사방은 북한군", "red"))
sc(1, ai("exhausted_gi"), label=DRAMA)
sc(1, text("총알보다 무서운 더위", "red"))
sc(1, ai("airdrop"), label=DRAMA)
sc(1, checklist("하늘에서 온 보급", [{"text": "1차 → 적의 진지로", "on": "첫 번째로", "bad": True}]))
sc(1, checklist("하늘에서 온 보급", [{"text": "1차 → 적의 진지로", "at": 0, "bad": True}, {"text": "2차 → 엉뚱한 골짜기", "on": "두 번째는", "bad": True}]))
sc(1, checklist("하늘에서 온 보급", [{"text": "1차 → 적의 진지로", "at": 0, "bad": True}, {"text": "2차 → 엉뚱한 골짜기", "at": 0, "bad": True}, {"text": "3차 → 물과 탄약 도착", "on": "세 번째가", "checkOn": "닿았습니다"}]))
sc(1, CO(line([[128.445, 35.118], [128.572, 35.197]], 0.2, "#ffd400"), mark("h342", "red", 0)), callouts=low("342고지 → 마산 · 20여 km"))
sc(1, m("east", "east", [mark("masan", "blue", 0), line([[128.572, 35.197], [129.04, 35.18]], 0.2, "#ffd400"), mark("busan", "blue", 0.5)], tilt=18),
   hook={"hud": [HUD("40~50km", "마산 → 부산", "직선거리", color="#FF3B3B", on="사오십")]})
sc(1, PR(LOCK("busan", 0.3, "남은 마지막 도시")), callouts=top("낙동강 방어선 · 1950. 8"))
sc(1, text("북한군 제6사단", "red", "부산의 문 앞까지"))
sc(1, ai("nk_column_coast"), label=DRAMA)
sc(1, ai("sobuk_peak"), label=DRAMA, hook={"hud": [HUD("739m", "서북산 해발", "한국 기록 기준", on="칠백삼십구")]})
sc(1, SB(LOCK("seobuk", 0.2), hud=True), callouts=low("마산 서쪽 · 위치 개략"), sfx=PING(0.3))
sc(1, text("주인이 19번 바뀐 산", "yellow"), hook={"hud": [HUD("19번", "산의 주인이 바뀐 횟수", "한국 기록 기준", color="#FF3B3B", on="열아홉")]})
sc(1, cmp("밤", "북한군이 빼앗고", "낮", "미군이 되찾고", "red", "blue"))
sc(1, text("45일", "dark", "1950. 8 ~ 9 · 마산 방어전"), hook={"hud": [HUD("45일", "마산 앞의 싸움", "1950. 8. 1 ~ 9. 14 무렵", on="사십오")]})
sc(3, black("“미군이 압도적이었으니", "당연히 막아냈다”"), hook={"neg": {"text": "당연히 막아냈다", "at": 0.4, "xOn": "그랬을까요"}})
sc(1, ai("gulch_dawn"), label=DRAMA, callouts=top("1950. 8. 12 · 봉암리", "red"))
sc(1, TF(blue_a(COL_C[:3], 0.1), dash_b(list(reversed(COL_C[:3])), 0.5)), callouts=low("첫 반격 → 출발선으로"))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, {"type": "titlecard", "title": "주인이 열아홉 번 바뀐 산", "sub": "진동리·마산 서북산 혈전 · 1950", "at": 0, "q": pin("sobuk_water")}, flash=True)
next_act()

# ===== 제1막 서쪽 끝의 빈틈 =====
sc(1, PR(), chapter={"num": "제1막", "title": "서쪽 끝의 빈틈"}, callouts=top("1950. 7 말 · 낙동강 방어선"))
sc(1, black("그런데", "한 곳이 비어 있었다"))
sc(1, PR(LOCK([128.45, 35.12], 0.3, "서쪽 끝 · 남해안", RED)), sfx=PING(0.4))
sc(1, m("korea", "korea", [red_a(MAIN_NK, 0.2), mark("seoul", "red", 0)], tilt=12), callouts=low("대부분은 경부선을 따라"))
sc(1, text("다른 길을 택한 1개 사단", "red"))
sc(1, m("korea", "korea", [dash_r(MAIN_NK, 0), red_a(NK6, 0.1, 1.2), mark("gwangju", "red", 0.5)], tilt=12), callouts=low("서해안 → 호남을 크게 돌아", "red"))
sc(1, text("북한군 제6사단", "red", "호남을 돌아 내려온 사단"))
sc(1, text("사단장 방호산 소장", "red", "북한군 제6사단"))
sc(1, checklist("방호산은 누구", [{"text": "중국에서 항일 투쟁", "on": "항일"}, {"text": "소련에서 군사 교육", "on": "소련에서"}]))
sc(1, text("중국 내전을 치른 조선인 병사들", "red", "중국 공산군 출신"))
sc(1, ai("rain_attack"), label=DRAMA)
sc(1, m("korea", "korea", [red_a(NK6, 0, 1.2), swarm(NK6[3:], 0.2, 100)], tilt=12))
sc(1, CO(red_a([[127.751, 35.067], [128.085, 35.18]], 0.1), mark("hadong", "red", on="하동을"), LOCK("jinju", 0.6, "진주 점령", RED)), callouts=top("1950. 7 하순 ~ 7 말", "red"))
sc(1, CO(red_a(JIN_MASAN, 0.2, 1.2)), callouts=low("진주 → 마산 · 산 몇 개"))
sc(1, m("east", "east", [mark("masan", "red", 0), red_a([[128.6, 35.2], [128.95, 35.18]], 0.2), mark("busan", "blue", 0.5)], tilt=18))
sc(1, stage([C("nk_point", 0.55, 480, prop="officer", face="smug", anim="tilt")], [pop("label", 0.5, 0.15, "사단장 방호산", on="방호산", color="red")]))
sc(1, text("“마산을 점령하면 적의 숨통을 조인다”", "red", "전해지는 말"))
sc(1, bars("마산 일대 국군", [{"label": "국군 병력", "value": 1000, "display": "1,000여 명", "color": "blue", "on": "천여"}]))
sc(1, text("급히 모은 부대와 경찰", "dark"))
sc(1, ph("walker_dean"), label=plabel("walker_dean"), callouts=low("미 제8군 사령관 워커 중장"))
sc(1, ai("walker_map"), label=DRAMA)
sc(1, PR(mark("sangju", "blue", 0.1), unit("sangju", "미 제25사단", "blue", 0.4)), callouts=top("경북 상주 → 남쪽 끝으로"))
sc(1, PR(blue_a(SANGJU_MASAN, 0.1, 1.2), mark("masan", "blue", 0.6)), hook={"hud": [HUD("200km+", "상주 → 마산", on="이백")]})
sc(1, ai("trucks_pass"), label=DRAMA)
sc(1, PR(blue_a(SANGJU_MASAN, 0), unit("masan", "미 제25사단", "blue", 0.3, True)), callouts=top("1950. 8. 3 밤 · 집결 완료"))
sc(1, text("북한군 도착 이틀 뒤", "yellow", "아슬아슬한 시간 차"))
sc(1, ai("walker_jeep"), label=DRAMA, callouts=top("1950. 7. 29 무렵 · 상주"))
sc(1, text("“더 이상의 후퇴는 없다”", "yellow", "워커 중장"))
sc(1, text("“죽음으로 지켜라”", "red"))
sc(1, ph("kean"), label=plabel("kean"), callouts=low("미 제25사단장 윌리엄 킨 소장"))
sc(1, text("미 제25사단 · 3개 연대", "blue"))
sc(1, text("제27연대 ‘울프하운드’", "blue", "늑대 사냥개"))
sc(1, text("제35연대", "blue"))
sc(1, ph("inf24"), label=plabel("inf24"), callouts=low("흑인 병사들로 이루어진 제24연대"))
sc(1, text("흑백을 나눈 부대", "dark", "1950년 미군"))
sc(1, ph("mortar_5rct"), label=plabel("mortar_5rct"), callouts=top("하와이에서 온 제5연대전투단"))
sc(1, ph("marines_arrive"), label=plabel("marines_arrive"))
sc(1, text("미 제1임시해병여단", "blue", "1950. 8. 2 부산 도착"))
sc(1, CO(unit("masan", "한미 연합", "blue", 0.1), unit("jinju", "북한군 제6사단", "red", 0.3, True)), sfx=WIND(0))
next_act()

# ===== 제2막 첫 반격의 여름 =====
sc(1, ai("command_decision"), label=DRAMA, chapter={"num": "제2막", "title": "첫 반격의 여름"})
sc(1, text("숨 고를 틈을 주지 마라", "yellow"))
sc(1, text("킨 특수임무부대", "blue", "Task Force Kean"))
sc(1, troops(30, side="us", cols=10, title="킨 특수임무부대 · 약 2만 명", labels=[{"x": 0.5, "y": 0.76, "text": "제25사단 + 제5연대전투단 + 해병여단", "at": 0.3, "color": "blue"}]))
sc(1, CO(LOCK("jinju", 0.2, "목표 · 진주", RED), hud=True), sfx=PING(0.3))
sc(1, text("미군의 첫 본격 반격", "yellow", "1950. 8. 7"))
sc(1, text("세 갈래 진격", "blue"))
sc(1, TF(blue_a(COL_N, 0.1), unit([128.33, 35.3], "제35연대", "blue", 0.5)), callouts=top("북쪽 길"))
sc(1, TF(blue_a(COL_N, 0), blue_a(COL_C, 0.1), unit([128.3, 35.145], "제5연대전투단", "blue", 0.5)), callouts=top("가운데 길"))
sc(1, m("coast", "coast", [blue_a(COL_N, 0), blue_a(COL_C, 0), blue_a(COL_S, 0.1), unit("goseong", "해병대", "blue", 0.5)], tilt=22), callouts=top("남쪽 해안 도로"))
sc(1, TF(blue_a(COL_N, 0), blue_a(COL_C, 0), LOCK("seobuk", 0.3, "그 사이의 산", RED)))
sc(1, ai("sobuk_peak"), label=DRAMA, kb="out", callouts=low("서북산"))
sc(1, SB(unit([128.42, 35.24], "제24연대", "blue", 0.2), swarm([[128.36, 35.2], [128.38, 35.215]], 0.3, 60, 0.12)), callouts=low("산 뒤쪽의 적을 몰아내라"))
sc(1, black("그런데 공격 전날부터", "일이 꼬였다"))
sc(1, HM(red_a([[128.34, 35.26], [128.38, 35.26]], 0.2), clash([128.385, 35.262], 0.4)), callouts=top("1950. 8. 6 · 함안 서쪽 매복", "red"), sfx=FAR(0.2))
sc(1, ai("trigger_hand"), label=DRAMA)
sc(1, text("윌리엄 톰프슨 일병", "yellow", "미 제24연대"))
sc(1, text("동료가 빠져나갈 때까지", "blue", "홀로 기관총을 쏘다 전사"))
sc(1, doc("명예훈장 (요지)", ["윌리엄 톰프슨 일병 · 미 제24연대", "1950. 8. 6 · 함안 부근 · 사후 추서"], "MEDAL", "미국 정부", "요약"))
sc(1, text("흑인 병사의 한국전쟁 첫 명예훈장", "yellow"))
sc(1, TF(blue_a(COL_C[:2], 0.2)), callouts=top("1950. 8. 7 아침 · 출발"), sfx=SW(0))
sc(1, CD(dash_b([[128.483, 35.108], [128.46, 35.09]], 0.2)), callouts=low("길을 잘못 든 1개 대대"))
sc(1, CD(swarm([[128.43, 35.13], [128.445, 35.12]], 0.1, 80, 0.15), red_a([[128.42, 35.135], [128.44, 35.122]], 0.3)))
sc(1, CD(LOCK("h342", 0.2, "342고지", RED), hud=True), sfx=PING(0.4))
sc(1, CD(unit("h342", "제5연대전투단 1개 중대", "blue", 0.2, True), swarm(H342_RING, 0.1, 90, 0.15)))
sc(1, ai("hill342_peak"), label=DRAMA, kb="out")
sc(1, CD(blue_a([[128.48, 35.11], [128.452, 35.117]], 0.2), unit([128.475, 35.112], "해병 1개 대대", "blue", 0.4)))
sc(1, black("그런데 적보다", "무서운 것이 있었다"))
sc(1, text("더위", "red"))
sc(1, bars("첫날 해병 1개 대대 · 미군 기록", [{"label": "전투 부상", "value": 1, "display": "1", "color": "blue", "at": 0.1}, {"label": "더위로 쓰러짐", "value": 6, "display": "6배", "color": "red", "on": "여섯"}]))
sc(1, ai("exhausted_gi"), label=DRAMA, kb="out")
sc(1, CD(plane(DROP, 0.1, 1, 2.6, 1.0), mark([128.425, 35.13], "red", 0.6, "빗나간 보급"), mark([128.455, 35.098], "red", 0.8)), callouts=low("두 번이나 빗나간 보급"))
sc(1, ai("airdrop"), label=DRAMA, kb="out")
sc(1, ai("marines_ridge"), label=DRAMA, callouts=top("1950. 8. 8 · 342고지 탈환"))
sc(1, CD(red_a([[128.53, 35.13], [128.51, 35.118]], 0.2), LOCK([128.51, 35.12], 0.4, "보급로 차단", RED)), callouts=low("진동리 동쪽 · 마산 가는 길"))
sc(1, text("사흘 만에 다시 연 보급로", "blue"))
sc(1, CD(mark("chindong", "blue", 0.1), radar("chindong", 0.3, 1.0, "blue", "1950. 8. 3")), callouts=top("며칠 앞선 또 하나의 싸움"))
sc(1, ai("jindong_ambush"), label=DRAMA, callouts=low("김성은 중령의 한국 해병대"))
sc(1, text("다음 편 · 진동리 지구 기습전", "yellow", "격전의 지도 EP34"))
sc(1, text("무겁게 시작된 첫걸음", "dark"), sfx=WIND(0))
next_act()

# ===== 제3막 피의 계곡 =====
MID = [nid()]
sc(1, m("coast", "coast", [blue_a(COL_S[:3], 0.1)], tilt=22), pauseBefore=0.5, chapter={"num": "제3막", "title": "피의 계곡"}, callouts=top("해안 도로를 따라"))
sc(1, m("coast", "coast", [blue_a(COL_S[:3], 0), LOCK("goseong", 0.4, "숨은 적 차량", RED)], tilt=24, hud=True), callouts=top("1950. 8. 11 · 고성 부근"), sfx=PING(0.5))
sc(1, m("coast", "coast", [swarm([[128.32, 34.975], [128.24, 35.0]], 0.1, 120, 0.12)], tilt=24), hook={"hud": [HUD("200여 대", "쏟아져 나온 적 차량", "미군 기록", color="#FF3B3B", on="이백여")]})
sc(1, ai("kosong_strike"), label=DRAMA)
sc(1, checklist("고성 부근 · 미군 기록", [{"text": "트럭 31대", "on": "트럭과"}, {"text": "지프 24대", "on": "지프와"}, {"text": "오토바이 45대", "on": "오토바이"}]))
sc(1, m("coast", "coast", [blue_a(COL_S, 0.1), mark("sacheon", "red", 0.6)], tilt=22), callouts=low("사천 코앞까지"))
sc(1, black("하지만", "가운데 길은 달랐다"))
sc(1, GU(unit([128.29, 35.15], "제5연대전투단", "blue", 0.2)), callouts=top("봉암리 · 위치 개략"))
sc(1, GU(badge([128.27, 35.15], "좁은 고개 하나", "#111", 0.3, -60), tilt=40))
sc(1, ai("command_decision"), label=DRAMA, kb="out", callouts=top("1950. 8. 11 밤 · 사단 명령"))
sc(1, doc("사단 명령 (요지)", ["오늘 밤 고개를 넘을 부대", "1개 대대 + 포병 1개 중대만"], "命令", "미 제25사단", "1950. 8. 11 · 재구성"))
sc(1, stage([C("us_shrug", 0.5, 470, prop="officer+helmet", face="worried+sweat", anim="tilt")], [pop("label", 0.5, 0.15, "연대장", on="연대장은", color="dark"), pop("ex", 0.75, 0.3, on="재앙을")]))
sc(1, ai("radio_dead"), label=DRAMA)
sc(1, GU(dash_b([[128.31, 35.15], [128.28, 35.152]], 0.2)), callouts=low("새벽 4시쯤 · 고개 쪽으로"))
sc(1, ai("basin_jam"), label=DRAMA, kb="out")
sc(1, GU(dash_b([[128.27, 35.16], [128.27, 35.18]], 0.2)), callouts=low("자리를 뜬 소대 하나", "red"))
sc(1, GU(dash_r(GULCH_ATK[0], 0.2)), callouts=low("소리 없이 다가온 적 전차·자주포", "red"))
sc(1, GU(red_a(GULCH_ATK[0], 0.1), red_a(GULCH_ATK[1], 0.25), red_a(GULCH_ATK[2], 0.4), shock([[128.268, 35.152], [128.274, 35.149]], 0.5)), callouts=top("1950. 8. 12 새벽", "red"), sfx=FAR(0.2))
sc(1, ph("how105"), label=plabel("how105"), callouts=low("들판에 놓인 105mm 곡사포 · 같은 사단 다른 부대"))
sc(1, text("포신을 낮추지 못한 큰 포", "red", "제90포병대대 · 155mm"))
sc(1, ai("artillery_rifles"), label=DRAMA)
sc(1, black("결과는", "참혹했다"))
sc(1, bars("제555포병대대 · 미군 기록", [{"label": "잃은 곡사포", "value": 8, "display": "8문 전부", "color": "red", "on": "여덟"}]))
sc(1, troops(20, keep=4, keepAt=0.6, side="us", cols=10, title="제555포병대대 · 다음 날", labels=[{"x": 0.5, "y": 0.76, "text": "전사 75~100명 추정", "at": 0.2, "color": "red"}]))
sc(1, troops(20, keep=4, keepAt=0.2, side="us", cols=10, title="다음 날 근무에 나온 병력", labels=[{"x": 0.5, "y": 0.76, "text": "10명 중 2명꼴", "on": "두 명꼴", "color": "red"}]))
sc(1, checklist("제90포병대대 · 미군 기록", [{"text": "155mm 곡사포 6문", "on": "여섯", "bad": True}, {"text": "차량 26대", "on": "스물여섯", "bad": True}]))
sc(1, troops(18, keep=2, keepAt=0.5, side="us", cols=9, title="고개 위의 1개 중대", labels=[{"x": 0.5, "y": 0.76, "text": "180여 명 → 23명", "on": "스물세", "color": "red"}]))
sc(1, ai("trucks_left"), label=DRAMA, callouts=top("‘피의 계곡’", "red"))
sc(1, ai("fire_brigade"), label=DRAMA)
sc(1, PR(LOCK("bulge", 0.3, "뚫릴 위기", RED)), callouts=low("낙동강 돌출부로 돌아오라"))
sc(1, m("coast", "coast", [dash_b(BACK_S, 0.2), mark("jinju", "red", 0)], tilt=22), callouts=low("진주를 코앞에 두고"))
sc(1, TF(dash_b(list(reversed(COL_C[:3])), 0.1), dash_b([[128.33, 35.3], [128.45, 35.3]], 0.2)), callouts=top("1950. 8. 14 · 거의 출발선으로"))
sc(1, text("8월 16일 · 해체", "dark", "킨 특수임무부대"))
sc(1, checklist("킨 특수임무부대의 목표", [{"text": "진주 탈환", "on": "진주를", "bad": True}]))
sc(1, text("겉으로 보면 실패", "red"))
sc(1, black("하지만 숫자를 다시 보면", "이야기가 달라진다"))
sc(1, CO(unit("jinju", "북한군 제6사단", "red", 0), badge("jinju", "공격 정지", RED, 0.3, -60)), callouts=top("1950. 8. 7 ~ 14"))
sc(1, troops(25, keep=9, keepAt=0.4, side="nk", cols=10, title="북한군 제6사단 · 포로 진술", labels=[{"x": 0.5, "y": 0.76, "text": "3,000~4,000명 수준", "on": "삼사천", "color": "red"}]))
sc(1, ai("ridge_prep"), label=DRAMA)
sc(1, SB(LOCK("seobuk", 0.2, "방어선 한가운데"), hud=True), sfx=PING(0.3))
next_act()

# ===== 제4막 바위산의 주인 =====
sc(1, ai("sobuk_peak"), label=DRAMA, chapter={"num": "제4막", "title": "바위산의 주인"}, callouts=top("마산 서쪽 10여 km"))
sc(1, text("해발 739m", "yellow", "한국 기록 기준 · 미군 지도 743고지"))
sc(1, text("함안군 · 창원시 마산합포구 경계", "dark", "오늘날 행정구역"))
sc(1, ai("op_post"), label=DRAMA)
sc(1, SB(line(ROAD, 0.2, "#ffffff"), mark("haman", "blue", 0.1), mark("chindong", "blue", 0.1)), callouts=low("함안 → 진동리 길"))
sc(1, SB(line(ROAD, 0, "#ffd400"), badge([128.44, 35.18], "사실상 유일한 남북 길", "#111", 0.3, -50)))
sc(1, text("산을 쥐면 길을 쥔다", "yellow"))
sc(1, text("길을 쥐면 마산을 쥔다", "red"))
sc(1, PK(LOCK("pilbong", 0.3, "필봉 · 743고지"), tilt=42, hud=True), sfx=PING(0.4))
sc(1, PK(line([[128.386, 35.193], [128.371, 35.205]], 0.2, "#ffd400"), LOCK("battle", 0.6, "665고지", RED), tilt=42))
sc(1, text("‘전투산’", "red", "미군이 붙인 이름 · Battle Mountain"))
sc(1, black("얼마나 자주 싸웠으면", "이름이 그렇게 붙었을까"))
sc(1, text("공평하지 않은 산", "dark"))
sc(1, PK(red_a(NK_BATTLE, 0.2), tilt=44), callouts=low("서쪽 · 비교적 완만", "red"))
sc(1, PK(red_a(NK_BATTLE, 0), blue_a(US_RETAKE, 0.2), tilt=44), callouts=low("동쪽 · 가파른 바위투성이"))
sc(1, checklist("사람의 등으로", [{"text": "식량", "on": "식량과"}, {"text": "물", "on": "물과"}, {"text": "탄약", "on": "탄약을"}]))
sc(1, ai("jige_porters"), label=DRAMA, callouts=low("지게를 멘 한국인 운반대"))
sc(1, SB(*DEF3(0.2)), callouts=top("미 제25사단 방어선 · 위치 개략"))
sc(1, SB(*DEF3(0), unit([128.42, 35.335], "제35연대", "blue", 0.2)), callouts=low("북쪽 · 남강"))
sc(1, SB(*DEF3(0), unit([128.35, 35.215], "제24연대", "blue", 0.2)), callouts=low("가운데 · 전투산·필봉"))
sc(1, SB(*DEF3(0), unit([128.44, 35.14], "제5연대전투단", "blue", 0.2)), callouts=low("남쪽 능선 → 진동리"))
sc(1, ph("rok25"), label=plabel("rok25"), callouts=low("사이사이를 메운 한국 경찰·국군"))
sc(1, PK(red_a(NK_BATTLE, 0.1, 1.2), clash("battle", 0.4)), callouts=top("1950. 8. 18 · 첫 공격", "red"), sfx=FAR(0.2))
sc(1, text("주인이 바뀌기 시작하다", "red"))
sc(1, ai("night_assault"), label=DRAMA)
sc(1, ai("day_retake"), label=DRAMA)
sc(1, ai("napalm"), label=DRAMA)
sc(1, ai("day_retake"), label=DRAMA, kb="out")
sc(1, cmp("밤", "잃고", "낮", "되찾고", "red", "blue"))
sc(1, text("직접 센 미군 정보 부사관", "dark", "미군 기록"))
sc(1, text("19번", "red", "전투산 · 미군 정보 부사관 집계"))
sc(1, text("20번 가까이", "dark", "후속 연구"))
sc(1, text("서북산 주인 19번", "yellow", "한국 쪽 기록"))
sc(1, SB(blue_a([[128.43, 35.17], [128.39, 35.192]], 0.2), unit([128.43, 35.17], "제5연대전투단 A중대", "blue", 0.1)), callouts=top("1950. 8. 23 · 서북산 공격"))
sc(1, text("로버트 티몬스 대위", "yellow", "미 제5연대전투단 A중대장"))
sc(1, ai("litter_captain"), label=DRAMA)
sc(1, text("후송 거부", "blue"))
sc(1, stage([C("us_point", 0.5, 480, prop="officer+helmet", face="determined+sweat", anim="shake")], [pop("label", 0.5, 0.15, "중대장 티몬스 대위", on="계속", color="dark")]))
sc(1, text("들것에 눕혀진 중대장", "dark"))
sc(1, ai("litter_captain"), label=DRAMA, kb="out")
sc(1, doc("은성무공훈장 공적서 (요지)", ["1950. 8. 23 · 서북산", "부상에도 후송 거부 · 들것 위에서 박격포 지휘"], "SILVER", "미 육군", "사후 추서 · 요약"))
sc(1, text("고향의 7살 아들", "yellow"), sfx=WIND(0))
next_act()

# ===== 제5막 스무 번의 밤 =====
MID.append(nid())
sc(1, ai("night_assault"), label=DRAMA, kb="out", pauseBefore=0.5, chapter={"num": "제5막", "title": "스무 번의 밤"})
sc(1, SB(red_a([[128.38, 35.17], [128.41, 35.16]], 0.2), clash([128.41, 35.16], 0.4)), callouts=top("1950. 8. 25 밤", "red"), sfx=FAR(0.2))
sc(1, text("멜빈 핸드리치 상사", "yellow", "미 제5연대전투단 C중대"))
sc(1, ai("flare_dark"), label=DRAMA)
sc(1, ai("wire_cut"), label=DRAMA)
sc(1, doc("명예훈장 (요지)", ["멜빈 핸드리치 상사 · 1950. 8. 25~26", "홀로 진지를 지키다 전사 · 사후 추서"], "MEDAL", "미국 정부", "요약"))
sc(1, PK(unit([128.355, 35.215], "제24연대", "blue", 0.1)), callouts=low("전투산의 제24연대"))
sc(1, stage([C("us_shock", 0.45, 470, prop="helmet", face="worried+tears", anim="exit")], [pop("label", 0.5, 0.15, "산을 내려오는 병사들", on="진지를", color="dark")]))
sc(1, bars("1950. 8 · 이탈병 (킨 사단장 집계)", [{"label": "제24연대", "value": 116, "display": "116명", "color": "red", "on": "백 명이"}, {"label": "제27연대", "value": 15, "display": "15명", "color": "blue", "at": 0.2}, {"label": "제35연대", "value": 12, "display": "12명", "color": "blue", "at": 0.3}]))
sc(1, text("다른 두 연대의 몇 배", "red"))
sc(1, text("“연대를 해체해야 한다”", "dark", "킨 사단장의 건의"))
sc(1, black("숫자만으로는", "다 설명할 수 없다"))
sc(1, reasons("제24연대의 사정", [{"text": "차별 속의 훈련·장비", "on": "차별"}, {"text": "지휘관 사이의 불신", "later": True}, {"text": "가장 험한 봉우리", "later": True}]))
sc(1, reasons("제24연대의 사정", [{"text": "차별 속의 훈련·장비", "at": 0}, {"text": "지휘관 사이의 불신", "on": "불신도"}, {"text": "가장 험한 봉우리", "later": True}]))
sc(1, reasons("제24연대의 사정", [{"text": "차별 속의 훈련·장비", "at": 0}, {"text": "지휘관 사이의 불신", "at": 0}, {"text": "가장 험한 봉우리", "on": "험한"}]))
sc(1, ai("trigger_hand"), label=DRAMA, kb="out", callouts=low("끝까지 자리를 지킨 병사들"))
sc(1, text("1951년 · 제24연대 해체", "dark", "병사들은 여러 부대로"))
sc(1, text("흑백 통합을 앞당긴 계기", "yellow"))
sc(1, ai("vt_burst"), label=DRAMA)
sc(1, PK(red_a(NK_BATTLE, 0.1), unit("battle", "북한군", "red", 0.4, True)), callouts=top("1950. 8. 29 밤", "red"))
sc(1, PK(blue_a(US_RETAKE, 0.1), unit("battle", "미군 1개 중대", "blue", 0.4)), callouts=top("다음 날 · 다시 정상"))
sc(1, black("분명한 것은", "하나였다"))
sc(1, SB(mark("masan", "blue", 0), badge([128.39, 35.2], "넘지 못한 산", RED, 0.3, -60)), callouts=low("마산으로 내려가지 못한 북한군"))
sc(1, text("하룻밤 승리의 비싼 대가", "red"))
sc(1, cmp("미군", "폭격기·대포", "북한군", "넉넉하지 않음", "blue", "red"))
sc(1, CO(dash_r([[127.75, 35.07], [128.085, 35.18]], 0.2), mark("jinju", "red", 0), badge("jinju", "끊겨 가는 보급", RED, 0.4, -60)))
sc(1, troops(30, side="nk", cols=10, title="북한군 제6사단 · 출발 당시", labels=[{"x": 0.5, "y": 0.76, "text": "1만 명 안팎 · 미군 추정", "on": "만 명", "color": "red"}]))
sc(1, troops(30, keep=17, keepAt=0.3, side="nk", cols=10, title="8월 중순", labels=[{"x": 0.5, "y": 0.76, "text": "절반 가까이 사라짐", "at": 0.5, "color": "red"}]))
sc(1, text("빈자리 = 끌려온 남쪽 청년들", "red", "미군 포로 심문 기록"))
sc(1, stage([C("nk_shrug", 0.5, 470, prop="nkcap", face="worried+coldsweat", anim="shake")], [pop("q", 0.3, 0.3, on="총 쏘는"), pop("label", 0.5, 0.15, "끌려온 청년", on="젊은이들이", color="red")]))
sc(1, text("이름만 남은 최정예", "red"))
sc(1, ph("marines_wounded"), label=plabel("marines_wounded"))
sc(1, ai("burnt_village"), label=DRAMA)
sc(1, black("그리고 구월", "마지막 카드"), sfx=WIND(0))
next_act()

# ===== 제6막 마지막 총공세 =====
sc(1, PR(red_a(OFF[0], 0.2), red_a(OFF[1], 0.3), red_a(OFF[2], 0.4), red_a(OFF[3], 0.5)), chapter={"num": "제6막", "title": "마지막 총공세"}, callouts=top("1950. 9. 1 · 북한군 총공세", "red"), sfx=FAR(0.2))
sc(1, PR(red_a(OFF[0], 0), red_a(OFF[1], 0), red_a(OFF[2], 0), mark("daegu", "blue", on="대구"), mark("bulge", "red", on="돌출부에서도"), mark("pohang", "red", on="포항에서도")))
sc(1, HM(unit([128.35, 35.33], "북한군 제7사단", "red", on="제칠사단이"), unit([128.34, 35.22], "북한군 제6사단", "red", on="제육사단과"), tilt=28))
sc(1, HM(red_a(NK7, 0.2, 1.2), mark("namgang", "red", 0.1)), callouts=low("남강을 건너 함안으로", "red"))
sc(1, SB(red_a(NK_BATTLE, 0.1), red_a([[128.36, 35.17], [128.4, 35.17]], 0.3)), callouts=low("서북산과 남쪽 능선", "red"))
sc(1, HM(red_a(NK7, 0), LOCK("haman", 0.3, "방어선 돌파", RED), hud=True), sfx=PING(0.4))
sc(1, ai("haman_breach"), label=DRAMA, callouts=top("함안 읍내 · 재연"))
sc(1, HM(blue_a(COUNTER27, 0.2, 1.2), unit([128.47, 35.275], "제27연대", "blue", 0.1)), callouts=low("예비대 ‘울프하운드’ 투입"))
sc(1, ph("inf27"), label=plabel("inf27"))
sc(1, PK(red_a(NK_BATTLE, 0.1), unit("battle", "북한군", "red", 0.3, True)))
sc(1, text("9월 7일부터 · 내주지 않은 봉우리", "red", "전투산"))
sc(1, PK(dash_b(US_RETAKE, 0.2), clash("battle", 0.4), tilt=44))
sc(1, PK(LOCK("pilbong", 0.3, "필봉 상실", RED), unit("pilbong", "북한군", "red", 0.5)), callouts=top("1950. 9 중순", "red"))
sc(1, troops(20, keep=6, keepAt=0.4, side="us", cols=10, title="미 제27연대 A중대 · 하루", labels=[{"x": 0.5, "y": 0.76, "text": "57명을 잃다", "on": "쉰일곱", "color": "red"}]))
sc(1, ai("shells_ridge"), label=DRAMA)
sc(1, black("바로 그때", "전쟁의 흐름이 바뀐다"))
sc(1, m("korea", "korea", [blue_a(INCH, 0.2, 1.3), LOCK("incheon", 0.5, "인천 상륙", RED)], tilt=12, hud=True), callouts=top("1950. 9. 15"), sfx=PING(0.6))
sc(1, ph("landing_inchon"), label=plabel("landing_inchon"))
sc(1, m("korea", "korea", [blue_a(INCH, 0), line([[126.6, 37.45], [127.2, 37.3]], 0.2, "#7fd3ff"), dash_r([[128.4, 35.6], [128.0, 36.4]], 0.4)], tilt=12), callouts=low("끊어진 보급로·퇴로", "red"))
sc(1, SB(dash_r(NK_OUT[:2], 0.2)), callouts=top("1950. 9. 18 밤 · 철수 시작"))
sc(1, CO(dash_r(NK_OUT, 0.2)), callouts=low("서북산 → 진주 쪽으로", "red"))
sc(1, PK(blue_a(US_RETAKE, 0.2), unit("battle", "미군", "blue", 0.5)), callouts=top("1950. 9. 19 · 텅 빈 정상"))
sc(1, text("45일의 싸움이 끝나다", "yellow", "마산 앞"))
sc(1, text("기록마다 다른 숫자", "dark"))
sc(1, doc("기록 ① (기념사업회 자료 인용 기사)", ["마산방어전투 45일", "경남신문·매일신문 등"], "記錄", "마산방어전투기념사업회", "인용 · 요약"))
sc(1, bars("기록 ① · 북한군", [{"label": "사망", "value": 4000, "display": "4,000여 명", "color": "red", "on": "사천여"}, {"label": "포로", "value": 3000, "display": "3,000여 명", "color": "blue", "on": "삼천여"}]))
sc(1, bars("기록 ① · 한미 연합군", [{"label": "전사", "value": 1000, "display": "1,000여 명", "color": "blue", "on": "천여"}]))
sc(1, text("미군 쪽 분석", "dark", "북한군 제6사단"))
sc(1, troops(30, keep=6, keepAt=0.5, side="nk", cols=10, title="북한군 제6사단 · 미군 분석", labels=[{"x": 0.5, "y": 0.76, "text": "1만 명 안팎 → 북으로 2,000명", "on": "이천", "color": "red"}]))
sc(1, text("10명 가운데 8명", "red", "돌아가지 못한 병사"))
sc(1, ai("valley_quiet"), label=DRAMA, sfx=WIND(0))
next_act()

# ===== 제7막 산이 남긴 것 =====
MID.append(nid())
sc(1, ai("yuhak_dawn"), label=DRAMA, pauseBefore=0.5, chapter={"num": "제7막", "title": "산이 남긴 것"})
sc(1, text("미군 주도 전투라 잊혔다는 지적", "dark"))
sc(1, black("그런데 이 산을", "잊지 않은 가족"))
sc(1, text("1951년 · 시신 발견", "dark", "로버트 티몬스 대위"))
sc(1, text("알링턴 국립묘지", "dark", "미국 워싱턴 부근"))
sc(1, text("7살 아들 리처드", "yellow", "아버지처럼 군인으로"))
sc(1, text("별 3개 · 육군 중장", "yellow", "리처드 티몬스"))
sc(1, doc("주한 미 제8군 사령관", ["리처드 티몬스 중장", "1994 ~ 1997"], "8TH ARMY", "주한 미 제8군", "요약"))
sc(1, text("아버지가 전사한 나라", "blue"))
sc(1, text("서북산 전적비", "yellow", "지역 사단장·마을 주민과 함께"))
sc(1, text("1995년 11월", "dark", "서북산 전적비 건립"))
sc(1, text("손자 · 미 육군 대위", "blue", "1996~1997 · 휴전선 부근 초소"))
sc(1, text("3대가 지킨 나라", "yellow"))
sc(1, doc("이달의 6·25 전쟁영웅", ["2026년 8월 · 로버트 티몬스 대위", "서북산 방어"], "英雄", "국가보훈부", "2026 · 요약"))
sc(1, ai("valley_today"), label=DRAMA, callouts=top("서북산 아래 마을 · 재연"))
sc(1, text("“포탄에 산이 낮아졌다”", "dark", "마을에 전해지는 이야기"))
sc(1, black("이제", "처음의 질문으로"))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05, "kicker": "■ 처음의 질문 ■"}})
sc(1, text("미군이 많아서만은 아니었다", "dark"))
sc(1, checklist("미군도 겪은 실패", [{"text": "피의 계곡 · 대포 상실", "on": "대포를", "bad": True}, {"text": "첫 반격 · 출발선으로", "on": "출발선에서", "bad": True}]))
sc(1, reasons("서북산의 4가지", [{"text": "이틀", "later": True}, {"text": "반격", "later": True}, {"text": "산", "later": True}, {"text": "되찾기", "later": True}]))
sc(1, reasons("서북산의 4가지", [{"text": "이틀", "on": "이틀이었습니다"}, {"text": "반격", "later": True}, {"text": "산", "later": True}, {"text": "되찾기", "later": True}]))
sc(1, PR(blue_a(SANGJU_MASAN, 0.1, 1.2), unit("masan", "미 제25사단", "blue", 0.5)), callouts=low("이틀 만의 이동"))
sc(1, reasons("서북산의 4가지", [{"text": "이틀", "at": 0}, {"text": "반격", "on": "반격이었습니다"}, {"text": "산", "later": True}, {"text": "되찾기", "later": True}]))
sc(1, TF(blue_a(COL_C[:3], 0.1), unit("jinju", "북한군 제6사단", "red", 0), badge([128.2, 35.17], "멈춰 선 일주일", RED, 0.4, -60)))
sc(1, reasons("서북산의 4가지", [{"text": "이틀", "at": 0}, {"text": "반격", "at": 0}, {"text": "산", "on": "자체였습니다"}, {"text": "되찾기", "later": True}]))
sc(1, SB(line(ROAD, 0.1, "#ffd400"), LOCK("seobuk", 0.4, "길을 내려다보는 능선")))
sc(1, reasons("서북산의 4가지", [{"text": "이틀", "at": 0}, {"text": "반격", "at": 0}, {"text": "산", "at": 0}, {"text": "되찾기", "on": "되찾기였습니다"}]))
sc(1, ai("day_retake"), label=DRAMA, kb="in")
sc(1, cmp("19번", "잃고", "19번", "다시 올라가다", "red", "blue"))
sc(1, troops(30, keep=6, keepAt=0.3, side="nk", cols=10, title="녹아내린 최정예 사단"))
sc(1, m("korea", "korea", [blue_a(INCH, 0.1), mark("masan", "blue", 0), line(PERI, 0, "#7fd3ff")], tilt=12), callouts=low("번 시간 → 인천 상륙"))
sc(1, text("산 하나 = 나라 하나", "yellow"))
sc(1, ai("rok_us"), label=DRAMA)
sc(1, ai("helmets_row"), label=DRAMA, kb="out")
SOMBER = nid()
sc(1, ai("river_dawn"), label=DRAMA)
sc(1, text("다음 편 · 진동리 지구 기습전", "yellow", "격전의 지도 EP34 · 한국 해병대"))
sc(1, {"type": "endcard", "title": "서북산을 지킨\n모든 이들을 기억하며", "q": pin("naktong_today")}, tail=1.0)
sc(1, black("격전의 지도"), tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 =====
# 재사용 (파일·서명 복사, 추가 비용 0) — 국적 확인: us = 성조기 볼 / nk = 인공기 볼 / kr = 태극기 볼, 사람 없는 풍경은 국적 무관
REUSE = {
    "exhausted_gi": "ep29-daejeon", "artillery_rifles": "ep29-daejeon", "radio_dead": "ep29-daejeon",
    "walker_map": "naktong", "walker_jeep": "naktong", "marines_ridge": "naktong", "fire_brigade": "naktong", "rain_attack": "naktong",
    "rok_us": "dabudong", "jige_porters": "dabudong", "yuhak_dawn": "dabudong",
    "nk_column_coast": "ep27-tongyeong", "jindong_ambush": "ep27-tongyeong",
    "napalm": "ep28-pohang", "river_dawn": "ep28-pohang",
    "trucks_pass": "ep24-hyeonri", "trucks_left": "ep24-hyeonri", "basin_jam": "ep24-hyeonri",
    "flare_dark": "ep25-capitalhill", "wire_cut": "ep25-capitalhill", "trigger_hand": "ep25-capitalhill",
    "command_decision": "ep22-pork-chop-hill", "vt_burst": "ep22-pork-chop-hill",
    "shells_ridge": "ep21-gapyeong", "helmets_row": "ep21-gapyeong",
    "summer_heat": "ep32-dongnak", "ridge_prep": "ep32-dongnak",
    "op_post": "ep31-hwaryeong", "valley_quiet": "ep31-hwaryeong", "valley_today": "ep31-hwaryeong",
}
# 새 그림 (Cloudflare Workers AI 무료 · 사람은 작은 실루엣·뒷모습 위주, 국기·글자 없음)
TAIL = ", painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, absolutely no flags, no banners, no text, no letters."
US = "soldiers in olive drab 1950 M1 steel helmets and sweat-soaked olive drab summer uniforms"
NK = "soldiers in plain khaki 1950 uniforms and soft field caps"
NEW = {
    "hill342_peak": "A small group of exhausted " + US + " lying behind rocks on a bare rocky hilltop in southern Korea under a blazing white August 1950 sun, heat haze shimmering, empty canteens on the ground, seen from behind and far away, small figures, faces not visible",
    "airdrop": "An old twin-engine C-47 transport plane flying low over a bare rocky Korean hilltop in August 1950, supply bundles falling under white parachutes, one parachute drifting away into a distant valley, hazy hot sky",
    "kosong_strike": "Gull-winged Corsair fighter planes diving and firing rockets at a long column of military trucks, jeeps and motorcycles fleeing on a dusty coastal road between green hills and the sea in southern Korea in August 1950, explosions and black smoke, seen from high above",
    "gulch_dawn": "Dawn attack on an artillery position in a narrow Korean valley in August 1950: 105mm howitzers standing in an open rice field, tanks firing from the dark hills on three sides, muzzle flashes, smoke and morning fog, small distant figures running, seen from a distant hillside",
    "sobuk_peak": "A steep rocky bald granite mountain peak rising above forested ridges in southern Korea in the summer of 1950, bomb craters and burnt trees on the summit, a coastal plain and a distant bay far below, hazy light",
    "night_assault": "Night on a steep bare rocky Korean mountain summit in August 1950, small dark silhouettes of " + NK + " crawling up the slope toward foxholes, grenade flashes, a parachute flare hanging overhead",
    "day_retake": "Small figures of " + US + " climbing a steep rocky bare mountainside in hot daylight, white smoke from napalm drifting over the summit above, seen from behind and below",
    "litter_captain": "On a smoky rocky mountainside in August 1950, a wounded officer in an olive drab M1 steel helmet lying on a canvas stretcher and pointing ahead while soldiers crouch around him and a mortar crew fires nearby, seen from behind, small figures, faces not visible",
    "burnt_village": "A burnt-out small rural Korean village of thatched houses at the foot of a mountain in August 1950, smoke rising, charred wooden beams, an empty dirt lane, no people visible",
    "haman_breach": "Night fighting in a small 1950 Korean county town of dark tiled-roof houses, muzzle flashes between buildings, a burning house, smoke, small distant silhouettes, chaos, seen from a hill",
}
NEW = {k: v + TAIL for k, v in NEW.items()}
AI = {}
AIDIR = ROOT / "public" / "ep" / EP / "ai"
AIDIR.mkdir(parents=True, exist_ok=True)
MAN = AIDIR.parent / "ai.json"  # ai_images.py가 읽는 위치 (public/ep/<ep>/ai.json)
man = json.loads(MAN.read_text()) if MAN.exists() else {}
for k, src in REUSE.items():
    AI[k] = json.loads((ROOT / "episodes" / src / "storyboard.json").read_text(encoding="utf-8"))["ai_images"][k]
    shutil.copyfile(ROOT / "public" / "ep" / src / "ai" / f"{k}.jpg", AIDIR / f"{k}.jpg")
    srcman = json.loads((ROOT / "public" / "ep" / src / "ai.json").read_text()) if (ROOT / "public" / "ep" / src / "ai.json").exists() else {}
    man[k] = srcman.get(k) or hashlib.sha1(f"gpt-image-1|high|{AI[k]}".encode()).hexdigest()[:12]
MAN.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
AI.update(NEW)
used = {s["visual"]["img"] for s in S if s["visual"]["type"] == "ai"}
assert not used - set(AI), used - set(AI)
assert not set(AI) - used, set(AI) - used

# ===== 캐릭터 반복 방지 자동 검사 (2026-11-12 사용자 규칙) =====
stages = [s for s in S if s["visual"]["type"] == "stage"]
assert len(stages) <= 0.25 * len(S), ("stage 25% 초과", len(stages), len(S))
cnt = collections.Counter()
prev = set()
for s in S:
    cur = {ch["c"] for ch in s["visual"].get("chars", [])} if s["visual"]["type"] == "stage" else set()
    assert not (cur & prev), ("같은 나라·포즈 연속", s["id"], cur & prev)
    for c in cur:
        cnt[c] += 1
    prev = cur
over = {k: v for k, v in cnt.items() if v > 3}
assert not over, ("같은 조합 3회 초과", over)
looks = collections.Counter((ch["c"], ch.get("face"), ch.get("prop"), ch.get("anim"), bool(ch.get("flip"))) for s in stages for ch in s["visual"]["chars"])
assert all(v == 1 for v in looks.values()), ("완전히 같은 모습 반복", [k for k, v in looks.items() if v > 1])

# 막 단위 통파일 TTS(tts_mode act): 콜드 오프닝 = 0, chapter가 달린 장면마다 1씩 증가
_a = 0
for s in S:
    if s.get("chapter"):
        _a += 1
    s["act"] = _a
ids = [s["id"] for s in S]
chap = [i for i, s in enumerate(S) if s.get("chapter")]
sid = lambda i: S[i]["id"]
prev_id = lambda x: ids[ids.index(x) - 1]
music = [{"id": "drone", "from": "s001", "to": sid(chap[0] - 1), "volume": 0.2},
         {"id": "theme", "from": sid(chap[0]), "to": sid(chap[1] - 1), "volume": 0.16},
         {"id": "march", "from": sid(chap[1]), "to": sid(chap[2] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[2]), "to": sid(chap[3] - 1), "volume": 0.17},
         {"id": "analysis", "from": sid(chap[3]), "to": sid(chap[4] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[4]), "to": sid(chap[6] - 1), "volume": 0.17},
         {"id": "analysis", "from": sid(chap[6]), "to": prev_id(SOMBER), "volume": 0.16},
         {"id": "somber", "from": SOMBER, "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "주인이 열아홉 번 바뀐 산", "subtitle": "진동리·마산 서북산 혈전 · 1950", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         "target_sec": 1230, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap],
      "ai", len(AI), "pins", len(PINS), "stage", len(stages), "photo", sum(1 for s in S if s["visual"]["type"] == "photo"))
print("char uses", dict(cnt))
