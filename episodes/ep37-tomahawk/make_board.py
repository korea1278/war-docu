# EP37 토마호크 작전(문산 공수작전) 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
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

SUBS = [
    ("천구백오십일년 삼월 이십삼일", "1951년 3월 23일"), ("천구백오십일년 일월 사일", "1951년 1월 4일"), ("천구백오십년 시월 이십일", "1950년 10월 20일"),
    ("삼월 이십이일", "3월 22일"), ("삼월 이십사일", "3월 24일"), ("삼월 이십오일", "3월 25일"), ("삼월 이십육일", "3월 26일"), ("삼월 이십칠일", "3월 27일"),
    ("삼월 십구일", "3월 19일"), ("삼월 이십일", "3월 20일"), ("삼월 칠일", "3월 7일"), ("삼월 중순", "3월 중순"), ("이월과 삼월", "2월과 3월"),
    ("오후 여섯 시 삼십 분", "오후 6시 30분"), ("오전 아홉 시", "오전 9시"), ("오전 열 시", "오전 10시"), ("오전 일곱 시", "오전 7시"), ("오후 세 시", "오후 3시"),
    ("열 시가", "10시가"), ("아홉 시간 반", "9시간 반"), ("약 이십이 시간", "약 22시간"), ("이십사 시간", "24시간"), ("약 두 시간", "약 2시간"), ("두 시간", "2시간"),
    ("약 오십 분", "약 50분"), ("약 사십오 분", "약 45분"),
    ("제백팔십칠공수연대전투단", "제187공수연대전투단"), ("삼천사백삼십칠 명", "3,437명"), ("삼천사백여 개", "3,400여 개"), ("삼천사백 명", "3,400명"), ("삼천삼백여 명", "3,300여 명"),
    ("약 삼십 킬로미터", "약 30km"), ("약 이십사 킬로미터", "약 24km"), ("이십사 킬로미터", "24km"), ("약 사십 킬로미터", "약 40km"), ("약 일점육 킬로미터", "약 1.6km"),
    ("일점육 킬로미터", "1.6km"), ("약 팔 킬로미터", "약 8km"), ("약 오 킬로미터", "약 5km"),
    ("백이십 대", "120대"), ("여덟 대", "8대"), ("전차 네 대", "전차 4대"), ("전차 두 대", "전차 2대"), ("교량전차 두 대", "교량전차 2대"), ("낙하산 두 개", "낙하산 2개"), ("중대 두 개", "중대 2개"),
    ("약 서른 명", "약 30명"), ("열두 명", "12명"), ("열세 명", "13명"), ("팔십사 명", "84명"), ("열아홉 명", "19명"), ("백삼십육 명", "136명"), ("백사십구 명", "149명"),
    ("삼백에서 오백 명", "300~500명"), ("약 사백 명", "약 400명"), ("열두 개", "12개"), ("백오십 개", "150개"), ("약 이십만 건", "약 20만 건"), ("십육 년", "16년"),
    ("진지 두 곳", "진지 2곳"), ("적 두 명이 쓰러지고 두 명이", "적 2명이 쓰러지고 2명이"), ("사수 두 명", "사수 2명"),
    ("인도군 제육십공정야전병원", "인도군 제60공정야전병원"), ("제이차 세계대전", "제2차 세계대전"), ("일사 후퇴", "1·4 후퇴"), ("미 팔군", "미 8군"),
    ("미 제일기병사단", "미 제1기병사단"), ("미 제일군단", "미 제1군단"), ("북한군 제일군단", "북한군 제1군단"), ("미 제이십오사단", "미 제25사단"), ("국군 제일사단", "국군 제1사단"),
    ("제삼사단", "제3사단"), ("미 제육전차대대", "미 제6전차대대"), ("제이레인저중대", "제2레인저중대"), ("제사레인저중대", "제4레인저중대"),
    ("제일대대장", "제1대대장"), ("제일대대", "제1대대"), ("제이대대", "제2대대"), ("제삼대대", "제3대대"), ("제십구사단", "제19사단"), ("제삼십육연대", "제36연대"),
    ("백오 밀리미터", "105mm"), ("이백십육고지", "216고지"), ("백오십일고지", "151고지"), ("이백오고지", "205고지"), ("이백이십팔고지", "228고지"),
    ("비중대", "B중대"), ("삼십삼번 도로", "33번 도로"), ("일번 국도", "1번 국도"),
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



# 좌표는 개략 (강하지점·216·205·151·228고지·신원리·파룬리 등은 기록과 현재 지형 기준 근사 — 화면에 '위치 개략' 표기)
P = {
    "seoul": [126.978, 37.566, "서울"], "munsan": [126.785, 37.858, "문산"], "dzn": [126.805, 37.872, "북쪽 강하지점"], "dzs": [126.83, 37.835, "남쪽 강하지점"],
    "h216": [126.848, 37.826, "216고지"], "h205": [126.792, 37.896, "205고지"], "h151": [126.818, 37.886, "151고지"], "ford": [126.775, 37.905, "임진강 나루"],
    "changneung": [126.886, 37.638, "창릉천"], "sinwon": [126.872, 37.66, "신원리"], "munsan_s": [126.792, 37.845, "문산 앞 1.6km"],
    "uijeongbu": [127.047, 37.738, "의정부"], "h228": [127.0, 37.8, "228고지"], "parun": [126.965, 37.812, "파룬리"], "r33": [127.055, 37.83, "33번 도로"],
    "taegu": [128.64, 35.9, "대구 비행장"], "chuncheon": [127.73, 37.88, "춘천"], "pyongyang": [125.755, 39.025, "평양"], "sukchon": [125.86, 39.41, "숙천"],
    "sunchon": [125.93, 39.43, "순천"], "kaesong": [126.555, 37.97, "개성"], "imjin": [126.9, 37.97, "임진강"], "han": [126.86, 37.58, "한강"],
    "front": [126.95, 37.68, "전선"], "turn": [127.9, 36.75, "엔진 고장 · 회항"], "india": [78.9, 22.0, "인도"], "georgia": [-84.9, 32.36, "미국 조지아주"],
    "vietnam": [106.7, 11.3, "베트남"], "panmun": [126.677, 37.956, "판문점"], "imjin_n": [126.85, 37.95, "임진강 북쪽"],
}
V = {
    "korea": {"center": [127.4, 37.6], "span": 6.6}, "south": {"center": [127.6, 36.9], "span": 3.8}, "cent": {"center": [127.25, 37.75], "span": 1.7},
    "nk": {"center": [126.4, 38.5], "span": 3.4}, "seoulnw": {"center": [126.88, 37.74], "span": 0.62}, "route": {"center": [126.85, 37.72], "span": 0.42},
    "munsan": {"center": [126.81, 37.862], "span": 0.24}, "east": {"center": [126.93, 37.8], "span": 0.46},
}
ROUTE1 = [[126.978, 37.57], [126.93, 37.61], [126.886, 37.638], [126.872, 37.66], [126.85, 37.7], [126.82, 37.75], [126.8, 37.8], [126.792, 37.845], [126.785, 37.858]]
IMJIN = [[126.67, 37.77], [126.72, 37.83], [126.76, 37.88], [126.8, 37.91], [126.86, 37.94], [126.93, 37.97], [127.0, 38.0], [127.07, 38.03]]
HAN = [[126.67, 37.77], [126.76, 37.65], [126.86, 37.58], [126.95, 37.53], [127.05, 37.52], [127.12, 37.54]]
FRONT = [[126.68, 37.67], [126.85, 37.67], [127.0, 37.68], [127.2, 37.7], [127.45, 37.73]]
FLIGHT = [[128.64, 35.9], [128.2, 36.45], [127.6, 37.05], [127.15, 37.55], [126.81, 37.87]]
RETURN = [[128.64, 35.9], [128.15, 36.5], [127.9, 36.75], [128.3, 36.3], [128.64, 35.92]]
EASTMV = [[126.81, 37.862], [126.88, 37.845], [126.94, 37.82], [126.965, 37.812], [127.0, 37.8]]
R33 = [[127.03, 37.6], [127.047, 37.738], [127.055, 37.83], [127.065, 37.93], [127.07, 38.0]]
NK_X = [[126.8, 37.82], [126.8, 37.93]]
NK_X2 = [[126.9, 37.8], [126.88, 37.96]]
CN_OUT = [[127.06, 37.82], [127.08, 37.98]]
CN_OUT2 = [[127.05, 37.86], [127.2, 38.0]]
HAMMER = [[126.86, 37.68], [126.84, 37.76]]
HAMMER2 = [[127.05, 37.7], [127.05, 37.78]]
HAMMER3 = [[127.2, 37.7], [127.15, 37.8]]
WRONG = [[126.95, 37.7], [126.86, 37.8], [126.81, 37.87]]
LONE = [[126.95, 37.7], [126.86, 37.79], [126.83, 37.835]]
HOOK = [[127.73, 37.6], [127.73, 37.88]]
KAESONG_RUN = [[126.85, 37.75], [126.7, 37.93], [126.56, 37.97]]

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
ring = lambda p, km, text=None, color=None, at=0.2, on=None: dict({"k": "ring", "p": p, "km": km}, **({"text": text} if text else {}), **({"color": color} if color else {}), **({"on": on} if on else {"at": at}))
plane = lambda path, n=6, dur=3.0, at=0.0, size=1.0: {"k": "plane", "path": path, "n": n, "dur": dur, "at": at, "size": size, "color": "#e8eef4"}
SW = lambda at=0: [{"id": "whoosh", "at": at}]
FAR = lambda at=0.1: [{"id": "artillery_far", "at": at}]
PING = lambda at=0.6: [{"id": "ping", "at": at}]
WIND = lambda at=0: [{"id": "wind", "at": at}]
WATER = lambda at=0: [{"id": "water", "at": at}]
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))
QUESTION = "3,400명이 하늘에서 친 덫은\n왜 텅 비어 있었나"
RED = "#c9242c"
YEL = "#ffd400"  # 1번 국도 · 특수임무부대 진격로
WHT = "#ffffff"  # 항로
CYA = "#4fa3ff"  # 강
LEG = [{"icon": "us", "text": "유엔군"}, {"icon": "nk", "text": "북한군"}, {"icon": "cn", "text": "중공군"}, {"icon": "route", "text": "1번 국도"}]
LEG_A = [{"icon": "us", "text": "제187공수연대"}, {"icon": "nk", "text": "북한군"}, {"icon": "route", "text": "강하지점"}]


