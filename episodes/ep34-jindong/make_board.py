# EP34 해병대 진동리 지구 기습전 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 지도사 방식 화면 표준 첫 편(지도 60%+ · 글자 카드 25%- · 작전 시계 date/clock · 범례 legend · 사료 인용 clip · 하단 제목 lower) + 롱폼 표준 + 초반 후킹 표준 · 목소리 승현 eleven_v3
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
    ("천구백오십년 팔월 삼일", "1950년 8월 3일"), ("천구백오십년 팔월 일일", "1950년 8월 1일"), ("천구백오십년 유월 이십오일", "1950년 6월 25일"),
    ("천구백사십구년 사월 십오일", "1949년 4월 15일"), ("천구백이십사년", "1924년"), ("천구백구십이년 십이월", "1992년 12월"),
    ("팔월 십칠일", "8월 17일"), ("팔월 십삼일", "8월 13일"), ("팔월 십이일", "8월 12일"), ("팔월 칠일", "8월 7일"), ("팔월 육일", "8월 6일"),
    ("팔월 삼일", "8월 3일"), ("팔월 이일", "8월 2일"), ("칠월 삼십일일", "7월 31일"), ("칠월 중순", "7월 중순"), ("칠월 하순", "7월 하순"),
    ("새벽 두 시", "새벽 2시"), ("저녁 여섯 시", "저녁 6시"), ("밤 열 시 반", "밤 10시 반"),
    ("일 년 넉 달", "1년 4개월"), ("일 년 이 개월", "1년 2개월"), ("창설 일 년", "창설 1년"), ("한 해 전", "한 해 전"),
    ("삼백팔십 명", "380명"), ("팔십칠 명", "87명"), ("육백여 명", "600여 명"), ("부상자 여섯 명", "부상자 6명"), ("부상 여섯 명", "부상 6명"), ("포로 네 명", "포로 4명"),
    ("전차 두 대", "전차 2대"), ("차량 여섯 대", "차량 6대"), ("트럭 네 대와 지프 두 대", "트럭 4대와 지프 2대"), ("기관총 여섯 정과 소총 쉰여덟 정", "기관총 6정과 소총 58정"),
    ("칠백삼십구 미터", "739m"), ("사백이십팔 고지", "428고지"), ("삼백사십사 고지", "344고지"), ("십여 킬로미터", "10여 km"), ("몇 킬로미터", "몇 km"),
    ("이십 대 중반", "20대 중반"), ("서른여덟 살", "38살"), ("칠십여 년", "70여 년"), ("스물일곱 번째", "27번째"), ("여덟 시간", "8시간"),
    ("중대 세 개", "중대 3개"), ("능선 세 곳", "능선 3곳"), ("세 능선", "3개 능선"), ("세 방향", "3방향"), ("네 가지", "4가지"), ("두 가지", "2가지"),
    ("한 계급씩", "1계급씩"), ("한 개 대대", "1개 대대"),
    ("삼팔선", "38선"), ("육이오", "6·25"),
    ("제이십오사단", "제25사단"), ("제이십칠연대", "제27연대"), ("제육사단", "제6사단"),
    ("제이중대", "제2중대"), ("제삼중대", "제3중대"), ("제칠중대", "제7중대"),
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




# 좌표는 개략 (고사리·344고지·428고지·제2중대 위치·매복 지점·야반산·전적비는 기록과 현재 지형 기준 근사 — 화면에 '위치 개략' 표기)
P = {
    "seoul": [126.978, 37.566, "서울"], "daejeon": [127.385, 36.35, "대전"], "daegu": [128.6, 35.87, "대구"], "sangju": [128.16, 36.41, "상주"],
    "gunsan": [126.71, 35.97, "군산"], "janghang": [126.69, 36.01, "장항"], "iri": [126.96, 35.95, "이리"], "gwangju": [126.85, 35.16, "광주"],
    "namwon": [127.39, 35.41, "남원"], "hamyang": [127.725, 35.52, "함양"], "jirisan": [127.73, 35.34, "지리산"],
    "yeosu": [127.66, 34.76, "여수"], "suncheon": [127.49, 34.95, "순천"], "hadong": [127.751, 35.067, "하동"],
    "jinju": [128.085, 35.18, "진주"], "goseong": [128.322, 34.973, "고성"], "tongyeong": [128.433, 34.854, "통영"],
    "masan": [128.572, 35.197, "마산"], "changwon": [128.69, 35.225, "창원"], "jinhae": [128.69, 35.15, "진해"], "busan": [129.04, 35.18, "부산"],
    "chindong": [128.483, 35.108, "진동리"], "school": [128.487, 35.112, "진동초등학교"], "haman": [128.406, 35.272, "함안"],
    "seobuk": [128.385, 35.195, "서북산"], "pilbong": [128.386, 35.193, "필봉"], "banseong": [128.29, 35.155, "반성"],
    "gosa": [128.415, 35.145, "고사리"], "cp": [128.418, 35.143, "고사리 지서"], "c2": [128.392, 35.172, "제2중대"], "c3": [128.402, 35.128, "제3중대 · 428고지"],
    "c7": [128.384, 35.141, "제7중대 · 344고지"], "amb": [128.378, 35.151, "매복 지점"], "yaban": [128.505, 35.152, "야반산"], "jisan": [128.515, 35.142, "전적비 · 지산리"],
}
V = {
    "korea": {"center": [127.7, 36.2], "span": 8.2}, "south": {"center": [127.55, 35.45], "span": 3.4}, "west": {"center": [126.95, 35.85], "span": 1.4},
    "peri": {"center": [128.45, 35.85], "span": 4.0}, "coast": {"center": [128.33, 35.15], "span": 0.9}, "east": {"center": [128.72, 35.17], "span": 0.85},
    "jinhae": {"center": [128.66, 35.16], "span": 0.32}, "road": {"center": [128.37, 35.155], "span": 0.3}, "gosa": {"center": [128.398, 35.15], "span": 0.15},
    "chindong": {"center": [128.47, 35.13], "span": 0.2}, "yaban": {"center": [128.49, 35.14], "span": 0.14}, "haman": {"center": [128.42, 35.22], "span": 0.32},
    "scoast": {"center": [128.5, 35.0], "span": 0.9},
}
ROAD2 = [[128.085, 35.18], [128.2, 35.165], [128.29, 35.155], [128.345, 35.155], [128.378, 35.151], [128.415, 35.145], [128.445, 35.127], [128.483, 35.108], [128.53, 35.15], [128.572, 35.197]]
ROAD_IN = [[128.33, 35.156], [128.36, 35.153], [128.378, 35.151]]   # 매복 지점까지 들어오는 정찰대대 대열
ROAD_N = [[128.085, 35.18], [128.25, 35.25], [128.406, 35.272], [128.52, 35.23], [128.572, 35.197]]   # 북쪽 길 (함안 경유)
NK6 = [[126.98, 37.5], [126.95, 36.8], [126.75, 36.05], [126.9, 35.4], [127.3, 35.0], [127.751, 35.067], [128.085, 35.18]]
MAIN_NK = [[127.0, 37.4], [127.4, 36.6], [127.9, 36.2], [128.3, 35.95]]
RETREAT = [[126.71, 35.97], [127.0, 35.7], [127.39, 35.41], [127.725, 35.52], [128.085, 35.18]]
SEA_GUNSAN = [[128.69, 35.1], [128.3, 34.75], [127.6, 34.55], [126.6, 34.45], [126.3, 35.2], [126.62, 35.95]]
SANGJU_MASAN = [[128.16, 36.41], [128.4, 36.0], [128.5, 35.6], [128.56, 35.25]]
PERI = [[129.45, 36.25], [128.95, 36.35], [128.5, 36.2], [128.37, 36.0], [128.42, 35.6], [128.45, 35.38], [128.4, 35.25], [128.43, 35.15], [128.48, 35.1]]
COL_N = [[128.56, 35.22], [128.45, 35.3], [128.33, 35.3], [128.2, 35.24]]
COL_C = [[128.483, 35.108], [128.38, 35.13], [128.27, 35.15], [128.15, 35.17]]
COL_S = [[128.483, 35.108], [128.4, 35.03], [128.322, 34.973], [128.2, 35.0]]
SEA_TY = [[128.69, 35.12], [128.62, 35.0], [128.52, 34.9], [128.45, 34.86]]
YB_ROAD = [[128.483, 35.108], [128.53, 35.15], [128.572, 35.197]]
FIRE = [[[128.392, 35.17], [128.38, 35.154]], [[128.4, 35.13], [128.381, 35.148]], [[128.386, 35.142], [128.379, 35.149]]]
SCATTER = [[[128.376, 35.152], [128.365, 35.168]], [[128.374, 35.15], [128.36, 35.138]], [[128.372, 35.152], [128.35, 35.158]]]

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
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))
QUESTION = "창설 1년 된 해병대는 어떻게\n전차를 앞세운 적 정찰대대를 무너뜨렸나"
RED = "#c9242c"
LEG = [{"icon": "kr", "text": "한국 해병대"}, {"icon": "nk", "text": "북한군 제6사단"}, {"icon": "us", "text": "미군"}, {"icon": "road", "text": "진주–마산 남쪽 길"}]
LEG_WIDE = [{"icon": "kr", "text": "국군 · 해병대"}, {"icon": "nk", "text": "북한군"}, {"icon": "route", "text": "이동 경로"}]


