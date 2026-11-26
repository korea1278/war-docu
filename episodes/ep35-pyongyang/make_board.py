# EP35 평양 최초 입성 작전 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 지도사 화면 표준 + DocuKit(punch·weapon·stamp·clip.recreated·src) + 롱폼 표준 + 초반 후킹 표준 · 목소리 승현 eleven_v3
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
    ("천구백오십년 시월 십구일", "1950년 10월 19일"), ("천구백오십년 구월 십오일", "1950년 9월 15일"), ("천구백오십년 십이월 오일", "1950년 12월 5일"),
    ("천구백오십년 사월", "1950년 4월"), ("천구백이십년 십일월", "1920년 11월"), ("천구백사십오년 십이월", "1945년 12월"), ("이천이십년", "2020년"),
    ("구월 이십팔일", "9월 28일"), ("시월 이십구일", "10월 29일"), ("시월 이십일일", "10월 21일"), ("시월 이십일", "10월 20일"), ("시월 십구일", "10월 19일"),
    ("시월 십팔일", "10월 18일"), ("시월 십칠일", "10월 17일"), ("시월 십육일", "10월 16일"), ("시월 십오일", "10월 15일"), ("시월 십사일", "10월 14일"),
    ("시월 십삼일", "10월 13일"), ("시월 십이일", "10월 12일"), ("시월 십일일", "10월 11일"), ("시월 구일", "10월 9일"), ("시월 칠일", "10월 7일"), ("시월 일일", "10월 1일"),
    ("십사일까지", "14일까지"), ("십칠일 황주", "17일 황주"), ("십팔일 밤", "18일 밤"),
    ("오전 아홉 시 삼십 분", "오전 9시 30분"), ("오전 열한 시 이 분", "오전 11시 2분"), ("오전 열한 시", "오전 11시"), ("오전 열 시 오십 분", "오전 10시 50분"), ("오전 열 시", "오전 10시"),
    ("오후 두 시 사십 분", "오후 2시 40분"), ("오후 다섯 시", "오후 5시"), ("아침 아홉 시", "아침 9시"),
    ("만 스물아홉 살", "만 29살"), ("삼백여 킬로미터", "300여 km"), ("백오십 킬로미터", "150km"), ("육십여 킬로미터", "60여 km"), ("오십 킬로미터", "50km"),
    ("팔 마일 약 십삼 킬로미터", "8마일(약 13km)"), ("삼십 마일 약 사십팔 킬로미터", "30마일(약 48km)"), ("사오백 미터", "400~500m"),
    ("팔천 명", "8,000명"), ("약 삼백 명", "약 300명"), ("만오천여 명", "1만 5천여 명"), ("오만여 명", "5만여 명"), ("삼십구 년", "39년"), ("구십육 일", "96일"), ("다섯 명", "5명"),
    ("전차 여섯 대", "전차 6대"), ("세 개 사단", "3개 사단"), ("두 개 사단", "2개 사단"), ("두 개 연대", "2개 연대"), ("한 개 중대", "1개 중대"), ("한 개 대대", "1개 대대"),
    ("세 배", "3배"), ("네 가지", "4가지"),
    ("제일기병사단", "제1기병사단"), ("제이십사사단", "제24사단"), ("제일사단", "제1사단"), ("제일군단", "제1군단"), ("제이군단", "제2군단"),
    ("제십이연대", "제12연대"), ("제십오연대", "제15연대"), ("제십일연대", "제11연대"), ("제이대대", "제2대대"), ("제칠사단", "제7사단"), ("제팔사단", "제8사단"),
    ("제팔연대", "제8연대"), ("제오기병연대", "제5기병연대"), ("삼팔선", "38선"), ("일번 도로", "1번 도로"), ("이차 대전", "2차 대전"),
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




# 좌표는 개략 (율리·지동리·선교리 로터리·여울·미림 비행장·김일성대학·대동문 등은 기록과 현재 지형 기준 근사 — 화면에 '위치 개략' 표기)
P = {
    "seoul": [126.978, 37.566, "서울"], "kaesong": [126.555, 37.971, "개성"], "korangpo": [126.88, 38.0, "고랑포"], "munsan": [126.78, 37.86, "문산"],
    "kumchon": [126.48, 38.15, "금천"], "hanpo": [126.43, 38.25, "한포리"], "namchon": [126.39, 38.33, "남천점"], "sohung": [126.1, 38.43, "서흥"],
    "sariwon": [125.756, 38.507, "사리원"], "hwangju": [125.776, 38.66, "황주"], "haeju": [125.71, 38.04, "해주"], "jinnampo": [125.4, 38.73, "진남포"],
    "sibyon": [126.73, 38.3, "시변리"], "singye": [126.53, 38.5, "신계"], "miudong": [126.6, 38.42, "미우동"], "suan": [126.36, 38.73, "수안"],
    "sangwon": [126.09, 38.85, "상원"], "yulli": [126.0, 38.9, "율리"], "jidong": [125.88, 38.95, "지동리"], "kangdong": [126.1, 39.14, "강동"],
    "pyongyang": [125.755, 39.025, "평양"], "seongyo": [125.772, 39.012, "선교리 로터리"], "bridge": [125.758, 39.019, "대동교"], "rail": [125.748, 39.012, "대동강 철교"],
    "bon": [125.745, 39.033, "본평양"], "east": [125.79, 39.012, "동평양"], "mirim": [125.83, 39.03, "미림 비행장"], "moran": [125.762, 39.048, "모란봉"],
    "kimuniv": [125.77, 39.058, "김일성대학"], "ford": [125.86, 39.07, "얕은 여울"], "neungra": [125.773, 39.04, "능라도"], "river": [125.765, 39.022, "대동강"],
    "dmun": [125.757, 39.026, "대동문"], "ulmil": [125.759, 39.044, "을밀대"], "yeongwang": [125.754, 39.022, "연광정"],
    "birth": [125.5, 38.93, "평남 강서군 덕흥리"], "kanggye": [126.6, 40.97, "강계"], "yalu": [124.45, 40.1, "압록강"], "sinuiju": [124.4, 40.1, "신의주"],
    "chosan": [125.8, 40.83, "초산"], "sunchon": [125.93, 39.43, "순천"], "sukchon": [125.66, 39.41, "숙천"], "unsan": [125.8, 40.0, "운산"],
    "yangyang": [128.62, 38.07, "양양"], "wonsan": [127.44, 39.15, "원산"], "dabudong": [128.5, 36.05, "다부동"], "daegu": [128.6, 35.87, "대구"],
    "inchon": [126.62, 37.47, "인천"], "naktong": [128.4, 35.95, "낙동강"],
}
V = {
    "korea": {"center": [127.4, 38.0], "span": 8.6}, "nk": {"center": [126.0, 39.6], "span": 6.2}, "south": {"center": [128.0, 36.6], "span": 3.6},
    "front": {"center": [126.62, 38.2], "span": 1.9}, "route": {"center": [126.22, 38.52], "span": 3.3}, "kumchon": {"center": [126.5, 38.18], "span": 0.85},
    "mid": {"center": [126.48, 38.55], "span": 1.6}, "outer": {"center": [125.9, 38.84], "span": 1.25}, "yulli": {"center": [125.95, 38.98], "span": 0.9},
    "pyong": {"center": [125.83, 39.0], "span": 0.55}, "jidong": {"center": [125.86, 38.97], "span": 0.32}, "city": {"center": [125.775, 39.032], "span": 0.2},
    "ford": {"center": [125.81, 39.05], "span": 0.26}, "pyongw": {"center": [125.62, 38.98], "span": 0.75}, "north": {"center": [125.85, 39.25], "span": 1.4},
    "yalu": {"center": [125.2, 40.35], "span": 2.6},
}
CAV = [[126.555, 37.971], [126.48, 38.15], [126.39, 38.33], [126.1, 38.43], [125.86, 38.48], [125.776, 38.66], [125.74, 38.86], [125.75, 38.99]]
ROK1 = [[126.88, 38.0], [126.73, 38.3], [126.53, 38.5], [126.36, 38.73], [126.09, 38.85], [126.0, 38.9], [125.88, 38.95], [125.772, 39.012]]
R15 = [[126.0, 38.9], [126.07, 39.0], [126.08, 39.1], [125.96, 39.1], [125.86, 39.07]]
R15X = [[125.86, 39.07], [125.81, 39.06], [125.765, 39.048]]
R7 = [[126.28, 39.1], [126.08, 39.11], [125.9, 39.09], [125.775, 39.058]]
ROK2 = [[127.35, 38.95], [126.85, 39.02], [126.4, 39.08]]
W24 = [[126.45, 37.95], [126.0, 37.98], [125.71, 38.04], [125.45, 38.62]]
EASTR = [[128.62, 38.07], [128.3, 38.6], [127.8, 39.0], [127.44, 39.15]]
P38 = [[124.6, 38.0], [125.5, 38.0], [126.5, 38.0], [127.5, 38.0], [128.7, 38.0]]
OUTER = [[125.776, 38.66], [125.88, 38.78], [126.0, 38.9]]
INNER = [[125.7, 38.985], [125.77, 39.005], [125.83, 39.02]]
NAK38 = [[128.5, 35.95], [128.2, 36.6], [127.6, 37.3], [126.9, 37.9]]
INCH = [[126.62, 37.47], [127.3, 37.05], [127.9, 36.6]]
ENV_L = [[126.5, 38.02], [126.36, 38.12], [126.43, 38.25]]
ENV_R = [[126.6, 38.02], [126.58, 38.17], [126.43, 38.25]]
FLEE = [[125.755, 39.03], [126.0, 39.6], [126.3, 40.3], [126.6, 40.97]]
CHINA = [[124.5, 40.6], [124.8, 40.2], [125.2, 39.9], [125.6, 39.6]]
CN_DOWN = [[125.4, 40.4], [125.6, 39.8], [125.75, 39.1]]
ALT = [[126.0, 38.9], [126.05, 39.2], [125.93, 39.43]]
ALT2 = [[126.0, 38.9], [125.9, 39.2], [125.66, 39.41]]
JD_HILLS = [[125.87, 38.95], [125.885, 38.958], [125.875, 38.94], [125.892, 38.948]]