def M(view, *items, tilt=22, **kw):
    return m(view, view, list(items), tilt=tilt, **kw)


RIV = lambda at=0: [line(IMJIN, at, CYA), line(HAN, at, CYA)]
R1 = lambda at=0: line(ROUTE1, at, YEL)
KR = lambda *items, tilt=10, **kw: M("korea", *items, tilt=tilt, **kw)
SO = lambda *items, tilt=12, **kw: M("south", *items, tilt=tilt, **kw)
CE = lambda *items, tilt=16, **kw: M("cent", *items, tilt=tilt, **kw)
NK = lambda *items, tilt=12, **kw: M("nk", *items, tilt=tilt, **kw)
SN = lambda *items, tilt=22, **kw: M("seoulnw", *items, tilt=tilt, **kw)
RT = lambda *items, tilt=28, **kw: M("route", *items, tilt=tilt, **kw)
MU = lambda *items, tilt=34, **kw: M("munsan", *items, tilt=tilt, **kw)
EA = lambda *items, tilt=26, **kw: M("east", *items, tilt=tilt, **kw)
DZ = lambda at=0: [ring("dzn", 1.1, "북쪽 강하지점", WHT, at), ring("dzs", 1.1, "남쪽 강하지점", WHT, at)]

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
    names = ["하루 늦은 덫", "지뢰와 깡통", "비와 진흙", "느린 망치"]
    items = []
    for i, nm in enumerate(names, 1):
        if i < n_on:
            items.append({"text": nm, "at": 0})
        elif i == n_on:
            items.append({"text": nm, "on": on})
        else:
            items.append({"text": nm, "later": True})
    return reasons("덫이 비어 있던 4가지 이유", items)


SRC = {"moss": [1], "whn": [2], "rng": [3], "usarpac": [4], "wiki": [5], "photo": [6], "india": [7], "ms_us": [1, 4], "ms_whn": [1, 2]}
ORG = "미 제8군 사령부"

# ===== 콜드 오프닝 =====
sc(1, MU(*DZ(0.3), LOCK("munsan", 0.2, "문산")), date="1951. 3. 23", clock="09:00", legend=LEG_A, src=SRC["ms_us"],
   hook={"hud": [HUD("1951. 3. 23", "경기도 문산", "오전 9시", count=False)]})
sc(1, SN(R1(0), mark("munsan", "blue", 0.2), line(IMJIN, 0.1, CYA)), sfx=WIND(0))
sc(1, phl("formation", "1951. 3", "편대를 이룬 C-119 수송기"), src=SRC["photo"])
sc(1, SO(plane(FLIGHT, 8, 4.0, 0.1), mark("taegu", "blue", 0), mark("munsan", "blue", 0.5)), hook={"hud": [HUD("약 120대", "C-119 · C-46 수송기", on="백이십")]}, src=SRC["wiki"])
sc(1, AI("door_jump", title="열린 뒷문", date="1951. 3. 23"), label=DRAMA, sfx=SW(0.1))
sc(1, phl("paras_1950", "1950", "C-119에서 쏟아져 나오는 공수부대원"))
sc(1, AI("sky_chutes", title="하늘을 덮은 낙하산", date="1951. 3. 23"), label=DRAMA)
sc(1, punch("낙하산"))
sc(1, troops(40, side="us", cols=10, title="미 제187공수연대전투단", labels=[{"x": 0.5, "y": 0.76, "text": "3,437명", "on": "삼천사백삼십칠", "color": "blue"}]), src=SRC["wiki"])
sc(1, AI("yellow_chutes", title="노란 낙하산의 무기 꾸러미", date="1951. 3. 23"), label=DRAMA, src=SRC["rng"])
sc(1, MU(*DZ(0), badge("dzn", "기관총 · 박격포 · 탄약", "#111", 0.3, -60)))
sc(1, CE(line(FRONT, 0.1, "#ff6a5a"), dash_b([[126.95, 37.68], [126.81, 37.86]], 0.3), mark("munsan", "blue", 0.5)), hook={"hud": [HUD("약 30km", "전선 → 문산", "적의 후방", on="삼십")]}, src=SRC["wiki"])
sc(1, MU(*DZ(0), LOCK("ford", 0.3, "목표 · 임진강 나루", RED)))
sc(1, SN(*RIV(0), red_a(NK_X, 0.2), LOCK("ford", 0.5, "임진강 · 퇴로", RED)))
sc(1, MU(*DZ(0), LOCK("ford", 0.4, "퇴로 차단")), stamp={"text": "덫", "on": "덫", "x": 0.5, "y": 0.42})
sc(1, {"type": "titlecard", "title": "토마호크 작전", "sub": "문산 공수작전 · 1951", "at": 0, "q": pin("nara_drop")}, flash=True)
sc(1, AI("dz_landing", title="논바닥에 내려선 병사들", date="1951. 3. 23"), label=DRAMA)
sc(1, MU(*DZ(0), radar("dzn", 0.2, 0.9, "blue"), badge("ford", "적은?", RED, 0.5, -60)), sfx=PING(0.4))
sc(1, RT(R1(0.1), LOCK("seoul", 0.3, "서울 출발 · 전차 부대")))
sc(1, RT(R1(0), mark("sinwon", "red", 0.2), badge("sinwon", "정지", RED, 0.4, -60)), hook={"hud": [HUD("약 24km", "문산까지 남은 거리", "오전 9시", color="#FF3B3B", on="이십사")]}, src=SRC["moss"])
sc(1, RT(R1(0), *[mark(p, "red", 0.1 + i * 0.1) for i, p in enumerate([[126.886, 37.638], [126.872, 37.66], [126.86, 37.68]])]))
sc(1, RT(R1(0), badge("sinwon", "깡통?", RED, 0.3, -60)), src=SRC["moss"])
sc(4, black("“한국전쟁 마지막 공수작전\n그리고 실패한 작전”"), hook={"neg": {"text": "그냥 실패한 작전", "at": 0.3, "xOn": "끝낼"}})
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, SN(*RIV(0), R1(0), badge("imjin", "전날 밤", RED, 0.3, -60), badge("sinwon", "24km의 길", "#111", 0.5, -60)))
sc(1, KR(mark("munsan", "blue", 0.2), LOCK("munsan", 0.3, "1951. 3. 23 · 문산")))
next_act()