def M(view, *items, tilt=26, **kw):
    return m(view, view, list(items), tilt=tilt, **kw)


ROADL = lambda at=0, color="#ffd400": line(ROAD2[3:8], at, color)
GS = lambda *items, tilt=40, **kw: M("gosa", ROADL(0), mark("gosa", "blue", 0), *items, tilt=tilt, **kw)
GSN = lambda *items, tilt=40, **kw: GS(*items, tilt=tilt, tone="night", **kw)
RD = lambda *items, tilt=32, **kw: M("road", line(ROAD2[1:9], 0, "#ffd400"), mark("gosa", "blue", 0), *items, tilt=tilt, **kw)
CD = lambda *items, tilt=34, **kw: M("chindong", mark("chindong", "blue", 0), *items, tilt=tilt, **kw)
YB = lambda *items, tilt=38, **kw: M("yaban", line(YB_ROAD, 0, "#ffd400"), mark("yaban", "red", 0), *items, tilt=tilt, **kw)
CO = lambda *items, tilt=22, **kw: M("coast", mark("masan", "blue", 0), mark("jinju", "red", 0), *items, tilt=tilt, **kw)
EA = lambda *items, tilt=20, **kw: M("east", mark("masan", "blue", 0), mark("jinhae", "blue", 0), *items, tilt=tilt, **kw)
SO = lambda *items, tilt=14, **kw: M("south", *items, tilt=tilt, **kw)
KR = lambda *items, tilt=12, **kw: M("korea", *items, tilt=tilt, **kw)
SC = lambda *items, tilt=22, **kw: M("scoast", mark("chindong", "blue", 0), mark("tongyeong", "blue", 0), *items, tilt=tilt, **kw)
UNITS3 = lambda at=0: [unit("c2", "제2중대", "blue", at), unit("c3", "제3중대", "blue", at), unit("c7", "제7중대", "blue", at)]


def clip(source, text, on=None, at=0.2, pos=None):
    d = {"source": source, "text": text}
    if on:
        d["on"] = on
    else:
        d["at"] = at
    if pos:
        d["pos"] = pos
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


def AI(img, kb="in", title=None, date=None, sub=None, tone=None):
    v = ai(img, kb)
    if title:
        lw = {"title": title}
        if date:
            lw["date"] = date
        if sub:
            lw["sub"] = sub
        v["lower"] = lw
    return v


# ===== 콜드 오프닝 (지도사 도입 구조: 결과 → 모순 → 반전 → 핵심 질문 → 타이틀) =====
sc(1, GSN(LOCK("amb", 0.3, "진동리 서쪽 산길 · 위치 개략", RED)), date="1950. 8. 3", clock="새벽", legend=LEG, sfx=WIND(0.2),
   hook={"hud": [HUD("1950. 8. 3", "경남 진동리 서쪽", "새벽", count=False)]})
sc(1, RD(LOCK("gosa", 0.3, "진주 → 마산 남쪽 길"), tone="night"))
sc(1, AI("gosari_road", title="새벽 산길의 정찰대대", date="1950. 8. 3", sub="재연"), label=DRAMA, sfx=TANK(0.2))
sc(1, GSN(swarm(ROAD_IN, 0.1, 70, 0.1), unit([128.34, 35.156], "북한군 제6사단 정찰대대", "red", 0.3, True)))
sc(1, CO(line(ROAD2[3:], 0.1, "#ffd400"), LOCK("masan", 0.5, "길 끝 · 마산")))
sc(1, EA(dash_r([[128.572, 35.197], [128.69, 35.15], [129.04, 35.18]], 0.2), badge("jinhae", "진해", "#111", on="진해가", dy=-50), mark("busan", "blue", on="부산이")))
sc(1, M("jinhae", mark("jinhae", "blue", 0), LOCK("jinhae", 0.3, "진해 · 해군의 고향"), tilt=24))
sc(1, GSN(*UNITS3(0.3)), callouts=low("길 양쪽 능선 · 위치 개략"))
sc(1, phl("kmc_pusan", "1950. 9", "한국 해병대"), hook={"hud": [HUD("1년 4개월", "해병대 창설 뒤", "1949. 4. 15 창설", count=False, on="넉 달")]})
sc(1, SO(dash_b(RETREAT, 0.1)), legend=LEG_WIDE, callouts=top("1950. 7 · 계속된 후퇴"))
sc(1, SO(dash_b(RETREAT, 0), badge("gunsan", "군산", RED, on="군산에서", dy=-50), badge("namwon", "남원", RED, on="남원에서", dy=-50), badge("jinju", "진주", RED, on="진주에서도", dy=-50)))
sc(1, black("그런데 이날 새벽", "결과는 달랐다"))
sc(1, GS(clash("amb", 0.1), shock([[128.378, 35.151], [128.372, 35.153]], 0.2)), legend=LEG, sfx=FAR(0.1),
   hook={"hud": [HUD("87명", "적 사살", "해병대 전투일지", color="#FF3B3B", on="팔십칠")]})
sc(1, GS(clash("amb", 0), badge("amb", "전차 2 · 차량 6 파괴", RED, 0.3, -80)),
   hook={"hud": [HUD("87명", "적 사살", "해병대 전투일지", color="#FF3B3B", count=False), HUD("2 + 6", "전차 · 차량 파괴", on="두 대와")]})