LOCK = lambda p, at=0.3, text=None, color=None, on=None: dict({"k": "lock", "p": p, "text": text or P[p][2]}, **({"on": on} if on else {"at": at}), **({"color": color} if color else {}))
badge = lambda p, t, c="#111", at=0.3, dy=-70, on=None: dict({"k": "badge", "p": p, "text": t, "color": c, "dy": dy}, **({"on": on} if on else {"at": at}))
red_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "red", "width": w}, **({"on": on} if on else {"at": at}))
blue_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "blue", "width": w}, **({"on": on} if on else {"at": at}))
dash_r = lambda path, at=0.2, on=None: dict({"k": "arrow", "path": path, "color": "red", "dash": True}, **({"on": on} if on else {"at": at}))
dash_b = lambda path, at=0.2, on=None: dict({"k": "arrow", "path": path, "color": "blue", "dash": True}, **({"on": on} if on else {"at": at}))
mark = lambda p, color="red", at=0, text=None, on=None: dict({"k": "marker", "p": p, "color": color}, **({"text": text} if text else {}), **({"on": on} if on else {"at": at}))
unit = lambda p, t, color="red", at=0.1, pulse=False, on=None: dict({"k": "unit", "p": p, "text": t, "color": color}, **({"on": on} if on else {"at": at}), **({"pulse": True} if pulse else {}))
clash = lambda p, at=0.3, size=1.0, on=None: dict({"k": "clash", "p": p, "period": 0.9, "size": size}, **({"on": on} if on else {"at": at}))
shock = lambda pts, at=0.2, period=0.7: {"k": "shock", "pts": pts, "at": at, "period": period}
swarm = lambda path, at=0.1, n=120, width=None: dict({"k": "swarm", "path": path, "at": at, "n": n}, **({"width": width} if width else {}))
line = lambda path, at=0.1, color="#ffd400", on=None: dict({"k": "line", "path": path, "color": color, "glow": True}, **({"on": on} if on else {"at": at}))
radar = lambda p, at=0.2, size=1.0, color="blue", text=None: dict({"k": "radar", "p": p, "at": at, "size": size, "color": color}, **({"text": text} if text else {}))
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]
SW = lambda at=0: [{"id": "whoosh", "at": at}]
FAR = lambda at=0.1: [{"id": "artillery_far", "at": at}]
PING = lambda at=0.6: [{"id": "ping", "at": at}]
WIND = lambda at=0: [{"id": "wind", "at": at}]
TANK = lambda at=0.1: [{"id": "tank", "at": at}]
WATER = lambda at=0: [{"id": "water", "at": at}]
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))
QUESTION = "이틀 늦게 출발한 국군 1사단은\n어떻게 미군보다 먼저 평양에 닿았나"
RED = "#c9242c"
US = "#7fd3ff"   # 미군 진격로 (하늘색)
KRY = "#ffd400"  # 국군 제1사단 진격로 (노랑)
LEG = [{"icon": "kr", "text": "국군 제1사단"}, {"icon": "us", "text": "미 제1기병사단"}, {"icon": "nk", "text": "북한군"}, {"icon": "route", "text": "진격로"}]
LEG_CITY = [{"icon": "kr", "text": "국군"}, {"icon": "us", "text": "미군"}, {"icon": "nk", "text": "북한군"}]


def M(view, *items, tilt=26, **kw):
    return m(view, view, list(items), tilt=tilt, **kw)


CAVL = lambda at=0, on=None: line(CAV, at, US, on)
ROKL = lambda at=0, on=None: line(ROK1, at, KRY, on)
RT = lambda *items, tilt=14, **kw: M("route", *items, tilt=tilt, **kw)
RT2 = lambda *items, tilt=14, **kw: RT(CAVL(0), ROKL(0), mark("pyongyang", "red", 0), *items, tilt=tilt, **kw)
FR = lambda *items, tilt=18, **kw: M("front", line(P38, 0, "#ff6a5a"), *items, tilt=tilt, **kw)
KC = lambda *items, tilt=26, **kw: M("kumchon", mark("kumchon", "red", 0), *items, tilt=tilt, **kw)
MD = lambda *items, tilt=18, **kw: M("mid", ROKL(0), *items, tilt=tilt, **kw)
YL = lambda *items, tilt=24, **kw: M("yulli", mark("pyongyang", "red", 0), mark("yulli", "blue", 0), *items, tilt=tilt, **kw)
PY = lambda *items, tilt=26, **kw: M("pyong", mark("pyongyang", "red", 0), *items, tilt=tilt, **kw)
JD = lambda *items, tilt=36, **kw: M("jidong", *items, tilt=tilt, **kw)
CT = lambda *items, tilt=34, **kw: M("city", *items, tilt=tilt, **kw)
FD = lambda *items, tilt=32, **kw: M("ford", *items, tilt=tilt, **kw)
PW = lambda *items, tilt=20, **kw: M("pyongw", mark("pyongyang", "red", 0), *items, tilt=tilt, **kw)
KR = lambda *items, tilt=10, **kw: M("korea", *items, tilt=tilt, **kw)
NK = lambda *items, tilt=10, **kw: M("nk", *items, tilt=tilt, **kw)


def clip(source, text, on=None, at=0.2, pos=None, recreated=True):
    d = {"source": source, "text": text}
    if on:
        d["on"] = on
    else:
        d["at"] = at
    if pos:
        d["pos"] = pos
    if recreated:
        d["recreated"] = True
    return d


def phl(key, date=None, title=None, sub=None, kb="in", pos=None):
    """사료 사진 + 하단 제목(lower, 지도사 방식 — 채널 고유 노란 막대 디자인)"""
    v = ph(key, pos=pos)
    v["kb"] = kb
    lw = {"title": title or PH[key]["label"]}
    if date:
        lw["date"] = date
    if sub:
        lw["sub"] = sub
    v["lower"] = lw
    return v


def AI(img, kb="in", title=None, date=None, sub="재연"):
    v = ai(img, kb)
    if title:
        lw = {"title": title}
        if date:
            lw["date"] = date
        if sub:
            lw["sub"] = sub
        v["lower"] = lw
    return v


def punch(t, sub=None, color=None):
    v = {"type": "punch", "text": t}
    if sub:
        v["sub"] = sub
    if color:
        v["color"] = color
    return v


SRC = {"kr": [1], "us": [2], "both": [1, 2], "7": [1, 2, 3], "paik": [4], "end": [1, 2, 5]}

# ===== 콜드 오프닝 (결과 → 모순 → 반전 → 핵심 질문 → 타이틀) =====
sc(1, CT(LOCK("river", 0.3, "대동강 · 평양"), mark("seongyo", "blue", 0.5)), date="1950. 10. 19", clock="11:00", legend=LEG_CITY, src=SRC["kr"],
   hook={"hud": [HUD("1950. 10. 19", "평양 대동강", "오전 11시 무렵", count=False)]})