# ===== 제1막 서울을 다시 찾다 =====
sc(1, KR(red_a([[127.0, 38.3], [127.0, 37.3]], 0.2, 1.3), LOCK("seoul", 0.4, "서울")), chapter={"num": "제1막", "title": "서울을 다시 찾다"}, date="1951. 1. 4", legend=LEG)
sc(1, phl("refugees_snow", "1951. 1. 8", "눈길을 걸어 남쪽으로 가는 피란민"))
sc(1, KR(red_a([[126.9, 38.2], [127.1, 37.2]], 0.1, 1.4), swarm([[126.9, 38.2], [127.1, 37.2]], 0.1, 100, 0.2), mark("seoul", "red", 0.5)))
sc(1, punch("1·4 후퇴"))
sc(1, KR(mark("seoul", "red", 0)), hook={"hud": [HUD("3번째", "서울의 주인이 바뀌다", "개전 반년", count=False, on="세 번째")]})
sc(1, SO(LOCK("taegu", 0.3, "미 8군 사령부 · 대구")), date="1950. 12. 26")
sc(1, phl("ridgway", "1951", "매슈 리지웨이"))
sc(1, text("제2차 세계대전 공수사단장", "dark", "직접 낙하산을 멘 장군"))
sc(1, phl("ridgway_jan", "1951. 1월 중순", "한국의 리지웨이 중장 (가운데)"))
sc(1, CE(line(FRONT, 0.1, "#ff6a5a")))
sc(1, CE(line(FRONT, 0, "#ff6a5a"), badge("front", "땅이 아니라 적을", "#111", 0.3, -60)))
sc(1, CE(line(FRONT, 0), badge("seoul", "도시보다 병력", "#111", 0.3, -60)))
sc(1, CE(blue_a([[127.3, 37.1], [127.3, 37.5]], 0.1), blue_a([[127.8, 37.1], [127.8, 37.55]], 0.2)), date="1951. 2~3")
sc(1, phl("thunderbolt_map", "1951. 2. 1~11", "썬더볼트 작전 상황도"))
sc(1, CE(blue_a([[127.0, 37.3], [127.0, 37.55]], 0.1, 1.1), blue_a([[127.6, 37.35], [127.6, 37.7]], 0.2, 1.1)))
sc(1, CE(blue_a([[127.3, 37.45], [127.3, 37.75]], 0.1, 1.2), blue_a([[127.75, 37.55], [127.75, 37.88]], 0.2, 1.2)), date="1951. 3. 7")
sc(1, CE(mark("seoul", "blue", 0.2), LOCK("seoul", 0.3, "서울 재수복")), date="1951. 3. 15 무렵")
sc(1, KR(mark("seoul", "blue", 0)), hook={"hud": [HUD("4번째", "서울의 주인", "1950. 6 → 1951. 3", count=False, on="네 번째")]})
sc(1, CE(line(FRONT, 0, "#ff6a5a"), radar("front", 0.3, 0.9, "red")))
sc(1, punch("적은 늘 빠져나갔다"))
sc(1, CE(blue_a([[127.3, 37.5], [127.3, 37.7]], 0.1), dash_r([[127.3, 37.75], [127.3, 37.95]], 0.3)))
sc(1, CE(dash_r([[127.3, 37.75], [127.3, 37.95]], 0), line([[126.9, 37.95], [127.3, 37.98], [127.7, 38.02]], 0.3, "#ff6a5a")))
sc(1, CE(line([[126.9, 37.95], [127.3, 37.98], [127.7, 38.02]], 0, "#ff6a5a"), badge([127.3, 37.98], "새 진지", RED, 0.3, -60)))
sc(1, CE(line(FRONT, 0), badge("front", "그대로 남은 적", RED, 0.3, -60)))
sc(1, CE(blue_a([[127.1, 37.5], [127.1, 37.68]], 0.1), dash_b([[126.95, 37.68], [126.81, 37.86]], 0.3)))
sc(1, CE(blue_a([[127.1, 37.5], [127.1, 37.68]], 0), mark("munsan", "blue", 0.2), badge("munsan", "뒤에서 막기", "#111", 0.3, -60)))
sc(1, SO(LOCK("taegu", 0.3, "대구 · 공수부대 대기")))
sc(1, SO(mark("taegu", "blue", 0), unit("taegu", "제187공수연대전투단", "blue", 0.2, True)))
next_act()

# ===== 제2막 취소된 낙하 =====
sc(1, phl("sukchon", "1950. 10. 20", "제187공수연대의 첫 강하"), chapter={"num": "제2막", "title": "취소된 낙하"}, legend=LEG)
sc(1, text("라카산", "yellow", "제187공수연대의 별명"))
sc(1, text("落下傘 · 떨어지는 우산", "dark", "일본 점령 시절 붙은 별명"))
sc(1, text("프랭크 바우엔 준장", "blue", "제187공수연대전투단장"))
sc(1, phl("paras_1950", "1950", "C-119에서 뛰어내리는 제187공수연대"))
sc(1, NK(LOCK("sukchon", 0.3), mark("sunchon", "blue", 0.4), mark("pyongyang", "red", 0)), date="1950. 10. 20")
sc(1, phl("sunchon", "1950. 10. 20", "순천 상공의 공수 강하"), hook={"hud": [HUD("3,300여 명", "숙천·순천 강하", "나흘 동안", on="삼천삼백")]}, src=SRC["photo"])
sc(1, NK(dash_r([[125.755, 39.025], [125.9, 39.6], [126.2, 40.2]], 0.2), mark("sukchon", "blue", 0)))
sc(1, NK(mark("sukchon", "blue", 0), badge("sukchon", "빈 덫", RED, 0.3, -60)))
sc(1, CE(mark("chuncheon", "blue", 0.2)), date="1951. 3")
sc(1, CE(LOCK("chuncheon", 0.3, "춘천 북쪽")))
sc(1, CE(mark("chuncheon", "blue", 0), badge("chuncheon", "호크 작전", "#111", 0.3, -60)), src=SRC["rng"])
sc(1, CE(mark("chuncheon", "blue", 0)), date="1951. 3. 20", src=SRC["rng"])
sc(1, CE(mark("chuncheon", "blue", 0)), stamp={"text": "취소", "on": "취소", "x": 0.5, "y": 0.42}, date="1951. 3. 19", src=SRC["rng"])
sc(1, CE(blue_a(HOOK, 0.1, 1.2), unit("chuncheon", "미 제1기병사단", "blue", 0.4)), src=SRC["rng"])
sc(1, CE(dash_r([[127.73, 37.92], [127.73, 38.2]], 0.2), badge("chuncheon", "비어 있던 춘천", RED, 0.4, -60)))
sc(1, CE(radar("munsan", 0.2, 0.9, "blue")))
sc(1, CE(LOCK("munsan", 0.3, "문산 · 서울 북서쪽"), mark("seoul", "blue", 0)))
sc(1, SN(line(IMJIN, 0.1, CYA), LOCK("imjin", 0.4, "임진강")), sfx=WATER(0.1))
sc(1, SN(line(IMJIN, 0, CYA), unit([126.85, 37.78], "북한군 제1군단", "red", 0.2), dash_r(NK_X, 0.4)), src=SRC["moss"])
sc(1, punch("토마호크", "TOMAHAWK"))
sc(1, CE(line(FRONT, 0, "#ff6a5a"), badge("seoul", "용감 작전", "#111", 0.3, -60)))
sc(1, SN(*RIV(0), line(FRONT, 0, "#ff6a5a"), badge([127.0, 37.68], "미 제1군단", "#111", 0.3, -60)), src=SRC["moss"])
sc(1, SN(*RIV(0), blue_a(HAMMER, 0.1), blue_a(HAMMER2, 0.2), blue_a(HAMMER3, 0.3), unit([126.86, 37.68], "국군 제1사단", "blue", on="국군"),
         unit([127.05, 37.7], "미 제3사단", "blue", on="제삼사단"), unit([127.2, 37.7], "미 제25사단", "blue", on="제이십오사단")), src=SRC["moss"])
