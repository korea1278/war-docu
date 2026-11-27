# EP36 초산·압록강 진격전 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
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
    ("천구백오십년 시월 이십육일", "1950년 10월 26일"), ("천구백오십년 유월 이십오일", "1950년 6월 25일"), ("천구백오십년 구월 십오일", "1950년 9월 15일"),
    ("천구백오십년 십일월 구일", "1950년 11월 9일"), ("천구백칠십오년", "1975년"), ("천구백팔십년", "1980년"),
    ("시월 이십육일", "10월 26일"), ("시월 이십오일", "10월 25일"), ("시월 이십사일", "10월 24일"), ("시월 이십삼일", "10월 23일"), ("시월 이십팔일", "10월 28일"),
    ("시월 이십구일", "10월 29일"), ("시월 삼십일", "10월 30일"), ("시월 십구일", "10월 19일"), ("시월 이십일", "10월 20일"),
    ("십일월 이십일일", "11월 21일"), ("십이월 오일", "12월 5일"), ("십일월 말", "11월 말"),
    ("오후 두 시 십오 분", "오후 2시 15분"), ("오후 여섯 시 삼십 분", "오후 6시 30분"), ("오전 여섯 시 삼십 분", "오전 6시 30분"), ("여섯 시 사십오 분", "6시 45분"),
    ("새벽 세 시 삼십 분", "새벽 3시 30분"), ("오전 일곱 시", "오전 7시"), ("오전 열한 시", "오전 11시"), ("오후 다섯 시", "오후 5시"), ("오후 일곱 시", "오후 7시"),
    ("새벽 다섯 시", "새벽 5시"), ("밤 열두 시", "밤 12시"),
    ("삼천오백오십이 명", "3,552명"), ("약 팔백칠십오 명", "약 875명"), ("약 이백 킬로미터", "약 200km"), ("약 팔십 킬로미터", "약 80km"), ("약 사십 킬로미터", "약 40km"),
    ("약 삼십 킬로미터", "약 30km"), ("삼십 킬로미터", "30km"), ("약 십삼 킬로미터", "약 13km"), ("약 육 킬로미터", "약 6km"), ("수백 킬로미터", "수백 km"),
    ("칠백오십 명", "750명"), ("약 사백 명", "약 400명"), ("약 삼천백 명", "약 3,100명"), ("약 이천칠백 명", "약 2,700명"), ("약 천육백 미터", "약 1,600m"),
    ("사십일 일", "41일"), ("한 시간 반", "1시간 반"), ("트럭 다섯 대", "트럭 5대"), ("오십에서 백오십 미터", "50~150m"), ("폭 오십 미터", "폭 50m"),
    ("열다섯 군데", "15군데"), ("야포 여섯 문", "야포 6문"), ("여덟 명 가운데 여섯 명", "8명 가운데 6명"), ("약 백팔십오 명", "약 185명"), ("약 육십 명", "약 60명"),
    ("병사 스무 명과 간호학생 두 명", "병사 20명과 간호학생 2명"), ("네 명 가운데 한 명꼴", "4명 가운데 1명꼴"), ("중대장 네 명", "중대장 4명"), ("천 미터", "1,000m"),
    ("포병 세 개 포대", "포병 3개 포대"), ("보병 세 개 대대", "보병 3개 대대"), ("오 년", "5년"), ("트럭 두 대", "트럭 2대"),
    ("제백이십오사단", "제125사단"), ("제삼백칠십삼연대", "제373연대"), ("제십구연대", "제19연대"), ("제십칠연대", "제17연대"), ("제십연대", "제10연대"),
    ("제사십군", "제40군"), ("제육사단", "제6사단"), ("제칠연대", "제7연대"), ("제이연대", "제2연대"), ("제이군단", "제2군단"), ("제팔사단", "제8사단"),
    ("제일사단", "제1사단"), ("제칠사단", "제7사단"), ("제일대대", "제1대대"), ("제이대대", "제2대대"), ("제삼대대", "제3대대"), ("제일중대", "제1중대"),
    ("제일선", "제1선"), ("제일차 공세", "제1차 공세"), ("미 팔군", "미 8군"), ("삼팔선", "38선"), ("한 개 사단", "1개 사단"), ("한 개 대대", "1개 대대"),
    ("한만 국경선", "한·만 국경선"),
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


# 좌표는 개략 (희천·온정·풍장·고장·초산·북진·벽동·매복 지점 등은 기록과 현재 지형 기준 근사 — 화면에 '위치 개략' 표기)
P = {
    "seoul": [126.978, 37.566, "서울"], "chuncheon": [127.73, 37.88, "춘천"], "hongcheon": [127.88, 37.69, "홍천"], "wonju": [127.95, 37.35, "원주"],
    "naktong": [128.4, 35.95, "낙동강"], "inchon": [126.62, 37.47, "인천"], "pyongyang": [125.755, 39.025, "평양"],
    "huichon": [126.28, 40.17, "희천"], "onjong": [125.85, 40.07, "온정"], "ambush2": [125.72, 40.06, "온정 서쪽 매복지"], "pukchin": [125.66, 40.2, "북진"],
    "pyoktong": [125.45, 40.6, "벽동"], "pungjang": [125.92, 40.3, "풍장"], "kojang": [125.9, 40.57, "고장"], "chosan": [125.8, 40.83, "초산"],
    "chosan_s": [125.82, 40.785, "초산 남쪽 약 6km"], "yalubank": [125.79, 40.848, "압록강 강변"], "unsan": [125.83, 40.0, "운산"],
    "kunuri": [125.97, 39.58, "군우리"], "yongbyon": [125.8, 39.81, "영변 · 청천강변"], "kanggye": [126.6, 40.97, "강계"], "manpo": [126.3, 41.15, "만포"],
    "hyesan": [128.18, 41.4, "혜산진"], "jeokyu": [126.0, 40.45, "적유령 산맥"], "manchuria": [125.6, 41.05, "만주"], "manchu2": [125.6, 40.92, "만주"],
    "cheorwon": [127.21, 38.25, "철원"], "saigon": [106.7, 10.78, "사이공"],
}
V = {
    "korea": {"center": [127.3, 38.6], "span": 8.6}, "south": {"center": [128.0, 36.6], "span": 3.6}, "chunc": {"center": [127.8, 37.82], "span": 1.2},
    "nk": {"center": [126.3, 39.9], "span": 6.2}, "yaluall": {"center": [126.6, 40.6], "span": 6.0}, "north": {"center": [125.95, 40.3], "span": 3.4},
    "corridor": {"center": [125.9, 40.45], "span": 2.4}, "huichon": {"center": [126.05, 40.13], "span": 1.0}, "onjong": {"center": [125.78, 40.08], "span": 0.6},
    "kojang": {"center": [125.85, 40.7], "span": 0.9}, "chosan": {"center": [125.8, 40.82], "span": 0.22}, "pungjang": {"center": [125.92, 40.3], "span": 0.26},
}
R7 = [[126.28, 40.17], [126.1, 40.12], [125.85, 40.07], [125.9, 40.2], [125.92, 40.3], [125.9, 40.45], [125.9, 40.57], [125.84, 40.72], [125.8, 40.83]]
R2 = [[125.85, 40.07], [125.72, 40.06], [125.66, 40.2]]
R2F = R2 + [[125.55, 40.42], [125.45, 40.6]]
R6N = [[127.73, 37.88], [127.45, 38.25], [127.2, 38.6], [126.8, 39.2], [126.4, 39.75], [126.28, 40.17]]
NAKUP = [[128.4, 35.95], [127.95, 37.35], [127.88, 37.69], [127.73, 37.88]]
FULL = NAKUP + R6N[1:] + R7[1:]
P38 = [[124.6, 38.0], [125.5, 38.0], [126.5, 38.0], [127.5, 38.0], [128.7, 38.0]]
INCH = [[126.62, 37.47], [127.3, 37.05], [127.9, 36.6]]
FLEE = [[125.755, 39.03], [126.0, 39.6], [126.3, 40.3], [126.6, 40.97]]
YALU = [[124.4, 40.1], [124.9, 40.45], [125.45, 40.62], [125.8, 40.86], [126.3, 41.15], [126.9, 41.6], [127.5, 41.5], [128.2, 41.4]]
CN1 = [[125.3, 40.95], [125.5, 40.6], [125.7, 40.3]]
CN2 = [[126.3, 41.2], [126.2, 40.7], [126.05, 40.3]]
CN_TRAIL = [[125.6, 40.7], [125.75, 40.45], [125.85, 40.2]]
CN_CLOSE = [[126.15, 40.45], [126.0, 40.36], [125.93, 40.31]]
SUPPLY = [[125.755, 39.025], [125.97, 39.58], [126.28, 40.17], [125.85, 40.07], [125.92, 40.3], [125.9, 40.57]]
BORDER = [[125.7, 40.862], [125.79, 40.858], [125.88, 40.874]]
VALLEY = [[125.915, 40.36], [125.92, 40.33], [125.922, 40.3], [125.918, 40.27], [125.92, 40.24]]
V_N = [125.92, 40.335]
V_S = [125.92, 40.28]
HILL_L = [125.895, 40.31]
HILL_R = [125.948, 40.3]
BLOCK = [[125.905, 40.295], [125.92, 40.293], [125.935, 40.296]]
ESCAPE = [[125.9, 40.4], [126.1, 40.1], [126.05, 39.8], [125.97, 39.58]]
SIDE_L = [[125.895, 40.34], [125.912, 40.31]]
SIDE_R = [[125.95, 40.27], [125.928, 40.29]]

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
WATER = lambda at=0: [{"id": "water", "at": at}]
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))
QUESTION = "가장 먼저 압록강에 닿은 연대는\n왜 사흘 만에 무너졌나"
RED = "#c9242c"
KRY = "#ffd400"  # 국군 제7연대 진격로 (노랑)
WHT = "#ffffff"  # 제2연대 진격로
LEG = [{"icon": "kr", "text": "국군 제6사단"}, {"icon": "cn", "text": "중공군"}, {"icon": "nk", "text": "북한군"}, {"icon": "route", "text": "진격로"}]
LEG_S = [{"icon": "kr", "text": "국군"}, {"icon": "nk", "text": "북한군"}]