sc(1, PY(LOCK("river", 0.2, "평양 남쪽 · 대동강")))
sc(1, phl("pyongyang_entry", "1950. 10. 19", "평양으로 들어가는 장병들"), sfx=TANK(0.2))
sc(1, CT(unit("seongyo", "국군 제1사단 제12연대", "blue", 0.2, True)), src=SRC["kr"])
sc(1, AI("taedong_blast", title="대동강 다리 폭파", date="1950. 10. 19"), label=DRAMA, sfx=FAR(0.1))
sc(1, CT(clash("bridge", 0.1), clash("rail", 0.3), badge("bridge", "대동교 · 철교 폭파", RED, 0.5, -80)), stamp={"text": "폭파", "on": "끊어", "x": 0.5, "y": 0.42}, src=SRC["kr"])
sc(1, CT(LOCK("bon", 0.3, "본평양 · 북한의 심장", RED)))
sc(1, RT(CAVL(0.1), unit("hwangju", "미 제1기병사단", "blue", 0.4, True)), legend=LEG)
sc(1, RT(CAVL(0), badge("sariwon", "가장 짧고 넓은 길", "#111", 0.3, -60)))
sc(1, RT(CAVL(0), ROKL(0.1), badge("suan", "산을 넘는 먼 길", "#111", 0.4, -60)))
sc(1, phl("cav_tank", "1950. 9. 19", "미 제1기병사단의 전차"))
sc(1, RT2(unit("korangpo", "국군 제1사단", "blue", 0.2)), hook={"hud": [HUD("+2일", "국군 제1사단 늦은 출발", "10. 9 → 10. 11", on="이틀이나")]}, src=SRC["kr"])
sc(1, black("누가 봐도", "정해진 경주"))
sc(1, CT(LOCK("seongyo", 0.3, "?", RED)))
sc(2, CT(mark("seongyo", "blue", 0), LOCK("seongyo", 0.2, "선교리 로터리 · 대동교 입구")), clock="10:50",
   clip=clip("국방일보 「평양탈환작전」 · 군사편찬연구소 (요지)", "대동교 입구 선교리 로터리에\n[[제일 먼저]] 도착한 부대 — 국군 제1사단", on="가장 먼저"),
   hook={"hud": [HUD("10:50", "선교리 로터리 도착", "한국 측 기록", count=False, on="오십 분")]}, src=SRC["kr"])
sc(1, phl("paik_oct", "1950. 10", "국군 제1사단장 백선엽 준장"), hook={"hud": [HUD("만 29세", "사단장 나이", "1920. 11. 23생", count=False, on="스물아홉")]}, src=SRC["paik"])
sc(1, PW(LOCK("birth", 0.3, "고향 · 평남 강서군 (현 남포)")), src=SRC["paik"])
sc(2, black("“미군이 길을 다 열어 줬다”"), hook={"neg": {"text": "미군이 열어 준 길을 따라갔다", "at": 0.3, "xOn": "그랬을까요"}})
sc(1, JD(mark(JD_HILLS[0], "red", 0.2), mark(JD_HILLS[1], "red", 0.3), mark(JD_HILLS[2], "red", 0.4), badge("jidong", "지뢰 · 토치카", RED, 0.5, -70), tone="night"), src=SRC["both"])
sc(1, AI("tank_riders", title="전차 위에 오른 보병", date="1950. 10"), label=DRAMA)
sc(1, RT2(LOCK("pyongyang", 0.3, "?", RED)), sfx=PING(0.4))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, YL(mark("yulli", "blue", 0.3), mark("jidong", "blue", 0.5), mark("ford", "blue", 0.7), badge("pyongyang", "세 곳", "#111", 0.3, -60)))
sc(1, YL(badge("yulli", "갈림길", "#111", on="갈림길"), badge("jidong", "비 내리던 밤", "#111", on="밤", dy=-90), badge("ford", "얕은 여울", "#111", on="여울", dy=-70)))
sc(1, {"type": "titlecard", "title": "열하루의 경주", "sub": "평양 최초 입성 작전 · 1950", "at": 0, "q": pin("welcome_arch")}, flash=True)
next_act()

# ===== 제1막 삼팔선 앞의 열흘 =====
sc(1, KR(mark("inchon", "blue", 0.3), mark("naktong", "red", 0.4)), chapter={"num": "제1막", "title": "삼팔선 앞의 열흘"}, date="1950. 9", legend=LEG)
sc(1, phl("inchon_craft", "1950. 9. 15", "인천으로 향하는 상륙정"))
sc(1, KR(blue_a(INCH, 0.1, 1.2), mark("naktong", "red", 0), badge("naktong", "앞뒤로 갇힌 북한군", RED, 0.5, -60)))
sc(1, phl("seoul_ceremony", "1950. 9. 29", "서울 환도식"), date="1950. 9. 28")
sc(1, KR(line(P38, 0.1, "#ff6a5a"), LOCK([126.9, 38.0], 0.4, "38선")))
sc(1, black("넘을 것인가", "멈출 것인가"))
sc(1, KR(line(P38, 0, "#ff6a5a"), unit("yangyang", "국군 제1군단", "blue", 0.3, True)))
sc(1, KR(line(P38, 0, "#ff6a5a"), blue_a(EASTR, 0.1, 1.2), LOCK("yangyang", 0.4, "동해안 38선 돌파")), date="1950. 10. 1", src=SRC["kr"])
sc(1, phl("parallel_sign", "1950. 9월 말", "38선 돌파를 알리는 국군 제3사단"))
sc(1, text("유엔 총회 북진 결의", "blue", "1950. 10. 7"), src=SRC["kr"])
sc(1, FR(unit("kaesong", "미군 · 국군 대기", "blue", 0.2)), clock="열흘")
sc(1, KR(dash_b(NAK38, 0.1), line(P38, 0, "#ff6a5a")), hook={"hud": [HUD("300여 km", "낙동강 → 38선", on="삼백여")]}, src=SRC["kr"])
sc(1, FR(unit("kaesong", "미군 · 국군", "blue", 0), radar("kumchon", 0.3, 0.8, "red")))
sc(1, troops(30, side="nk", cols=10, title="새로 만든 북한군 3개 사단", labels=[{"x": 0.5, "y": 0.76, "text": "3개 사단", "on": "세 개", "color": "red"}]), src=SRC["kr"])
sc(1, KC(unit("kumchon", "북한군 2개 사단", "red", 0.2, True)), src=SRC["kr"])
sc(1, FR(blue_a([[126.555, 37.971], [126.5, 38.1]], 0.2, 1.2), mark("kumchon", "red", 0)), date="1950. 10. 9", clock="09:00", sfx=FAR(0.3), src=SRC["kr"])
sc(1, RT(LOCK("pyongyang", 0.3, "목표 · 적의 수도 평양", RED)), clock="")
sc(1, phl("milburn", "1950", "미 제1군단장 밀번"))
sc(1, phl("cav_mg", "1950", "미 제1기병사단 기관총반"))
sc(1, AI("dust_column", title="큰길을 달리는 기병사단", date="1950. 10"), label=DRAMA)
sc(1, RT(CAVL(0.1), mark("kaesong", "blue", on="개성에서"), mark("kumchon", "blue", on="금천과"), mark("sariwon", "blue", on="사리원"), mark("hwangju", "blue", on="황주를")))
sc(1, RT(CAVL(0), badge("sohung", "1번 도로", "#111", 0.3, -60)))
sc(1, RT(CAVL(0), ROKL(0.2), unit("korangpo", "국군 제1사단", "blue", 0.4)))
sc(1, MD(mark("korangpo", "blue", on="고랑포에서"), mark("sibyon", "blue", 0.5), mark("singye", "blue", 0.6), mark("suan", "blue", 0.7), tilt=20))
sc(1, RT(ROKL(0), dash_b([[126.88, 38.0], [125.755, 39.025]], 0.2)), hook={"hud": [HUD("150km+", "고랑포 → 평양 직선", "지도 계산", on="백오십")]}, src=[7])
sc(1, punch("문제는 길이 아니었다"))
sc(1, phl("rok_march", "1950. 8", "걸어서 이동하는 국군"))
sc(1, FR(LOCK("korangpo", 0.2, "고랑포 · 38선 돌파"), blue_a([[126.88, 38.0], [126.8, 38.15]], 0.4)), date="1950. 10. 11", src=SRC["kr"])
sc(1, FR(mark("korangpo", "blue", 0), mark("kumchon", "red", 0)), hook={"hud": [HUD("+2일", "미군보다 늦은 출발", "10. 9 → 10. 11", on="이틀")]}, src=SRC["kr"])
sc(1, KC(clash("kumchon", 0.1), unit([126.53, 38.06], "미 제1기병사단", "blue", 0.3)), sfx=FAR(0.2))
sc(1, KC(badge([126.46, 38.12], "지뢰", RED, 0.2, -50), badge([126.52, 38.13], "지뢰", RED, 0.4, -50), badge([126.5, 38.1], "지뢰", RED, 0.6, -50)), src=SRC["kr"])
sc(1, KC(blue_a(ENV_L, 0.1), blue_a(ENV_R, 0.3)))
sc(1, KC(blue_a(ENV_L, 0), blue_a(ENV_R, 0), LOCK("hanpo", 0.3, "한포리 · 적의 등 뒤")), date="1950. 10. 12", src=SRC["kr"])
sc(1, KC(clash("kumchon", 0), badge("kumchon", "북한군 2개 사단 붕괴", RED, 0.3, -70)), date="1950. 10. 14", src=SRC["kr"])
sc(1, RT(line(CAV, 0.1, "#ffffff")), callouts=low("평양으로 가는 큰길"))
sc(1, RT(CAVL(0), unit("kumchon", "미 제1기병사단", "blue", 0.2), unit("korangpo", "국군 제1사단", "blue", 0.4), badge("kumchon", "한참 앞선 미군", "#111", 0.6, -90)))
next_act()