sc(1, SN(*RIV(0), blue_a(HAMMER, 0), mark("munsan", "blue", 0.2), *DZ(0.3)))
sc(1, {"type": "weapon", "bg": "blueprint", "units": [{"kind": "plane", "x": 0.5, "y": 0.4, "w": 620, "label": "모루", "sub": "하늘에서 내려온 공수부대"},
                                                     {"kind": "tank", "x": 0.5, "y": 0.78, "w": 520, "label": "망치", "sub": "밀고 올라가는 지상군"}], "title": "망치와 모루"})
sc(1, AI("anvil", title="모루와 망치", sub="비유"), label=DRAMA)
sc(1, SN(*RIV(0), blue_a(HAMMER, 0.1, 1.2), badge("munsan", "모루", "#111", on="모루"), badge([126.86, 37.68], "망치", "#111", on="망치")))
sc(1, MU(*DZ(0), badge("munsan", "조건 2가지", "#111", 0.3, -60)), src=SRC["moss"])
sc(1, checklist("강하 조건", [{"text": "강하하는 날 날씨가 좋을 것", "on": "날씨"}]))
sc(1, checklist("강하 조건", [{"text": "강하하는 날 날씨가 좋을 것", "at": 0}, {"text": "24시간 안에 지상군과 연결", "on": "이십사"}]))
sc(1, MU(*DZ(0), unit("dzn", "공수부대", "blue", 0.2)))
sc(1, {"type": "weapon", "bg": "blueprint", "units": [{"kind": "cannon", "x": 0.5, "y": 0.64, "w": 640, "label": "전차 없음 · 대포 몇 문", "sub": "공수연대의 무게"}], "title": "가벼운 부대"})
sc(1, MU(*DZ(0), ring("dzn", 3.2, "하루를 넘기면?", RED, 0.3)))
sc(1, MU(*DZ(0), red_a([[126.76, 37.92], [126.79, 37.88]], 0.2), red_a([[126.87, 37.82], [126.84, 37.84]], 0.3)))
sc(1, SO(LOCK("taegu", 0.3, "대구 · 미 8군 사령부")), date="1951. 3. 22", clock="밤", tone="night", src=SRC["moss"])
sc(1, SO(mark("taegu", "blue", 0), radar("taegu", 0.2, 0.8, "blue")), tone="night", src=SRC["moss"])
sc(1, doc("작전 회의 (요지)", ["공군: 내일 날씨 강하에 적합", "작전 참모: 하루 안에 연결 가능"], "軍 秘", ORG), src=SRC["moss"])
sc(1, phl("ridgway", "1951", "결정을 내린 리지웨이"))
sc(1, SO(mark("taegu", "blue", 0), mark("munsan", "blue", 0.3)), clock="09:00", hook={"hud": [HUD("오전 9시", "강하 시각", "1951. 3. 23", count=False, on="아홉 시")]}, src=SRC["moss"])
next_act()

# ===== 제3막 대구 비행장의 새벽 =====
sc(1, SO(LOCK("taegu", 0.3, "대구 비행장")), chapter={"num": "제3막", "title": "대구 비행장의 새벽"}, date="1951. 3. 23", clock="새벽", legend=LEG_A)
sc(1, AI("taegu_dawn", title="엔진을 데우는 수송기들", date="1951. 3. 23"), label=DRAMA, src=SRC["wiki"])
sc(1, phl("c119_flight", "1952", "'날아다니는 화물차' C-119"))
sc(1, {"type": "weapon", "bg": "blueprint", "units": [{"kind": "plane", "x": 0.5, "y": 0.55, "w": 820, "label": "C-119 '날아다니는 화물차'", "sub": "뒤쪽이 통째로 열리는 수송기"}], "title": "수송기"})
sc(1, phl("boarding", "1951. 3. 23", "문산 강하를 앞두고 C-119에 오르는 공수부대원"), src=SRC["photo"])
sc(1, checklist("한 사람의 짐", [{"text": "낙하산 2개", "on": "낙하산"}, {"text": "소총과 탄약", "on": "소총"}, {"text": "사흘치 식량", "on": "사흘치"}]))
sc(1, SO(mark("taegu", "blue", 0), badge("taegu", "공수연대만이 아니다", "#111", 0.3, -60)))
sc(1, text("레인저 중대 2개", "blue", "제2 · 제4레인저중대"), src=SRC["rng"])
sc(1, text("제2레인저중대", "yellow", "아주 특별한 부대"), src=SRC["rng"])
sc(1, phl("ranger2", None, "제2레인저중대 참전 용사 대표들 (훗날)"), src=SRC["rng"])
sc(1, SO(mark("taegu", "blue", 0), badge("taegu", "흑인과 백인", "#111", 0.3, -60)))
sc(1, troops(24, side="us", cols=8, title="제2레인저중대", labels=[{"x": 0.5, "y": 0.76, "text": "C-46 8대", "on": "여덟", "color": "blue"}]), src=SRC["rng"])
sc(1, SO(plane(FLIGHT[:2], 8, 2.5, 0.1), mark("taegu", "blue", 0)), hook={"hud": [HUD("약 30명", "C-46 1대당", on="서른")]}, src=SRC["rng"])
sc(1, AI("sand_table", title="흙으로 만든 문산 지형 모형", sub="재연"), label=DRAMA, src=SRC["rng"])
sc(1, punch("레인저 첫 실전 강하"), src=SRC["rng"])
sc(1, SO(mark("taegu", "blue", 0), badge("taegu", "또 한 무리", "#111", 0.3, -60)))
sc(1, flat([92.0, 26.0], 60, pins=[fpin([78.9, 22.0], "인도", on="인도군"), fpin([127.0, 37.5], "한국", at=0.3)], routes=[route([78.9, 22.0], [127.0, 37.5], "제60공정야전병원", at=0.4, bend=0.25)], title="인도 → 한국"), src=SRC["india"])
sc(1, text("총 대신 의사와 간호병", "blue", "인도 제60공정야전병원"), src=SRC["india"])
sc(1, AI("medics_chutes", title="낙하산을 멘 인도 의무대", sub="재연"), label=DRAMA, src=SRC["india"])
sc(1, MU(*DZ(0), mark("dzn", "blue", 0.2), badge("dzn", "부상병은 여기에", "#111", 0.4, -60)))
sc(1, SO(plane(FLIGHT[:2], 4, 2.5, 0.2), mark("taegu", "blue", 0)), clock="07:00", sfx=SW(0.2), src=SRC["ms_whn"])
sc(1, SN(R1(0.2), LOCK("seoul", 0.3, "서울")), clock="07:00")
sc(1, SN(R1(0), unit("seoul", "그라우든 특수임무부대", "blue", 0.2, True)), src=SRC["moss"])
sc(1, SN(*RIV(0), blue_a(ROUTE1[:5], 0.1, 1.2), badge("seoul", "망치의 머리", "#111", 0.4, -60)))
sc(1, SN(R1(0.1), mark("seoul", "blue", 0), mark("munsan", "blue", 0.6), unit("munsan", "제187공수연대", "blue", 0.7)))
sc(1, SN(R1(0), unit("seoul", "미 제6전차대대 · M46", "blue", 0.2)), src=SRC["moss"])
sc(1, phl("tiger", "1951. 3. 7", "호랑이 얼굴을 그린 제6전차대대 M46 · 양평"), src=SRC["photo"])
sc(1, phl("tiger2", "1951. 3", "호랑이 도색을 한 제6전차대대 M46 전차들"), src=SRC["photo"])
sc(1, checklist("그라우든 특수임무부대", [{"text": "M46 전차 대대", "at": 0}, {"text": "보병 대대", "on": "보병"}, {"text": "포병", "on": "포병"}, {"text": "공병", "on": "공병이"}]), src=SRC["moss"])
sc(1, phl("glosters", "1951. 3", "고지 공격에 나선 영국군 전차와 글로스터 대대"), src=SRC["moss"])
sc(1, {"type": "weapon", "bg": "blueprint", "units": [{"kind": "tank", "x": 0.5, "y": 0.62, "w": 760, "label": "처칠 교량전차", "sub": "스스로 다리를 놓는 전차"}], "title": "영국군 교량전차 2대"})
sc(1, RT(R1(0), mark("changneung", "blue", 0.2), badge("changneung", "끊어진 개울", "#111", 0.3, -60)))
sc(1, SN(R1(0.1), mark("seoul", "blue", 0), mark("munsan", "blue", 0)), hook={"hud": [HUD("약 40km", "서울 → 문산", "1번 국도", on="사십")]}, src=SRC["rng"])
sc(1, SN(R1(0), blue_a(ROUTE1, 0.2, 1.1)))
sc(1, SN(R1(0), line(FRONT, 0, "#ff6a5a"), blue_a(ROUTE1[:4], 0.2, 1.2), unit([126.86, 37.68], "국군 제1사단", "blue", 0.3)), clock="07:00 직후", src=SRC["moss"])
next_act()

