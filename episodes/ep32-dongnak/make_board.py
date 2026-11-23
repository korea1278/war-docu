# EP32 동락리 전투 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
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

# 자막 숫자 표기 (사용자 지시: 쇼츠·롱폼 자막 숫자는 숫자로) — 긴 것부터 (부분 문자열 겹침 주의)
# 자막 숫자 표기 (사용자 지시: 롱폼 자막 숫자는 숫자로) — 긴 것부터 (부분 문자열 겹침 주의)
SUBS = [
    ("천구백오십년 칠월 칠일", "1950년 7월 7일"), ("천구백오십년 유월 이십오일", "1950년 6월 25일"), ("천구백오십년 유월", "1950년 6월"), ("천구백오십년", "1950년"),
    ("천구백삼십일년", "1931년"), ("천구백육십삼년 십이월", "1963년 12월"), ("이천십이년", "2012년"),
    ("칠월 칠일", "7월 7일"), ("칠월 오일", "7월 5일"), ("칠월 사일", "7월 4일"), ("칠월 초", "7월 초"), ("오후 다섯 시", "오후 5시"),
    ("이천백팔십육 명", "2,186명"), ("백삼십이 명", "132명"), ("팔백여 명", "800여 명"), ("구십 명", "90명"), ("이백칠십 명", "270명"), ("여섯 명", "6명"),
    ("대전차포 한 문", "대전차포 1문"), ("차량 육십 대", "차량 60대"), ("장갑차 세 대", "장갑차 3대"), ("소총 천여 정", "소총 1,000여 정"),
    ("박격포 서른다섯 문", "박격포 35문"), ("기관총 마흔일곱 정", "기관총 47정"), ("대포 열두 문", "대포 12문"),
    ("사 킬로미터", "4km"), ("열아홉 살", "19살"), ("서른두 살", "32살"), ("열사흘", "13일"),
    ("한 개 연대", "1개 연대"), ("두 개 대대", "2개 대대"), ("한 개 대대", "1개 대대"), ("한 계급", "1계급"),
    ("이달의 육이오 전쟁영웅", "이달의 6·25 전쟁영웅"),
    ("제육사단", "제6사단"), ("제칠연대", "제7연대"), ("제일군단", "제1군단"), ("제일사단", "제1사단"), ("제십오사단", "제15사단"), ("제사십팔연대", "제48연대"),
    ("제일대대", "제1대대"), ("제이대대", "제2대대"), ("제삼대대", "제3대대"), ("제십구연대", "제19연대"), ("제십칠연대", "제17연대"),
    ("제육중대", "제6중대"), ("제칠중대", "제7중대"), ("제팔중대장", "제8중대장"), ("제팔중대", "제8중대"),
    ("삼팔선", "38선"),
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



DRAMA = "재연 일러스트"

# 좌표는 개략 (동락초등학교·무극리·기름고개·백야리·부용산 진지·310고지·용원리는 현재 지형 기준 근사 — 화면에 '위치 개략' 표기)
P = {
    "seoul": [126.978, 37.566, "서울"], "suwon": [127.03, 37.27, "수원"], "chuncheon": [127.73, 37.88, "춘천"], "hongcheon": [127.88, 37.69, "홍천"],
    "wonju": [127.92, 37.342, "원주"], "chungju": [127.926, 36.991, "충주"], "janghowon": [127.64, 37.11, "장호원"], "eumseong": [127.69, 36.94, "음성"],
    "jincheon": [127.435, 36.855, "진천"], "cheongju": [127.49, 36.64, "청주"], "daejeon": [127.385, 36.35, "대전"], "suanbo": [127.99, 36.85, "수안보"],
    "iwha": [127.995, 36.77, "이화령"], "sangju": [128.16, 36.41, "상주"], "hwaryeong": [127.988, 36.443, "화령장"], "boeun": [127.729, 36.489, "보은"],
    "daegu": [128.6, 35.87, "대구"], "busan": [129.04, 35.18, "부산"], "chosan": [125.8, 40.83, "초산"], "pyongyang": [125.75, 39.03, "평양"],
    "dongnak": [127.71, 37.0, "동락초등학교"], "mugeuk": [127.588, 36.995, "무극리"], "giryum": [127.66, 37.03, "기름고개"], "baegya": [127.6, 36.965, "백야리"],
    "buyong": [127.7, 36.972, "제2대대 진지"], "h310": [127.737, 37.008, "310고지"], "yongwon": [127.745, 36.995, "용원리"],
    "cut6": [127.703, 37.009, "제6중대"], "cut7": [127.72, 37.01, "제7중대"], "co8": [127.698, 36.98, "제8중대"],
}
V = {
    "korea": {"center": [127.4, 37.0], "span": 6.2}, "r6": {"center": [127.8, 37.45], "span": 2.4}, "corps": {"center": [127.65, 36.95], "span": 1.5},
    "front": {"center": [127.665, 36.995], "span": 0.42}, "dn": {"center": [127.708, 36.986], "span": 0.14},
    "sobaek": {"center": [127.85, 36.72], "span": 1.4}, "south": {"center": [128.35, 36.1], "span": 2.4}, "north": {"center": [126.6, 39.3], "span": 5.6},
}
L38 = {"k": "line", "path": [[124.6, 38.0], [126.5, 38.0], [128.6, 38.3]], "color": "#ffffff", "at": 0, "dash": True}
INVADE = [[[126.9, 38.2], [126.98, 37.62]], [[127.7, 38.15], [127.73, 37.9]], [[128.3, 38.1], [128.4, 37.6]]]
SOUTH_PUSH = [[126.98, 37.5], [127.03, 37.27], [127.1, 37.0]]
R6 = [[127.73, 37.88], [127.88, 37.69], [127.92, 37.36], [127.926, 37.0]]
NK15 = [[127.637, 37.3], [127.64, 37.11], [127.66, 37.03], [127.69, 36.96]]
TO_JIN = [[127.49, 36.66], [127.435, 36.85]]
TO_EUM = [[127.6, 36.75], [127.69, 36.93]]
ROAD = [[127.64, 37.11], [127.66, 37.03], [127.69, 36.94], [127.926, 36.991]]
ROAD2 = [[127.69, 36.94], [127.49, 36.64]]
MUG_ATK = [[127.63, 37.05], [127.6, 37.01]]
MUG_IN = [[127.62, 36.97], [127.588, 36.99]]
MUG_OUT = [[127.588, 36.995], [127.6, 36.967]]
B2_UP = [[127.69, 36.94], [127.7, 36.968]]
B3_BACK = [[127.69, 37.05], [127.72, 37.03], [127.737, 37.012]]
NK_FOLLOW = [[127.66, 37.05], [127.69, 37.015], [127.708, 37.002]]
WALK = [[127.71, 36.999], [127.707, 36.99], [127.703, 36.981], [127.7, 36.974]]
CUT_ROAD = [[127.71, 37.0], [127.71, 37.012], [127.712, 37.03]]
FIRE8 = [[127.699, 36.978], [127.709, 36.997]]
FIRE3 = [[127.735, 37.006], [127.713, 37.0]]
FLEE = [[127.71, 37.0], [127.71, 37.008]]
HW_ROUTE = [[127.69, 36.96], [127.786, 36.815], [127.85, 36.6], [127.925, 36.51], [127.988, 36.443]]
SIX_SOUTH = [[127.926, 36.99], [127.99, 36.85], [127.995, 36.77], [128.1, 36.6]]
CHOSAN = [[127.0, 37.5], [126.6, 38.5], [125.9, 39.6], [125.8, 40.8]]
PUSAN = [[128.37, 36.3], [128.4, 36.0], [128.42, 35.6], [128.38, 35.3], [128.25, 35.1]]
SCHOOL_FIRE = [[127.708, 37.001], [127.71, 36.999], [127.712, 37.001]]
LOCK = lambda p, at=0.3, text=None, color=None, on=None: dict({"k": "lock", "p": p, "text": text or P[p][2]}, **({"on": on} if on else {"at": at}), **({"color": color} if color else {}))
badge = lambda p, t, c="#111", at=0.3, dy=-70, on=None: dict({"k": "badge", "p": p, "text": t, "color": c, "dy": dy}, **({"on": on} if on else {"at": at}))
red_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "red", "width": w}, **({"on": on} if on else {"at": at}))
blue_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "blue", "width": w}, **({"on": on} if on else {"at": at}))
dash_r = lambda path, at=0.2: {"k": "arrow", "path": path, "color": "red", "dash": True, "at": at}
mark = lambda p, color="red", at=0, text=None, on=None: dict({"k": "marker", "p": p, "color": color}, **({"text": text} if text else {}), **({"on": on} if on else {"at": at}))
unit = lambda p, t, color="red", at=0.1, pulse=False, on=None: dict({"k": "unit", "p": p, "text": t, "color": color}, **({"on": on} if on else {"at": at}), **({"pulse": True} if pulse else {}))
clash = lambda p, at=0.3, size=1.0: {"k": "clash", "p": p, "at": at, "period": 0.9, "size": size}
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
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))