def M(view, *items, tilt=22, **kw):
    return m(view, view, list(items), tilt=tilt, **kw)


R7L = lambda at=0: line(R7, at, KRY)
KR = lambda *items, tilt=10, **kw: M("korea", *items, tilt=tilt, **kw)
NK = lambda *items, tilt=12, **kw: M("nk", *items, tilt=tilt, **kw)
YA = lambda *items, tilt=12, **kw: M("yaluall", *items, tilt=tilt, **kw)
NO = lambda *items, tilt=18, **kw: M("north", *items, tilt=tilt, **kw)
CO = lambda *items, tilt=20, **kw: M("corridor", *items, tilt=tilt, **kw)
HC = lambda *items, tilt=24, **kw: M("huichon", *items, tilt=tilt, **kw)
OJ = lambda *items, tilt=28, **kw: M("onjong", *items, tilt=tilt, **kw)
KJ = lambda *items, tilt=26, **kw: M("kojang", *items, tilt=tilt, **kw)
CS = lambda *items, tilt=32, **kw: M("chosan", *items, tilt=tilt, **kw)
PJ = lambda *items, tilt=38, **kw: M("pungjang", *items, tilt=tilt, **kw)


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


def RS(n_on, on=None):
    """이유 카드 4가지 — n_on번째(1~4)를 on 단어에 띄우고 그 앞은 이미 표시"""
    names = ["혼자 너무 앞섰다", "길은 하나뿐", "이틀의 기다림", "보이지 않는 적 · 좁은 계곡의 밤"]
    items = []
    for i, nm in enumerate(names, 1):
        if i < n_on:
            items.append({"text": nm, "at": 0})
        elif i == n_on:
            items.append({"text": nm, "on": on})
        else:
            items.append({"text": nm, "later": True})
    return reasons("사흘 만에 무너진 4가지 이유", items)


SRC = {"kr": [1], "us": [2], "both": [1, 2], "lee": [3], "lee_us": [2, 3], "end": [5, 6], "misc": [4], "seg": [8]}

# ===== 콜드 오프닝 =====
sc(1, CS(LOCK("yalubank", 0.3, "압록강 · 초산")), date="1950. 10. 26", clock="14:15", legend=LEG_S, src=SRC["kr"],
   hook={"hud": [HUD("1950. 10. 26", "평안북도 초산", "오후 2시 15분", count=False)]})
sc(1, CS(mark("chosan", "blue", 0.2), badge("chosan", "초산읍", "#111", 0.4, -60)))
sc(1, AI("first_snow", title="첫눈 덮인 국경의 산", date="1950. 10. 26"), label=DRAMA, src=SRC["kr"])
sc(1, AI("yalu_bank", title="강둑을 내려가는 병사들", date="1950. 10. 26"), label=DRAMA, sfx=WATER(0.2))
sc(1, KR(line(FULL, 0.1, KRY), mark("chosan", "blue", 0.6)), hook={"hud": [HUD("수백 km", "낙동강 → 압록강", "산길", count=False, on="수백")]})
sc(1, CS(badge("yalubank", "넓은 강", "#111", 0.3, -60)))
sc(1, punch("압록강", "북한과 만주를 가르는 국경"))
sc(1, NK(dash_b([[125.755, 39.025], [125.8, 40.83]], 0.2), mark("pyongyang", "blue", 0), mark("chosan", "blue", 0.5)),
   hook={"hud": [HUD("약 200km", "평양 → 초산", "미군 기록 130마일", on="이백")]}, src=[6])
sc(1, NK(LOCK("manchuria", 0.3, "강 건너 · 만주", RED)))
sc(1, CS(mark("yalubank", "blue", 0)), stamp={"text": "태극기", "on": "태극기", "x": 0.5, "y": 0.42}, src=SRC["kr"])
sc(1, AI("river_drink", title="압록강 물을 마시는 병사", date="1950. 10. 26"), label=DRAMA, src=SRC["misc"])
sc(1, AI("river_drink", kb="out", title="국경의 강물", sub="재연"), label=DRAMA, src=SRC["lee"])
sc(1, AI("canteen_fill", title="수통에 담은 압록강 물", date="1950. 10. 26"), label=DRAMA, src=SRC["lee"])
sc(1, KR(dash_b([[125.8, 40.83], [126.978, 37.566]], 0.2), LOCK("seoul", 0.5, "서울 · 이승만 대통령")), src=SRC["lee"])
sc(1, CS(unit("chosan", "국군 제6사단 제7연대", "blue", 0.2, True)), src=SRC["kr"])
sc(1, NK(mark("chosan", "blue", 0), badge("chosan", "유엔군 최초", "#111", 0.3, -60)), hook={"hud": [HUD("1번째", "압록강 도달", "유엔군 가운데", count=False, on="가장 먼저")]}, src=SRC["us"])
sc(1, NK(mark("chosan", "blue", 0)), clip=clip("애플먼 『낙동강에서 압록강으로』 (요지)", "미 8군 소속으로 압록강에 닿은\n[[유일한 부대]]", on="유일한"), src=SRC["us"])
sc(1, phl("welcome_arch", "1950. 10. 2", "북진하는 국군을 맞는 환영 아치"))
sc(1, black("“이제 전쟁은 끝났다”"))
sc(1, AI("dust_column", title="북쪽으로 달리는 트럭 행렬", date="1950. 10"), label=DRAMA)
sc(1, black("그로부터", "사흘 뒤"))
sc(1, CO(R7L(0), mark("chosan", "blue", 0), clash("pungjang", 0.3)), legend=LEG)
sc(1, troops(40, keep=10, keepAt=0, side="kr", cols=10, title="국군 제7연대", labels=[{"x": 0.5, "y": 0.76, "text": "3,552명 → 약 875명", "on": "팔백칠십오", "color": "red"}]), src=SRC["us"])
sc(1, punch("4명 중 1명"))
sc(1, AI("helmets_row", title="돌아오지 못한 병사들", sub="재연"), label=DRAMA)
sc(3, black("“너무 깊이 들어갔다가\n운 나쁘게 만났을 뿐”"), hook={"neg": {"text": "운 나쁘게 중공군을 만났을 뿐", "at": 0.3, "xOn": "그것뿐이었을까요"}})
sc(1, CO(R7L(0.1), radar("kojang", 0.3, 0.8, "red")), sfx=PING(0.4))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, CO(mark("huichon", "blue", 0.2), mark("onjong", "red", 0.35), mark("kojang", "blue", 0.5), mark("pungjang", "red", 0.65), badge("chosan", "네 곳", "#111", 0.3, -60)))
sc(1, CO(badge("huichon", "갈림길", "#111", on="갈림길"), badge("onjong", "밤", RED, on="온정의"), badge("kojang", "기다림", "#111", on="기다림"), badge("pungjang", "좁은 계곡", RED, on="계곡", dy=-90)))
sc(1, {"type": "titlecard", "title": "압록강의 수통", "sub": "초산·압록강 진격전 · 1950", "at": 0, "q": pin("rok_snow")}, flash=True)
next_act()