sc(1, GS(*UNITS3(0)), hook={"hud": [HUD("87명", "적 사살", count=False, color="#FF3B3B"), HUD("2 + 6", "전차 · 차량 파괴", count=False), HUD("6명", "해병대 부상", "기록 기준", color="#4FA3FF", on="여섯 명")]})
sc(1, phl("kmc_flag", "1950. 9", "태극기를 앞세운 한국 해병대"))
sc(1, text("부대원 전원 1계급 특진", "yellow", "국군 역사에 드문 일"))
sc(2, black("“운 좋은 기습 한 번”"), hook={"neg": {"text": "운 좋은 기습 한 번", "at": 0.3, "xOn": "그랬을까요"}})
sc(1, CO(LOCK("jinju", 0.2, "1950. 7. 31 · 진주 함락", RED), mark("gosa", "blue", 0.5)), hook={"hud": [HUD("3일", "진주 함락 → 고사리", on="사흘")]})
sc(1, phl("kmc_amtrac", "1950. 9", "같은 부대 · 같은 병사들"))
sc(1, GSN(LOCK("gosa", 0.3, "?", RED)), sfx=PING(0.4))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, RD(LOCK("gosa", 0.3, "지도 위 작은 마을")))
sc(1, {"type": "titlecard", "title": "새벽 길목의 해병대", "sub": "진동리 지구 기습전 · 1950", "at": 0, "q": pin("kmc_dukw")}, flash=True)
next_act()

# ===== 제1막 일 년 넉 달 =====
sc(1, KR(mark("jinhae", "blue", 0.3)), chapter={"num": "제1막", "title": "일 년 넉 달"}, date="1949. 4. 15", legend=LEG_WIDE)
sc(1, M("jinhae", LOCK("jinhae", 0.2, "경남 진해"), tilt=24))
sc(1, AI("jinhae_1949", title="진해 군항", date="1949", sub="재연"), label=DRAMA)
sc(1, text("대한민국 해병대", "blue", "1949. 4. 15 · 진해"))
sc(1, troops(38, side="kr", cols=10, title="처음 모인 인원", labels=[{"x": 0.5, "y": 0.76, "text": "380명", "on": "삼백팔십", "color": "blue"}]))
sc(1, M("jinhae", unit("jinhae", "해병대 · 대대 1개 크기", "blue", 0.2, True), tilt=24))
sc(1, SO(mark("jinhae", "blue", 0), mark("yeosu", "red", 0.4), mark("suncheon", "red", 0.4)))
sc(1, SO(mark("yeosu", "red", 0), mark("suncheon", "red", 0)), date="1948. 10")
sc(1, SO(clash("yeosu", 0.2), clash("suncheon", 0.4), LOCK("yeosu", 0.5, "여수·순천", RED)))
sc(1, AI("naval_feint_dusk", title="바다로 나간 해군 함정", sub="재연"), label=DRAMA)
sc(1, SO(dash_b([[127.75, 34.5], [127.66, 34.72]], 0.2), badge("yeosu", "땅에 오를 군대 없음", RED, 0.5, -60)))
sc(1, text("신현준 중령", "blue", "함대를 이끈 지휘관"))
sc(1, SO(mark("yeosu", "red", 0)), clip=clip("신현준 중령의 보고 (요지)", "[[상륙군]] 없이는\n반란군을 완전히 진압할 수 없다", on="상륙군"))
sc(1, phl("sohn", "1951", "손원일 해군참모총장"))
sc(1, M("jinhae", badge("jinhae", "바다에서 땅으로 오르는 군대", "#111", 0.3, -60), tilt=24))
sc(1, text("초대 사령관 신현준 대령", "blue", "1949"))
sc(1, text("참모장 김성은 중령", "blue", "20대 중반"))
sc(1, EA(LOCK("changwon", 0.3, "창원 · 1924년생")), date="1924")
sc(1, CO(mark("changwon", "blue", 0), LOCK("gosa", 0.3, "같은 창원 땅"), mark("chindong", "blue", 0.4)), date="1950. 8")
sc(1, CO(LOCK("gosa", 0, "같은 창원 땅"), radar("gosa", 0.2, 0.8, "blue")))
sc(1, SO(mark("jirisan", "red", 0.2)), date="1949")
sc(1, SO(LOCK("jirisan", 0.2, "지리산 일대 · 산악 토벌"), mark("jinju", "blue", 0.3)))
sc(1, AI("misty_gorge", title="지리산 자락의 골짜기", sub="재연"), label=DRAMA)
sc(1, AI("summer_heat", title="산에서 익힌 싸움", sub="재연"), label=DRAMA)
sc(1, M("jinhae", unit("jinhae", "1개 대대 → 2개 대대", "blue", 0.3, True), tilt=24), date="1949. 8")
sc(2, checklist("1950년 해병대의 무기", [{"text": "일본군이 남긴 소총", "on": "일본군이"}, {"text": "미군이 넘겨준 낡은 장비", "on": "미군이"}]))
sc(2, checklist("1950년 해병대의 무기", [{"text": "일본군이 남긴 소총", "at": 0}, {"text": "미군이 넘겨준 낡은 장비", "at": 0}, {"text": "전차 0대", "on": "한 대도", "bad": True}, {"text": "대전차포 거의 없음", "on": "큰 포도", "bad": True}]))
sc(1, KR(red_a(MAIN_NK, 0.2, 1.2), mark("seoul", "red", 0.5)), date="1950. 6. 25", sfx=FAR(0.2))
sc(1, KR(red_a(MAIN_NK, 0), LOCK("jinhae", 0.3, "진해에 닿은 소식")))
sc(1, KR(mark("jinhae", "blue", 0)), hook={"hud": [HUD("1년 2개월", "창설 → 개전", on="이 개월")]})
sc(1, phl("navy_ship", None, "6·25전쟁 당시 한국 해군 함정"))
sc(1, SO(blue_a(SEA_GUNSAN, 0.2, 1.1), mark("jinhae", "blue", 0)), callouts=low("바다로 어디든"))
sc(1, AI("strait_night", title="해군 함정에 오른 해병대", sub="재연"), label=DRAMA)
sc(1, SO(blue_a(SEA_GUNSAN, 0), LOCK("gunsan", 0.4, "첫 시험대")))
sc(1, black("그 시험은", "후퇴로 시작됐다"))
next_act()