# ===== 제2막 투명지 지도 한 장 =====
sc(1, AI("acetate_map", title="군단 작전 지도", date="1950. 10"), label=DRAMA, chapter={"num": "제2막", "title": "투명지 지도 한 장"})
sc(1, phl("paik_maj", "1950", "백선엽"))
sc(1, text("사단장 백선엽 준장", "blue", "국군 제1사단 · 1950"))
sc(1, PW(LOCK("birth", 0.3, "평남 강서군 덕흥리")), date="1920. 11", src=SRC["paik"])
sc(1, PW(mark("birth", "blue", 0), dash_b([[125.5, 38.93], [125.755, 39.025]], 0.3), badge("birth", "지금의 남포시", "#111", 0.4, -60)))
sc(1, phl("ulmildae", None, "평양 을밀대 (옛 엽서)"), src=SRC["paik"])
sc(1, flat([125.5, 42.0], 12, pins=[fpin([123.43, 41.8], "봉천(선양) · 군관학교", at=0.3)], title="만주국 · 1940년대"), src=SRC["paik"])
sc(1, flat([125.5, 42.0], 12, pins=[fpin([123.43, 41.8], "봉천(선양)", at=0), fpin([129.5, 42.9], "간도특설대", at=0.3, color=RED)], title="만주국 · 1940년대"), src=SRC["paik"])
sc(1, text("전쟁 영웅 · 친일 경력 비판", "dark", "두 평가가 함께"), src=SRC["paik"])
sc(1, PW(LOCK("pyongyang", 0.3, "해방 뒤 · 평양")), date="1945", src=SRC["paik"])
sc(1, KR(dash_b([[125.755, 39.025], [126.978, 37.566]], 0.2), mark("seoul", "blue", 0.6)), date="1945. 12", src=SRC["paik"])
sc(1, text("국군 제1사단장 · 만 29세", "blue", "1950. 4"), src=SRC["paik"])
sc(1, FR(clash("kaesong", 0.2), LOCK("kaesong", 0.4, "개성 · 개전 첫날", RED)), date="1950. 6. 25", sfx=FAR(0.2))
sc(1, M("south", LOCK("dabudong", 0.3, "다부동 · 낙동강 방어선"), tilt=14), date="1950. 8 ~ 9")
sc(1, AI("letters_table", title="작전 지도 앞의 사단장", sub="재연"), label=DRAMA)
sc(1, AI("acetate_map", kb="out", title="투명지 위의 화살표", sub="재연"), label=DRAMA)
sc(1, RT(blue_a(CAV, 0.1, 1.2), badge("pyongyang", "국군 제1사단 없음", RED, 0.5, -60)), src=SRC["kr"])
sc(1, RT(blue_a(W24, 0.1), mark("haeju", "blue", on="해주와"), mark("jinnampo", "blue", on="진남포")), src=SRC["kr"])
sc(1, phl("paik_taegu", "1950. 9. 18", "대구 부근 지휘소의 백선엽 준장"))
sc(1, RT(blue_a(CAV, 0), mark("pyongyang", "red", 0)), clip=clip("백선엽의 건의 (요지) · 국방일보", "적의 수도 공격에\n[[한국군이 빠져서는 안 된다]]", on="빠져서는"), src=SRC["kr"])
sc(1, text("청일전쟁 · 1894", "dark", "일본군의 평양 공격"), src=SRC["kr"])
sc(1, YL(dash_b([[126.3, 38.96], [126.0, 38.95], [125.79, 39.012]], 0.2), badge([126.3, 38.96], "옛 싸움의 길", "#111", 0.4, -60)))
sc(1, YL(blue_a([[126.3, 38.96], [126.0, 38.95], [125.79, 39.012]], 0.1), LOCK("east", 0.4, "평양의 동쪽")))
sc(1, PW(mark("birth", "blue", 0), badge("birth", "자란 땅", "#111", 0.3, -60)))
sc(1, phl("milburn", "1950", "미 제1군단장 밀번"), src=SRC["kr"])
sc(1, RT(blue_a(ROK1, 0.1, 1.1, on="제일사단과"), dash_b(W24, on="이십사사단의")), src=SRC["kr"])
sc(1, RT(blue_a(ROK1, 0), blue_a(W24, 0), badge("jinnampo", "미 제24사단", "#111", 0.2, -60), badge("yulli", "국군 제1사단", "#111", 0.4, -60)))
sc(1, RT(ROKL(0.1), LOCK("pyongyang", 0.4, "국군 제1사단 → 평양 동쪽")))
sc(1, black("화살표만", "바뀌었다"))
sc(1, cmp("미 제1기병사단", "트럭·대포 넉넉", "국군 제1사단", "트럭·대포 부족", "blue", "blue"))
sc(1, FR(clash([126.86, 38.06], 0.2), badge([126.86, 38.06], "첫날부터 막힘", RED, 0.4, -60)), date="1950. 10. 11", src=SRC["kr"])
sc(1, phl("cav_tank", "1950. 9. 19", "미군 전차"))
sc(1, FR(unit("korangpo", "미 전차 1개 중대 배속", "blue", on="한 개 중대", pulse=True)), src=SRC["kr"])
sc(1, {"type": "weapon", "bg": "blueprint", "units": [{"kind": "tank", "x": 0.5, "y": 0.64, "w": 760, "label": "미군 전차 중대", "sub": "국군 제1사단에 배속"}], "title": "대등한 경쟁"}, src=SRC["kr"])
sc(1, RT2(unit("korangpo", "국군 제1사단", "blue", 0.2), unit("kumchon", "미 제1기병사단", "blue", 0.3)), callouts=top("경주 시작"))
next_act()