# ===== 제4막 오전 아홉 시 문산 상공 =====
sc(1, SO(plane(FLIGHT, 8, 5.0, 0.1), mark("munsan", "blue", 0.4)), chapter={"num": "제4막", "title": "오전 9시 문산 상공"}, legend=LEG_A, hook={"hud": [HUD("약 2시간", "대구 → 문산 비행", on="두 시간")]})
sc(1, MU(plane([[126.9, 37.78], [126.81, 37.87]], 6, 2.5, 0.1), LOCK("dzn", 0.5)), clock="09:00", sfx=SW(0.1), src=SRC["ms_us"])
sc(1, MU(*DZ(0.2)))
sc(1, MU(*DZ(0), mark("munsan", "blue", 0), badge("dzn", "북동쪽", "#111", on="북동쪽"), badge("dzs", "남동쪽", "#111", on="남동쪽")), src=SRC["moss"])
sc(1, AI("sky_chutes", kb="out", title="북쪽 강하지점", date="1951. 3. 23 · 09:00"), label=DRAMA)
sc(1, MU(*DZ(0), unit("dzn", "제3대대 · 제4레인저중대", "blue", 0.2, True)), src=SRC["moss"])
sc(1, black("그런데"))
sc(1, SO(plane(RETURN, 1, 3.0, 0.1), badge("turn", "엔진 고장", RED, 0.3, -60), mark("taegu", "blue", 0)), src=SRC["moss"])
sc(1, SO(plane(RETURN, 1, 3.0, 0), badge("turn", "제1대대장 탑승기", "#111", 0.2, -60)), src=SRC["moss"])
sc(1, MU(plane(WRONG, 5, 3.0, 0.1), *DZ(0)), src=SRC["moss"])
sc(1, MU(*DZ(0), blue_a([[126.84, 37.83], [126.81, 37.866]], 0.2), unit("dzn", "제1대대", "blue", 0.5)), stamp={"text": "오강하", "on": "북쪽", "x": 0.5, "y": 0.42}, src=SRC["ms_whn"])
sc(1, MU(*DZ(0), unit("dzn", "제1·제3대대", "blue", 0, True), badge("dzn", "포화", RED, 0.3, -70)), clip=clip("공수연대 장교 회고 (요지)", "북쪽 강하지점은 처음엔\n1대대의 [[잘못된 강하]]로 사람이 넘쳤다", at=0.3), src=SRC["whn"])
sc(1, phl("c46_jump", "1951", "C-46에서 뛰어내리는 제187공수연대전투단"), src=SRC["moss"])
sc(1, MU(*DZ(0)), hook={"hud": [HUD("약 50분", "전체 강하 시간", on="오십")]}, src=SRC["rng"])
sc(1, phl("c119_heavy", "1952", "중장비를 떨어뜨리는 C-119 편대"), clock="10:00", src=SRC["moss"])
sc(1, phl("howitzer105", "1950. 8", "105mm 곡사포"))
sc(1, punch("실전 첫 공수 대포", "105mm 곡사포"), src=SRC["wiki"])
sc(1, AI("l19_field", title="들판에 내린 작은 연락기", date="1951. 3. 23"), label=DRAMA, src=SRC["moss"])
sc(1, phl("ridgway_jan", "1951", "리지웨이 사령관 (가운데)"), src=SRC["moss"])
sc(1, MU(*DZ(0), mark("dzs", "blue", 0.2)), clock="10:00 무렵", src=SRC["moss"])
sc(1, MU(plane(LONE, 1, 3.0, 0.1), ring("dzs", 1.1, "남쪽 강하지점", WHT, 0)), src=SRC["moss"])
sc(1, SO(plane(FLIGHT, 1, 3.0, 0.1), badge("taegu", "갈아탄 비행기", "#111", 0.3, -60)), src=SRC["moss"])
sc(1, MU(ring("dzs", 1.1, "남쪽 강하지점", WHT, 0), unit("dzs", "제1대대장 일행", "blue", 0.2, True), badge("dzs", "홀로", RED, 0.4, -70)))
sc(1, MU(red_a([[126.848, 37.826], [126.834, 37.834]], 0.2), LOCK("h216", 0.3, "216고지 · 위치 개략", RED), clash("dzs", 0.5)), sfx=FAR(0.2), src=SRC["moss"])
sc(1, MU(ring("dzs", 1.1, "남쪽 강하지점", WHT, 0), mark("h216", "red", 0), badge("dzs", "적의 눈앞", RED, 0.3, -70)))
sc(1, MU(clash("dzs", 0), unit("dzs", "고립", "blue", 0, True)))
sc(1, MU(blue_a([[126.81, 37.866], [126.84, 37.83]], 0.2, 1.1), mark("h216", "blue", 0.5), clash("h216", 0.4)), clock="15:00", src=SRC["moss"])
sc(1, MU(*DZ(0), clash("h151", 0.3, 0.8)))
sc(1, MU(ring("dzn", 1.1, "북쪽 강하지점", WHT, 0), mark([126.812, 37.878], "red", 0.2, "기관총"), mark([126.8, 37.88], "red", 0.3, "기관총")), src=SRC["rng"])
sc(1, AI("bayonet_hill", title="총검을 꽂고 언덕으로", date="1951. 3. 23"), label=DRAMA, src=SRC["rng"])
sc(1, MU(clash([126.812, 37.878], 0.2, 0.8), badge([126.812, 37.878], "사살 2 · 포로 2", "#111", 0.5, -60)), src=SRC["rng"])
sc(1, phl("pow_interrog", "1950. 9. 18", "북한군 포로 심문 (참고)"))
sc(1, MU(LOCK("h151", 0.3, "151고지 · 위치 개략"), mark("h151", "blue", 0.5)), src=SRC["rng"])
sc(1, phl("f51", "1950", "미 공군 F-51 무스탕"), src=SRC["rng"])
sc(1, MU(LOCK("h205", 0.3, "205고지 · 위치 개략", RED), line(IMJIN, 0, CYA), mark("ford", "red", 0.4)), src=SRC["whn"])
sc(1, MU(shock([[126.785, 37.9], [126.798, 37.893]], 0.2), badge("h205", "빗나간 공습", RED, 0.4, -60)), src=SRC["whn"])
sc(1, MU(blue_a([[126.793, 37.892], [126.8, 37.878]], 0.2), badge("h205", "부상 13명", RED, 0.4, -60)), src=SRC["whn"])
sc(1, MU(mark("h205", "blue", 0.3), badge("h205", "빈 고지", "#111", 0.5, -60)), date="1951. 3. 24", clock="새벽", src=SRC["whn"])
sc(1, MU(dash_r([[126.792, 37.896], [126.78, 37.92]], 0.2), line(IMJIN, 0, CYA)), tone="night")
sc(1, AI("dz_landing", kb="out", title="강하 부상", sub="재연"), label=DRAMA)
sc(1, MU(*DZ(0)), hook={"hud": [HUD("84명", "강하 부상", "절반가량은 치료 뒤 복귀", color="#FF3B3B", on="팔십사")]}, src=SRC["moss"])
sc(1, MU(*DZ(0), mark("munsan", "blue", 0.2), mark("h151", "blue", 0.3), mark("h216", "blue", 0.4)), clock="12:00 무렵", src=SRC["whn"])
sc(1, MU(*DZ(0), badge("munsan", "모루", "#111", on="모루")))
sc(1, MU(*DZ(0), badge("ford", "쇠는?", RED, 0.3, -60)))
sc(1, SN(R1(0), blue_a(ROUTE1[:4], 0.2), badge("sinwon", "망치는?", "#111", 0.4, -60)))
next_act()