# ===== 제2막 밀려난 열흘 =====
sc(1, SO(blue_a(SEA_GUNSAN, 0.1, 1.1), mark("gunsan", "blue", 0.6)), chapter={"num": "제2막", "title": "밀려난 열흘"}, date="1950. 7 중순")
sc(1, M("west", red_a([[126.9, 36.9], [126.8, 36.3], [126.72, 36.02]], 0.2, 1.2), mark("gunsan", "blue", 0), tilt=18))
sc(1, M("west", mark("gunsan", "blue", on="군산과"), mark("janghang", "blue", on="장항"), mark("iri", "blue", on="이리에서"), clash("gunsan", 0.7), tilt=18), sfx=FAR(0.5))
sc(1, KR(red_a(NK6[:4], 0.1, 1.2), mark("seoul", "red", 0)))
sc(1, text("사단장 방호산", "red", "북한군 제6사단"))
sc(1, phl("nk_captured", "1950. 7. 29", "진주 남쪽에서 붙잡힌 북한군"))
sc(1, M("west", unit([126.85, 36.15], "북한군 제6사단", "red", 0.2, True), tilt=18))
sc(1, AI("column_in_mist", title="남으로 내려오는 북한군 대열", sub="재연"), label=DRAMA)
sc(1, cmp("해병대", "1개 대대", "북한군", "1개 사단 + 전차"))
sc(1, M("west", LOCK("gunsan", 0.2, "군산 함락", RED), dash_b([[126.71, 35.97], [127.0, 35.7]], 0.4), tilt=18))
sc(1, SO(red_a(NK6[2:5], 0.1, 1.2)))
sc(1, SO(red_a(NK6[2:], 0, 1.2), mark("jinju", "red", 0.6)))
sc(1, KR(red_a(MAIN_NK, 0.1), mark("daejeon", "red", 0.3), mark("daegu", "blue", 0.5)), callouts=low("대부분은 가운데 길로"))
sc(1, KR(dash_r(MAIN_NK, 0), red_a(NK6, 0.1, 1.3)), callouts=low("서쪽 끝을 크게 돈 1개 사단", "red"))
sc(1, SO(red_a(NK6[3:], 0), badge([127.4, 35.1], "막을 군대가 거의 없음", RED, 0.3, -60)))
sc(1, SO(unit("namwon", "해병대", "blue", 0.2, True)), date="1950. 7 하순")
sc(1, SO(mark("namwon", "blue", on="남원과"), mark("hamyang", "blue", on="함양"), mark("jinju", "blue", on="진주였습니다")))
sc(1, text("김성은 중령", "blue", "해병대 지휘관"))
sc(1, text("‘김성은 부대’", "yellow", "지휘관 이름이 곧 부대 이름"))
sc(1, AI("op_post", title="물러서며 버티는 싸움", sub="재연"), label=DRAMA)
sc(1, SO(dash_b(RETREAT[2:], 0.1), clash("namwon", 0.2), clash("hamyang", 0.5)))
sc(1, SO(dash_b(RETREAT[2:], 0), badge("hamyang", "지연전", "#111", 0.3, -60)))
sc(1, CO(red_a([[127.751, 35.067], [128.085, 35.18]], 0.1), LOCK("jinju", 0.5, "진주 함락", RED)), date="1950. 7. 31", sfx=FAR(0.3))
sc(1, CO(red_a(ROAD2[:7], 0.2, 1.1)), callouts=low("진주 → 마산 · 산 몇 개"))
sc(1, EA(line([[128.572, 35.197], [129.04, 35.18]], 0.2, "#ff6a5a"), mark("busan", "blue", 0.5)), callouts=low("마산 → 부산 · 하루 길"))
sc(1, M("peri", line(PERI, 0, "#7fd3ff"), LOCK([128.45, 35.12], 0.3, "남쪽 끝 · 맨살", RED), tilt=14))
sc(1, CO(unit("masan", "마산 · 병력 적음", "blue", 0.2)))
sc(1, phl("rok_move", "1950. 8. 25", "전선으로 이동하는 국군"))
sc(1, M("peri", unit("sangju", "미 제25사단", "blue", 0.1), dash_b(SANGJU_MASAN, 0.3), tilt=14), callouts=low("아직 상주에서 내려오는 중"))
sc(1, CO(unit("jinju", "북한군 제6사단", "red", 0.1, True), red_a([[128.1, 35.18], [128.25, 35.17]], 0.4)))
sc(1, AI("hill342_peak", title="열흘의 후퇴", sub="재연"), label=DRAMA)
sc(1, AI("letters_table", title="한 장의 명령", sub="재연"), label=DRAMA)
next_act()

# ===== 제3막 여덟 시간 =====
sc(1, CO(unit("jinju", "북한군 제6사단", "red", 0)), chapter={"num": "제3막", "title": "여덟 시간"}, date="1950. 8. 1", legend=LEG)
sc(1, text("서남지구전투사령관", "dark", "이응준 소장"))
sc(2, CO(red_a([[128.1, 35.18], [128.3, 35.16]], 0.2), LOCK("chindong", 0.5, "진동리 서쪽")),
   clip=clip("서남지구전투사령부 명령 (요지) · 1950. 8. 1", "마산을 향해 동진하는 적을\n[[진동리 서쪽]]에서 저지하여 섬멸하라", on="막아"))
sc(1, CD(line([[128.483, 35.108], [128.53, 35.15], [128.572, 35.197]], 0.2, "#ffd400"), LOCK("chindong", 0.4, "바닷가 마을 · 진동리")), hook={"hud": [HUD("10여 km", "마산 → 진동리", on="십여")]})
sc(1, CO(line(ROAD2, 0.1, "#ffd400"), mark("goseong", "red", 0.3)), callouts=low("남쪽 길"))
sc(1, CO(line(ROAD2, 0), line(ROAD_N, 0.1, "#7fd3ff"), unit("haman", "미군", "blue", 0.4)), callouts=top("북쪽 길 · 미군"))
sc(1, CO(line(ROAD2, 0, "#ff6a5a"), badge("gosa", "빈자리", RED, 0.3, -60)))
sc(1, CO(line(ROAD2, 0), unit("masan", "해병대", "blue", 0.2, True)))
sc(1, CO(blue_a(list(reversed(ROAD2[5:])), 0.2), unit("masan", "김성은 부대", "blue", 0)), clock="18:00", sfx=SW(0))
sc(1, CD(unit([128.46, 35.118], "김성은 부대", "blue", 0.2), tone="night"), clock="22:30")
sc(1, AI("night_climb", title="밤길의 행군", date="1950. 8. 1", sub="재연"), label=DRAMA)
sc(1, RD(dash_b([[128.46, 35.118], [128.43, 35.135], [128.415, 35.145]], 0.2), tone="night"))
sc(1, RD(LOCK("gosa", 0.3, "적이 반드시 지나는 곳"), tone="night"))
sc(1, GSN(blue_a([[128.445, 35.127], [128.418, 35.143]], 0.1)), date="1950. 8. 2", clock="02:00", hook={"hud": [HUD("02:00", "고사리 도착", count=False)]})
sc(1, GSN(LOCK("gosa", 0.3, "진전면 고사리")))
sc(1, GSN(unit("gosa", "김성은 부대", "blue", 0)), hook={"hud": [HUD("8시간", "마산 출발 → 고사리", "18:00 → 02:00", on="여덟")]})
sc(1, AI("police_box", title="고사리 지서", date="1950. 8. 2", sub="재연"), label=DRAMA)
sc(1, GSN(LOCK("cp", 0.2, "지휘소 · 고사리 지서")))
sc(1, GS(badge("amb", "산 사이를 지나는 길", "#111", 0.3, -60), tilt=44), clock="")
sc(1, RD(LOCK("seobuk", 0.3, "서북산")), hook={"hud": [HUD("739m", "서북산 해발", "한국 기록 기준", on="칠백삼십구")]})
sc(1, GS(badge("c3", "낮은 능선", "#111", 0.2, -50), badge([128.37, 35.135], "낮은 능선", "#111", 0.5, -50), tilt=44))
sc(1, GS(badge("amb", "깔때기 모양", RED, 0.2, -80), tilt=48))
sc(1, text("길목", "yellow", "길 양쪽이 높고 가운데가 낮은 곳"))
sc(1, GS(*UNITS3(0.3), tilt=44), callouts=top("중대 3개 · 능선 3곳"))
sc(1, GS(unit("c2", "제2중대", "blue", on="제이중대는"), LOCK("c2", 0.4, "서북산 남쪽 기슭"), tilt=44))
sc(1, GS(unit("c2", "제2중대", "blue", 0), unit("c3", "제3중대", "blue", on="제삼중대는"), LOCK("c3", 0.4, "428고지 서쪽 능선"), tilt=44))
sc(1, GS(unit("c2", "제2중대", "blue", 0), unit("c3", "제3중대", "blue", 0), unit("c7", "제7중대", "blue", on="제칠중대는"), LOCK("c7", 0.5, "길 바로 앞 · 344고지"), tilt=44))
sc(1, GS(*UNITS3(0), *[dash_b(f, 0.2 + 0.15 * i) for i, f in enumerate(FIRE)], tilt=46), callouts=low("세 방향에서 내려다보는 배치"))
sc(1, text("제7중대장 안창관 중위", "blue", "가장 앞에 선 중대"))
sc(1, AI("trench_dig", title="능선에 판 참호", sub="재연"), label=DRAMA)
sc(1, GSN(*UNITS3(0)), clock="낮 → 밤")
sc(1, RD(unit("banseong", "북한군 제6사단", "red", 0.2), badge("gosa", "?", RED, 0.5, -60)))
sc(1, CO(unit("jinju", "북한군 제6사단", "red", 0)), clip=clip("국방부 군사편찬연구소 『6·25전쟁사』 (요지)", "북한군 제6사단은 마산에\n[[전투부대가 없는 것으로 오판]]", on="믿고"))
sc(1, AI("column_in_mist", kb="out", title="거리낌 없는 진격", sub="재연"), label=DRAMA)
sc(1, black("그 믿음의", "대가"))
next_act()