road = lambda at=0, on=None: line(ROAD, at, "#ffffff", on)
QUESTION = "연전연패하던 국군은 어떻게\n운동장의 적 1개 연대를 무너뜨렸나"
RED = "#c9242c"
DN = lambda *items, tilt=36, **kw: m("dn", "dn", [mark("dongnak", "red", 0)] + list(items), tilt=tilt, **kw)
FR = lambda *items, tilt=26, **kw: m("front", "front", [road(0)] + list(items), tilt=tilt, **kw)

# ===== 콜드 오프닝 (초반 후킹 표준: 절정 → 수치 HUD 누적 → 통념 X → 핵심 질문 카드 → 타이틀) =====
sc(1, ai("school_trucks"), label=DRAMA, hook={"hud": [HUD("1950. 7. 7", "음성과 충주 사이", "동락리 · 오후", count=False)]}, sfx=WIND(0.2))
sc(1, ai("village_school"), label=DRAMA, callouts=low("동락초등학교 · 재연"))
sc(1, ai("su76_advance"), label=DRAMA)
sc(1, ai("cook_smoke"), label=DRAMA)
sc(1, checklist("운동장의 북한군", [{"text": "총을 내려놓고", "at": 0}, {"text": "웃통을 벗고", "on": "웃통을"}, {"text": "밥을 짓고", "on": "밥을"}]))
sc(1, black("“이 근처에", "국군은 없다”"), hook={"neg": {"text": "국군은 없다", "at": 0.3}})
sc(1, ai("teacher_gate"), label=DRAMA)
sc(1, ai("mountain_path"), label=DRAMA)
sc(1, DN(line(WALK, 0.1, "#ffd400"), mark("buyong", "blue", 0.5), tilt=34, hud=True), hook={"hud": [HUD("4km", "산 위 국군 진지까지", "위치 개략", on="사 킬로미터")]}, sfx=PING(0.5))
sc(1, text("부임한 지 한 달도 안 된 선생님", "yellow", "동락초등학교"))
sc(1, text("19살", "yellow", "김재옥 선생님"), hook={"hud": [HUD("19살", "선생님의 나이", color="#FFD83A", on="열아홉")]})
sc(1, DN(shock(SCHOOL_FIRE, 0.2, 0.6), tilt=38), sfx=FAR(0.1))
sc(1, ai("schoolyard_blast"), label=DRAMA)
sc(1, black("그 저녁이 끝났을 때", "적 연대는 더 이상 연대가 아니었다"))
sc(1, text("개전 13일째", "red"), hook={"hud": [HUD("13일", "개전 이후", "1950. 6. 25 ~ 7. 7", color="#FF3B3B", on="열사흘")]})
sc(1, black("국군은", "밀리기만 했다"), hook={"neg": {"text": "밀리기만 했다", "at": 0.2, "xAt": 0.7}})
sc(1, m("korea", "korea", [L38, mark("seoul", "red", on="서울을"), mark("suwon", "red", on="수원을")]), callouts=top("서울 · 한강 · 수원 상실", "red"))
sc(1, text("국군의 첫 승전 소식", "blue", "동락리 · 1950. 7. 7"))
sc(1, black("이상하지", "않습니까"))
sc(1, cmp("국군", "병력·무기 부족", "북한군", "소련제 대포·트럭", "blue", "red"))
sc(1, ai("t34_column"), label=DRAMA)
sc(1, text("총을 쥐어 본 적도 없는 선생님", "yellow"))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, {"type": "titlecard", "title": "운동장에 모인 적 연대", "sub": "동락리 전투 · 국군 제6사단 제7연대 · 1950", "at": 0, "q": pin("rok_july")}, flash=True)
next_act()