# ===== 제5막 지뢰와 맥주 깡통 =====
sc(1, RT(R1(0.1), mark("seoul", "blue", 0)), chapter={"num": "제5막", "title": "지뢰와 맥주 깡통"}, date="1951. 3. 23", legend=LEG)
sc(1, RT(R1(0), LOCK("changneung", 0.3, "창릉천 · 위치 개략")), src=SRC["moss"])
sc(1, AI("creek_tanks", title="개울을 건너는 전차", date="1951. 3. 23"), label=DRAMA)
sc(1, RT(R1(0), clash("changneung", 0.3, 0.9)), sfx=FAR(0.2), src=SRC["moss"])
sc(1, punch("지뢰"))
sc(1, AI("tank_blast", title="지뢰를 밟은 전차", date="1951. 3. 23"), label=DRAMA)
sc(1, phl("m46_haengju", "1951 무렵", "멈춰 선 M46 전차 · 행주"))
sc(1, AI("mine_probe", kb="out", title="지뢰 탐지기를 든 공병", sub="재연"), label=DRAMA)
sc(1, RT(R1(0), mark("changneung", "red", 0)), hook={"hud": [HUD("12개", "그 자리에서 더 나온 지뢰", on="열두")]}, src=SRC["moss"])
sc(1, RT(R1(0), blue_a([[126.886, 37.638], [126.872, 37.66]], 0.1)), hook={"hud": [HUD("약 1.6km", "다시 울린 탐지기", on="일점육")]}, src=SRC["moss"])
sc(1, RT(R1(0), LOCK("sinwon", 0.3, "신원리 · 위치 개략")), src=SRC["moss"])
sc(1, MU(*DZ(0), plane([[126.9, 37.78], [126.81, 37.87]], 6, 2.5, 0.1)), clock="09:00")
sc(1, SN(R1(0), mark("sinwon", "red", 0), mark("munsan", "blue", 0), dash_b([[126.872, 37.66], [126.785, 37.858]], 0.2)), hook={"hud": [HUD("약 24km", "신원리 → 문산", color="#FF3B3B", on="이십사")]}, src=SRC["moss"])
sc(1, SN(R1(0), *[mark(p, "red", 0.1 + i * 0.08) for i, p in enumerate([[126.86, 37.69], [126.84, 37.72], [126.82, 37.75], [126.81, 37.78], [126.8, 37.81]])]))
sc(1, RT(R1(0)), hook={"hud": [HUD("150개+", "진짜 지뢰", "미군 기록", color="#FF3B3B", on="백오십")]}, src=SRC["moss"])
sc(1, RT(R1(0), badge("sinwon", "부비트랩", RED, 0.3, -60)), src=SRC["moss"])
sc(1, bars("지뢰 (미군 기록)", [{"label": "진짜 지뢰", "value": 150, "display": "150개 이상", "color": "red"}, {"label": "가짜 지뢰", "value": 140, "display": "거의 같은 수", "color": "blue", "at": 0.5}]), src=SRC["moss"])
sc(1, RT(R1(0), line([[126.85, 37.7], [126.82, 37.75], [126.81, 37.77]], 0.2, "#ff6a5a")), hook={"hud": [HUD("약 8km", "깡통이 묻힌 구간", on="팔")]}, src=SRC["moss"])
sc(1, AI("cans_dug", kb="out", title="전투식량 깡통과 맥주 깡통", sub="재연"), label=DRAMA, src=SRC["moss"])
sc(1, cmp("깡통", "쇳덩이", "지뢰", "쇳덩이", "blue", "red"))
sc(1, RT(R1(0), mark("sinwon", "red", 0), badge("sinwon", "손으로 흙을", "#111", 0.3, -60)))
sc(1, RT(R1(0), badge("sinwon", "또 정지", RED, 0.3, -60)), sfx=PING(0.3))
sc(1, punch("사람 걸음보다 느린 전차"))
sc(1, RT(R1(0), blue_a(ROUTE1[3:6], 0.1, 0.8)), date="1951. 3. 23", clock="오후")
sc(1, troops(8, keep=4, keepAt=0, side="us", cols=4, title="지뢰에 잃은 M46 전차", labels=[{"x": 0.5, "y": 0.76, "text": "4대", "on": "네 대", "color": "red"}]), src=SRC["moss"])
sc(1, MU(R1(0), LOCK("munsan_s", 0.3, "문산 앞 1.6km", RED)), src=SRC["moss"])
sc(1, MU(R1(0), clash("munsan_s", 0.1), shock([[126.792, 37.845], [126.796, 37.84]], 0.3)), sfx=FAR(0.1), src=SRC["moss"])
sc(1, MU(R1(0), badge("munsan_s", "전차 2대 더", RED, 0.3, -60)), src=SRC["moss"])
sc(1, MU(R1(0), mark("munsan", "blue", 0)), clock="18:30", src=SRC["ms_us"])
sc(1, MU(R1(0), blue_a(ROUTE1[-3:], 0.1, 1.1), LOCK("munsan", 0.4, "연결")), sfx=SW(0.1), src=SRC["ms_us"])
sc(1, AI("linkup_dusk", title="전차를 맞는 공수부대", date="1951. 3. 23"), label=DRAMA)
sc(1, MU(R1(0), mark("munsan", "blue", 0)), hook={"hud": [HUD("9시간 반", "강하 → 연결", "09:00 → 18:30", on="아홉 시간")]})
sc(1, SN(R1(0), blue_a(ROUTE1, 0.1)), date="1951. 3. 24", clock="07:00", src=SRC["moss"])
sc(1, SN(R1(0), mark("munsan", "blue", 0)), hook={"hud": [HUD("약 22시간", "강하 → 꼬리 도착", on="이십이")]}, src=SRC["moss"])
sc(1, checklist("강하 조건", [{"text": "강하하는 날 날씨가 좋을 것", "at": 0, "checkOn": "아슬아슬하게"}, {"text": "24시간 안에 지상군과 연결", "at": 0, "checkOn": "지켜졌습니다"}]))
sc(1, SN(*RIV(0), radar("imjin_n", 0.3, 0.9, "red")))
next_act()