# ===== 제4막 새벽 고사리 =====
sc(1, GSN(*UNITS3(0)), chapter={"num": "제4막", "title": "새벽 고사리"}, date="1950. 8. 3", clock="새벽", legend=LEG)
sc(1, GSN(*UNITS3(0), radar([128.34, 35.156], 0.2, 0.8, "red")), sfx=TANK(0.1))
sc(1, AI("gosari_road", kb="out", title="먼저 나타난 전차", sub="재연"), label=DRAMA)
sc(1, GS(red_a(ROAD_IN[:2], 0.1), unit([128.345, 35.155], "전차 2대", "red", 0.3)))
sc(1, GS(red_a(ROAD_IN[:2], 0), swarm([[128.31, 35.157], [128.345, 35.155]], 0.1, 40, 0.08), unit([128.32, 35.157], "사이드카", "red", 0.4)))
sc(1, GS(swarm([[128.29, 35.156], [128.35, 35.155]], 0, 70, 0.08), unit([128.3, 35.157], "트럭·지프", "red", 0.3)))
sc(1, GS(LOCK([128.33, 35.156], 0.2, "북한군 제6사단 정찰대대", RED)))
sc(1, text("정찰대대", "red", "본대보다 먼저 가서 길을 여는 부대"))
sc(1, RD(unit([128.33, 35.156], "정찰대대", "red", 0.1), badge([128.33, 35.156], "사단의 눈과 귀", RED, 0.4, -80)))
sc(1, CO(dash_r(ROAD2[:9], 0.2), unit([128.15, 35.17], "사단 본대", "red", 0.4)))
sc(1, GS(red_a(ROAD_IN, 0.1), swarm(ROAD_IN, 0.1, 70, 0.08)))
sc(1, GS(red_a(ROAD_IN, 0), badge([128.34, 35.156], "“앞에 적은 없다”", RED, 0.2, -70)))
sc(1, AI("ridge_prep", title="능선 위의 해병대", sub="재연"), label=DRAMA)
sc(1, GS(red_a(ROAD_IN, 0), unit("c7", "제7중대", "blue", 0), LOCK("amb", 0.3, "제7중대 진지 앞", RED), tilt=46))
sc(1, GS(clash("amb", 0.1, 1.2), shock([[128.378, 35.151], [128.374, 35.152]], 0.1), unit("c7", "제7중대", "blue", 0), tilt=46), sfx=FAR(0.1))
sc(2, GS(clash("amb", 0), *UNITS3(0), tilt=46), clip=clip("해병대 진동리 전투일지 · 1950. 8. 3", "진지 앞을 지나는 적 전차 및 차량부대를\n[[기습 공격]]", on="기습"))
sc(1, AI("ambush_fire", title="능선에서 쏟아진 사격", date="1950. 8. 3", sub="재연"), label=DRAMA)
sc(1, GS(badge("amb", "앞차가 멈추면 뒤차도", RED, 0.3, -80), swarm(ROAD_IN[:2], 0, 60, 0.08), tilt=46))
sc(1, GS(badge("c2", "산", "#111", 0.2, -40), badge("c3", "산", "#111", 0.4, -40), clash("amb", 0), tilt=50))
sc(1, GS(*UNITS3(0), *[blue_a(f, 0.1 + 0.12 * i) for i, f in enumerate(FIRE)], shock([[128.378, 35.151], [128.372, 35.153], [128.366, 35.154]], 0.3), tilt=46))
sc(1, text("수류탄전", "red", "해병대 기록"))
sc(1, GS(clash("amb", 0), unit("c7", "제7중대", "blue", 0), badge("c7", "수류탄이 닿는 거리", "#111", 0.3, -60), tilt=50))
sc(1, text("김종식 대위", "blue", "해병대 장교 · 기록에 남은 이름"))
sc(1, GS(clash("amb", 0, 1.3), LOCK("amb", 0.3, "정찰대대 기습", RED), tilt=46))
sc(1, AI("burning_tank", title="멈춰 선 전차", sub="재연"), label=DRAMA)
sc(1, GS(badge("c7", "대전차포 거의 없음", RED, 0.3, -60), tilt=46))
sc(1, GS(LOCK("amb", 0.3, "?", RED), tilt=46))
sc(1, GS(badge("amb", "전차 2대 · 정지", RED, 0.3, -80), tilt=46))
sc(1, AI("sidecar_wreck", title="길 위에서 불탄 차량", sub="재연"), label=DRAMA)
sc(1, GS(*[dash_r(s, 0.1 + 0.15 * i) for i, s in enumerate(SCATTER)], tilt=46), callouts=low("차를 버리고 산으로", "red"))
sc(1, GS(*UNITS3(0), tilt=40), callouts=top("해병대 진동리 전투일지 · 1950. 8. 3"))
sc(1, GS(*UNITS3(0), tilt=40), hook={"hud": [HUD("87명", "적 사살", color="#FF3B3B", on="팔십칠")]})
sc(1, GS(*UNITS3(0), tilt=40), hook={"hud": [HUD("87명", "적 사살", color="#FF3B3B", count=False), HUD("4명", "포로", on="네 명")]})
sc(1, GS(*UNITS3(0), badge("amb", "전차 2 · 차량 6", RED, 0.3, -80), tilt=40),
   hook={"hud": [HUD("87명", "적 사살", color="#FF3B3B", count=False), HUD("4명", "포로", count=False), HUD("2 + 6", "전차 · 차량 파괴", on="여섯 대")]})