# ===== 제1막 무너지는 전선 =====
sc(1, m("korea", "korea", [L38, red_a(INVADE[0], 0.2), red_a(INVADE[1], 0.3), red_a(INVADE[2], 0.4)]), chapter={"num": "제1막", "title": "무너지는 전선"}, callouts=top("1950. 6. 25 새벽"), sfx=FAR(0.2))
sc(1, ai("t34_column"), label=DRAMA)
sc(1, text("탱크를 막을 무기가 거의 없었다", "red"))
sc(1, m("korea", "korea", [L38, red_a(INVADE[0], 0), mark("seoul", "red", on="서울이")]), callouts=top("1950. 6. 28 · 서울 함락", "red"))
sc(1, ph("han_bridge"), label=plabel("han_bridge"))
sc(1, black("모든 전선이", "똑같이 무너진 것은 아니었다"))
sc(1, m("r6", "r6", [L38, LOCK("chuncheon", 0.3)], tilt=18, hud=True), callouts=top("동쪽 · 춘천"), sfx=PING(0.4))
sc(1, text("국군 제6사단", "blue", "춘천을 지키던 부대"))
sc(1, ai("kim_alert"), label=DRAMA, callouts=low("사단장 김종오 대령"))
sc(1, text("부임 보름 만에 터진 전쟁", "dark", "1950. 6. 10 사단장 부임"))
sc(1, ai("direct_fire"), label=DRAMA)
sc(1, m("r6", "r6", [L38, mark("chuncheon", "blue", 0), unit("chuncheon", "제7연대", "blue", on="제칠연대")], tilt=20))
sc(1, text("연대장 임부택 중령", "yellow", "국군 제7연대"))
sc(1, ai("dawn_rain"), label=DRAMA, callouts=top("1950. 6. 25 · 춘천"))
sc(1, cmp("북한군 계획", "하루", "실제", "사흘", "red", "blue"))
sc(1, text("북한군 계획 1일 → 실제 3일", "yellow", "춘천 점령까지"))
sc(1, m("korea", "korea", [L38, mark("seoul", "red", 0), mark("chuncheon", "blue", 0), line([[126.6, 37.5], [127.3, 37.4]], 0.2, "#7fd3ff")]), callouts=low("한강 남쪽에서 숨을 돌린 사흘"))
sc(1, black("버티는 것과", "이기는 것은 다르다"))
sc(1, m("r6", "r6", [L38, mark("seoul", "red", 0), blue_a(R6[:2], 0.3)], tilt=18), callouts=low("제6사단도 남쪽으로"))
sc(1, stage([C("kr_shrug", 0.5, 470, prop="officer+helmet", face="worried", anim="tilt")], [pop("label", 0.5, 0.15, "옆 부대가 무너지면…", on="무너지면", color="dark")]))
sc(1, m("r6", "r6", [L38, blue_a(R6, 0.1), mark("hongcheon", "blue", on="홍천과"), mark("wonju", "blue", on="원주를"), mark("chungju", "blue", on="충주")], tilt=18))
sc(1, m("r6", "r6", [L38, blue_a(R6, 0), swarm(R6[:3], 0.2, 120)], tilt=18), callouts=low("바짝 따라붙는 북한군", "red"))
sc(1, text("7월 초 · 큰 결심", "yellow"))
sc(1, text("흩어진 부대로 군단을 새로", "blue"))
sc(1, doc("제1군단 명령 (요지)", ["1950. 7. 4 · 군단장 김홍일 소장", "부대를 다시 짜 북한군을 막는다"], "命令", "국군 제1군단", "1950. 7. 4 · 재구성"))
sc(1, m("corps", "corps", [blue_a(TO_JIN, 0.2), mark("jincheon", "blue", 0.4)], tilt=16), callouts=top("수도사단 → 진천"))
sc(1, m("corps", "corps", [mark("jincheon", "blue", 0), blue_a(TO_EUM, 0.2), mark("eumseong", "blue", 0.4)], tilt=16), callouts=top("제1사단 → 음성"))
sc(1, m("corps", "corps", [mark("jincheon", "blue", 0), mark("eumseong", "blue", 0), unit("janghowon", "제6사단 연대들", "blue", 0.3)], tilt=16), callouts=low("앞에서 적을 막는 엄호 부대"))
sc(1, m("front", "front", [road(0.1), unit("giryum", "제7연대", "blue", 0.3)], tilt=24), callouts=top("음성 북쪽 · 위치 개략"))
sc(1, m("corps", "corps", [line(ROAD, 0.1, "#ffd400"), line(ROAD2, 0.4, "#ffd400"), mark("chungju", "blue", on="충주와"), mark("cheongju", "blue", on="청주로")], tilt=16), callouts=low("장호원 – 음성 – 충주·청주"))
sc(1, m("corps", "corps", [line(ROAD, 0, "#ffd400"), dash_r(NK15, 0.2), badge("eumseong", "충청도의 문", RED, 0.4, -60)], tilt=18))
sc(1, text("북한군 제15사단", "red", "음성으로 내려오던 적"))
sc(1, text("사단장 박성철 소장", "red", "북한군 제15사단"))
sc(1, m("corps", "corps", [mark("janghowon", "red", 0.1), red_a(NK15, 0.3)], tilt=18), callouts=top("장호원 점령 → 음성으로", "red"))
sc(1, text("선두 · 제48연대", "red", "북한군 제15사단"))
sc(1, text("대포와 트럭을 앞세운 연대", "red"))
sc(1, ph("rok_march_aug"), label=plabel("rok_march_aug"))
sc(1, m("r6", "r6", [blue_a(R6, 0.1)], tilt=18), callouts=low("춘천에서부터 열흘 넘게"))
sc(1, ph("rok_cook"), label=plabel("rok_cook"))
sc(1, black("그래도 이 부대에는", "한 가지가 남아 있었다"))
sc(1, text("춘천에서 적을 막아 본 경험", "blue"))
sc(1, text("“우리도 버틸 수 있다”", "yellow", "제7연대 병사들의 감각"))
sc(1, ai("withdraw"), label=DRAMA, sfx=WIND(0))
next_act()