# ===== 제6막 비어 있던 덫 =====
sc(1, phl("pow_interrog", "1950. 9. 18", "북한군 포로 심문 (참고 사진)"), chapter={"num": "제6막", "title": "비어 있던 덫"}, legend=LEG)
sc(1, MU(*DZ(0), unit([126.83, 37.88], "북한군 제19사단 제36연대", "red", 0.2)), src=SRC["moss"])
sc(1, troops(30, keep=3, keepAt=0, side="nk", cols=10, title="문산 일대의 북한군", labels=[{"x": 0.5, "y": 0.76, "text": "300~500명", "on": "삼백", "color": "red"}]), src=SRC["moss"])
sc(1, SN(*RIV(0), unit([126.85, 37.78], "북한군 제1군단?", "red", 0.2)))
sc(1, SN(*RIV(0), LOCK("imjin_n", 0.3, "임진강 북쪽", RED), swarm(NK_X2, 0.1, 100, 0.03)))
sc(1, SN(*RIV(0), red_a(NK_X, 0.1, 1.2), red_a(NK_X2, 0.2, 1.2)), date="1951. 3. 22", clock="밤", tone="night", src=SRC["ms_us"])
sc(1, AI("night_crossing", title="강을 건너는 북한군", date="1951. 3. 22 밤"), label=DRAMA)
sc(1, MU(*DZ(0), unit([126.83, 37.88], "뒷부대", "red", 0.2)))
sc(1, cmp("적 사살", "136명", "포로", "149명", "red", "red"), src=SRC["ms_us"])
sc(1, MU(*DZ(0)), hook={"hud": [HUD("19명", "공수부대 전사", "강하 부상 84명 별도", color="#FF3B3B", on="열아홉")]}, src=SRC["ms_us"])
sc(1, MU(*DZ(0)), clip=clip("미 태평양육군 「토마호크 작전」 (요지)", "전사 [[19명]] · 부상 수십 명\n적 사살 136 · 포로 149", at=0.2), src=SRC["ms_us"])
sc(1, cmp("떨어뜨린 병력", "3,437명", "첫날 전과", "285명", "blue", "red"))
sc(1, phl("ridgway", "1951", "덫을 포기하지 않은 리지웨이"))
sc(1, EA(blue_a(EASTMV, 0.2, 1.2), mark("munsan", "blue", 0)))
sc(1, EA(line(R33, 0.1, YEL), LOCK("uijeongbu", 0.4, "의정부")))
sc(1, EA(line(R33, 0, YEL), badge("r33", "33번 도로", "#111", 0.3, -60)), src=SRC["moss"])
sc(1, EA(line(R33, 0, YEL), unit("r33", "중공군", "red", 0.2), blue_a([[127.05, 37.66], [127.05, 37.72]], 0.3), unit([127.05, 37.66], "미 제3사단", "blue", 0.4)), src=SRC["moss"])
sc(1, EA(line(R33, 0, YEL), blue_a(EASTMV, 0.1), ring("r33", 3.0, "덫 2", WHT, 0.4)))
sc(1, EA(blue_a(EASTMV, 0.1, 1.1)), date="1951. 3. 24", clock="저녁", src=SRC["whn"])
sc(1, black("하늘이", "도와주지 않았다"))
sc(1, AI("rain_mud", title="비 내리는 흙길", date="1951. 3. 25"), label=DRAMA, sfx=WATER(0), src=SRC["moss"])
sc(1, EA(blue_a(EASTMV, 0), badge("parun", "장대비", "#111", 0.3, -60)))
sc(1, AI("stuck_truck", title="진흙에 빠진 트럭", sub="재연"), label=DRAMA)
sc(1, EA(blue_a(EASTMV[:3], 0), badge([126.94, 37.82], "젖은 총", RED, 0.3, -60)), src=SRC["whn"])
sc(1, EA(blue_a(EASTMV[:4], 0), clash("parun", 0.3)), date="1951. 3. 25", clock="13:00", sfx=FAR(0.2), src=SRC["whn"])
sc(1, AI("mg_hold", title="끝까지 자리를 지킨 기관총 사수", sub="재연"), label=DRAMA, src=SRC["whn"])
sc(1, EA(clash("parun", 0)), hook={"hud": [HUD("약 45분", "치명상 뒤에도 사격", on="사십오")]}, src=SRC["whn"])
sc(1, EA(clash("parun", 0), badge("parun", "다른 기관총조 엄호", "#111", 0.3, -60)), src=SRC["whn"])
sc(1, text("미 육군 수훈십자훈장", "yellow", "두 기관총 사수 · 사후 수여"), src=SRC["whn"])
sc(1, EA(blue_a(EASTMV[:4], 0), line(R33, 0, YEL), dash_b([[126.965, 37.812], [127.055, 37.83]], 0.2)), hook={"hud": [HUD("약 5km", "의정부 길까지", "3. 26 밤", on="오")]}, src=SRC["whn"])
sc(1, EA(LOCK("h228", 0.3, "228고지 · 위치 개략", RED)), src=SRC["moss"])
sc(1, EA(mark("h228", "red", 0), unit("h228", "중공군 약 400명", "red", 0.2)), src=SRC["whn"])
sc(1, AI("hill228_rain", title="빗속의 228고지", date="1951. 3. 26"), label=DRAMA, src=SRC["whn"])
sc(1, phl("c119_heavy", "1952", "보급 꾸러미를 떨어뜨리는 C-119"), src=SRC["whn"])
sc(1, EA(blue_a([[126.98, 37.79], [127.0, 37.8]], 0.2, 1.1), mark("h228", "blue", 0.5)), date="1951. 3. 27", clock="09:00", src=SRC["moss"])
sc(1, EA(mark("h228", "blue", 0), blue_a([[127.0, 37.8], [127.06, 37.81]], 0.2)), date="1951. 3. 28", src=SRC["moss"])
sc(1, EA(line(R33, 0, YEL), blue_a([[127.05, 37.7], [127.055, 37.8]], 0.2), mark("r33", "blue", 0.5)), src=SRC["moss"])
sc(1, EA(line(R33, 0, YEL), ring("r33", 3.0, "덫 2", WHT, 0), badge("r33", "아무도 없다", RED, 0.3, -60)), src=SRC["moss"])
sc(1, EA(line(R33, 0, YEL), dash_r(CN_OUT, 0.2)), src=SRC["moss"])
sc(1, EA(line(R33, 0, YEL), dash_r(CN_OUT2, 0.2)), src=SRC["moss"])
sc(1, punch("덫 2번 · 2번 모두 빈 덫"))
next_act()