sc(1, GS(*UNITS3(0), tilt=40), hook={"hud": [HUD("87명", "적 사살", color="#FF3B3B", count=False), HUD("6 + 58", "기관총 · 소총 노획", on="쉰여덟")]})
sc(1, GS(*UNITS3(0), LOCK("c7", 0.3, "해병대 피해는?"), tilt=40))
sc(1, bars("1950. 8. 3 고사리 · 해병대 전투일지 등", [{"label": "적 사살", "value": 87, "display": "87명", "color": "red", "at": 0.1}, {"label": "해병대 부상", "value": 6, "display": "6명", "color": "blue", "on": "여섯"}]))
sc(1, cmp("북한군", "사살 87", "해병대", "부상 6", "red", "blue"))
sc(1, AI("valley_quiet", title="싸움이 끝난 길", sub="재연"), label=DRAMA)
sc(1, GS(*UNITS3(0), LOCK("gosa", 0.3, "숫자 너머"), tilt=36))
sc(1, RD(unit([128.36, 35.153], "정찰대대", "red", 0), badge([128.36, 35.153], "사단의 눈", RED, 0.3, -70)))
sc(1, RD(LOCK("amb", 0.2, "눈이 감기다", RED)))
sc(1, CO(unit("jinju", "북한군 제6사단", "red", 0), dash_r([[128.1, 35.18], [128.3, 35.16]], 0.3), badge([128.25, 35.17], "?", RED, 0.6, -60)))
next_act()

# ===== 제5막 같은 날 진동 =====
sc(1, CD(clash("school", 0.3), mark("gosa", "blue", 0)), chapter={"num": "제5막", "title": "같은 날 진동"}, date="1950. 8. 3", clock="새벽", sfx=FAR(0.3))
sc(1, AI("village_school", title="학교 운동장의 미군 천막", sub="재연"), label=DRAMA)
sc(1, CD(unit("school", "미 제27연대 본부 + 1개 대대", "blue", 0.2)))
sc(1, phl("inf27", "1950. 9. 4", "미 제27연대 장병"))
sc(1, CD(red_a([[128.46, 35.13], [128.484, 35.114]], 0.1), clash("school", 0.4)))
sc(1, CD(unit("school", "미 제27연대", "blue", 0), badge([128.46, 35.13], "“전투부대 없다”", RED, 0.3, -60)))
sc(1, phl("how105", "1950. 8", "미 제25사단 포병"))
sc(1, CD(blue_a([[128.487, 35.112], [128.465, 35.128]], 0.1), shock([[128.462, 35.13], [128.455, 35.135]], 0.3)))
sc(1, CD(unit("school", "미 제27연대", "blue", 0)), hook={"hud": [HUD("600여 명", "북한군 사망", "한국 쪽 기록", color="#FF3B3B", on="육백여")]})
sc(1, CO(clash("gosa", 0.1, 0.8), clash("school", 0.3, 0.8), LOCK("gosa", 0.5, "서쪽"), LOCK("school", 0.6, "동쪽")))
sc(1, CO(unit("jinju", "북한군 제6사단", "red", 0), badge([128.3, 35.16], "멈칫", RED, 0.3, -60)))
sc(1, AI("night_assault", title="다시 움직인 북한군", sub="재연"), label=DRAMA)
sc(1, CD(dash_r([[128.44, 35.17], [128.5, 35.155]], 0.2)))
sc(1, YB(LOCK("yaban", 0.3, "야반산 · 위치 개략", RED), unit("yaban", "북한군", "red", 0.5), tone="night"), date="1950. 8. 6", clock="새벽")
sc(1, YB(line(YB_ROAD, 0.1), badge("yaban", "진동 → 마산 길을 내려다보는 산", "#111", 0.3, -80)))
sc(1, YB(line(YB_ROAD, 0, "#ff6a5a"), dash_r([[128.505, 35.152], [128.525, 35.145]], 0.3)), callouts=low("끊길 수 있는 마산 길", "red"))
sc(1, YB(unit("chindong", "미군 · 고립 위기", "blue", 0.2)))
sc(1, YB(blue_a([[128.49, 35.125], [128.503, 35.148]], 0.2)), clock="오전")
sc(1, YB(dash_b([[128.503, 35.148], [128.49, 35.125]], 0.2), badge("yaban", "반격 실패", RED, 0.4, -80)))
sc(1, YB(unit([128.485, 35.12], "김성은 부대 → 미 제27연대 배속", "blue", 0.2)))
sc(1, text("기다리는 싸움 → 올라가는 싸움", "yellow"))
sc(1, YB(blue_a([[128.485, 35.12], [128.503, 35.15]], 0.1, 1.2), unit([128.485, 35.12], "해병대", "blue", 0)), clock="오후")
sc(1, AI("day_retake", title="야반산 비탈을 오르다", date="1950. 8. 6", sub="재연"), label=DRAMA)
sc(1, YB(clash("yaban", 0.1), LOCK("yaban", 0.5, "야반산 탈환")), sfx=FAR(0.1))
sc(1, YB(line(YB_ROAD, 0.1, "#7fd3ff"), unit("yaban", "해병대", "blue", 0)), callouts=low("다시 열린 마산 길"))
sc(1, phl("kean", "1950", "미 제25사단장 킨 소장"))
sc(1, CO(blue_a(COL_N, 0.1), blue_a(COL_C, 0.2), blue_a(COL_S, 0.3)), date="1950. 8. 7")
sc(1, text("킨 특수임무부대", "blue", "미 제25사단 중심 · 첫 본격 반격"))
sc(1, CO(blue_a(COL_C, 0), unit([128.43, 35.16], "해병대 · 옆구리", "blue", 0.2)))
sc(1, M("haman", line([[128.483, 35.108], [128.53, 35.15], [128.572, 35.197]], 0, "#7fd3ff"), blue_a([[128.44, 35.16], [128.4, 35.19]], 0.2), LOCK("seobuk", 0.4, "서북산 일대"), tilt=30))
sc(1, M("haman", blue_a([[128.44, 35.24], [128.395, 35.2]], 0.2), LOCK("pilbong", 0.5, "오봉산 · 필봉"), tilt=30), date="1950. 8. 12")
sc(1, AI("sobuk_peak", title="서북산 줄기", sub="재연"), label=DRAMA)
sc(1, text("1950. 7. 31 ~ 8. 13", "dark", "해병대 진동리 지구 전투"))
sc(1, CO(LOCK("gosa", 0.2, "진동리 지구")), hook={"hud": [HUD("14일", "진동리 지구 전투", "7. 31 ~ 8. 13", on="보름이")]})
sc(1, CO(unit("jinju", "북한군 제6사단", "red", 0), line([[128.43, 35.25], [128.4, 35.17], [128.45, 35.12]], 0.1, "#7fd3ff"), badge("masan", "마산 진입 실패", RED, 0.4, -60)))
next_act()