# ===== 제1막 산을 넘어온 사단 =====
sc(1, KR(mark("chuncheon", "blue", 0.3)), chapter={"num": "제1막", "title": "산을 넘어온 사단"}, date="1950. 6", legend=LEG)
sc(1, KR(line(P38, 0.1, "#ff6a5a"), red_a([[127.73, 38.3], [127.73, 37.95]], 0.3)), date="1950. 6. 25", sfx=FAR(0.2))
sc(1, phl("rok7_1949", "1949. 7. 21", "38선의 국군 제6사단 제7연대 장병"))
sc(1, M("chunc", LOCK("chuncheon", 0.2, "춘천"), mark("hongcheon", "blue", 0.4), tilt=20))
sc(1, text("개전 초 국군의 첫 승전", "blue", "춘천·홍천 · 1950. 6"), src=[10])
sc(1, phl("kimchongoh", "1954. 5. 4", "김종오 (1954 · 훗날 소장)"))
sc(1, text("제7연대장 임부택", "blue", "국군 제6사단"), src=[10])
sc(1, text("태극무공훈장", "yellow", "임부택 · 춘천 전투의 공"), src=[10])
sc(1, KR(red_a([[127.5, 37.5], [128.3, 36.2]], 0.2, 1.2)))
sc(1, M("south", LOCK("naktong", 0.3, "낙동강 방어선"), tilt=14), date="1950. 8")
sc(1, phl("rok_m1", "1950. 7. 29", "M1 소총을 든 국군 병사"), hook={"hud": [HUD("4명", "두 달 사이 전사한 중대장", "제7연대 제1중대 · 이대용 회고", color="#FF3B3B", on="네 명")]}, src=SRC["lee"])
sc(1, phl("inchon_craft", "1950. 9. 15", "인천으로 향하는 상륙정"), date="1950. 9. 15")
sc(1, KR(blue_a(INCH, 0.1, 1.2), badge("naktong", "무너진 북한군", RED, 0.5, -60)))
sc(1, KR(blue_a(NAKUP[:2], 0.1)))
sc(1, KR(line(NAKUP, 0.1, KRY)))
sc(1, KR(line(NAKUP, 0, KRY), mark("wonju", "blue", on="원주와"), mark("hongcheon", "blue", on="홍천"), mark("chuncheon", "blue", on="춘천을"), line(P38, 0.2, "#ff6a5a")), src=SRC["lee"])
sc(1, phl("parallel_sign", "1950. 9월 말", "38선 돌파를 알리는 국군"), date="1950. 10")
sc(1, phl("pyongyang_entry", "1950. 10. 19", "평양에 들어가는 장병들"), date="1950. 10. 19", src=[6])
sc(1, NK(dash_r(FLEE, 0.1), LOCK("kanggye", 0.5, "강계 · 북쪽 산골", RED)))
sc(1, NK(LOCK("pyongyang", 0.3, "평양 · 지난 편")))
sc(1, NK(mark("pyongyang", "blue", 0), dash_b([[125.755, 39.025], [125.8, 40.83]], 0.2)))
sc(1, punch("누가 먼저 압록강 물을 뜰 것인가"))
sc(1, NK(line(YALU, 0.1, "#4fa3ff"), LOCK("chosan", 0.5, "압록강 · 국경")))
sc(1, NK(line(R6N, 0.1, KRY), unit([126.8, 39.2], "국군 제6사단", "blue", 0.3)))
sc(1, NK(line(R6N, 0, KRY), badge([126.6, 39.6], "한반도의 등뼈", "#111", 0.3, -60), tilt=24))
sc(1, AI("autumn_ridge", title="큰길도 철도도 없는 산악", date="1950. 10"), label=DRAMA)
sc(1, NK(LOCK("yongbyon", 0.3)), src=SRC["seg"])
sc(1, text("김일성의 소련제 승용차", "dark", "6사단 수색대 노획 (전해짐) · 전쟁기념관 전시"), src=SRC["seg"])
sc(1, NK(LOCK("manchuria", 0.3, "압록강 건너편", RED), tone="night"), date="1950. 10. 19", clock="밤", src=[6])
sc(1, NK(swarm(CN1, 0.1, 120, 0.1), tone="night"), src=[6])
sc(1, NK(red_a(CN1, 0.1, 1.2), red_a(CN2, 0.2, 1.2), badge("manchuria", "중국 인민지원군", RED, 0.4, -60), tone="night"), src=[6])
sc(1, AI("cn_night_march", title="밤에만 움직인 군대", sub="재연"), label=DRAMA)
sc(1, phl("macarthur_korea", "1950", "맥아더 원수"))
sc(2, doc("육군본부 작전 명령 (요지)", ["국군 제2군단 → 한·만 국경선으로 진출", "제6사단 · 제8사단 → 희천·온정리 경유 압록강"], "軍 秘", "육군본부", "재구성 · 내용 요약"), date="1950. 10. 20", src=SRC["kr"])
sc(1, NK(blue_a(R6N[-3:], 0.1), mark("huichon", "blue", on="희천과"), mark("onjong", "blue", on="온정리를")), src=SRC["kr"])
sc(1, NO(LOCK("huichon", 0.3, "희천 · 청천강 상류")), date="1950. 10. 23", clock="밤", src=SRC["us"])
next_act()