# ===== 제3막 멈추지 않는 사단 =====
sc(1, MD(LOCK("sibyon", 0.3, "시변리")), chapter={"num": "제3막", "title": "멈추지 않는 사단"}, date="1950. 10. 13", legend=LEG, src=SRC["kr"])
sc(1, MD(mark("sibyon", "blue", 0), badge("sibyon", "산골의 갈림길", "#111", 0.3, -60)))
sc(1, PY(LOCK("bon", 0.3, "평양", RED), tone="night"))
sc(1, NK(dash_r(FLEE, 0.1), LOCK("kanggye", 0.5, "강계로 · 북한 지도부", RED)), src=SRC["kr"])
sc(1, FR(mark("kumchon", "red", 0), badge("kumchon", "금천 붕괴 하루 전", RED, 0.3, -60)))
sc(1, MD(LOCK("singye", 0.3, "신계")), date="1950. 10. 14", src=SRC["kr"])
sc(1, KC(clash("kumchon", 0.1), badge("kumchon", "북한군 2개 사단 섬멸", RED, 0.4, -70)))
sc(1, MD(unit("miudong", "북한군 연대 규모", "red", 0.2, True)), date="1950. 10. 15", src=SRC["us"])
sc(1, MD(unit("miudong", "북한군", "red", 0), clash("miudong", 0.2)), hook={"hud": [HUD("6대", "북한군 전차", "미군 기록", color="#FF3B3B", on="여섯")]}, src=SRC["us"])
sc(1, phl("f51_line", "1950", "미 공군 F-51 전투기"))
sc(1, MD(blue_a(ROK1[2:4], 0.1, 1.1), mark("miudong", "red", 0)))
sc(1, MD(LOCK("suan", 0.3, "수안")), date="1950. 10. 16", src=SRC["both"])
sc(1, RT(ROKL(0), dash_b([[126.36, 38.73], [125.755, 39.025]], 0.2)), hook={"hud": [HUD("60여 km", "수안 → 평양 직선", "미군 기록 40마일", on="육십여")]}, src=SRC["us"])
sc(2, MD(blue_a(ROK1[1:5], 0.1, 1.1)), clip=clip("애플먼 『낙동강에서 압록강으로』 (요지)", "백선엽이 밝힌 전술은\n[[멈추지 않는다]]", on="멈추지"), src=SRC["us"])
sc(1, AI("tank_riders", kb="out", title="전차 위의 보병", sub="재연"), label=DRAMA, sfx=TANK(0.2))
sc(1, phl("tank_desant", "1950. 9", "전차에 오른 보병 (미 제2사단 제9연대)"))
sc(1, RT(CAVL(0.1), unit("sohung", "미 제1기병사단", "blue", 0.3, True)))
sc(1, RT(CAVL(0), LOCK("sohung", 0.3, "서흥")), date="1950. 10. 16", src=SRC["kr"])
sc(1, RT(CAVL(0), badge("sariwon", "사리원 우회", "#111", 0.2, -60), LOCK("hwangju", 0.5, "황주")), date="1950. 10. 17", src=SRC["kr"])
sc(1, RT(CAVL(0), dash_b([[125.776, 38.66], [125.755, 39.025]], 0.2)), hook={"hud": [HUD("50여 km", "황주 → 평양", "지도 계산", on="오십")]}, src=[7])
sc(1, RT2(unit("hwangju", "미 제1기병사단", "blue", 0.2), unit("suan", "국군 제1사단", "blue", 0.3)))
sc(1, phl("gay", "1950. 8. 25", "미 제1기병사단장 게이 소장"))
sc(1, flat([130.0, 25.0], 34, pins=[fpin([120.98, 14.6], "마닐라", on="마닐라"), fpin([139.69, 35.69], "도쿄", on="도쿄에")], title="미 제1기병사단 · 2차 대전"), src=[6])
sc(1, text("평양에도 가장 먼저", "blue", "미 제1기병사단의 목표"), src=[6])
sc(1, phl("rok_hills", "1950. 8", "고지로 오르는 국군"))
sc(1, text("태극기를 먼저", "yellow", "나라의 자존심"))
sc(1, PW(mark("birth", "blue", 0), LOCK("birth", 0.3, "사단장의 고향")))
sc(1, RT2(unit("hwangju", "미 기병사단", "blue", 0), unit("suan", "국군 제1사단", "blue", 0), badge("yulli", "경쟁", "#111", 0.3, -60)))
sc(1, MD(unit([126.4, 38.76], "제11연대", "blue", 0.2), unit([126.32, 38.7], "제12연대", "blue", 0.35), unit([126.42, 38.68], "제15연대", "blue", 0.5)), src=SRC["kr"])
sc(1, RT2(radar("pyongyang", 0.2, 0.8, "red")), callouts=low("열하루 경주의 절반"))
next_act()

# ===== 제4막 율리 갈림길 =====
sc(1, YL(LOCK("yulli", 0.3, "율리 · 위치 개략"), mark("sangwon", "blue", on="상원을")), chapter={"num": "제4막", "title": "율리 갈림길"}, date="1950. 10. 17", legend=LEG, src=SRC["kr"])
sc(1, YL(badge("yulli", "평양 코앞의 갈림길", "#111", 0.3, -60)))
sc(1, PY(unit("bon", "평양 방위 사령부", "red", 0.3, True)), src=SRC["kr"])
sc(1, M("outer", mark("pyongyang", "red", 0), radar("pyongyang", 0.2, 1.0, "red"), tilt=22))
sc(1, M("outer", line(OUTER, 0.1, "#ff6a5a", on="바깥"), mark("hwangju", "red", 0.3), mark("yulli", "red", 0.4), tilt=22), src=SRC["kr"])
sc(1, M("outer", line(OUTER, 0, "#ff6a5a"), line(INNER, 0.1, "#ff6a5a", on="안쪽"), tilt=22), src=SRC["kr"])
sc(1, PY(line(INNER, 0, "#ff6a5a")), hook={"hud": [HUD("8,000명 이하", "평양 방어 북한군", "미 8군 정보 판단", color="#FF3B3B", on="팔천")]}, src=SRC["both"])
sc(1, KR(LOCK("seoul", 0.3, "서울")), date="1950. 10. 17")
sc(1, text("이승만 대통령 → 정일권 총사령관", "dark", "1950. 10. 17 · 밀명"), src=SRC["kr"])
sc(1, RT2(), clip=clip("이승만 대통령의 밀명 (요지) · 국방일보", "무슨 일이 있더라도\n[[평양만큼은 국군이 먼저]]", on="평양만큼은"), src=SRC["kr"])
sc(1, RT(blue_a(ROK2, 0.2, 1.1), unit([127.35, 38.95], "국군 제2군단", "blue", 0.4)), src=SRC["kr"])
sc(1, YL(blue_a(R7, 0.1), unit([126.28, 39.1], "제7사단", "blue", on="제칠사단과"), unit([126.25, 39.0], "제8사단", "blue", on="제팔사단이")), src=SRC["kr"])
sc(1, YL(LOCK("yulli", 0.3, "백선엽 · 율리")))
sc(1, YL(blue_a(ROK1[5:], 0.1), badge("yulli", "한 길로만?", "#111", 0.4, -60)))
sc(1, YL(swarm(ROK1[5:], 0.1, 90, 0.05), badge("jidong", "막히면 전체가 멈춘다", RED, 0.4, -70)))
sc(1, YL(unit("yulli", "제15연대", "blue", on="제십오연대를", pulse=True)), src=SRC["kr"])
sc(1, YL(blue_a(R15, 0.1, 1.1), mark("kangdong", "blue", on="강동")), src=SRC["kr"])
sc(1, YL(blue_a(R15, 0), blue_a(R15X, 0.1), LOCK("moran", 0.5, "대동강 북쪽 · 모란봉")), src=SRC["kr"])
sc(1, YL(blue_a(R15, 0), blue_a(ROK1[5:], 0.2, 1.1), badge("east", "제11·12연대 → 동평양", "#111", 0.5, -60)))
sc(1, YL(blue_a(R15, 0), blue_a(ROK1[5:], 0)), sfx=PING(0.4), callouts=top("왜 둘로?"))
sc(1, CT(LOCK("river", 0.3, "평양을 가로지르는 대동강")), legend=LEG_CITY)
sc(1, CT(badge("river", "강폭 400~500m", "#111", 0.3, -70)), hook={"hud": [HUD("400~500m", "대동강 강폭", "평양 구간", on="사오백")]}, src=SRC["kr"])
sc(1, AI("pyongyang_1950", title="대동강 건너 평양", date="1950"), label=DRAMA)
sc(1, CT(mark("east", "blue", 0), mark("bon", "red", 0), badge("river", "대동강", "#111", 0.3, -50)), callouts=low("강을 사이에 둔 두 도시"))
sc(1, CT(badge("east", "동평양", "#111", on="동평양이고"), badge("bon", "본평양", RED, on="본평양이었습니다")), src=SRC["kr"])
sc(1, phl("han_bridge", "1950", "서울 한강"))
sc(1, CT(LOCK("bon", 0.3, "북한 정부 주요 기관", RED)), src=SRC["kr"])
sc(1, CT(LOCK("bridge", 0.2, "대동교", on="대동교와"), mark("rail", "blue", on="철교")), src=SRC["kr"])
sc(1, CT(mark("bridge", "blue", 0), mark("rail", "blue", 0), badge("bridge", "끊기면?", RED, 0.3, -80)))
sc(1, phl("paik_oct", "1950. 10", "평양에서 자란 사단장"))
sc(1, FD(LOCK("ford", 0.3, "얕은 여울 · 위치 개략")), src=SRC["both"])
sc(1, YL(blue_a(R15, 0.1), line(R15, 0.1, KRY), mark("ford", "blue", 0.5)))
sc(1, FD(dash_b(R15X, 0.2), mark("ford", "blue", 0), badge("ford", "다리 없이 건널 길", "#111", 0.4, -60)))
sc(1, RT(CAVL(0), unit([125.75, 38.8], "미 제1기병사단", "blue", 0.2, True)))
sc(1, PY(mark("jidong", "blue", 0.2), tone="night"), callouts=low("마지막 하룻밤"))
next_act()