# ===== 제6막 한 계급 =====
sc(1, EA(LOCK("masan", 0.3, "전과 보고")), chapter={"num": "제6막", "title": "한 계급"}, date="1950. 8")
sc(1, black("그리고", "이례적인 결정"))
sc(1, phl("kmc_search", "1950. 9", "한국 해병대"))
sc(1, checklist("부대원 전원 1계급 특진", [{"text": "이등병 → 일등병", "on": "이등병은"}, {"text": "소위 → 중위", "on": "소위는"}]))
sc(1, checklist("부대원 전원 1계급 특진", [{"text": "이등병 → 일등병", "at": 0}, {"text": "소위 → 중위", "at": 0}, {"text": "김성은 중령 → 대령", "on": "대령이"}]))
sc(1, phl("kmc_hay", "1950. 9", "한국 해병대"))
sc(1, cmp("훈장", "한 사람에게", "특진", "부대 전체에", "yellow", "blue"))
sc(2, EA(mark("chindong", "blue", 0)), clip=clip("기록마다 다른 서술", "국군 [[최초]] — 문화일보 · 공정식 회고\n국군 [[세 번째]] — 나무위키 「마산 전투」", on="최초였는지"))
sc(2, RD(mark("gosa", "blue", 0), LOCK("amb", 0.2, "8. 3 고사리"), mark("yaban", "blue", 0.4)),
   clip=clip("특진의 계기", "8. 3 [[고사리]] 전과 — 해병대 전투일지\n8. 6 [[야반산]] 탈환 — 백과사전 · 보훈부", on="계기도"))
sc(1, CO(line([[128.38, 35.15], [128.45, 35.12], [128.505, 35.152]], 0.1, "#7fd3ff"), badge("chindong", "진동리 일대 싸움 전체", "#111", 0.4, -60)))
sc(1, black("또 하나의", "이야기"))
sc(1, text("‘귀신 잡는 해병’", "yellow"))
sc(1, phl("kmc_today", "2007", "오늘의 한국 해병대"))
sc(1, SC(badge("chindong", "①", "#111", 0.2, -50), badge("tongyeong", "②", "#111", 0.4, -50)))
sc(1, SC(LOCK("tongyeong", 0.3, "통영 상륙작전")), date="1950. 8. 17")
sc(1, phl("higgins", None, "종군기자 마거리트 히긴스"))
sc(1, SC(LOCK("chindong", 0.3, "진동리")), date="1950. 8")
sc(1, SC(mark("chindong", "blue", 0)), clip=clip("매일신문 2022 · 마산방어전투기념사업회 자료", "미 제25사단장 킨 소장으로부터\n[[‘귀신 잡는 해병’]]이라는 극찬", on="칭찬했다는"))
sc(1, text("공정식", "blue", "훗날 해병대 사령관"))
sc(1, SC(mark("chindong", "blue", 0)), clip=clip("문화일보 2014 · 공정식 회고 (요지)", "히긴스 기사는 입증되지 않았지만\n진동리 전투의 [[통신사 인터뷰 타전]]은 기록으로 남아", on="타전은"))
sc(1, black("어느 쪽이든", "같은 것 하나"))
sc(1, SC(LOCK("chindong", 0.2), LOCK("tongyeong", 0.4), line([[128.483, 35.108], [128.433, 34.854]], 0.5, "#ffd400")), callouts=low("두 번의 승리 위에서"))
sc(1, EA(LOCK("masan", 0.3, "공정식의 회고")))
sc(1, text("맥아더 사령관", "dark", "“처음에는 반신반의”"))
sc(1, phl("marines_arrive", "1950. 8. 2", "부산에 도착한 미 제1임시해병여단"))
sc(1, CO(LOCK("gosa", 0.3, "사실 확인"), unit("chindong", "한국 해병대", "blue", 0.5)))
sc(1, M("peri", line(PERI, 0, "#7fd3ff"), unit([128.45, 35.12], "한국 해병대", "blue", 0.3, True), tilt=14), legend=LEG_WIDE)
sc(1, black("이제", "처음의 질문으로"))
sc(1, GSN(LOCK("gosa", 0.3, "사흘 사이에?", RED)), legend=LEG)
next_act()