# ===== 제2막 희천의 갈림길 =====
sc(1, HC(LOCK("huichon", 0.3, "희천")), chapter={"num": "제2막", "title": "희천의 갈림길"}, legend=LEG)
sc(1, NO(badge("jeokyu", "겹겹의 산줄기", "#111", 0.3, -60), tilt=30))
sc(1, NO(LOCK("jeokyu", 0.3, "적유령 산맥"), tilt=30))
sc(1, CO(tilt=40), hook={"hud": [HUD("1,000m+", "적유령 산맥 봉우리", on="천 미터")]})
sc(1, HC(mark("huichon", "blue", 0), dash_b(R7[:3], 0.2), dash_b(R2, 0.4)), src=SRC["kr"])
sc(1, CO(R7L(0.1), unit("kojang", "제7연대", "blue", 0.4)), src=SRC["kr"])
sc(1, CO(R7L(0), mark("pungjang", "blue", on="풍장과"), mark("kojang", "blue", on="고장을"), LOCK("chosan", 0.6, "초산")), src=SRC["kr"])
sc(1, NO(line(R2F, 0.1, WHT), unit("pukchin", "제2연대", "blue", 0.3)), src=SRC["kr"])
sc(1, NO(line(R2F, 0, WHT), mark("onjong", "blue", on="온정과"), mark("pukchin", "blue", on="북진을"), LOCK("pyoktong", 0.6, "벽동")), src=SRC["kr"])
sc(1, NO(line(YALU, 0, "#4fa3ff"), mark("chosan", "blue", 0.2), mark("pyoktong", "blue", 0.3), badge("manchu2", "만주", RED, 0.4, -60)))
sc(1, HC(blue_a(R7[:3], 0.1)), hook={"hud": [HUD("약 40km", "희천 → 온정", "미군 기록 26마일", on="사십")]}, src=SRC["us"])
sc(1, NO(R7L(0.1), line(R2F, 0.2, WHT), badge("onjong", "갈라지는 길", "#111", 0.4, -60)))
sc(1, CO(dash_b([[125.85, 40.07], [125.8, 40.83]], 0.2)), hook={"hud": [HUD("약 80km", "온정 → 초산 직선", "미군 기록 50마일", on="팔십")]}, src=SRC["us"])
sc(1, CO(line(R7, 0.1, WHT), badge("kojang", "계곡 길 하나", "#111", 0.4, -60)))
sc(1, troops(32, side="kr", cols=8, title="국군 제6사단 제7연대", labels=[{"x": 0.5, "y": 0.76, "text": "3,552명", "on": "삼천오백오십이", "color": "blue"}]), src=SRC["us"])
sc(1, {"type": "weapon", "bg": "blueprint", "units": [{"kind": "cannon", "x": 0.5, "y": 0.64, "w": 720, "label": "야포 · 대전차포", "sub": "트럭에 싣고 달린 연대"}], "title": "기계화된 연대"}, src=SRC["lee_us"])
sc(1, text("미 군사고문단 (KMAG)", "blue", "국군 제7연대에 배속"), src=SRC["us"])
sc(1, text("해리 플레밍 소령", "blue", "제7연대 고문관"), src=SRC["us"])
sc(1, phl("big_switch", "1953", "판문점 포로 교환 '빅 스위치'"), src=SRC["us"])
sc(1, AI("dust_column", kb="out", title="북쪽으로 달리는 트럭", sub="재연"), label=DRAMA, sfx=SW(0.1))
sc(2, NO(R7L(0), dash_r([[125.9, 40.3], [125.82, 40.8]], 0.2), badge("kojang", "물러나는 북한군", RED, 0.4, -60)), src=SRC["us"])
sc(1, CO(R7L(0)), clip=clip("TIME (1950) · 국군 지휘관들의 보고 (요지)", "압록강에 [[칼을 씻을 때까지]]\n멈추지 않겠다", on="칼을"), src=[6])
sc(1, HC(blue_a(R7[:3], 0.1, 1.1)), date="1950. 10. 24", clock="07:00", src=SRC["kr"])
sc(1, OJ(blue_a(R7[1:4], 0.1), LOCK("onjong", 0.4, "온정")), clock="밤", src=SRC["us"])
sc(1, OJ(blue_a(R7[2:5], 0.1, 1.1)))
sc(1, OJ(R7L(0), blue_a(R2, 0.2), unit("ambush2", "제2연대", "blue", 0.4)), src=SRC["us"])
sc(1, OJ(R7L(0), line(R2, 0, WHT), badge([125.78, 40.14], "산", "#111", 0.3, -50), tilt=40))
sc(1, NO(R7L(0), line(R2F, 0, WHT), badge("onjong", "볼 수도 · 도울 수도 없다", RED, 0.3, -70)))
sc(1, CO(blue_a(R7[3:7], 0.1, 1.2)), sfx=SW(0.1))
sc(1, KJ(LOCK("kojang", 0.3, "고장 점령")), date="1950. 10. 25", clock="18:30", src=SRC["kr"])
sc(1, KJ(badge("kojang", "산골 읍내", "#111", 0.3, -60)), src=SRC["us"])
sc(1, KJ(dash_b([[125.9, 40.57], [125.8, 40.83]], 0.2)), hook={"hud": [HUD("30km", "고장 → 국경선", "한국 측 기록", on="삼십")]}, src=SRC["kr"])
sc(1, KJ(R7L(0), LOCK("chosan", 0.3, "하루 거리 · 압록강")))
sc(1, KJ(mark("kojang", "blue", 0), tone="night"), clock="밤", src=SRC["us"])
sc(1, NO(mark("kojang", "blue", 0), radar("onjong", 0.2, 0.9, "red"), tone="night"))
next_act()

# ===== 제3막 온정의 밤 =====
sc(1, OJ(LOCK("ambush2", 0.3, "온정 서쪽 약 13km · 위치 개략")), chapter={"num": "제3막", "title": "온정의 밤"}, date="1950. 10. 25", legend=LEG, src=SRC["us"])
sc(1, OJ(blue_a(R2, 0.1), unit("ambush2", "제2연대 제3대대", "blue", 0.3)), src=SRC["us"])
sc(1, AI("onjong_ambush", title="골짜기의 매복", date="1950. 10. 25"), label=DRAMA, sfx=FAR(0.1))
sc(1, OJ(red_a([[125.7, 40.11], [125.72, 40.07]], 0.1), red_a([[125.74, 40.02], [125.722, 40.055]], 0.2), clash("ambush2", 0.3)), stamp={"text": "매복", "on": "매복", "x": 0.5, "y": 0.42})
sc(1, OJ(clash("ambush2", 0), swarm([[125.7, 40.11], [125.72, 40.06]], 0.1, 80, 0.03)))
sc(1, OJ(clash("ambush2", 0), badge("ambush2", "대대 붕괴", RED, 0.3, -70)))
sc(1, troops(30, keep=16, keepAt=0, side="kr", cols=10, title="제2연대 제3대대", labels=[{"x": 0.5, "y": 0.76, "text": "750명 → 약 400명", "on": "칠백오십", "color": "red"}]), src=SRC["us"])
sc(1, phl("cn_pow_padded", "1950. 12", "누빔옷 차림의 중공군 포로 (장진호)"))
sc(1, phl("first_cn_pow", "1950. 10. 31", "국군 제1군단이 붙잡은 첫 중공군 포로"))
sc(1, punch("중공군", "중국 인민지원군"))
sc(1, NO(LOCK("ambush2", 0.3, "첫 만남", RED)))
sc(1, NO(LOCK("unsan", 0.3, "운산 · 국군 제1사단"), clash("unsan", 0.4)), src=[4])
sc(1, text("중공군 제1차 공세", "dark", "1950. 10. 25 ~ 11월 초"))
sc(1, OJ(red_a([[125.95, 40.12], [125.88, 40.09]], 0.1), red_a([[125.8, 40.02], [125.84, 40.06]], 0.2), tone="night"), clock="밤", src=SRC["us"])
sc(1, OJ(clash("onjong", 0.2, 1.3), shock([[125.85, 40.07], [125.86, 40.08]], 0.3), tone="night"), date="1950. 10. 26", clock="03:30", sfx=FAR(0.1), src=SRC["us"])
sc(1, OJ(clash("onjong", 0), badge("onjong", "제2연대 붕괴", RED, 0.3, -70), tone="night"))
sc(1, troops(31, keep=27, keepAt=0, side="kr", cols=10, title="제2연대", labels=[{"x": 0.5, "y": 0.76, "text": "약 3,100명 → 약 2,700명", "on": "이천칠백", "color": "red"}]), src=SRC["us"])
sc(1, AI("trucks_left", title="길 위에 버려진 장비", sub="재연"), label=DRAMA)
sc(1, OJ(mark("onjong", "red", 0), LOCK("onjong", 0.3, "온정 · 중공군 손에", RED), tone="night"))
sc(1, text("미 군사고문단 장교 포로", "dark", "제2연대 배속 고문관"), src=SRC["us"])
sc(1, black("포로수용소에서", "숨진 고문관"), src=SRC["us"])
sc(1, NO(radar("onjong", 0.2, 0.9, "red"), radar("unsan", 0.3, 0.8, "red")))
sc(1, NO(red_a([[125.6, 40.3], [125.75, 40.1]], 0.1), red_a([[126.1, 40.35], [125.9, 40.12]], 0.2), badge("onjong", "국군을 먼저", RED, 0.4, -60)), src=[9])
sc(1, NO(R7L(0), red_a(CN_TRAIL, 0.1)), clip=clip("뉴데일리 「이승만史」 (요지)", "장비가 약한 한국군을 집중 타격해\n[[미군의 손발을 잘라라]]", on="잘라"), src=[9])
sc(1, NO(LOCK("manchu2", 0.3, "?", RED)))
sc(1, AI("cn_night_march", kb="out", title="큰길을 피한 행군", sub="재연"), label=DRAMA)
sc(1, NO(swarm(CN_TRAIL, 0.1, 140, 0.08), tone="night"))
sc(1, NO(swarm(CN_TRAIL, 0, 140, 0.08), badge("jeokyu", "차량 거의 없음", "#111", 0.3, -60), tone="night"))
sc(1, CO(badge("jeokyu", "텅 빈 산?", "#111", 0.3, -60), tilt=40))
sc(1, phl("macarthur_korea", "1950", "유엔군 사령관 맥아더 원수", kb="out"))
sc(1, NO(swarm(CN_TRAIL, 0.1, 200, 0.12), swarm(CN2, 0.2, 160, 0.1), LOCK("jeokyu", 0.4, "골짜기마다", RED), tone="night"), hook={"hud": [HUD("수만 명", "적유령 산맥의 중공군", "추정", count=False, on="수만")]})
sc(1, CO(R7L(0.1)))
sc(1, CO(R7L(0), LOCK("onjong", 0.3, "온정 · 제7연대가 지나온 길목", RED)))
sc(1, CO(R7L(0), mark("chosan", "blue", on="초산과"), mark("kojang", "blue", on="고장에서"), dash_b([[125.9, 40.57], [125.9, 40.2], [125.85, 40.07]], 0.4)))
sc(1, CO(R7L(0), clash("onjong", 0.2), badge("onjong", "닫힌 뒷문", RED, 0.4, -70)), stamp={"text": "차단", "on": "닫혀", "x": 0.5, "y": 0.42})
sc(1, KJ(unit("kojang", "제7연대", "blue", 0.2, True)))
sc(1, KJ(blue_a([[125.9, 40.57], [125.8, 40.83]], 0.2), LOCK("chosan", 0.5, "압록강")))
next_act()