# ===== 제2막 무극리의 첫 충돌 =====
sc(1, FR(mark("giryum", "red", 0.3), mark("dongnak", "red", 0.5)), chapter={"num": "제2막", "title": "무극리의 첫 충돌"}, callouts=top("1950. 7. 5 · 기름고개·동락리"))
sc(1, ai("misty_ridge"), label=DRAMA)
sc(1, text("상대가 어디까지 왔는지 모른다", "dark"))
sc(1, text("안개 속에서 손을 더듬는 싸움", "dark"))
sc(1, FR(blue_a(MUG_IN, 0.2), LOCK("mugeuk", 0.5)), callouts=top("제1대대 · 무극리 점령"), sfx=PING(0.6))
sc(1, ai("market_village"), label=DRAMA, callouts=low("무극리 · 장터 마을"))
sc(1, FR(unit("mugeuk", "제1대대", "blue", 0.2)))
sc(1, bars("무극리 전투 · 국군 기록", [{"label": "적 사살", "value": 270, "display": "270명", "color": "red", "on": "이백칠십"}]))
sc(1, checklist("무극리 전과", [{"text": "포로 6명", "on": "포로"}, {"text": "대전차포 1문 노획", "on": "대전차포"}]))
sc(1, black("하지만 기쁨은", "오래가지 않았다"))
sc(1, FR(unit("mugeuk", "제1대대", "blue", 0), red_a(MUG_ATK, 0.2, 1.2), shock([[127.59, 36.995], [127.585, 36.99]], 0.3)), sfx=FAR(0.2))
sc(1, cmp("국군 대포", "거의 없음", "북한군 대포", "포격 지원", "blue", "red"))
sc(1, FR(blue_a(MUG_OUT, 0.2), mark("baegya", "blue", 0.5)), callouts=low("무극리 → 백야리 · 위치 개략"))
sc(1, stage([C("kr_point", 0.5, 480, prop="officer+helmet", face="determined", anim="tilt")], [pop("label", 0.5, 0.15, "연대장 임부택 중령", on="임부택", color="dark")]))
sc(1, FR(mark("eumseong", "blue", 0), red_a([[127.6, 36.97], [127.67, 36.945]], 0.2)), callouts=low("밀리면 음성이 위험", "red"))
sc(1, text("예비대 · 제2대대", "blue", "아껴 두었던 마지막 카드"))
sc(1, FR(blue_a(B2_UP, 0.2), unit("buyong", "제2대대", "blue", 0.5)), callouts=top("동락리 남쪽 산 · 위치 개략"))
sc(1, text("가운데를 단단히", "blue"))
sc(1, FR(unit("baegya", "제1대대", "blue", 0.1), unit([127.61, 36.955], "제19연대 제2대대", "blue", 0.4)))
sc(1, FR(unit("baegya", "2개 대대", "blue", 0.1), line([[127.59, 36.975], [127.615, 36.96]], 0.3, "#7fd3ff")), callouts=low("백야리 · 어깨를 맞대고"))
sc(1, text("제2대대장 김종수 소령", "yellow", "국군 제7연대"))
sc(1, ai("op_post"), label=DRAMA)
sc(1, DN(mark("buyong", "blue", 0), tilt=40), callouts=low("산 아래 들판과 마을"))
sc(1, DN(mark("buyong", "blue", 0), LOCK("dongnak", 0.3), tilt=40, hud=True), callouts=top("동락 마을 · 초등학교"), sfx=PING(0.4))
sc(1, FR(blue_a(B3_BACK, 0.2)), callouts=low("앞쪽에서 물러나던 제3대대"))
sc(1, black("그런데", "뒤따라오던 적이 이상했다"))
sc(1, FR(blue_a(B3_BACK, 0), dash_r(NK_FOLLOW, 0.2)), callouts=low("제48연대 정찰대 · 남쪽으로", "red"))
sc(1, checklist("북한군의 이상한 모습", [{"text": "싸울 대형 없음", "on": "대형을"}]))
sc(1, checklist("북한군의 이상한 모습", [{"text": "싸울 대형 없음", "at": 0}, {"text": "허술한 경계", "on": "경계도"}]))
sc(1, stage([C("nk_idle", 0.5, 470, prop="nkcap", face="smug", anim="bounce")], [pop("label", 0.5, 0.15, "“패잔병일 뿐이야”", on="패잔병일", color="red")]))
sc(1, text("열흘 넘게 이기기만 한 군대", "red"))
sc(1, text("이긴 군대는 쉽게 방심한다", "yellow"))
sc(1, stage([C("kr_salute", 0.45, 470, prop="helmet+notebook", face="determined", flip=True)], [pop("label", 0.5, 0.15, "정찰 보고", on="보고를", color="dark")]))
sc(1, FR(blue_a(B3_BACK, 0.1), unit("h310", "제3대대", "blue", 0.5)), callouts=top("310고지 부근 · 위치 개략"))
sc(1, ai("crest_wait"), label=DRAMA)
sc(1, DN(unit("buyong", "제2대대", "blue", 0.1), unit("h310", "제3대대", "blue", 0.3), tilt=36))
sc(1, DN(unit("buyong", "국군", "blue", 0), unit("h310", "국군", "blue", 0), badge("dongnak", "“국군은 다 떠났다”", RED, 0.3, -60), tilt=36))
sc(1, black("하지만 산 위의 국군도", "한 가지를 몰랐다"))
sc(1, stage([C("kr_shrug", 0.5, 470, prop="officer", face="worried+sweat")], [pop("q", 0.3, 0.3, on="어디에"), pop("q", 0.7, 0.3, on="얼마나")]))
sc(1, black("그 답을 가져다줄 사람은", "군인이 아니었다"), sfx=WIND(0))
next_act()

# ===== 제3막 열아홉 살 선생님 =====
MID = [nid()]
sc(1, ai("teacher_portrait"), label=DRAMA, pauseBefore=0.5, chapter={"num": "제3막", "title": "열아홉 살 선생님"}, callouts=top("김재옥 선생님"))
sc(1, text("1931년생 · 19살", "yellow", "김재옥"))
sc(1, text("충주사범학교 강습과", "dark", "갓 선생님이 된 새내기"))
sc(1, text("1950년 6월 · 동락초등학교 부임", "blue"))
sc(1, text("전쟁 닷새 전", "red", "부임 시기 · 전해지는 기록"))
sc(1, ai("classroom_1950"), label=DRAMA)
sc(1, black("그리고 전쟁이", "마을까지 내려왔다"))
sc(1, DN(swarm(NK_FOLLOW, 0.1, 100, 0.2), unit("dongnak", "제48연대", "red", 0.5, True), tilt=38), callouts=top("1950. 7. 7 · 동락초등학교"))
sc(1, ai("school_trucks"), label=DRAMA, kb="out")
sc(1, text("교실 = 적의 숙소", "red"))
sc(1, checklist("운동장 한가운데", [{"text": "포진지", "on": "포진지가"}, {"text": "쌓인 탄약", "on": "탄약이"}]))
sc(1, stage([C("nk_point", 0.6, 480, prop="officer", face="smug", flip=True)], [pop("label", 0.5, 0.15, "북한군 장교", on="장교들은", color="red")]))
sc(1, stage([C("nk_shrug", 0.5, 470, prop="nkcap", face="angry")], [pop("bubble", 0.5, 0.2, "국군은 어디 있나?", on="어디")]))
sc(1, stage([C("nk_idle", 0.45, 470, prop="officer+glasses", face="angry", anim="tilt")], [pop("bubble", 0.55, 0.2, "군인이 남아 있나?", on="남아")]))
sc(1, text("그 자리에서 내린 결심", "yellow"))
sc(1, text("“국군에게 알려야 한다”", "yellow"))
sc(1, black("그것은", "목숨을 거는 일"))
sc(1, text("들키면 그 자리에서 총살", "red"))
sc(1, ai("teacher_gate"), label=DRAMA, kb="out")
sc(1, text("농사꾼 옷으로 변장", "dark"))
sc(1, ai("mountain_path"), label=DRAMA, kb="out")
sc(1, DN(line(WALK, 0.1, "#ffd400"), mark("buyong", "blue", 0.6), tilt=34), callouts=low("4km가 넘는 산길 · 위치 개략"))
sc(1, ai("summer_heat"), label=DRAMA)
sc(1, stage([C("kr_shock", 0.3, 400, prop="helmet", face="shock"), C("nk_shock", 0.7, 400, prop="nkcap", face="worried", flip=True)], [pop("q", 0.5, 0.25, on="아무도")]))
sc(1, text("어느 쪽 총에 맞아도 이상하지 않은 길", "red"))
sc(1, text("혼자 걸은 길", "yellow"))
sc(1, ai("ridge_meet"), label=DRAMA)
sc(1, stage([C("kr_point", 0.55, 470, prop="helmet", face="worried", anim="shake")], [pop("label", 0.5, 0.15, "첩자일지도…", on="의심했습니다", color="dark")]))
sc(1, text("낯선 민간인 = 적의 첩자?", "dark"))
sc(1, text("제2대대장 김종수 소령 앞으로", "blue"))
sc(1, text("하나하나 털어놓은 것", "yellow"))
sc(1, checklist("선생님이 본 것", [{"text": "학교에 모인 적의 규모", "on": "얼마나"}]))
sc(1, checklist("선생님이 본 것", [{"text": "학교에 모인 적의 규모", "at": 0}, {"text": "대포와 트럭의 위치", "on": "대포와"}]))
sc(1, checklist("선생님이 본 것", [{"text": "학교에 모인 적의 규모", "at": 0}, {"text": "대포와 트럭의 위치", "at": 0}, {"text": "쉬고 있는 병사들", "on": "쉬고"}]))
sc(1, doc("제보 요지 (재구성)", ["적 제15사단 제48연대 주력", "포병대 · 운동장 포진지"], "諜報", "국군 제7연대 제2대대", "1950. 7. 7 · 재구성"))
sc(1, DN(unit("dongnak", "제48연대·포병대", "red", 0.2, True), LOCK("dongnak", 0.5, "적 배치 확인", RED), tilt=38, hud=True), sfx=PING(0.5))
sc(1, ai("binocular_view"), label=DRAMA)
sc(1, ai("school_trucks"), label=DRAMA, kb="in")
sc(1, text("보이지 않는 경계병", "red"))
sc(1, text("다시 오기 힘든 기회", "yellow", "김종수 소령의 판단"))
sc(1, black("그때 선생님이", "한 가지를 더 해냈다"))
sc(1, text("“학교로 돌아가겠습니다”", "yellow"), sfx=WIND(0), hudCta={"at": 0, "dur": 7.0})
next_act()