# ===== 제7막 고향의 길목 =====
sc(1, GS(*UNITS3(0), tilt=40), chapter={"num": "제7막", "title": "고향의 길목"}, date="1950. 8. 3")
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05, "kicker": "■ 처음의 질문 ■"}})
sc(1, GS(*UNITS3(0), badge("gosa", "답은 4가지", "#111", 0.3, -60), tilt=40))
sc(1, reasons("고사리의 4가지", [{"text": "자리", "on": "자리였습니다"}, {"text": "시간", "later": True}, {"text": "적의 믿음", "later": True}, {"text": "멈추지 않음", "later": True}]))
sc(1, GS(badge("amb", "깔때기 모양 길목", RED, 0.2, -80), tilt=50))
sc(1, GS(*UNITS3(0), *[blue_a(f, 0.2 + 0.1 * i) for i, f in enumerate(FIRE)], tilt=46))
sc(1, AI("burning_tank", kb="out", title="좁은 길의 전차", sub="재연"), label=DRAMA)
sc(1, reasons("고사리의 4가지", [{"text": "자리", "at": 0}, {"text": "시간", "on": "시간이었습니다"}, {"text": "적의 믿음", "later": True}, {"text": "멈추지 않음", "later": True}]))
sc(1, CO(blue_a(list(reversed(ROAD2[5:])), 0.2), mark("gosa", "blue", 0.6)), hook={"hud": [HUD("8시간", "명령 → 길목 도착", on="여덟")]})
sc(1, GSN(*UNITS3(0)), clock="하루")
sc(1, text("먼저 닿은 쪽이 길목의 주인", "yellow"))
sc(1, reasons("고사리의 4가지", [{"text": "자리", "at": 0}, {"text": "시간", "at": 0}, {"text": "적의 믿음", "on": "믿음이었습니다"}, {"text": "멈추지 않음", "later": True}]))
sc(1, RD(unit("banseong", "북한군 제6사단", "red", 0), badge("banseong", "“싸울 부대 없다”", RED, 0.3, -70)), clock="")
sc(1, GS(red_a(ROAD_IN, 0.1), swarm(ROAD_IN, 0.1, 70, 0.08), badge([128.34, 35.156], "정찰 대신 행군", RED, 0.4, -70)))
sc(1, CD(clash("school", 0.2), LOCK("school", 0.4, "같은 착각", RED)))
sc(1, reasons("고사리의 4가지", [{"text": "자리", "at": 0}, {"text": "시간", "at": 0}, {"text": "적의 믿음", "at": 0}, {"text": "멈추지 않음", "on": "않은 것이었습니다"}]))
sc(1, GS(*UNITS3(0), LOCK("gosa", 0.3, "고사리 승리"), tilt=40))
sc(1, YB(blue_a([[128.485, 35.12], [128.503, 35.15]], 0.1, 1.2), LOCK("yaban", 0.5, "야반산 탈환")), date="1950. 8. 6")
sc(1, cmp("기다릴 때", "기다리고", "올라갈 때", "올라가다", "blue", "blue"))
sc(1, SO(dash_b(RETREAT, 0.1), mark("gosa", "blue", 0.6)), legend=LEG_WIDE)
sc(1, AI("marines_dawn_ridge", title="같은 병사들", sub="재연"), label=DRAMA)
sc(1, GS(*UNITS3(0), line(ROAD2[3:8], 0, "#ff6a5a"), tilt=44), legend=LEG)
sc(1, GS(*UNITS3(0), badge("gosa", "스스로 고른 자리", "#111", 0.3, -60), tilt=44))
sc(1, EA(LOCK("changwon", 0.2, "김성은 출생지 · 창원"), mark("chindong", "blue", 0.4)), date="오늘의 창원시")
sc(1, text("고향의 길목", "yellow"))
sc(1, EA(dash_b([[128.483, 35.108], [128.6, 35.12], [128.69, 35.15]], 0.2)), date="1950. 8 중순")
sc(1, SC(blue_a(SEA_TY, 0.2, 1.2)), date="1950. 8. 17")
sc(1, SC(LOCK("tongyeong", 0.3, "통영 · 한국군 첫 단독 상륙")))
sc(1, phl("tongyeong_air", None, "오늘의 통영"))
sc(1, text("격전의 지도 EP27", "yellow", "통영상륙작전"))
sc(1, phl("kim_2007", "2007", "김성은 전 해병대사령관·국방부 장관"))
sc(1, text("38살 국방부 장관", "yellow", "1963 ~ 1968"))
sc(1, doc("국방부 장관 김성은", ["해병대 출신 첫 국방부 장관", "1963 ~ 1968 · 최장수 재임"], "國防", "대한민국 국방부", "요약"))
sc(1, YB(LOCK("jisan", 0.3, "진동리 전투 전적비")), date="1992. 12")
sc(1, YB(mark("jisan", "blue", 0), badge("jisan", "창원시 마산합포구 진북면 지산리", "#111", 0.3, -70)))
sc(1, AI("valley_today", title="오늘의 시골길", sub="재연"), label=DRAMA, date="오늘")
sc(1, GS(line(ROAD2[3:8], 0.1, "#7fd3ff"), badge("amb", "부산으로 가는 문 하나", "#111", 0.4, -80), tilt=40), date="1950. 8. 3")
sc(1, AI("yuhak_dawn", title="창설 1년 4개월의 부대", sub="재연"), label=DRAMA)
SOMBER = nid()
sc(1, AI("helmets_row", kb="out", title="이름 없이 쓰러진 병사들", sub="재연"), label=DRAMA)
sc(1, EA(line([[128.572, 35.197], [128.69, 35.15], [129.04, 35.18]], 0.1, "#7fd3ff"), mark("busan", "blue", 0.3)), date="오늘")
sc(1, text("다음 편 · 평양 최초 입성 작전", "yellow", "격전의 지도 EP35"))
sc(1, {"type": "endcard", "title": "진동리 길목을 지킨\n모든 해병을 기억하며", "q": pin("navy_chinhae")}, tail=1.0)
sc(1, black("격전의 지도"), tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 =====
# 재사용 (파일·서명 복사, 추가 비용 0) — 지도사 표준: 실사풍 시네마틱 재연만 (국기 볼 캐릭터 그림은 쓰지 않음)
REUSE = {
    "naval_feint_dusk": "ep27-tongyeong", "strait_night": "ep27-tongyeong",
    "misty_gorge": "ep31-hwaryeong", "column_in_mist": "ep31-hwaryeong", "letters_table": "ep31-hwaryeong", "village_school": "ep31-hwaryeong",
    "summer_heat": "ep33-seobuksan", "op_post": "ep33-seobuksan", "hill342_peak": "ep33-seobuksan", "ridge_prep": "ep33-seobuksan",
    "valley_quiet": "ep33-seobuksan", "night_assault": "ep33-seobuksan", "day_retake": "ep33-seobuksan", "sobuk_peak": "ep33-seobuksan",
    "valley_today": "ep33-seobuksan", "yuhak_dawn": "ep33-seobuksan", "helmets_row": "ep33-seobuksan",
}
# 새 그림 (Cloudflare Workers AI 무료) — docs/REFERENCE_JIDOSA_121.md 4-5항 실사풍 시네마틱 재연, 사람은 멀리·뒷모습, 얼굴 식별 불가, 국기·글자 없음
TAIL = ", cinematic photorealistic reenactment, 1950 Korean War, muted desaturated film color, 35mm documentary still, film grain, faces not identifiable, absolutely no flags, no banners, no text, no letters, no numbers."
KMC = "South Korean marines in 1950 olive drab US-style fatigues and M1 steel helmets"
NEW = {
    "gosari_road": "Early dawn mist on a narrow dirt road winding between steep pine-covered hills in southern Korea in August 1950, two Soviet-made T-34 tanks leading a column of motorcycles with sidecars and old military trucks, seen from high on a ridge through pine branches, small distant vehicles, blue-grey dawn light",
    "ambush_fire": "From a pine-covered hill ridge at dawn, " + KMC + " seen from behind lying in shallow foxholes and firing rifles and a light machine gun down at a column of vehicles stopped on a narrow road in the valley below, smoke and muzzle flashes, grenade bursts on the road, small figures",
    "burning_tank": "A Soviet-made T-34 tank stopped and burning on a narrow dirt road between green rice paddies and steep wooded hills in southern Korea in August 1950, black smoke rising into the morning sky, an abandoned truck behind it, no people visible",
    "sidecar_wreck": "An overturned military motorcycle with a sidecar and a burning old army truck lying on a dusty narrow Korean country road at morning in August 1950, scattered wooden ammunition boxes, smoke drifting over the hillside, no people visible",
    "night_climb": "Night in August 1950, a long column of small dark silhouettes of " + KMC + " walking quietly up a winding mountain dirt road in southern Korea under a pale moon, rifles slung, mist in the valley, seen from far behind",
    "police_box": "A small 1950 rural Korean police substation, a single-story wooden building with a dark tiled roof in a tiny mountain village at night, a dim kerosene lantern glowing in the window, a few soldiers in M1 steel helmets as dark silhouettes at the door, a folded paper map on a wooden table inside, quiet and tense",
    "trench_dig": "Night on a pine-covered ridge above a narrow valley road in southern Korea in August 1950, " + KMC + " quietly digging shallow foxholes with entrenching tools, seen from behind as dark silhouettes against a faint moonlit sky",
    "jinhae_1949": "A small Korean naval harbor in 1949 with a few grey patrol boats and an old minesweeper moored at a stone pier, green hills and cherry trees behind, a small group of young soldiers in olive drab uniforms standing in formation far away on the pier, hazy morning light",
    "marines_dawn_ridge": "Tired " + KMC + " resting on a rocky hillside at sunrise after a battle in August 1950, seen from behind looking down at a quiet valley road with a thin column of smoke, small figures",
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
board = {"title": "새벽 길목의 해병대", "subtitle": "진동리 지구 기습전 · 1950", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         # 2026-11-24 지도사 방식 화면·목소리 표준 (첫 편) — 채널 목소리 승현 · eleven_v3 · 배속 없음 · 쉼 0.65초
         "look": "archive", "sub_style": "dark", "map_tone": "day", "tts_model": "eleven_v3", "tempo": 1.0, "max_pause": 0.65, "card_max": 0.25,
         "voice": "0mlAtfsvMzFpppUuNWkV", "voice_settings": {"stability": 0.5, "similarity_boost": 0.78},
         "target_sec": 1230, "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AIMG, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
cnt = collections.Counter(s["visual"]["type"] for s in S)
w = collections.Counter()
for s in S:
    w[s["visual"]["type"]] += sum(len(say(l)) for l in s["lines"]) + 8
CARDS = {"text", "black", "checklist", "reasons", "bars", "compare", "versus", "factors", "gauges", "weekbar", "hanja"}
tot = sum(w.values())
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap], "ai", len(AIMG), "pins", len(PINS))
print("types", dict(cnt))
print(f"추정 비율: 지도 {w['map'] / tot:.0%} · 카드 {sum(v for k, v in w.items() if k in CARDS) / tot:.0%}")