# ===== 제4막 압록강의 수통 =====
sc(1, KJ(LOCK("kojang", 0.3, "고장")), chapter={"num": "제4막", "title": "압록강의 수통"}, date="1950. 10. 26", clock="아침", legend=LEG_S, src=SRC["kr"])
sc(1, AI("first_snow", kb="out", title="첫눈", date="1950. 10. 26"), label=DRAMA, sfx=WIND(0.1))
sc(1, KJ(blue_a([[125.9, 40.57], [125.84, 40.72]], 0.1, 1.1)), clock="07:00", src=SRC["kr"])
sc(1, KJ(unit([125.88, 40.62], "제1대대 · 김용배 중령", "blue", 0.2, True)), src=SRC["lee"])
sc(1, CS(LOCK("chosan_s", 0.3)), sfx=FAR(0.2), src=SRC["kr"])
sc(1, CS(unit("chosan_s", "북한군 제8사단 혼성 부대", "red", 0.2, True)), src=SRC["kr"])
sc(1, CS(clash("chosan_s", 0.1)), hook={"hud": [HUD("1시간 반", "초산 남쪽 교전", "한국 측 기록", count=False, on="한 시간 반")]}, src=SRC["kr"])
sc(1, CS(clash("chosan_s", 0), dash_r([[125.82, 40.785], [125.8, 40.83]], 0.3)))
sc(1, CS(blue_a([[125.82, 40.785], [125.8, 40.825]], 0.1), LOCK("chosan", 0.4, "초산읍")), src=SRC["kr"])
sc(1, AI("chosan_town", title="압록강변의 국경 읍", date="1950. 10"), label=DRAMA)
sc(1, CS(blue_a([[125.8, 40.825], [125.79, 40.848]], 0.1), LOCK("yalubank", 0.4, "압록강 강변")), clock="14:15",
   hook={"hud": [HUD("14:15", "압록강 도착", "한국 측 기록", count=False, on="두 시 십오 분")]}, src=SRC["kr"])
sc(1, CS(mark("yalubank", "blue", 0)), clip=clip("애플먼 『낙동강에서 압록강으로』 (요지)", "고문관 플레밍 소령이\n[[수색소대와 함께]] 초산에 들어갔다", on="함께"), src=SRC["us"])
sc(1, AI("pontoon_bridge", title="압록강 위의 좁은 부교", date="1950. 10. 26"), label=DRAMA, src=SRC["us"])
sc(1, CS(dash_r([[125.79, 40.852], [125.785, 40.872]], 0.1), badge([125.785, 40.872], "만주 쪽으로", RED, 0.3, -50)), src=SRC["us"])
sc(1, CS(line(BORDER, 0.1, "#ff6a5a")))
sc(1, CS(line(BORDER, 0, "#ff6a5a"), badge([125.79, 40.858], "강 한가운데 = 국경선", RED, 0.3, -60)))
sc(1, CS(mark("yalubank", "blue", 0), badge("yalubank", "기관총", "#111", 0.2, -50)), src=SRC["us"])
sc(1, CS(line(BORDER, 0, "#ff6a5a"), badge([125.79, 40.868], "중국 땅", RED, 0.3, -60)), src=SRC["us"])
sc(1, punch("기관총 하나에 담긴 고민"))
sc(1, AI("river_drink", kb="in", title="압록강 강가", sub="재연"), label=DRAMA, sfx=WATER(0.2))
sc(1, CS(mark("yalubank", "blue", 0), tilt=40))
sc(1, text("제1중대장 이대용 대위", "blue", "제7연대 제1대대"), src=SRC["lee"])
sc(1, CS(mark("yalubank", "blue", 0)), clip=clip("이대용 회고 (서울신문 1991) · 대대장의 지시 (요지)", "압록강 물을 수통에 떠서\n[[대통령께 보내라]]", on="대통령께"), src=SRC["lee"])
sc(1, AI("canteen_fill", kb="out", title="압록강 물을 담은 수통", date="1950. 10. 26"), label=DRAMA, src=SRC["misc"])
sc(1, CS(clash([125.782, 40.858], 0.2), badge([125.782, 40.858], "뗏목다리", "#111", 0.1, -60)), stamp={"text": "절단", "on": "끊었습니다", "x": 0.5, "y": 0.42}, src=SRC["lee"])
sc(1, CS(line([[125.75, 40.852], [125.79, 40.849], [125.83, 40.857]], 0.1, KRY)), hook={"hud": [HUD("약 1,600m", "제1중대 경계 구간", "이대용 회고", on="천육백")]}, src=SRC["lee"])
sc(1, NK(LOCK("manchuria", 0.3, "중국 대륙", RED)))
sc(1, NK(blue_a([[125.755, 39.025], [125.8, 40.83]], 0.1)), hook={"hud": [HUD("7일", "평양 함락 → 압록강", "10. 19 → 10. 26", count=False, on="일주일")]})
sc(1, KR(dash_b([[125.8, 40.83], [126.978, 37.566]], 0.2), mark("seoul", "blue", 0.5)), src=SRC["kr"])
sc(1, KR(line(FULL, 0.1, KRY)), hook={"hud": [HUD("41일", "낙동강 반격 → 압록강", "한국 측 기록", on="사십일")]}, src=SRC["kr"])
sc(1, text("통일이 눈앞에", "yellow", "1950. 10. 26"), src=SRC["kr"])
sc(1, CO(R7L(0), mark("chosan", "blue", 0), LOCK("onjong", 0.3, "그 시각 · 온정", RED), tone="night"))
sc(1, KJ(radar("kojang", 0.2, 0.8, "blue", "무전")), clock="저녁", sfx=PING(0.4), src=SRC["us"])
sc(1, AI("field_phone", title="사단 사령부의 무전", sub="재연"), label=DRAMA)
sc(1, punch("남쪽으로 철수하라"), src=SRC["us"])
next_act()