# ===== 제5막 지동리의 밤 =====
sc(1, JD(LOCK("jidong", 0.3, "지동리 · 위치 개략")), chapter={"num": "제5막", "title": "지동리의 밤"}, date="1950. 10. 18", legend=LEG, src=SRC["kr"])
sc(1, PY(mark("jidong", "red", 0), badge("jidong", "평양 동남쪽 마지막 관문", RED, 0.3, -70)))
sc(1, JD(*[mark(p, "red", 0.2 + 0.12 * i) for i, p in enumerate(JD_HILLS)], badge(JD_HILLS[1], "토치카", RED, 0.6, -60)), src=SRC["kr"])
sc(1, AI("mined_road", title="지뢰가 묻힌 길", date="1950. 10"), label=DRAMA)
sc(1, PY(dash_r([[125.755, 39.03], [125.72, 39.3]], 0.2), badge("pyongyang", "빠져나갈 시간 벌기", RED, 0.4, -60)), src=SRC["kr"])
sc(1, JD(blue_a([[125.92, 38.92], [125.885, 38.945]], 0.1), clash("jidong", 0.4)))
sc(1, JD(*[mark(p, "red", 0) for p in JD_HILLS], tone="night"), clock="밤 · 비", sfx=WIND(0.1), src=SRC["us"])
sc(1, AI("rain_barrage", title="빗속의 포격", date="1950. 10. 18"), label=DRAMA, sfx=FAR(0.1), src=SRC["kr"])
sc(1, JD(*[mark(p, "red", 0) for p in JD_HILLS], shock(JD_HILLS, 0.1, 0.6), tone="night"), src=SRC["kr"])
sc(1, CT(LOCK("bon", 0.3, "평양 시내"), tone="night"))
sc(1, CT(mark("dmun", "blue", on="대동문과"), mark("ulmil", "blue", on="을밀대"), mark("yeongwang", "blue", on="연광정"), badge("ulmil", "포격 금지", "#111", 0.7, -60), tone="night"), src=SRC["kr"])
sc(1, flat([137.0, 35.5], 9, pins=[fpin([135.77, 35.01], "교토", on="교토를")], title="2차 대전 · 일본"), src=SRC["kr"])
sc(1, CT(mark("dmun", "blue", 0), mark("ulmil", "blue", 0), mark("yeongwang", "blue", 0), badge("dmun", "미군도 동의", "#111", 0.3, -60), tone="night"), src=SRC["kr"])
sc(1, JD(*[mark(p, "red", 0) for p in JD_HILLS], tone="night"), clock="새벽")
sc(1, JD(blue_a([[125.92, 38.92], [125.86, 38.97]], 0.1, 1.2)), clock="아침", src=SRC["us"])
sc(1, JD(unit([125.92, 38.92], "미 전차 중대", "blue", 0.2, True)), src=SRC["us"])
sc(1, JD(blue_a([[125.92, 38.925], [125.9, 38.96], [125.87, 38.965]], 0.1), blue_a([[125.92, 38.925], [125.88, 38.93], [125.86, 38.95]], 0.2), clash("jidong", 0.4), shock(JD_HILLS[:2], 0.5)), sfx=TANK(0.1), src=SRC["us"])
sc(1, JD(clash("jidong", 0)), hook={"hud": [HUD("약 300명", "북한군 사살 (추정)", "미군 기록", color="#FF3B3B", on="삼백")]}, src=SRC["us"])
sc(1, AI("field_phone", title="버려진 진지의 전화선", sub="재연"), label=DRAMA, src=SRC["kr"])
sc(1, text("통신 참모 윤혁표 대위", "blue", "국군 제1사단"), src=SRC["kr"])
sc(1, PY(radar("bon", 0.2, 0.9, "red", "북한군 총사령부 통신")), sfx=PING(0.5), src=SRC["kr"])
sc(2, phl("paik_taegu", "1950", "백선엽 준장"), src=SRC["kr"])
sc(2, PY(radar("bon", 0, 0.9, "red")), clip=clip("백선엽 회고 · 감청된 북한군 통신병 (요지)", "미군 전차 수백 대가 몰려온다\n[[도망쳐야갔시요]]", on="도망쳐야"), src=SRC["kr"])
sc(1, PY(swarm([[125.755, 39.03], [125.73, 39.2]], 0.1, 80, 0.06), badge("bon", "흔들리는 적", RED, 0.4, -60)))
sc(1, RT2(unit("jidong", "국군 제1사단", "blue", 0.2), unit([125.75, 38.62], "미 기병사단 선두", "blue", 0.3), tone="night"), src=SRC["us"])
sc(1, RT2(unit("jidong", "국군 제1사단", "blue", 0), tone="night"), hook={"hud": [HUD("8마일", "국군 제1사단 → 평양", "약 13km · 10. 18 밤", color="#FFD400", on="팔 마일")]}, src=SRC["us"])
sc(1, RT2(unit([125.75, 38.62], "미 기병사단 선두", "blue", 0), tone="night"), hook={"hud": [HUD("8마일", "국군 제1사단", "약 13km", color="#FFD400", count=False), HUD("30마일", "미 기병사단 선두", "약 48km", color="#4FA3FF", on="삼십 마일")]}, src=SRC["us"])
sc(1, RT2(unit("jidong", "국군 제1사단", "blue", 0), unit([125.75, 38.62], "미 기병사단", "blue", 0), badge("jidong", "3배 넘게 가까이", "#111", 0.3, -70), tone="night"))
sc(1, black("아직", "끝나지 않았다"))
sc(1, CT(LOCK("river", 0.3, "대동강"), tone="night"))
next_act()