# ===== 제7막 덫은 왜 비어 있었나 =====
sc(1, MU(*DZ(0)), chapter={"num": "제7막", "title": "덫은 왜 비어 있었나"}, legend=LEG)
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, reasons("덫이 비어 있던 4가지 이유", [{"text": n, "later": True} for n in ["하루 늦은 덫", "지뢰와 깡통", "비와 진흙", "느린 망치"]]))
sc(1, RS(1, "하루"))
sc(1, CE(line(FRONT, 0, "#ff6a5a"), dash_r([[126.95, 37.7], [126.85, 37.93]], 0.2), mark("seoul", "blue", 0)), src=SRC["moss"])
sc(1, SO(mark("taegu", "blue", 0)), date="1951. 3. 22", clock="밤", tone="night", src=SRC["moss"])
sc(1, SN(*RIV(0), red_a(NK_X, 0.1, 1.2), red_a(NK_X2, 0.2, 1.2)), tone="night", src=SRC["usarpac"])
sc(1, AI("night_crossing", kb="out", title="덫이 놓이기 전날 밤", sub="재연"), label=DRAMA)
sc(1, RS(2, "지뢰와"))
sc(1, RT(R1(0), *[mark(p, "red", 0.1 + i * 0.08) for i, p in enumerate([[126.886, 37.638], [126.872, 37.66], [126.85, 37.7], [126.82, 37.75]])]))
sc(1, cmp("진짜 지뢰", "150개+", "가짜 깡통", "거의 같은 수", "red", "red"), src=SRC["moss"])
sc(1, RS(3, "비와"))
sc(1, EA(blue_a(EASTMV, 0), badge("parun", "장대비", "#111", 0.3, -60)))
sc(1, AI("stuck_truck", kb="out", title="진흙에 묶인 발", sub="재연"), label=DRAMA)
sc(1, RS(4, "망치가"))
sc(1, SO(plane(FLIGHT, 6, 3.0, 0.1), mark("munsan", "blue", 0.4)), hook={"hud": [HUD("2시간", "모루 · 하늘길", on="두 시간")]})
sc(1, SN(R1(0), blue_a(ROUTE1, 0.1, 0.8)), hook={"hud": [HUD("하루", "망치 · 땅길", color="#FF3B3B", on="하루")]})
sc(1, {"type": "weapon", "bg": "blueprint", "units": [{"kind": "plane", "x": 0.5, "y": 0.4, "w": 560, "label": "모루"}, {"kind": "tank", "x": 0.5, "y": 0.78, "w": 480, "label": "망치"}], "title": "같은 순간에"})
sc(1, SN(*RIV(0), blue_a(HAMMER, 0.1), mark("munsan", "blue", 0), dash_r(NK_X, 0.3)))
sc(1, punch("그 틈 · 꼬박 하루"))
sc(1, SN(*RIV(0), R1(0), dash_r(NK_X, 0.2)))
sc(1, SN(*RIV(0), dash_r(NK_X, 0), dash_r(NK_X2, 0.2), badge("imjin_n", "싸우지 않고 물러나다", RED, 0.4, -60)))
sc(1, RT(R1(0), badge("sinwon", "시간을 버는 함정", RED, 0.3, -60)))
sc(1, black("정말", "실패였을까"))
sc(1, phl("rok_march", "1950", "북쪽으로 행군하는 장병들 (참고)"))
sc(1, SN(*RIV(0), dash_r(NK_X, 0.1), dash_r(NK_X2, 0.2), badge("imjin_n", "임진강 너머로", RED, 0.4, -60)), src=SRC["moss"])
sc(1, SN(*RIV(0), line([[126.7, 37.84], [126.8, 37.88], [126.9, 37.9], [127.0, 37.93], [127.1, 37.96]], 0.2, "#5bc0ff")), date="1951. 3. 28", src=SRC["moss"])
sc(1, CE(mark("seoul", "blue", 0), ring("seoul", 25, "포격 거리", RED, 0.3)))
sc(1, MU(*DZ(0), badge("munsan", "남긴 기록", "#111", 0.3, -60)))
sc(1, MU(*DZ(0), plane([[126.9, 37.78], [126.81, 37.87]], 6, 2.5, 0.1)), stamp={"text": "마지막 공수작전", "on": "마지막", "x": 0.5, "y": 0.42}, src=SRC["wiki"])
sc(1, flat([140.0, 20.0], 95, pins=[fpin([126.8, 37.86], "문산 1951", at=0.1, color="#4fa3ff"), fpin([106.7, 11.3], "베트남 1967", on="베트남", color=RED)], title="16년 뒤"), src=SRC["wiki"])
sc(1, phl("ranger2", None, "제2레인저중대 참전 용사 대표들"), src=SRC["rng"])
sc(1, AI("medics_chutes", kb="out", title="인도 제60공정야전병원", sub="재연"), label=DRAMA, src=SRC["india"])
sc(1, text("약 20만 건의 치료", "blue", "인도 제60공정야전병원 · 1950~1954"), src=SRC["india"])
sc(1, text("랑가라지 중령", "yellow", "2020. 7 이달의 6·25전쟁영웅"), src=SRC["india"])
sc(1, flat([-60.0, 35.0], 120, pins=[fpin([-84.9, 32.36], "미국 조지아주", at=0.2, color="#4fa3ff"), fpin([126.8, 37.86], "문산", at=0.4, color="#4fa3ff")], title="공수부대 기념 공원"))
sc(1, MU(mark("munsan", "blue", 0.2), LOCK("munsan", 0.3, "문산")))
sc(1, phl("munsan_1952", "1952. 3. 15", "문산리 유엔 대표단 기지 부근 판문점 길"), src=SRC["photo"])
sc(1, SN(R1(0.1), mark("panmun", "blue", 0.4), LOCK("panmun", 0.5, "판문점")))
sc(1, AI("sky_chutes", kb="in", title="문산 하늘의 낙하산", sub="재연"), label=DRAMA)
SOMBER = nid()
sc(1, AI("helmets_row", kb="out", title="뛰어내린 용기", sub="재연"), label=DRAMA)
sc(1, MU(*DZ(0), mark("munsan", "blue", 0)))
sc(1, {"type": "endcard", "title": "문산 하늘로 뛰어내린\n모든 병사를 기억하며", "q": pin("boarding")}, tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 =====
REUSE = {"helmets_row": "ep33-seobuksan"}
TAIL = ", cinematic photorealistic reenactment, early spring 1951 Korean War, muted desaturated film color, 35mm documentary still, film grain, faces not identifiable, absolutely no flags, no banners, no text, no letters, no numbers."
GI = "American paratroopers in 1951 olive drab jump uniforms and M1 steel helmets with chin straps, no patches, no insignia, no flags"
PL = "plain unpainted silver-grey 1950 twin-boom cargo transport airplanes with absolutely no markings, no stars, no numbers, no roundels"
TK = "plain olive drab 1950 American medium tanks with absolutely no markings, no stars and no numbers"
NKS = "North Korean soldiers in plain khaki 1950 uniforms and soft field caps, no insignia, no red stars"
NEW = {
    "door_jump": "Interior view from inside the dark cargo hold of a 1950 transport airplane looking toward the wide open rear door, a line of " + GI + " stepping out one after another into bright grey sky, static lines, the brown farmland of Korea far below",
    "sky_chutes": "Morning in March 1951 over flat brown rice paddies and low bare hills near a wide river in Korea, the sky filled with hundreds of round white military parachutes with soldiers hanging under them, a line of " + PL + " flying low in the distance, seen from the ground",
    "yellow_chutes": "Many pale yellow cargo parachutes carrying olive drab equipment bundles and ammunition containers descending over brown early spring Korean rice paddies in March 1951, a few white parachutes with soldiers below, grey sky",
    "dz_landing": "A dry brown rice paddy in early spring 1951 Korea strewn with collapsed white parachutes, " + GI + " gathering their gear and running toward a low hill, a small village of thatched houses in the distance, quiet, no enemy in sight",
    "mine_probe": "Morning in March 1951 on a narrow dirt road in a Korean valley, a few soldiers in olive drab M1 steel helmets walking slowly ahead sweeping the road with long 1940s mine detectors, a line of " + TK + " waiting behind them, bare trees",
    "cans_dug": "Close-up of gloved hands carefully digging an old rusty olive drab tin ration can and a battered beer can out of the dirt of a road, a bayonet used as a probe beside them, shallow depth of field",
    "anvil": "A dark old blacksmith workshop, a glowing red-hot iron bar lying on a heavy black anvil, a large hammer raised above it in a muscular arm, sparks flying, dramatic warm light",
    "taegu_dawn": "Dawn at a 1951 Korean airfield, a long row of " + PL + " with propellers turning on a steel-plank runway, lines of " + GI + " walking toward the open rear doors under heavy packs, pale orange sky",
    "sand_table": "Close-up of hands shaping a small terrain model of hills, a river and roads from damp earth and sand on a wooden board, little sticks and strings marking routes, inside a canvas tent, warm lamp light",
    "medics_chutes": "Military medics in 1951 olive drab uniforms with maroon berets and white armbands without any symbols carrying a canvas stretcher across a brown field strewn with white parachutes, a small first aid tent, seen from far away",
    "l19_field": "A small single-engine high-wing 1950 army liaison airplane with no markings, no stars and no numbers landed on a dry brown field beside collapsed white parachutes, a few soldiers walking toward it, grey morning",
    "bayonet_hill": "A few " + GI + " charging up a small grassy hill with fixed bayonets in March 1951, smoke from a machine gun position near the top, seen from behind and far away, small figures",
    "creek_tanks": "Morning in March 1951, " + TK + " crossing a shallow rocky creek one after another on a dirt road bypass, muddy water splashing, soldiers watching from the bank, bare willows",
    "tank_blast": "A plain olive drab 1950 American medium tank with absolutely no markings, no stars and no numbers stopped on a narrow dirt road, a cloud of dirt and smoke bursting under its track from a land mine, other tanks halted behind it",
    "linkup_dusk": "Dusk on 23 March 1951 at the edge of a small Korean town, " + TK + " rolling in on a dirt road while " + GI + " wave their helmets in the air to greet them, warm last light",
    "night_crossing": "Night in March 1951, a long column of " + NKS + " wading across a wide shallow river at a ford, carrying rifles above their heads, faint moonlight on the water, seen from far away as dark silhouettes",
    "rain_mud": "Heavy driving rain in late March 1951 on a muddy Korean country road, a long line of " + GI + " in ponchos trudging through deep mud, low grey clouds over brown hills",
    "stuck_truck": "A plain olive drab 1940s army truck with no markings, no stars and no numbers stuck to its axles in deep mud on a rainy Korean country road in March 1951, soldiers in ponchos pushing it, heavy rain",
    "mg_hold": "A lone soldier in an M1 steel helmet and rain-soaked olive drab poncho firing a 1940s light machine gun from behind rocks on a rainy Korean hillside in March 1951, smoke and rain, seen from behind",
    "hill228_rain": "A steep muddy Korean hill in heavy rain in March 1951, small figures of " + GI + " climbing the slippery slope under smoke, shell bursts on the summit, grey clouds",
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

# 출처: 숫자가 들어간 문장에 src가 없으면 기본 [1, 2] (모스먼 요약 · USARPAC — research.md)
for s in S:
    if "src" not in s and any(ch.isdigit() for l in s["lines"] for ch in (l if isinstance(l, str) else l["t"])):
        s["src"] = [1, 4]

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
board = {"title": "토마호크 작전", "subtitle": "문산 공수작전 · 1951", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
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