# ===== 제5막 고장의 기다림 =====
sc(1, KJ(mark("kojang", "blue", 0), LOCK("kojang", 0.3, "철수 명령")), chapter={"num": "제5막", "title": "고장의 기다림"}, date="1950. 10. 26", legend=LEG, src=SRC["us"])
sc(1, CS(mark("yalubank", "blue", 0), badge("yalubank", "몇 시간 전 · 태극기", "#111", 0.3, -60)))
sc(1, KJ(unit("kojang", "제7연대", "blue", 0.2)))
sc(1, NO(line(SUPPLY, 0.1, WHT), badge("kojang", "보급선의 끝", RED, 0.4, -60)), src=SRC["us"])
sc(1, checklist("보급 상황", [{"text": "연료", "on": "연료", "bad": True}, {"text": "탄약", "on": "탄약", "bad": True}]))
sc(1, text("플레밍 소령의 답신", "blue", "고문관 → 사단"), src=SRC["us"])
sc(1, KJ(mark("kojang", "blue", 0)), clip=clip("애플먼 『낙동강에서 압록강으로』 (요지)", "보급을 받지 못하면\n연대는 [[움직일 수 없다]]", on="움직일 수 없다"), src=SRC["us"])
sc(1, KJ(unit("kojang", "제7연대 · 대기", "blue", 0.2, True)), src=SRC["us"])
sc(1, KJ(mark("kojang", "blue", 0), tone="night"), clock="10. 27")
sc(1, KJ(mark("kojang", "blue", 0)), clock="10. 28")
sc(1, CO(R7L(0), swarm(CN_CLOSE, 0.1, 120, 0.06), red_a(CN_CLOSE, 0.2)))
sc(1, KJ(LOCK("kojang", 0.3, "공중 보급")), date="1950. 10. 28", clock="11:00", src=SRC["us"])
sc(1, AI("airdrop", title="하늘에서 떨어진 보급품", sub="재연"), label=DRAMA)
sc(1, phl("airdrop_sunchon", "1950. 10. 20", "숙천·순천 공수 작전의 C-119 수송기"))
sc(1, CO(R7L(0), swarm(CN_CLOSE, 0, 120, 0.06), badge("pungjang", "같은 이틀", RED, 0.3, -60)))
sc(1, black("만약", "그 이틀이 없었다면?"))
sc(1, CO(R7L(0), dash_b([[125.9, 40.57], [125.9, 40.45], [125.92, 40.3], [125.9, 40.2], [125.85, 40.07]], 0.2)))
sc(1, HC(LOCK("huichon", 0.3, "희천 · 제6사단")), src=SRC["us"])
sc(1, HC(blue_a([[126.28, 40.17], [126.1, 40.12], [125.95, 40.1]], 0.1), unit([126.15, 40.15], "제19연대 · 제10연대", "blue", 0.3)), src=SRC["us"])
sc(1, HC(mark("onjong", "red", 0), badge("onjong", "버려진 장비", RED, 0.3, -60)), src=SRC["us"])
sc(1, HC(clash([126.0, 40.11], 0.2), red_a([[125.95, 40.2], [126.0, 40.12]], 0.1)), sfx=FAR(0.1), src=SRC["us"])
sc(1, HC(clash([126.0, 40.11], 0), badge([126.0, 40.11], "차량 · 포병 손실", RED, 0.3, -70)), hook={"hud": [HUD("3개 포대", "잃은 포병", "미군 기록", color="#FF3B3B", on="세 개")]}, src=SRC["us"])
sc(1, CO(R7L(0), mark("kojang", "blue", 0), radar("kojang", 0.2, 1.0, "red")))
sc(1, punch("스스로 길을 뚫어야 했다"))
sc(1, CS(mark("yalubank", "blue", 0)), date="1950. 10. 28", clock="17:00", src=SRC["lee"])
sc(2, doc("제1대대 작전 명령 (요지)", ["온정에서 패한 제2연대를 구하러 남하", "제1중대는 오후 7시까지 초산읍 집결"], "軍 秘", "국군 제7연대 제1대대", "재구성 · 이대용 회고"), src=SRC["lee"])
sc(1, CS(blue_a([[125.79, 40.848], [125.8, 40.825]], 0.1)), clock="18:45", hook={"hud": [HUD("5대", "트럭", "제1중대", count=False, on="다섯 대")]}, src=SRC["lee"])
sc(1, AI("night_trucks", title="어둠 속 트럭 행렬", sub="재연"), label=DRAMA)
sc(1, CS(mark("yalubank", "blue", 0), tone="night"), hook={"hud": [HUD("2일+", "압록강에 머문 시간", "10. 26 → 10. 28", count=False, on="이틀")]})
sc(1, KJ(blue_a([[125.8, 40.83], [125.86, 40.7]], 0.1), tone="night"), date="1950. 10. 29", clock="05:00", src=SRC["lee"])
sc(1, KJ(blue_a([[125.8, 40.83], [125.84, 40.72], [125.9, 40.57]], 0.1, 1.1)), clock="06:30", src=SRC["lee"])
sc(1, KJ(unit("kojang", "제7연대 집결", "blue", 0.2, True)), src=SRC["lee"])
sc(1, CO(R7L(0), unit("pungjang", "중공군", "red", 0.2, True), LOCK("pungjang", 0.4, "풍장", RED)), src=SRC["lee"])
sc(1, CO(R7L(0), clash("pungjang", 0.1), badge("pungjang", "단 하나의 길 차단", RED, 0.3, -70)), stamp={"text": "차단", "on": "막고서", "x": 0.5, "y": 0.42})
next_act()