# ===== 제6막 대동강 =====
sc(1, PY(mark("jidong", "blue", 0)), chapter={"num": "제6막", "title": "대동강"}, date="1950. 10. 19", clock="아침", legend=LEG_CITY)
sc(1, PY(blue_a([[125.88, 38.95], [125.79, 39.0]], 0.1), blue_a([[125.9, 38.97], [125.81, 39.015]], 0.2)), src=SRC["kr"])
sc(1, PY(badge([125.84, 38.98], "지뢰", RED, 0.2, -50), badge([125.81, 39.0], "지뢰", RED, 0.4, -50)), src=[6])
sc(1, AI("mined_road", kb="out", title="지뢰에 부서진 지프", date="1950. 10. 19"), label=DRAMA, src=[6])
sc(1, CT(LOCK("seongyo", 0.3, "선교리 로터리")), clock="10:50", hook={"hud": [HUD("10:50", "선교리 로터리 도착", "한국 측 기록", count=False)]}, src=SRC["kr"])
sc(1, CT(unit("seongyo", "제12연대 제2대대", "blue", 0.2, True)), clock="11:00", src=SRC["both"])
sc(1, CT(clash("bridge", 0.1, 1.3), clash("rail", 0.2, 1.3)), stamp={"text": "폭파", "on": "폭파했습니다", "x": 0.5, "y": 0.42}, sfx=FAR(0.1), src=SRC["both"])
sc(1, CT(clash("bridge", 0), badge("bridge", "미군 1개 대대 진입 직전", RED, 0.3, -80)), src=SRC["kr"])
sc(1, CT(badge("river", "배 · 부교가 필요", "#111", 0.3, -60)))
sc(1, phl("cav_mg", "1950", "미 제1기병사단 병사들"))
sc(1, PY(unit([125.75, 38.99], "미 제5기병연대 F중대", "blue", 0.2, True)), clock="11:02", hook={"hud": [HUD("11:02", "미군 공식 기록", "제5기병연대 F중대", color="#4FA3FF", count=False, on="이 분")]}, src=SRC["us"])
sc(1, CT(mark("seongyo", "blue", 0), mark([125.752, 39.0], "blue", 0)), clip=clip("애플먼 『낙동강에서 압록강으로』 (요지)", "두 부대는\n[[거의 동시에]] 평양에 들어왔다", on="거의 동시에"), src=SRC["us"])
sc(1, cmp("한국 측 기록", "10:50", "미군 공식 기록", "11:02", "blue", "blue"), src=SRC["both"])
sc(1, punch("강은 달랐다", "다리 없이 건너는 싸움"))
sc(1, CT(LOCK("mirim", 0.3, "미림 비행장"), unit("mirim", "제11연대 + 미 전차", "blue", 0.5)), clock="14:40", src=SRC["both"])
sc(1, FD(blue_a(R15[2:], 0.1), unit("ford", "제15연대", "blue", 0.4, True)), src=SRC["both"])
sc(1, FD(LOCK("ford", 0.3, "기억 속의 얕은 여울")))
sc(2, FD(mark("ford", "blue", 0)), clip=clip("애플먼 · 백선엽의 말 (요지)", "나는 평양 사람이다\n[[여울을 안다]]", on="여울이"), src=SRC["us"])
sc(1, AI("ford_crossing", title="해 질 녘 · 대동강 북쪽으로", date="1950. 10. 19"), label=DRAMA, clock="해 질 녘", sfx=WATER(0.2), src=SRC["us"])
sc(1, CT(dash_b([[125.765, 39.01], [125.757, 39.026]], 0.2), badge("river", "미군 부교 · 10. 20 새벽", "#111", 0.4, -60)), clock="", src=SRC["kr"])
sc(1, YL(blue_a(R7, 0.1, 1.1), unit([126.28, 39.1], "제7사단 제8연대", "blue", 0.3)), src=SRC["both"])
sc(1, CT(LOCK("kimuniv", 0.3, "김일성대학")), clock="17:00", src=SRC["us"])
sc(1, text("7사단 측 기록 · 10. 18 밤", "dark", "대학 옥상에 태극기"), src=SRC["7"])
sc(1, CT(badge("seongyo", "1사단 10:50", "#111", 0.1, -60), badge([125.752, 39.0], "5기병 11:02", "#111", 0.3, -60), badge("kimuniv", "7사단 10. 18?", "#111", 0.5, -60)), src=SRC["7"])
sc(3, doc("『6·25전쟁사』 6권 (2009) 정리", ["동평양 — 국군 제1사단 제11·12연대 + 미 제5기병연대", "본평양 — 국군 제1사단 제15연대 + 제7사단 제8연대"], "戰史", "국방부 군사편찬연구소", "요약"), src=SRC["kr"])
sc(1, CT(LOCK("bon", 0.3, "평양 전역 확보")), date="1950. 10. 20", clock="10:00", src=SRC["us"])
sc(1, AI("pyongyang_1950", kb="out", title="종소리가 울린 도시", date="1950. 10. 20"), label=DRAMA, src=SRC["us"])
sc(1, phl("milburn", "1950", "미 제1군단장 밀번"), clock="")
sc(1, phl("gay", "1950", "미 제1기병사단장 게이 소장"), src=[6])
sc(1, phl("pyongyang_entry", "1950. 10. 19", "평양에 들어간 장병들", kb="out"), src=[6])
next_act()