# ===== 제4막 거짓말 한마디 =====
sc(1, black("왜", "돌아가야 했을까"), chapter={"num": "제4막", "title": "거짓말 한마디"})
sc(1, text("오래 안 보이면 의심받는다", "red"))
sc(1, text("사라진 선생님 = 다시 서는 경계", "dark"))
sc(1, DN(line(list(reversed(WALK)), 0.1, "#ffd400"), tilt=34), callouts=low("다시 4km 산길"))
sc(1, ai("teacher_return"), label=DRAMA)
sc(1, stage([C("nk_point", 0.55, 480, prop="nkcap", face="angry", anim="bounce")], [pop("label", 0.5, 0.15, "다시 묻는 북한군", on="물었습니다", color="red")]))
sc(1, text("“국군은 어디 있느냐”", "red"))
sc(1, text("그녀의 대답", "yellow", "전해지는 이야기"))
sc(1, text("“국군은 차를 타고 다 도망갔어요”", "yellow"))
sc(1, stage([C("nk_idle", 0.5, 470, prop="officer", face="smug+blush", anim="tilt")], [pop("label", 0.5, 0.15, "안심한 적", on="놓게", color="red")]))
sc(1, text("이미 믿고 있던 것", "red", "“국군은 쫓겨 가는 중”"))
sc(1, text("그 믿음에 찍힌 도장", "yellow"))
sc(1, black("사람은 듣고 싶은 말을 들으면", "의심하지 않는다"))
sc(1, DN(unit("dongnak", "경계 해제", "red", 0.2), tilt=38))
sc(1, checklist("운동장의 저녁", [{"text": "줄어든 보초", "on": "보초는"}, {"text": "더 편하게 쉬는 병사들", "on": "편하게"}]))
sc(1, ai("ridge_prep"), label=DRAMA)
sc(1, text("대대를 나누다", "blue", "김종수 소령"))
sc(1, DN(line(CUT_ROAD, 0.1, "#ffffff"), unit("cut6", "제6중대", "blue", on="제육중대와"), unit("cut7", "제7중대", "blue", on="제칠중대는"), tilt=36), callouts=low("도망칠 길을 막아라"))
sc(1, DN(line(CUT_ROAD, 0, "#ffffff"), unit("cut6", "제6중대", "blue", 0), unit("cut7", "제7중대", "blue", 0), LOCK([127.711, 37.01], 0.3, "퇴로 차단"), tilt=36))
sc(1, DN(unit("cut6", "제6중대", "blue", 0), unit("cut7", "제7중대", "blue", 0), unit("co8", "공격 중대", "blue", 0.3), tilt=36))
sc(1, text("제8중대장 신용관 중위", "yellow", "훗날 예비역 준장"))
sc(1, ph("rok_mortar"), label=plabel("rok_mortar"))
sc(1, DN(unit("co8", "제8중대", "blue", 0), LOCK("dongnak", 0.3, "운동장 한가운데", RED), tilt=40, hud=True), sfx=PING(0.4))
sc(1, checklist("첫 표적", [{"text": "적의 대포", "on": "대포와"}, {"text": "쌓아 둔 탄약", "on": "탄약이"}]))
sc(1, stage([C("kr_salute", 0.5, 470, prop="officer+helmet", face="determined", anim="bounce")], [pop("label", 0.5, 0.15, "연대에 보고", on="올라갔습니다", color="dark")]))
sc(1, DN(unit("h310", "제3대대", "blue", 0.2), tilt=36), callouts=top("제3대대 · 공격 준비 완료"))
sc(1, DN(unit("buyong", "제2대대", "blue", 0), unit("h310", "제3대대", "blue", 0), blue_a([[127.735, 37.006], [127.714, 37.0]], 0.2), blue_a([[127.7, 36.974], [127.708, 36.996]], 0.3), tilt=36))
sc(1, ai("trench_wait"), label=DRAMA)
sc(1, text("열흘 넘게 물러서기만 했다", "dark"))
sc(1, text("“이번만은 다르다”", "yellow"))
sc(1, black("실수 한 번이면", "모든 것이 끝"))
sc(1, text("성급한 한 발 = 흩어지는 적 · 반격", "red"))
sc(1, cmp("국군 대포", "적다", "적의 대포", "훨씬 많다", "blue", "red"))
sc(1, text("기습이 실패하면 · 대포가 산 위로", "red"))
sc(1, text("흐르는 시간", "dark"))
sc(1, ai("dusk_sun"), label=DRAMA)
sc(1, ai("cook_smoke"), label=DRAMA, kb="out")
sc(1, ai("valley_dusk_trucks"), label=DRAMA)
sc(1, black("그리고", "명령이 떨어졌다"), sfx=WIND(0))
next_act()