# ===== 제6막 풍장의 좁은 계곡 =====
sc(1, PJ(LOCK("pungjang", 0.3, "고장 남쪽 · 풍장 계곡 · 위치 개략")), chapter={"num": "제6막", "title": "풍장의 좁은 계곡"}, date="1950. 10. 29", clock="아침", legend=LEG, src=SRC["lee"])
sc(1, CO(dash_b([[125.9, 40.57], [125.92, 40.3]], 0.2)), hook={"hud": [HUD("약 30km", "고장 → 차단선", "미군 기록 20마일", on="삼십")]}, src=SRC["us"])
sc(1, PJ(line(BLOCK, 0.1, "#ff6a5a"), badge("pungjang", "차단선", RED, 0.3, -60)), src=SRC["us"])
sc(1, PJ(blue_a([[125.915, 40.355], [125.92, 40.31]], 0.1), blue_a([[125.93, 40.355], [125.925, 40.31]], 0.2), unit([125.92, 40.345], "제2·3대대", "blue", 0.3)), sfx=FAR(0.2), src=SRC["lee"])
sc(1, phl("f51", "1950", "한국전쟁의 F-51 전투기"), src=SRC["lee"])
sc(1, PJ(blue_a([[125.92, 40.33], [125.921, 40.305]], 0.1), dash_r([[125.92, 40.295], [125.92, 40.27]], 0.2)), src=SRC["lee"])
sc(1, text("플레밍 소령의 증언", "blue", "미 군사고문단"), src=SRC["us"])
sc(1, PJ(mark("pungjang", "red", 0)), clip=clip("애플먼 · 플레밍 소령의 말 (요지)", "[[낮 동안에는]]\n우리가 버틸 수 있었다", on="낮 동안에는"), src=SRC["us"])
sc(1, PJ(swarm(SIDE_L, 0.1, 90, 0.02), swarm(SIDE_R, 0.2, 90, 0.02), badge("pungjang", "두꺼운 포위망", RED, 0.4, -70)))
sc(1, PJ(LOCK("pungjang", 0.2, "풍장 계곡"), tilt=48))
sc(1, PJ(line(VALLEY, 0.1, WHT), tilt=48), hook={"hud": [HUD("50~150m", "계곡 폭", "이대용 회고", on="오십에서")]}, src=SRC["lee"])
sc(1, PJ(line(VALLEY, 0, WHT), badge(V_N, "폭 50m ≈ 트럭 2대", "#111", 0.3, -60), tilt=48))
sc(1, PJ(mark(HILL_L, "red", 0.2), mark(HILL_R, "red", 0.3), badge(HILL_L, "가파른 산", "#111", 0.4, -50), tilt=48), src=SRC["lee"])
sc(1, PJ(LOCK(HILL_R, 0.3, "길을 내려다보는 고지", RED), tilt=48))
sc(1, PJ(line(VALLEY, 0, KRY), badge("pungjang", "길은 한 줄", "#111", 0.3, -60), tilt=48), src=SRC["lee"])
sc(1, AI("valley_trucks", title="계곡에 늘어선 차량", sub="재연"), label=DRAMA)
sc(1, PJ(line(VALLEY, 0, KRY), clash(V_N, 0.2), clash(V_S, 0.3), badge("pungjang", "앞뒤가 막히면", RED, 0.4, -60), tilt=48))
sc(1, PJ(line(VALLEY, 0, KRY), tone="night", tilt=48), clock="밤", sfx=WIND(0.1), src=SRC["lee"])
sc(1, PJ(red_a([[125.895, 40.32], [125.915, 40.31]], 0.1), red_a([[125.95, 40.29], [125.925, 40.295]], 0.2), red_a([[125.94, 40.34], [125.922, 40.33]], 0.3), tone="night", tilt=48), clock="00:00", sfx=FAR(0.1), src=SRC["lee"])
sc(1, AI("valley_night_attack", title="산비탈에서 내려온 그림자", date="1950. 10. 29 밤"), label=DRAMA)
sc(1, text("“야간 전투가 놀랄 만큼 능숙했다”", "dark", "이대용 회고 (요지)"), src=SRC["lee"])
sc(1, PJ(clash(V_S, 0.1), shock([V_S, [125.918, 40.29]], 0.2), tone="night", tilt=48), src=SRC["lee"])
sc(1, PJ(dash_b([[125.92, 40.29], [125.92, 40.33], [125.915, 40.36]], 0.1), tone="night", tilt=48), src=SRC["lee"])
sc(1, PJ(red_a([[125.94, 40.36], [125.918, 40.345]], 0.1), clash(V_N, 0.3), tone="night", tilt=48), src=SRC["lee"])
sc(1, CO(swarm([[125.92, 40.3], [125.8, 40.4]], 0.1, 60, 0.15), swarm([[125.92, 40.3], [126.05, 40.2]], 0.2, 60, 0.15), tone="night"), src=SRC["lee"])
sc(1, AI("valley_quiet", title="날이 밝은 계곡", sub="재연"), label=DRAMA, clock="새벽", src=SRC["us"])
sc(1, CS(mark("yalubank", "blue", 0)), hook={"hud": [HUD("사흘+", "압록강 → 붕괴", "10. 26 → 10. 30", count=False, on="사흘")]})
sc(1, text("플레밍 소령 포로", "dark", "1950. 10. 30 오전 6시 30분"), date="1950. 10. 30", clock="06:30", src=SRC["us"])
sc(1, black("몸 열다섯 군데의", "상처"), hook={"hud": [HUD("15군데", "플레밍 소령의 상처", "미군 기록", color="#FF3B3B", on="열다섯")]}, src=SRC["us"])
sc(1, phl("big_switch", "1953", "1953년 포로 교환으로 돌아온 포로들", kb="out"), src=SRC["us"])
sc(1, AI("trucks_left", kb="out", title="버려진 트럭과 야포", sub="재연"), label=DRAMA, hook={"hud": [HUD("6문", "버린 야포", "이대용 회고", color="#FF3B3B", on="여섯 문")]}, src=SRC["lee"])
sc(1, troops(8, keep=2, keepAt=0, side="kr", cols=8, title="연대 영관급 장교", labels=[{"x": 0.5, "y": 0.76, "text": "8명 중 6명", "on": "여덟", "color": "red"}]), src=SRC["lee"])
sc(1, NO(LOCK("pungjang", 0.3, "?", RED)))
sc(1, text("중공군 제40군 1개 사단", "dark", "이대용 회고"), src=SRC["lee"])
sc(2, doc("노획한 중공군 문서 (요지)", ["매복 부대 — 제125사단 제373연대 1개 대대"], "鹵獲", "미 8군 정보 기록", "재구성 · 애플먼 인용"), src=SRC["us"])
sc(1, cmp("이대용 회고", "제40군 1개 사단", "미군 노획 문서", "제125사단 1개 대대", "red", "red"), src=SRC["lee_us"])
sc(1, CO(R7L(0), mark("chosan", "blue", 0), clash("pungjang", 0.2)), stamp={"text": "사흘", "on": "사흘", "x": 0.5, "y": 0.42})
next_act()