# ===== 제7막 열하루의 답 =====
sc(1, RT2(LOCK("pyongyang", 0.3, "평양")), chapter={"num": "제7막", "title": "열하루의 답"}, legend=LEG)
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, reasons("열하루의 4가지", [{"text": "멈추지 않음", "later": True}, {"text": "빌려 온 전차", "later": True}, {"text": "율리 갈림길", "later": True}, {"text": "고향의 여울", "later": True}]))
sc(1, reasons("열하루의 4가지", [{"text": "멈추지 않음", "on": "멈추지"}, {"text": "빌려 온 전차", "later": True}, {"text": "율리 갈림길", "later": True}, {"text": "고향의 여울", "later": True}]))
sc(1, RT(line(ROK1, 0.1, KRY), *[mark(p, "blue", 0.2 + 0.1 * i) for i, p in enumerate(["sibyon", "singye", "suan", "yulli", "jidong"])]))
sc(1, JD(shock(JD_HILLS, 0.1, 0.6), tone="night"))
sc(1, reasons("열하루의 4가지", [{"text": "멈추지 않음", "at": 0}, {"text": "빌려 온 전차", "on": "빌려"}, {"text": "율리 갈림길", "later": True}, {"text": "고향의 여울", "later": True}]))
sc(1, phl("tank_desant", "1950. 9", "전차 위의 보병"))
sc(1, JD(blue_a([[125.92, 38.925], [125.9, 38.96], [125.87, 38.965]], 0.1), blue_a([[125.92, 38.925], [125.88, 38.93], [125.86, 38.95]], 0.2), clash("jidong", 0.4)))
sc(1, reasons("열하루의 4가지", [{"text": "멈추지 않음", "at": 0}, {"text": "빌려 온 전차", "at": 0}, {"text": "율리 갈림길", "on": "율리"}, {"text": "고향의 여울", "later": True}]))
sc(1, YL(blue_a(R15, 0.1), blue_a(ROK1[5:], 0.2)))
sc(1, CT(clash("bridge", 0.1), dash_b(R15X, 0.3)))
sc(1, reasons("열하루의 4가지", [{"text": "멈추지 않음", "at": 0}, {"text": "빌려 온 전차", "at": 0}, {"text": "율리 갈림길", "at": 0}, {"text": "고향의 여울", "on": "여울"}]))
sc(1, FD(LOCK("ford", 0.3, "얕은 물길")))
sc(1, AI("ford_crossing", kb="out", title="강을 길로 바꾼 지휘관", sub="재연"), label=DRAMA)
sc(1, black("그리고", "하나 더"))
sc(1, NK(dash_r(FLEE, 0.1), mark("kanggye", "red", 0.5)), src=SRC["kr"])
sc(1, PY(badge("pyongyang", "생각보다 빨리 열린 평양", "#111", 0.3, -60)))
sc(1, phl("paik_1951", "1951", "백선엽"))
sc(1, text("“평양에 들어간 날이\n내 생애 최고의 날”", "yellow", "백선엽 회고"), src=SRC["paik"])
sc(1, PW(mark("birth", "blue", 0)), hook={"hud": [HUD("1만 5천여 명", "지휘한 한·미 장병", "백선엽 회고", on="만오천")]}, src=SRC["paik"])
sc(1, phl("macarthur_korea", "1950", "맥아더 원수"), date="1950. 10. 21", src=SRC["us"])
sc(1, CT(unit([125.745, 39.0], "제5기병연대 F중대 사열", "blue", 0.2)), src=SRC["us"])
sc(1, text("96일 전 함께 온 병사", "dark", "앞으로 나오라"), src=SRC["us"])
sc(1, troops(5, side="us", cols=5, title="앞으로 나온 병사", labels=[{"x": 0.5, "y": 0.76, "text": "5명", "on": "다섯", "color": "blue"}]), src=SRC["us"])
sc(1, CT(LOCK("neungra", 0.3, "능라도 비행장")), date="1950. 10. 29", clock="09:30", src=SRC["kr"])
sc(1, CT(LOCK("bon", 0.2, "평양 시청")), hook={"hud": [HUD("5만여 명", "평양 시청 앞 군중", on="오만")]}, src=SRC["kr"])
sc(1, text("39년 만의 평양", "yellow", "이승만 대통령"), src=SRC["kr"])
sc(1, black("아무도", "몰랐던 일"), clock="")
sc(1, M("yalu", red_a(CHINA, 0.2, 1.3), swarm(CHINA, 0.1, 160, 0.12), LOCK("yalu", 0.5, "압록강", RED), tilt=14), date="1950. 10. 19", src=SRC["end"])
sc(1, phl("peng", None, "중국 인민지원군 사령관 펑더화이"), date="1950. 10. 25", src=SRC["end"])
sc(1, NK(red_a(CN_DOWN, 0.2, 1.2), LOCK("pyongyang", 0.5, "평양 다시 함락", RED)), date="1950. 12. 5", src=SRC["end"])
sc(1, phl("desfor", "1950. 12", "끊어진 대동강 철교 위의 피란민"))
sc(1, phl("refugees_ford", "1950. 12. 3", "대동강을 걸어서 건너는 피란민"), hook={"hud": [HUD("두 달 미만", "국군의 평양 확보", "10. 19 → 12. 5", count=False, on="두 달")]})
sc(1, text("다른 평가도 있다", "dark", "군사편찬연구소 연구원의 분석"), src=SRC["kr"])
sc(1, M("north", mark("pyongyang", "red", 0), dash_b(ALT, 0.1), dash_b(ALT2, 0.3), LOCK("sunchon", 0.5, "순천"), mark("sukchon", "blue", on="숙천"), tilt=20), src=SRC["kr"])
sc(1, RT(line(ROK1, 0.1, KRY), LOCK("seongyo", 0.5, "대동강 강가")))
sc(1, phl("paik_2011", "2011. 7. 27", "백선엽 장군 (정전 58주년)"), src=SRC["paik"])
SOMBER = nid()
sc(1, AI("helmets_row", kb="out", title="이름 없이 쓰러진 병사들", sub="재연"), label=DRAMA)
sc(1, NK(blue_a([[125.93, 39.43], [125.9, 40.1], [125.8, 40.83]], 0.2), LOCK("chosan", 0.5, "초산 · 압록강")))
sc(1, text("다음 편 · 초산·압록강 진격전", "yellow", "격전의 지도 EP36"))
sc(1, {"type": "endcard", "title": "평양으로 가는 길 위의\n모든 병사를 기억하며", "q": pin("taedong_today")}, tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 =====
REUSE = {"letters_table": "ep31-hwaryeong", "helmets_row": "ep33-seobuksan"}
TAIL = ", cinematic photorealistic reenactment, 1950 Korean War, muted desaturated film color, 35mm documentary still, film grain, faces not identifiable, absolutely no flags, no banners, no text, no letters, no numbers."
ROK = "South Korean soldiers in 1950 olive drab US-style fatigues and M1 steel helmets, absolutely no collar tabs, no patches, no red, no stars"
NEW = {
    "taedong_blast": "A long steel truss bridge over a wide river exploding in the middle in October 1950, huge plume of black smoke and dust, an old Korean city with tiled roofs on the far bank, autumn haze, tiny distant silhouettes of soldiers on the near riverbank seen from behind",
    "tank_riders": ROK + ", many infantrymen riding on top of plain olive drab M4 Sherman tanks with no markings, no stars and no numbers, driving along a dusty winding mountain dirt road through autumn hills in North Korea in October 1950, seen from behind and above, small figures",
    "acetate_map": "Close view of a 1950 military operations map on a wooden field table inside a canvas tent, a clear transparent acetate overlay sheet on top with hand-drawn grease pencil arrows and lines only, a kerosene lantern, a compass and a pencil, the map shows only blank terrain contours and rivers without any writing, no people",
    "dust_column": "From a hilltop, a long column of olive drab army trucks and tanks with no markings driving north on a wide dusty dirt road through golden autumn rice fields in North Korea in October 1950, clouds of dust, small distant vehicles, no people close",
    "mined_road": "A destroyed old 1940s army jeep with no markings lying tilted beside a crater on a narrow autumn dirt road near a river in North Korea in October 1950, thin smoke, scattered debris, wet ground, no people visible",
    "rain_barrage": "Night in heavy rain in October 1950, a row of artillery guns and dark tanks with no markings firing toward low hills, bright muzzle flashes reflected in puddles, smoke and rain streaks, gun crews as dark silhouettes seen from behind",
    "field_phone": "An abandoned muddy trench on a hill at grey dawn after rain in October 1950, an old hand-crank military field telephone in a wooden case with a long black wire running along the trench, spent shell casings, no people",
    "pyongyang_1950": "A hazy autumn morning view across a wide calm river toward an old Korean city in 1950, a traditional Korean gate pavilion with curved tiled roof on the riverbank, low tiled roofs, a wooded hill with an old pavilion behind, smoke rising in the distance, no flags anywhere, no people",
    "ford_crossing": "Dusk in October 1950, a long line of " + ROK + " wading across a wide shallow river holding rifles above their heads, cold mist on the water, low hills on the far bank, seen from far behind as dark silhouettes",
}
NEW = {k: v + TAIL for k, v in NEW.items()}

AIMG = {}
AIDIR = ROOT / "public" / "ep" / EP / "ai"
AIDIR.mkdir(parents=True, exist_ok=True)
MAN = AIDIR.parent / "ai.json"  # ai_images.py가 읽는 위치 (public/ep/<ep>/ai.json)
man = json.loads(MAN.read_text()) if MAN.exists() else {}
for k, src in REUSE.items():
    AIMG[k] = json.loads((ROOT / "episodes" / src / "storyboard.json").read_text(encoding="utf-8"))["ai_images"][k]
    shutil.copyfile(ROOT / "public" / "ep" / src / "ai" / f"{k}.jpg", AIDIR / f"{k}.jpg")
    srcman = json.loads((ROOT / "public" / "ep" / src / "ai.json").read_text()) if (ROOT / "public" / "ep" / src / "ai.json").exists() else {}
    man[k] = srcman.get(k) or hashlib.sha1(f"gpt-image-1|high|{AIMG[k]}".encode()).hexdigest()[:12]
MAN.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
AIMG.update(NEW)
used = {s["visual"]["img"] for s in S if s["visual"]["type"] == "ai"}
assert not used - set(AIMG), used - set(AIMG)
assert not set(AIMG) - used, set(AIMG) - used


# ===== on 단어 검사 (대사에 없는 단어면 실패) =====
def ons(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("on", "xOn", "checkOn", "untilOn", "takenOn") and isinstance(v, str):
                yield v
            else:
                yield from ons(v)
    elif isinstance(o, list):
        for v in o:
            yield from ons(v)


say = lambda l: l if isinstance(l, str) else l["say"]
for s in S:
    full = " ".join(say(l) for l in s["lines"])
    for w in ons({k: v for k, v in s.items() if k != "lines"}):
        assert w in full, ("on 단어 없음", s["id"], w, full)

# 출처: 숫자가 들어간 문장에 src가 없으면 기본 [1, 2] (국방일보 평양탈환작전 · 애플먼 31장 — research.md)
for s in S:
    if "src" not in s and any(ch.isdigit() for l in s["lines"] for ch in (l if isinstance(l, str) else l["t"])):
        s["src"] = [1, 2]

# 막 단위 통파일 TTS(tts_mode act): 콜드 오프닝 = 0, chapter가 달린 장면마다 1씩 증가
_a = 0
for s in S:
    if s.get("chapter"):
        _a += 1
    s["act"] = _a
ids = [s["id"] for s in S]
chap = [i for i, s in enumerate(S) if s.get("chapter")]
MID = [S[chap[2]]["id"], S[chap[4]]["id"], S[chap[6]]["id"]]  # 제3·5·7막 첫 장면 (미드롤)
for i in (chap[2], chap[4], chap[6]):
    S[i]["pauseBefore"] = 0.5
sid = lambda i: S[i]["id"]
prev_id = lambda x: ids[ids.index(x) - 1]
music = [{"id": "drone", "from": "s001", "to": sid(chap[0] - 1), "volume": 0.2},
         {"id": "theme", "from": sid(chap[0]), "to": sid(chap[2] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[2]), "to": sid(chap[3] - 1), "volume": 0.17},
         {"id": "march", "from": sid(chap[3]), "to": sid(chap[5] - 1), "volume": 0.16},
         {"id": "analysis", "from": sid(chap[5]), "to": prev_id(SOMBER), "volume": 0.16},
         {"id": "somber", "from": SOMBER, "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "열하루의 경주", "subtitle": "평양 최초 입성 작전 · 1950", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         # 2026-11-24 지도사 방식 화면·목소리 표준 (첫 편) — 채널 목소리 승현 · eleven_v3 · 배속 없음 · 쉼 0.65초
         "look": "archive", "sub_style": "dark", "map_tone": "day", "tts_model": "eleven_v3", "tempo": 1.0, "max_pause": 0.65, "card_max": 0.25,
         "voice": "0mlAtfsvMzFpppUuNWkV", "voice_settings": {"stability": 0.5, "similarity_boost": 0.78},
         "target_sec": 1230, "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AIMG, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
cnt = collections.Counter(s["visual"]["type"] for s in S)
w = collections.Counter()
for s in S:
    w[s["visual"]["type"]] += sum(len(say(l)) for l in s["lines"]) + 8
CARDS = {"text", "black", "punch", "checklist", "reasons", "bars", "compare", "versus", "factors", "gauges", "weekbar", "hanja"}
tot = sum(w.values())
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap], "ai", len(AIMG), "pins", len(PINS))
print("types", dict(cnt))
print(f"추정 비율: 지도 {w['map'] / tot:.0%} · 카드 {sum(v for k, v in w.items() if k in CARDS) / tot:.0%}")