# ===== 제5막 운동장의 저녁 =====
MID.append(nid())
sc(1, DN(unit("co8", "제8중대", "blue", 0), tilt=38), pauseBefore=0.5, chapter={"num": "제5막", "title": "운동장의 저녁"}, callouts=top("오후 5시 무렵 · 전해지는 기록"))
sc(1, DN(blue_a(FIRE8, 0.1), shock([[127.709, 36.998]], 0.4, 0.7), tilt=40), sfx=FAR(0.2))
sc(1, text("제8중대의 박격포", "blue"))
sc(1, DN(blue_a(FIRE8, 0), shock(SCHOOL_FIRE, 0.1, 0.6), LOCK("dongnak", 0.3, "포진지 명중", RED), tilt=40, hud=True))
sc(1, ai("schoolyard_blast"), label=DRAMA)
sc(1, DN(shock(SCHOOL_FIRE, 0, 0.45), clash("dongnak", 0.2, 1.2), tilt=40), sfx=FAR(0.1))
sc(1, text("자랑하던 대포가 · 적을 덮치는 불길로", "red"))
sc(1, stage([C("nk_shock", 0.5, 480, prop="nkcap", face="shock+sweat", anim="shake")], [pop("ex", 0.75, 0.25, on="알 수"), pop("q", 0.25, 0.3, on="무슨")]))
sc(1, text("“국군은 다 도망갔다”더니", "red"))
sc(1, DN(blue_a(FIRE8, 0), blue_a(FIRE3, 0.2), shock(SCHOOL_FIRE, 0, 0.5), tilt=38))
sc(1, ph("dshk", marks=[{"text": "기관총", "x": 0.5, "y": 0.2, "on": "기관총이", "color": "red"}]), label=plabel("dshk"))
sc(1, text("총을 찾을 겨를도 없었다", "red"))
sc(1, ai("panic_yard"), label=DRAMA)
sc(1, checklist("버리고 간 것", [{"text": "트럭", "on": "트럭도"}, {"text": "대포", "on": "대포도"}]))
sc(1, DN(red_a(FLEE, 0.2), tilt=38), callouts=low("북쪽으로 달아나는 적", "red"))
sc(1, DN(red_a(FLEE, 0), unit("cut6", "제6중대", "blue", 0.1), unit("cut7", "제7중대", "blue", 0.2), LOCK([127.711, 37.01], 0.4, "퇴로 차단"), tilt=38))
sc(1, DN(unit("cut6", "제6중대", "blue", 0), unit("cut7", "제7중대", "blue", 0), clash([127.711, 37.009], 0.2), tilt=38))
sc(1, ph("pow_interrog"), label=plabel("pow_interrog"))
sc(1, DN(blue_a(FIRE3, 0.1, 1.2), unit("h310", "제3대대", "blue", 0), tilt=38))
sc(1, DN(blue_a(FIRE8, 0.1), blue_a(FIRE3, 0.1), clash("dongnak", 0.3, 1.3), tilt=40))
sc(1, ai("abandoned_guns"), label=DRAMA)
sc(1, ph("captured_equip"), label=plabel("captured_equip"), callouts=top("박격포·기관총·탄약 그대로"))
sc(1, text("내릴 시간조차 없었다", "red"))
sc(1, ai("valley_quiet"), label=DRAMA)
sc(1, ai("dawn_victory"), label=DRAMA)
sc(1, text("개전 이후 처음 보는 광경", "yellow"))
sc(1, ai("abandoned_guns"), label=DRAMA, kb="out")
sc(1, text("운동장을 메운 적의 트럭", "dark"))
sc(1, black("쫓기기만 하던 국군이", "처음으로 적을 쫓아낸 저녁"))
sc(1, black("하지만 싸움은", "아직 끝나지 않았다"))
sc(1, DN(swarm([[127.69, 37.04], [127.705, 37.012]], 0.1, 80, 0.2), red_a([[127.69, 37.04], [127.705, 37.012]], 0.3), tilt=36), callouts=low("흩어졌던 적의 반격", "red"))
sc(1, DN(blue_a([[127.71, 36.998], [127.7, 36.975]], 0.2), tilt=36), callouts=low("노획 장비를 챙겨 질서 있게"))
sc(1, text("이긴 자리에 오래 머물지 않는다", "blue"))
sc(1, text("지연전의 원칙", "yellow", "적 증원이 오기 전에 빠진다"))
sc(1, text("이기고 나서 물러날 줄 아는 군대", "blue"))
sc(1, ai("night_march_proud"), label=DRAMA)
sc(1, ph("rok_m1"), label=plabel("rok_m1"))
sc(1, m("corps", "corps", [mark("dongnak", "blue", 0.1), radar("dongnak", 0.2, 1.4, "blue", "첫 승전보")], tilt=16), sfx=PING(0.5))
next_act()

# ===== 제6막 숫자가 서로 다른 이유 =====
sc(1, black("그날 북한군은", "얼마나 잃었을까"), chapter={"num": "제6막", "title": "숫자가 서로 다른 이유"})
sc(1, text("하나의 답이 없다", "red"))
sc(1, doc("기록 ① (국군 공식 기록 인용)", ["국방부 군사편찬연구소 자료 인용", "뉴시스 2020. 6. 24"], "記錄", "국방부 군사편찬연구소", "인용 기록 · 요약"))
sc(1, bars("기록 ① · 국군 공식 기록 기준", [{"label": "적 사살", "value": 2186, "display": "2,186명", "color": "red", "on": "이천백팔십육"}]))
sc(1, bars("기록 ① · 국군 공식 기록 기준", [{"label": "적 사살", "value": 2186, "display": "2,186명", "color": "red", "at": 0}, {"label": "포로", "value": 132, "display": "132명", "color": "blue", "on": "백삼십이"}]))
sc(1, troops(24, keep=0, keepAt=0.5, side="nk", cols=12, title="북한군 제48연대", labels=[{"x": 0.5, "y": 0.74, "text": "사실상 사라진 연대", "at": 0.6, "color": "red"}]))
sc(1, text("다른 기록은 조금 다르다", "dark"))
sc(1, bars("기록 ② · 한국교육신문 (2008)", [{"label": "적 사살", "value": 800, "display": "800여 명", "color": "red", "on": "팔백여"}, {"label": "포로", "value": 90, "display": "90명", "color": "blue", "on": "구십"}]))
sc(1, checklist("기록 ② 노획", [{"text": "차량 60대", "on": "차량"}, {"text": "장갑차 3대", "on": "장갑차"}]))
sc(1, checklist("기록 ② 노획", [{"text": "소총 1,000여 정", "on": "소총"}, {"text": "박격포 35문", "on": "박격포"}, {"text": "기관총 47정", "on": "기관총"}, {"text": "대포 12문", "on": "대포"}]))
sc(1, cmp("기록 ① 사살", "2,186명", "기록 ② 사살", "800여 명", "red", "red"))
sc(1, text("전과를 셀 여유가 없던 군대", "dark", "전쟁 초기 국군"))
sc(1, ai("night_count"), label=DRAMA)
sc(1, text("너무나 간절했던 승리", "yellow"))
sc(1, text("13일 만의 첫 승리", "blue"))
sc(1, text("부풀려졌을 수도", "red"))
sc(1, text("빠진 숫자가 있을 수도", "blue"))
sc(1, text("전쟁 초기 기록 · 드물지 않은 일", "dark"))
sc(1, cmp("국군 기록", "?", "미군 기록", "?", "blue", "blue"))
sc(1, text("여러 기록을 나란히 놓고 비교", "yellow", "역사학자들의 방법"))
sc(1, text("숫자 하나로는 판단하기 어렵다", "dark"))
sc(1, text("두 기록을 모두 보여 드립니다", "yellow", "격전의 지도"))
sc(1, black("분명한 것은", "하나"))
sc(1, text("제48연대 · 싸울 수 없는 연대로", "red"))
sc(1, checklist("한꺼번에 잃은 것", [{"text": "대포", "on": "대포와"}, {"text": "트럭", "on": "트럭과"}, {"text": "탄약", "on": "탄약을"}]))
sc(1, text("정부의 응답", "blue"))
sc(1, doc("포상 (요지)", ["국군 제7연대", "대통령 부대 표창"], "表彰", "대한민국 정부", "1950. 7 · 요약"))
sc(1, doc("포상 (요지)", ["국군 제7연대", "대통령 부대 표창", "전 장병 1계급 특진"], "特進", "대한민국 정부", "1950. 7 · 요약"))
sc(1, text("연대 전체가 한꺼번에 진급", "yellow", "매우 드문 일"))
sc(1, text("그만큼 절실했던 승리", "dark"))
sc(1, ph("rok_kp"), label=plabel("rok_kp"))
sc(1, text("“우리도 이길 수 있다”는 증거", "yellow"))
sc(1, ai("kim_alert"), label=DRAMA, kb="out", callouts=low("김종오 · 곧 준장 진급"))
sc(1, m("sobaek", "sobaek", [blue_a(SIX_SOUTH, 0.1), mark("chungju", "blue", on="충주와"), mark("suanbo", "blue", on="수안보와"), mark("iwha", "blue", on="이화령에서")], tilt=18))
sc(1, black("그렇다면 무너진", "제48연대는?"))
sc(1, text("다시 채워 넣은 연대", "red", "북한군 제48연대"))
sc(1, m("sobaek", "sobaek", [red_a(HW_ROUTE, 0.2), mark("sangju", "red", 0.6)], tilt=18), callouts=top("열흘 뒤 · 상주를 향해", "red"))
sc(1, m("sobaek", "sobaek", [red_a(HW_ROUTE, 0), LOCK("hwaryeong", 0.3)], tilt=20, hud=True), callouts=low("보은과 상주 사이 · 화령장"), sfx=PING(0.4))
sc(1, m("sobaek", "sobaek", [red_a(HW_ROUTE, 0), clash("hwaryeong", 0.3)], tilt=20))
sc(1, text("국군 제17연대", "blue", "화령장 매복"))
sc(1, text("지난 이야기 · 화령장 전투", "yellow", "격전의 지도 EP31"))
sc(1, cmp("7월 7일", "동락리", "7월 17일~", "화령장", "blue", "blue"))
sc(1, text("두 번의 공통점", "yellow"))
sc(1, checklist("두 번의 공통점", [{"text": "“국군은 없다”는 믿음", "on": "믿었습니다"}]))
sc(1, checklist("두 번의 공통점", [{"text": "“국군은 없다”는 믿음", "at": 0}, {"text": "마을 사람의 신고", "on": "신고였습니다"}]), sfx=WIND(0))
next_act()