# ===== 제7막 압록강이 남긴 답 =====
sc(1, NO(swarm(ESCAPE, 0.1, 60, 0.1), tone="night"), chapter={"num": "제7막", "title": "압록강이 남긴 답"}, legend=LEG)
sc(1, AI("mountain_escape", title="밤에 걷는 병사들", sub="재연"), label=DRAMA, src=SRC["lee"])
sc(1, punch("이번에는 국군이 숨었다"))
sc(1, text("제1중대장 이대용 대위", "blue", "포위망 탈출"), src=SRC["lee"])
sc(1, troops(37, keep=25, keepAt=0, side="kr", cols=10, title="이대용 대위의 중대", labels=[{"x": 0.5, "y": 0.76, "text": "약 185명 중 약 60명 손실", "on": "육십", "color": "red"}]), src=SRC["lee"])
sc(1, NK(blue_a(ESCAPE, 0.1)), date="1950. 11. 9", src=SRC["lee"])
sc(1, text("병사 20명 · 간호학생 2명", "yellow", "1950. 11. 9 사단 사령부 도착"), src=SRC["lee"])
sc(1, NK(LOCK("kunuri", 0.3, "군우리"), blue_a(ESCAPE, 0)), src=SRC["us"])
sc(1, troops(40, keep=10, keepAt=0, side="kr", cols=10, title="돌아온 병사", labels=[{"x": 0.5, "y": 0.76, "text": "3,552명 → 약 875명", "on": "팔백칠십오", "color": "red"}]), src=SRC["us"])
sc(1, text("연대장 임부택 대령", "blue", "포위망 탈출"), src=SRC["lee_us"])
sc(1, CO(R7L(0.1)))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, reasons("사흘 만에 무너진 4가지 이유", [{"text": n, "later": True} for n in ["혼자 너무 앞섰다", "길은 하나뿐", "이틀의 기다림", "보이지 않는 적 · 좁은 계곡의 밤"]]))
sc(1, RS(1, "혼자"))
sc(1, NO(R7L(0), clash("onjong", 0.2), mark("chosan", "blue", 0)))
sc(1, NO(R7L(0), line(R2F, 0, WHT), badge("onjong", "사라진 이웃", RED, 0.3, -60)))
sc(1, RS(2, "하나뿐"))
sc(1, CO(line(R7, 0.1, WHT)))
sc(1, CO(R7L(0), clash("pungjang", 0.2)))
sc(1, RS(3, "이틀"))
sc(1, NO(line(SUPPLY, 0, WHT), badge("kojang", "보급 없음", RED, 0.3, -60)))
sc(1, CO(swarm(CN_CLOSE, 0.1, 120, 0.06), R7L(0)))
sc(1, RS(4, "넷째"))
sc(1, NO(swarm(CN_TRAIL, 0.1, 140, 0.08), tone="night"))
sc(1, PJ(red_a([[125.895, 40.32], [125.915, 40.31]], 0.1), red_a([[125.95, 40.29], [125.925, 40.295]], 0.2), tone="night", tilt=48))
sc(1, black("하나만", "이었다면"))
sc(1, CO(R7L(0), mark("huichon", "red", 0.1), mark("onjong", "red", 0.2), mark("kojang", "red", 0.3), mark("pungjang", "red", 0.4)))
sc(2, text("압록강까지 데려간 속도가\n연대를 무너뜨린 덫", "yellow"))
sc(1, phl("rok_snow", "1952. 1. 15", "눈 덮인 들판의 국군 제6사단 (1952)"))
sc(1, KR(line(FULL, 0.1, KRY)))
sc(1, CS(mark("yalubank", "blue", 0.2)))
sc(1, YA(LOCK("hyesan", 0.3, "혜산진 · 미 제7사단 제17연대"), mark("chosan", "blue", 0)), date="1950. 11. 21", src=SRC["end"])
sc(1, YA(red_a([[125.4, 40.9], [125.8, 40.2]], 0.1, 1.3), red_a([[127.0, 41.2], [126.8, 40.4]], 0.2, 1.3), swarm([[125.4, 40.9], [125.8, 40.2]], 0.1, 120, 0.15)), date="1950. 11월 말")
sc(1, NK(red_a([[125.8, 40.0], [125.755, 39.1]], 0.2), LOCK("pyongyang", 0.4, "평양 다시 함락", RED)), date="1950. 12. 5", src=[6])
sc(1, phl("refugees_pyongyang", "1950. 12", "대동강을 건너는 피란민"))
sc(1, KR(red_a([[126.0, 39.5], [126.9, 38.0]], 0.1, 1.3), line(P38, 0, "#ff6a5a")))
sc(1, phl("rok6_today", None, "참전 노병과 함께한 오늘의 육군 제6사단"))
sc(1, text("초산진 부대", "yellow", "국군 제6사단 제7연대의 이름"), src=SRC["misc"])
sc(1, KR(LOCK("cheorwon", 0.3, "철원 · 휴전선")), src=SRC["misc"])
sc(1, text("제1중대장 이대용", "blue", "훗날 장군 · 외교관"), src=SRC["seg"])
sc(1, flat([108.0, 14.0], 22, pins=[fpin([106.7, 10.78], "사이공", on="사이공", color=RED)], title="1975 · 베트남"), src=SRC["seg"])
sc(1, text("5년 억류 → 1980 귀국", "dark", "이대용"), src=SRC["seg"])
sc(1, CS(mark("yalubank", "blue", 0)))
sc(1, AI("canteen_fill", kb="in", title="압록강의 수통", sub="재연"), label=DRAMA, src=SRC["misc"])
sc(1, CS(mark("yalubank", "blue", 0), tilt=40))
sc(1, AI("first_snow", kb="in", title="어느 가을날의 희망", sub="재연"), label=DRAMA)
SOMBER = nid()
sc(1, AI("helmets_row", kb="out", title="돌아오지 못한 병사들", sub="재연"), label=DRAMA)
sc(1, KR(line(FULL, 0, KRY), mark("chosan", "blue", 0)))
sc(1, {"type": "endcard", "title": "압록강까지 걸어간\n모든 병사를 기억하며", "q": pin("rok7_1949")}, tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 =====
REUSE = {"dust_column": "ep35-pyongyang", "field_phone": "ep35-pyongyang", "helmets_row": "ep33-seobuksan", "trucks_left": "ep33-seobuksan",
         "airdrop": "ep33-seobuksan", "valley_quiet": "ep31-hwaryeong"}
TAIL = ", cinematic photorealistic reenactment, 1950 Korean War, muted desaturated film color, 35mm documentary still, film grain, faces not identifiable, absolutely no flags, no banners, no text, no letters, no numbers."
ROK = "clearly East Asian Korean young men as South Korean soldiers in 1950 olive drab US-style fatigues and M1 steel helmets, absolutely no collar tabs, no patches, no red, no stars"
CN = "Chinese infantrymen in plain padded khaki-green 1950 winter uniforms and soft caps with ear flaps, rifles, no insignia, no red stars, no flags"
NEW = {
    "first_snow": "Late October 1950, a thin first snow lightly dusting steep forested mountains and a narrow winding dirt road in the far north of Korea near the border, bare autumn trees, grey dawn light, mist in the valleys, no people",
    "yalu_bank": "Afternoon in late October 1950, a few " + ROK + " running down a steep grassy riverbank toward a very wide calm river, low hills on the far bank across the water, light snow on distant hills, seen from behind, small figures",
    "river_drink": "Late October 1950, " + ROK + " kneeling at the edge of a very wide cold river, cupping water in their hands and drinking, rifles beside them, wide river and far hills in the background, seen from the side and behind, faces turned away",
    "canteen_fill": "Close-up of hands of a soldier in an olive drab 1950 field jacket sleeve filling an old dented aluminum 1940s military canteen in cold clear river water at the bank, pebbles, light snow on the stones, shallow depth of field",
    "autumn_ridge": "Endless steep forested mountain ridges in northern Korea in late October 1950, autumn colors of red and brown, a single narrow dirt road winding along a valley floor far below, no villages, haze, aerial view from a high ridge, no people",
    "cn_night_march": "Night in October 1950, a very long single file of " + CN + " walking silently along a narrow mountain path through a dark pine forest, faint moonlight, no fires, no lights, seen from far behind as dark silhouettes",
    "onjong_ambush": "Late October 1950, a column of " + ROK + " on a narrow dirt road at the bottom of a deep valley suddenly under fire from both steep wooded slopes, muzzle flashes among the trees on the hillsides, dust and smoke, soldiers diving for cover, seen from above and far away, small figures",
    "chosan_town": "A small 1950 Korean border town of low dark tiled-roof and thatched houses on the bank of a very wide river in late autumn, light snow on the roofs, low hills across the river, thin smoke from chimneys, an empty dirt street, no people close, no signs",
    "pontoon_bridge": "A very wide river in late October 1950 with a long narrow makeshift floating footbridge of wooden rafts and planks stretching to the far bank, tiny distant figures crossing it away from the camera toward low hills on the far side, grey sky, seen from the near riverbank",
    "night_trucks": "Dusk turning to night in late October 1950, a short convoy of plain olive drab 1940s army trucks with no markings, no stars and no numbers driving on a narrow snowy dirt road in a dark mountain valley, dim headlights off, soldiers sitting in the open cargo beds as silhouettes",
    "valley_trucks": "A long line of plain olive drab 1940s army trucks with no markings, no stars and no numbers and towed artillery guns stopped bumper to bumper on a single narrow dirt road at the bottom of a very narrow steep mountain gorge in late October 1950, steep rocky slopes on both sides, grey afternoon, seen from a high slope",
    "valley_night_attack": "Night in a very narrow mountain gorge in late October 1950, many dark silhouettes of " + CN + " running down steep slopes toward a line of stopped trucks on the valley road, scattered muzzle flashes and a burning truck lighting the smoke, no moon, seen from far away",
    "mountain_escape": "Dusk in early November 1950, a few exhausted " + ROK + " walking in single file over a bare rocky mountain ridge covered with thin snow, carrying rifles and blankets, cold wind, seen from far behind as small silhouettes against a pale sky",
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

# 출처: 숫자가 들어간 문장에 src가 없으면 기본 [1, 2] (한국민족문화대백과 초산전투 · 애플먼 33장 — research.md)
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
board = {"title": "압록강의 수통", "subtitle": "초산·압록강 진격전 · 1950", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
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