# ===== 제7막 동락이 남긴 것 =====
MID.append(nid())
sc(1, ai("teacher_portrait"), label=DRAMA, kb="out", pauseBefore=0.5, chapter={"num": "제7막", "title": "동락이 남긴 것"})
sc(1, text("소대장 이득주 소위", "blue", "그날 산 위에서 만난 인연"))
sc(1, text("결혼해 꾸린 가정", "yellow"))
sc(1, text("선생님과 군인의 이야기", "dark"))
sc(1, text("김종수 소령이 남긴 책", "blue"))
sc(1, text("『전쟁과 여교사』", "yellow"))
sc(1, black("하지만 그녀의 이야기는", "행복하게 끝나지 않는다"))
sc(1, text("1963년 12월", "dark", "남편과 함께 세상을 떠나다"))
sc(1, text("32살", "dark"))
sc(1, ai("mountain_path"), label=DRAMA, kb="out")
sc(1, text("오랫동안 잊혔던 이름", "dark"))
sc(1, doc("서훈 (요지)", ["2012. 10. 1 국군의 날", "보국훈장 추서"], "敍勳", "대한민국 정부", "2012 · 요약"))
sc(1, doc("서훈 (요지)", ["2013 · 이달의 6·25 전쟁영웅", "국가보훈처 선정"], "英雄", "국가보훈처", "2013 · 요약"))
sc(1, text("민간인 첫 이달의 6·25 전쟁영웅", "yellow"))
sc(1, ai("valley_today"), label=DRAMA, callouts=top("충주시 신니면 · 동락초등학교 일대"))
sc(1, text("첫 전승지 전승비", "yellow", "동락초등학교 교정 · 김재옥 교사 기념관"))
sc(1, text("해마다 7월 7일", "blue", "첫 승리를 기리는 행사"))
sc(1, ai("kids_playground"), label=DRAMA)
sc(1, black("이제", "처음의 질문으로"))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05, "kicker": "■ 처음의 질문 ■"}})
sc(1, text("더 많은 병력도 · 더 좋은 무기도 아니었다", "dark"))
sc(1, reasons("동락리의 4가지", [{"text": "정보", "on": "정보였습니다"}, {"text": "기만", "later": True}, {"text": "인내", "later": True}, {"text": "표적", "later": True}]))
sc(1, DN(unit("dongnak", "제48연대·포병대", "red", 0.1), LOCK("dongnak", 0.3, "적 배치 확인", RED), tilt=38))
sc(1, reasons("동락리의 4가지", [{"text": "정보", "at": 0}, {"text": "기만", "on": "기만이었습니다"}, {"text": "인내", "later": True}, {"text": "표적", "later": True}]))
sc(1, text("“국군은 다 도망갔어요”", "yellow"))
sc(1, reasons("동락리의 4가지", [{"text": "정보", "at": 0}, {"text": "기만", "at": 0}, {"text": "인내", "on": "인내였습니다"}, {"text": "표적", "later": True}]))
sc(1, DN(unit("cut6", "제6중대", "blue", 0.1), unit("cut7", "제7중대", "blue", 0.2), LOCK([127.711, 37.01], 0.4, "퇴로부터"), tilt=36))
sc(1, reasons("동락리의 4가지", [{"text": "정보", "at": 0}, {"text": "기만", "at": 0}, {"text": "인내", "at": 0}, {"text": "표적", "on": "표적이었습니다"}]))
sc(1, DN(blue_a(FIRE8, 0.1), shock(SCHOOL_FIRE, 0.3, 0.6), LOCK("dongnak", 0.4, "대포·탄약", RED), tilt=40))
sc(1, text("네 가지를 이어 준 한 사람의 용기", "yellow"))
sc(1, text("적은 우리를 모른다고 믿었다", "red"))
sc(1, text("우리는 적을 손바닥 보듯 알았다", "blue"))
sc(1, text("열아홉 살 선생님의 4km", "yellow"))
SOMBER = nid()
sc(1, black("전쟁의 흐름이", "바뀌지는 않았다"))
sc(1, m("south", "south", [line(PUSAN, 0.2, "#7fd3ff")], tilt=12), callouts=low("낙동강까지 밀려난 국군"))
sc(1, black("하지만 동락리가", "가르쳐 준 것"))
sc(1, text("“우리도 이길 수 있다”", "yellow"))
sc(1, ai("dabu_night"), label=DRAMA, callouts=top("1950. 8 · 낙동강의 여름"))
sc(1, black("그리고", "뒷이야기 하나"))
sc(1, m("north", "north", [blue_a(CHOSAN[:3], 0.2)], tilt=10), callouts=top("1950년 가을 · 북쪽으로"))
sc(1, m("north", "north", [blue_a(CHOSAN, 0.1), LOCK("chosan", 0.5, "압록강 · 초산")], tilt=10, hud=True), sfx=PING(0.5))
sc(1, text("동락리의 제7연대", "blue"))
sc(1, text("운동장의 첫 승리 → 석 달 뒤 압록강", "yellow"))
sc(1, text("그 이야기는 다른 편에서", "dark", "격전의 지도"))
sc(1, ai("village_school"), label=DRAMA, kb="out")
sc(1, {"type": "endcard", "title": "운동장의 첫 승리를 만든\n모든 이들을 기억하며", "q": pin("rok_july")}, tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 =====
# 재사용 (파일·서명 복사, 추가 비용 0)
REUSE = {
    "village_school": "ep31-hwaryeong", "op_post": "ep31-hwaryeong", "kim_alert": "ep31-hwaryeong", "dawn_rain": "ep31-hwaryeong", "t34_column": "ep31-hwaryeong",
    "withdraw": "ep31-hwaryeong", "crest_wait": "ep31-hwaryeong", "trench_wait": "ep31-hwaryeong", "dawn_victory": "ep31-hwaryeong",
    "dabu_night": "ep31-hwaryeong", "valley_today": "ep31-hwaryeong", "valley_quiet": "ep31-hwaryeong",
    "direct_fire": "chuncheon", "su76_advance": "chuncheon", "classroom_1950": "ep28-pohang",
}
# 새 그림 (Cloudflare Workers AI 무료 · 사람은 작은 실루엣·뒷모습 위주, 국기·글자 없음)
TAIL = ", painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no flags, no text, no letters."
NK = "soldiers in plain khaki 1950 uniforms and soft field caps"
NEW = {
    "school_trucks": "The dirt playground of a small one-story 1950 rural Korean elementary school with a dark tiled roof, crowded with old Soviet-made military trucks and towed field guns parked in rows, small distant " + NK + " resting in the shade of old trees, green mountains behind, hot July afternoon in 1950",
    "cook_smoke": "Thin cooking smoke rising from black iron pots over small fires in a rural Korean schoolyard in the late afternoon of July 1950, rifles stacked in tripods, military trucks parked beside a wooden school building, small relaxed distant " + NK + " sitting on the ground, seen from far away on a hillside",
    "teacher_gate": "A young Korean woman in 1950 plain rural work clothes and a headscarf seen from behind slipping quietly out through the small back gate of a wooden rural school fence toward green rice paddies and a forested mountain, hot July afternoon, tense, her face not visible",
    "mountain_path": "A lone young Korean woman in plain 1950 rural work clothes and a headscarf seen from behind climbing a steep narrow forest path up a green Korean mountain under a hot hazy July sun, cicada summer heat, small figure among pine trees",
    "schoolyard_blast": "Mortar shells exploding in a rural Korean schoolyard at dusk in July 1950, a towed field gun position and stacked wooden ammunition crates erupting in a fireball, burning military trucks, a small wooden school building lit by orange flames, seen from a distant hilltop, no visible people, absolutely no flags, no banners, no poles",
    "misty_ridge": "Low morning fog over green rolling hills and a dirt road in rural central Korea in July 1950, a small mountain pass with a few pine trees, eerie and quiet, no people visible",
    "market_village": "A small 1950 rural Korean market village with thatched and tiled roofs along a dusty crossroads, empty market stalls, abandoned A-frame carriers, green hills behind, hot July day, no people visible",
    "teacher_portrait": "A young Korean woman teacher in a 1950 white jeogori blouse and long black skirt standing by the window of an old wooden classroom, seen from the side in silhouette with her face in shadow, warm afternoon light through the window, a blackboard and wooden desks behind, quiet and resolute",
    "summer_heat": "A hot hazy summer sun over a forested Korean mountain ridge in July 1950, shimmering heat, cicadas, a narrow dusty trail winding up through pine trees and tall grass, no people visible",
    "ridge_meet": "On a forested Korean mountain ridge in July 1950, a small young woman in plain rural work clothes and a headscarf standing before a few cautious soldiers in olive drab M1 steel helmets lowering their rifles, seen from far behind bushes, small figures, faces not visible",
    "binocular_view": "A view through old binoculars, round black binocular vignette, looking down from a mountain at a distant rural Korean schoolyard crowded with parked military trucks and towed field guns in July 1950, haze, hot afternoon",
    "teacher_return": "A young Korean woman in plain 1950 rural clothes and a headscarf walking calmly back through the front gate of a small wooden rural school whose yard is full of parked military trucks, seen from far behind, small distant figures of " + NK + " in the yard, hot late afternoon",
    "ridge_prep": "Soldiers in olive drab M1 steel helmets quietly setting up a 60mm mortar and a light machine gun behind rocks and pine trees on a Korean hill above rice paddies in the late afternoon of July 1950, seen from behind, faces not visible, tense silence",
    "dusk_sun": "The summer sun sinking low behind green mountains over rice paddies and a small rural village in Korea in July 1950, long golden shadows, smoke from cooking fires, calm before a storm, no people visible",
    "valley_dusk_trucks": "Military trucks and towed field guns parked under old trees beside a small wooden rural Korean school at golden dusk in July 1950, a few small distant " + NK + " lying down resting, seen from a hilltop far away through leaves",
    "panic_yard": "Chaos in a smoke-filled rural Korean schoolyard at dusk in July 1950, small distant silhouettes of " + NK + " running away from burning trucks and exploding guns, dust and flames, seen from a distant hill",
    "abandoned_guns": "Abandoned towed field guns, burnt-out military trucks loaded with mortars and machine guns, and scattered wooden ammunition boxes in a smoky rural Korean schoolyard at twilight in July 1950, a small wooden school building behind, no people visible",
    "night_march_proud": "A column of soldiers in olive drab M1 steel helmets marching at night along a Korean country road carrying captured machine guns and mortar tubes on their shoulders, moonlight, seen from behind, small figures, a sense of quiet pride",
    "night_count": "A dark Korean hillside at night after a battle, scattered abandoned equipment in the grass under moonlight, a lantern on a rock beside an open notebook, smoke drifting, no people visible",
    "kids_playground": "Small Korean schoolchildren in colorful summer clothes running and playing on the dirt playground of a small rural school today, seen from far away and from behind, bright summer day, green hills, joyful",
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
         {"id": "tension", "from": sid(chap[1]), "to": sid(chap[2] - 1), "volume": 0.17},
         {"id": "analysis", "from": sid(chap[2]), "to": sid(chap[3] - 1), "volume": 0.16},
         {"id": "march", "from": sid(chap[3]), "to": sid(chap[5] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[5]), "to": sid(chap[6] - 1), "volume": 0.17},
         {"id": "analysis", "from": sid(chap[6]), "to": prev_id(SOMBER), "volume": 0.16},
         {"id": "somber", "from": SOMBER, "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "운동장에 모인 적 연대", "subtitle": "동락리 전투 · 국군 제6사단 제7연대 · 1950", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         "target_sec": 1230, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap],
      "ai", len(AI), "pins", len(PINS), "stage", len(stages), "photo", sum(1 for s in S if s["visual"]["type"] == "photo"))
print("char uses", dict(cnt))
