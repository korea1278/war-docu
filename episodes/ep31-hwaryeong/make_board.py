# EP31 화령장 전투 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 연출 스타일 v2 + 화면 업그레이드 2단계 + 롱폼 표준(LONGFORM_STANDARD) + 캐릭터 반복 방지 규칙 + 초반 후킹 표준(docs/HOOK_STANDARD.md)
# 그림: 다른 에피소드 재사용(파일·서명 복사) + 새 그림은 Cloudflare 무료 엔진 (2026-11-18 Gemini 충전 중단)
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
SUBS = [
    ("천구백오십년 칠월 이십일일", "1950년 7월 21일"), ("천구백오십년 유월 이십오일", "1950년 6월 25일"), ("천구백오십년", "1950년"), ("이천십팔년 시월", "2018년 10월"),
    ("칠월 이십일일", "7월 21일"), ("칠월 이십오일", "7월 25일"), ("칠월 십칠일", "7월 17일"), ("칠월 십팔일", "7월 18일"), ("칠월 십구일", "7월 19일"),
    ("칠월 십사일", "7월 14일"), ("칠월 십이일", "7월 12일"), ("칠월 오일", "7월 5일"), ("구월 십오일", "9월 15일"),
    ("새벽 여섯 시", "새벽 6시"), ("오후 세 시", "오후 3시"), ("오후 두 시", "오후 2시"),
    ("삼백오십육 대 넷", "356 대 4"), ("삼백오십육 명", "356명"), ("육백이십오 명", "625명"), ("오십육 명", "56명"), ("이십육 명", "26명"),
    ("전사 네 명 부상 서른 명", "전사 4명 부상 30명"), ("단 네 명", "단 4명"), ("이백오십여 명", "250여 명"), ("삼십여 명", "30여 명"),
    ("육백여 명", "600여 명"), ("오십여 명", "50여 명"), ("이천육백여 명", "2,600여 명"), ("이천육백 명", "2,600명"), ("열두 명", "12명"), ("두 명이", "2명이"),
    ("박격포 스무 문", "박격포 20문"), ("사십오 밀리 대전차포 일곱 문", "45mm 대전차포 7문"), ("소총 천이백여 정", "소총 1,200여 정"),
    ("박격포 열여섯 문", "박격포 16문"), ("대전차포 두 문", "대전차포 2문"), ("기관총 쉰세 정", "기관총 53정"), ("소총 백팔십육 정", "소총 186정"), ("무전기 한 대", "무전기 1대"),
    ("마흔 대", "40대"), ("열 대", "10대"), ("여섯 개 마을", "6개 마을"), ("두 개 대대", "2개 대대"), ("두 개 연대", "2개 연대"),
    ("한 개 대대", "1개 대대"), ("한 개 연대", "1개 연대"), ("한 개 중대", "1개 중대"), ("문서 두 통", "문서 2통"), ("두 장", "2장"),
    ("삼십 년", "30년"), ("칠십오 년 전", "75년 전"), ("스무 날", "20일"), ("한 시간", "1시간"), ("육사 삼기", "육사 3기"), ("세 가지", "3가지"),
    ("제십칠연대", "제17연대"), ("제십오사단", "제15사단"), ("제사십팔연대", "제48연대"), ("제사십오연대", "제45연대"), ("제이십사사단", "제24사단"),
    ("제이십오사단", "제25사단"), ("제이십사연대", "제24연대"), ("제이군단", "제2군단"), ("제십군단", "제10군단"), ("제팔군", "제8군"),
    ("제일사단", "제1사단"), ("제일대대", "제1대대"), ("제이대대", "제2대대"), ("제삼대대", "제3대대"), ("제칠중대장", "제7중대장"), ("제육중대", "제6중대"),
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


def doc(head, rows, stamp="軍 秘", org="국군 제17연대", note="재구성 · 내용 요약"):
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


# 좌표는 개략 (화령장·상곡리·갈령·봉황산·동관리·관기리·동비령은 현재 지형 기준 근사 — 화면에 '위치 개략' 표기)
P = {
    "seoul": [126.978, 37.566, "서울"], "ongjin": [125.36, 37.93, "옹진반도"], "incheon": [126.62, 37.47, "인천"], "osan": [127.07, 37.15, "오산"],
    "daejeon": [127.385, 36.35, "대전"], "cheongju": [127.49, 36.64, "청주"], "chuncheon": [127.73, 37.88, "춘천"], "wonju": [127.92, 37.342, "원주"],
    "yeoju": [127.637, 37.298, "여주"], "janghowon": [127.64, 37.11, "장호원"], "goesan": [127.786, 36.815, "괴산"], "boeun": [127.729, 36.489, "보은"],
    "gwangi": [127.84, 36.44, "관기리"], "dongbi": [127.9, 36.58, "동비령"], "songni": [127.87, 36.545, "속리산"], "hamchang": [128.18, 36.56, "함창"],
    "mungyeong": [128.19, 36.59, "문경"], "sangju": [128.16, 36.41, "상주"], "gimcheon": [128.11, 36.14, "김천"], "daegu": [128.6, 35.87, "대구"],
    "busan": [129.04, 35.18, "부산"], "dabudong": [128.55, 36.06, "다부동"], "yeongcheon": [128.94, 35.97, "영천"], "pohang": [129.36, 36.02, "포항"],
    "hwaryeong": [127.988, 36.443, "화령장"], "sanggok": [127.958, 36.47, "상곡리"], "galryeong": [127.925, 36.505, "갈령"], "bonghwang": [127.935, 36.452, "봉황산"],
    "dongkwan": [127.915, 36.43, "동관리"], "sg_w": [127.95, 36.474, "능선"], "sg_e": [127.966, 36.466, "능선"], "sg_mid": [127.958, 36.47, "상곡리 골짜기"],
    "dk_n": [127.913, 36.437, "북쪽 능선"], "dk_s": [127.918, 36.423, "남쪽 능선"], "dk_op": [127.926, 36.434, "대대 관측소"],
}
V = {
    "korea": {"center": [127.6, 36.7], "span": 5.5}, "ongjin": {"center": [126.0, 37.8], "span": 2.2}, "mid": {"center": [127.75, 37.0], "span": 2.4},
    "sobaek": {"center": [127.95, 36.56], "span": 1.1}, "south": {"center": [128.35, 36.15], "span": 1.9}, "naktong": {"center": [128.7, 35.75], "span": 2.4},
    "hwar": {"center": [127.95, 36.462], "span": 0.2}, "sanggok": {"center": [127.955, 36.476], "span": 0.12}, "dongkwan": {"center": [127.918, 36.432], "span": 0.11},
}
L38 = {"k": "line", "path": [[124.6, 38.0], [126.5, 38.0], [128.6, 38.3]], "color": "#ffffff", "at": 0, "dash": True}
INVADE = [[[126.9, 38.2], [126.98, 37.62]], [[127.7, 38.1], [127.73, 37.88]], [[128.3, 38.1], [128.4, 37.6]]]
ONGJIN_ATK = [[125.5, 38.3], [125.4, 38.0]]
ONGJIN_OUT = [[125.36, 37.9], [125.8, 37.55], [126.5, 37.4]]
SOUTH_PUSH = [[126.98, 37.5], [127.07, 37.15], [127.385, 36.4]]
R15A = [[127.73, 37.88], [127.92, 37.36], [127.637, 37.3]]
R15B = [[127.637, 37.3], [127.64, 37.11], [127.786, 36.82]]
R15C = [[127.786, 36.815], [127.85, 36.65], [127.925, 36.51], [127.988, 36.443]]
SANGJU_DAEGU = [[127.988, 36.443], [128.16, 36.41], [128.11, 36.14], [128.6, 35.87]]
CUT_BEHIND = [[127.9, 36.6], [127.75, 36.45], [127.5, 36.35]]
BOEUN_HAMCHANG = [[127.729, 36.489], [127.988, 36.443], [128.18, 36.56]]
BOEUN_GWANGI = [[127.729, 36.489], [127.84, 36.44]]
BOEUN_SANGJU = [[127.729, 36.489], [127.84, 36.44], [127.988, 36.443], [128.16, 36.41]]
CHEONGJU_HW = [[127.49, 36.64], [127.729, 36.489], [127.988, 36.443]]
GAL_ROAD = [[127.925, 36.505], [127.94, 36.49], [127.952, 36.478], [127.958, 36.47], [127.97, 36.457], [127.988, 36.443]]
PASSED = [[127.988, 36.443], [128.06, 36.43], [128.13, 36.415]]
HW_SG = [[127.988, 36.443], [127.97, 36.457], [127.96, 36.468]]
FLEE1 = [[127.958, 36.47], [127.945, 36.48], [127.935, 36.49]]
FLEE2 = [[127.958, 36.47], [127.975, 36.48], [127.985, 36.492]]
DONG_ROAD = [[127.888, 36.44], [127.9, 36.436], [127.912, 36.432], [127.922, 36.428], [127.934, 36.424]]
HW_BONG = [[127.988, 36.443], [127.96, 36.448], [127.94, 36.447]]
SUPPLY = [[127.9, 36.45], [127.91, 36.443], [127.918, 36.438]]
COUNTER = [[127.92, 36.5], [127.95, 36.475], [127.975, 36.455]]
PUSAN = [[128.37, 36.3], [128.4, 36.0], [128.42, 35.6], [128.38, 35.3], [128.25, 35.1]]
PUSAN_E = [[128.37, 36.3], [128.9, 36.15], [129.4, 36.08]]
SANGJU_FIGHT = [[128.05, 36.5], [128.12, 36.44]]
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
groad = lambda at=0, on=None: line(GAL_ROAD, at, "#ffffff", on)
droad = lambda at=0, on=None: line(DONG_ROAD, at, "#ffffff", on)
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]
SW = lambda at=0: [{"id": "whoosh", "at": at}]
FAR = lambda at=0.1: [{"id": "artillery_far", "at": at}]
PING = lambda at=0.6: [{"id": "ping", "at": at}]
WIND = lambda at=0: [{"id": "wind", "at": at}]
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))
flags = lambda title, items: {"type": "flaggrid", "title": title, "items": items}
QUESTION = "고립된 국군 1개 연대는 어떻게\n정예 사단을 협곡에 가뒀나"
TC = "#2e66d8"
RED = "#c9242c"
DK_FIRE = [[127.9, 36.436], [127.912, 36.432], [127.922, 36.428]]
SG_FIRE = [[127.955, 36.473], [127.958, 36.47], [127.962, 36.466]]

# ===== 콜드 오프닝 (초반 후킹 표준: 절정 → 수치 HUD 누적 → 통념 X → 핵심 질문 카드 → 타이틀) =====
sc(1, ai("misty_gorge"), label=DRAMA, hook={"hud": [HUD("1950. 7. 21", "경북 상주", "동관리 계곡 · 새벽", count=False)]}, sfx=WIND(0.2))
sc(1, ai("column_in_mist"), label=DRAMA)
sc(1, checklist("계곡으로 들어온 대열", [{"text": "배낭", "on": "배낭을"}, {"text": "총 끝의 대검", "on": "대검을"}]))
sc(1, ph("dshk", marks=[{"text": "바퀴 달린 기관총", "x": 0.5, "y": 0.2, "on": "바퀴", "color": "red"}]), label=plabel("dshk"))
sc(1, m("dongkwan", "dongkwan", [droad(0), unit("dk_n", "국군", "blue", 0.3), unit("dk_s", "국군", "blue", 0.4)], tilt=34, hud=True),
   hook={"hud": [HUD("1개 대대", "계곡 양쪽 능선의 국군", "제17연대 제2대대", on="한 개 대대")]}, sfx=PING(0.5))
sc(1, stage([C("kr_point", 0.5, 480, prop="officer+helmet", face="determined", anim="tilt")], [pop("label", 0.5, 0.15, "대대장의 지시", on="일러", color="dark")]))
sc(1, text("“나의 명령 없이는 절대 쏘지 마라”", "yellow", "대대장의 지시"))
sc(1, black("성급한 한 발이", "모든 것을 망친다"))
sc(1, m("dongkwan", "dongkwan", [droad(0), unit("dk_n", "국군", "blue", 0), unit("dk_s", "국군", "blue", 0), swarm(DONG_ROAD, 0.1, 110, 0.25)], tilt=34))
sc(1, ai("red_flag"), label=DRAMA)
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD, 0, 110, 0.25), shock(DK_FIRE, 0.1, 0.6), clash([127.912, 36.432], 0.3)], tilt=34), sfx=FAR(0.1))
sc(1, ai("valley_quiet"), label=DRAMA, hook={"hud": [HUD("356명", "사살된 북한군", "1950. 7. 21 하루", color="#FF3B3B", on="삼백오십육")]})
sc(1, text("포로 26명", "red", "동관리 계곡"))
sc(1, cmp("북한군 사살", "356명", "국군 전사", "4명", "red", "blue"), hook={"hud": [HUD("4명", "국군 전사자", color="#4f8dff", on="네 명")]})
sc(3, black("개전 이후 국군은", "밀리기만 했다"), hook={"neg": {"text": "밀리기만 했다", "at": 0.2, "xOn": "그랬을까요"}})
sc(1, ai("bicycle_courier"), label=DRAMA)
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, {"type": "titlecard", "title": "협곡에 갇힌 정예 사단", "sub": "화령장 전투 · 국군 제17연대 단독 매복전 · 1950", "at": 0, "q": pin("rok_july")}, flash=True)
next_act()

# ===== 제1막 무너지는 남쪽 =====
sc(1, m("korea", "korea", [L38]), chapter={"num": "제1막", "title": "무너지는 남쪽"}, callouts=top("1950. 6. 25 새벽"))
sc(1, ai("dawn_rain"), label=DRAMA, sfx=FAR(0.2))
sc(1, m("ongjin", "ongjin", [L38, LOCK("ongjin", 0.4)], tilt=18, hud=True), callouts=top("서해 · 옹진반도"), sfx=PING(0.5))
sc(1, text("국군 제17연대", "blue", "옹진반도를 지키던 부대"))
sc(1, m("ongjin", "ongjin", [L38, mark("ongjin", "blue", 0), red_a(ONGJIN_ATK, 0.2)], tilt=18), callouts=low("육지로 남쪽과 이어지지 않는 외딴 땅"))
sc(1, m("ongjin", "ongjin", [L38, blue_a(ONGJIN_OUT, 0.2)]), callouts=top("배를 타고 바다로"))
sc(1, m("korea", "korea", [L38, red_a(INVADE[0], 0.1), red_a(INVADE[1], 0.2), red_a(INVADE[2], 0.3), mark("seoul", "red", on="서울이")]), callouts=top("1950. 6. 28 · 서울 함락", "red"))
sc(1, ph("han_bridge"), label=plabel("han_bridge"))
sc(1, ph("tfs_station"), label=plabel("tfs_station"), callouts=top("1950. 7. 5 · 미군의 첫 전투"))
sc(1, text("스미스 특수임무부대", "blue", "오산 죽미령"))
sc(1, ai("t34_column"), label=DRAMA)
sc(1, m("mid", "mid", [red_a(SOUTH_PUSH, 0.1, 1.1), mark("daejeon", "red", on="대전까지")], tilt=16), callouts=top("7월 중순 · 금강을 건너 대전까지"))
sc(1, ai("trucks"), label=DRAMA)
sc(1, text("육군본부 직할 독립 연대", "blue", "국군 제17연대"))
sc(1, checklist("제17연대", [{"text": "사단 소속 없음", "on": "사단에"}, {"text": "홀로 움직이는 연대", "on": "홀로"}]))
sc(1, troops(26, side="kr", cols=13, title="국군 제17연대", labels=[{"x": 0.5, "y": 0.74, "text": "약 2,600명", "on": "이천육백", "color": "blue"}]))
sc(1, stage([C("kr_shock", 0.5, 470, prop="officer+helmet", face="sweat", anim="exit")], [pop("label", 0.5, 0.15, "연대장 부상 · 후송", on="후송됩니다", color="red")]))
sc(1, text("김희준 중령", "yellow", "제17연대 부연대장"))
sc(1, text("연대장 대리", "dark", "이름표만 바뀐 부연대장"))
sc(1, ai("nk_plan"), label=DRAMA)
sc(2, doc("북한군 제2군단 작전 (요지)", ["소백산맥을 넘어", "남쪽 깊숙이 돌파"], "作戰", "북한군 제2군단", "1950. 7 · 재구성"))
sc(1, m("mid", "mid", [mark("daejeon", "blue", 0), mark("cheongju", "blue", 0), red_a(CUT_BEHIND, 0.2, 1.1)], tilt=18), callouts=low("국군·미군의 뒤를 끊는다", "red"))
sc(1, text("선봉 · 북한군 제15사단", "red"))
sc(1, m("mid", "mid", [red_a(R15A, 0.1)], tilt=16), callouts=top("춘천 → 원주 → 서쪽으로"))
sc(1, m("mid", "mid", [red_a(R15A, 0), red_a(R15B, 0.1), clash("janghowon", 0.5)], tilt=16), callouts=low("여주 → 장호원 격전"))
sc(1, m("mid", "mid", [red_a(R15A, 0), red_a(R15B, 0), LOCK("goesan", 0.3, color=RED)], tilt=18, hud=True), callouts=top("1950. 7. 12 · 괴산"), sfx=PING(0.4))
sc(1, m("sobaek", "sobaek", [mark("goesan", "red", 0), line(R15C[:3], 0.2, "#ff6b5b"), badge("songni", "속리산", "#111", 0.4, -50)], tilt=26))
sc(1, m("sobaek", "sobaek", [line(R15C, 0, "#ff6b5b"), LOCK("sangju", 0.3, color=RED)], tilt=24))
sc(1, m("south", "south", [red_a(SANGJU_DAEGU, 0.1), mark("gimcheon", "red", on="김천"), mark("daegu", "red", on="대구였습니다")], tilt=14))
sc(1, text("대구 · 임시 수도", "dark", "1950. 7월 중순 정부가 옮겨 온 곳"))
sc(1, m("korea", "korea", [line(R15C + SANGJU_DAEGU[1:], 0.1, "#ffd400")]), callouts=low("한반도 등뼈를 가로지르는 지름길"))
sc(1, text("좁지만 가장 빠른 길", "yellow"))
sc(1, m("south", "south", [dash_r(SANGJU_DAEGU, 0.1), line(PUSAN, 0.3, "#7fd3ff")], tilt=12), callouts=low("마지막 방어선이 서기도 전에", "red"))
sc(1, m("sobaek", "sobaek", [line(R15C, 0, "#ffd400"), badge("hwaryeong", "공백 지대", RED, 0.3, -60)], tilt=24))
sc(1, stage([C("kr_shrug", 0.5, 470, prop="helmet", face="sweat", anim="tilt")], [pop("label", 0.5, 0.15, "병력이 모자라!", on="손이", color="dark")]))
sc(1, text("“대부대는 못 올 산길”", "dark", "당시의 판단"))
sc(1, ai("nk766_infiltrate"), label=DRAMA, sfx=WIND(0))
next_act()

# ===== 제2막 비어 있는 길 =====
sc(1, m("sobaek", "sobaek", [mark("dongbi", "blue", 0.3)], tilt=22), chapter={"num": "제2막", "title": "비어 있는 길"}, callouts=top("1950. 7. 14 정오 무렵"))
sc(1, m("sobaek", "sobaek", [LOCK("dongbi", 0.3)], tilt=26, hud=True), callouts=top("동비령 고개 · 위치 개략"), sfx=PING(0.4))
sc(1, text("산속 공백 지대 정찰", "dark", "국군 정찰대"))
sc(1, stage([C("kr_point", 0.45, 470, prop="helmet+notebook", face="shock", flip=True)], [pop("ex", 0.75, 0.28, on="맞닥뜨립니다")]))
sc(1, bars("동비령 · 사로잡은 북한군 첨병", [{"label": "포로", "value": 12, "display": "12명", "color": "blue", "on": "열두"}]))
sc(1, ph("pow_interrog"), label=plabel("pow_interrog"))
sc(1, m("sobaek", "sobaek", [swarm(R15C[:3], 0.2, 90), red_a(R15C[:3], 0.3)], tilt=24), callouts=low("북한군 대부대 남하", "red"))
sc(1, stage([C("kr_plead", 0.5, 470, prop="officer", face="worried")], [pop("q", 0.76, 0.3, on="찾습니다")]))
sc(1, m("sobaek", "sobaek", [blue_a(BOEUN_HAMCHANG, 0.2)], tilt=22), callouts=top("제17연대 · 보은 → 함창 이동 중"))
sc(2, doc("육군본부 명령 (요지)", ["제17연대는 화령장에서", "남하하는 적을 저지하라"], "命令", "대한민국 육군본부", "1950. 7 · 재구성"))
sc(1, black("문제는", "연대가 흩어져 있었다"))
sc(1, m("mid", "mid", [unit("boeun", "제1대대", "blue", on="제일대대만")], tilt=16))
sc(1, m("mid", "mid", [unit("boeun", "제1대대", "blue", 0), unit("cheongju", "2개 대대", "blue", on="나머지")], tilt=16), callouts=low("청주 부근에서 빠져나오는 중"))
sc(1, m("sobaek", "sobaek", [unit("boeun", "제1대대", "blue", 0), blue_a(BOEUN_HAMCHANG, 0.2)], tilt=22))
sc(1, text("제1대대장 이관수 소령", "yellow", "육사 3기"))
sc(1, ph("rok_july"), label=plabel("rok_july"), callouts=top("1950. 7. 17 새벽 6시 출발"))
sc(1, m("sobaek", "sobaek", [blue_a(BOEUN_GWANGI, 0.1), LOCK("gwangi", 0.4)], tilt=24), callouts=top("보은 관기리 · 위치 개략"))
sc(1, m("sobaek", "sobaek", [mark("gwangi", "blue", 0), red_a([[127.925, 36.505], [127.988, 36.443], [128.15, 36.415]], 0.2)], tilt=24), callouts=low("적은 이미 상주 쪽으로", "red"))
sc(1, stage([C("kr_shrug", 0.5, 470, prop="officer+helmet", face="worried+sweat", flip=True)], [pop("q", 0.25, 0.3, on="앞에"), pop("q", 0.75, 0.3, on="뒤에")]))
sc(1, m("hwar", "hwar", [LOCK("hwaryeong", 0.3)], tilt=30, hud=True), callouts=top("경북 상주시 화서면"), sfx=PING(0.4))
sc(2, text("화령장", "yellow", "장이 서던 산골 마을"))
sc(1, m("sobaek", "sobaek", [line(BOEUN_SANGJU, 0.1, "#ffffff"), mark("hwaryeong", "blue", 0.3)], tilt=22), callouts=low("보은 – 화령장 – 상주"))
sc(1, m("hwar", "hwar", [mark("hwaryeong", "blue", 0), badge("galryeong", "갈령", "#111", 0.2, -50), badge([127.93, 36.53], "속리산 방면", "#111", 0.4, -40)], tilt=34))
sc(1, ai("village_school"), label=DRAMA, callouts=top("화령초등학교"))
sc(1, ai("elder_runs"), label=DRAMA)
sc(1, text("주민 엄봉림", "yellow", "화령장 마을 주민"))
sc(1, text("“북한군을 봤습니다”", "yellow", "주민의 신고"))
sc(1, m("hwar", "hwar", [mark("hwaryeong", "blue", 0), blue_a(HW_SG, 0.2)], tilt=30), callouts=top("이관수 소령 · 직접 정찰"))
sc(1, m("sanggok", "sanggok", [groad(0), LOCK([127.962, 36.466], 0.3, "상곡리 쪽 다리")], tilt=34, hud=True), callouts=low("위치 개략"), sfx=PING(0.4))
sc(1, ai("bicycle_courier"), label=DRAMA)
sc(1, stage([C("nk_idle", 0.5, 470, prop="nkcap", face="smug", anim="enter")], [pop("label", 0.5, 0.15, "북한군 병사", on="북한군", color="red")]))
sc(1, text("전령", "red", "명령을 전하러 오가는 연락병"))
sc(1, stage([C("nk_plead", 0.5, 470, prop="nkcap", face="shock+sweat", anim="shake")], [pop("label", 0.5, 0.15, "붙잡힌 전령", on="사로잡았습니다", color="red")]))
sc(1, ph("pow_19th"), label=plabel("pow_19th"))
sc(1, doc("전령 심문 (요지)", ["소속 · 북한군 제15사단 제48연대"], "訊問", "국군 제17연대 제1대대", "1950. 7. 17 · 재구성"))
sc(1, m("sobaek", "sobaek", [LOCK("sangju", 0.3, "임무 · 상주 점령", RED)], tilt=22), sfx=PING(0.4))
sc(1, m("hwar", "hwar", [mark("hwaryeong", "blue", 0), red_a(PASSED, 0.2), badge([128.04, 36.43], "1개 대대 · 어젯밤 통과", RED, 0.4, -50)], tilt=28))
sc(1, m("hwar", "hwar", [groad(0), swarm(GAL_ROAD[:3], 0.2, 70, 0.3), unit("galryeong", "제48연대 본대", "red", 0.4, True)], tilt=30))
sc(1, black("전령을 놓쳤다면", "적의 한가운데로"))
sc(1, stage([C("kr_plead", 0.5, 470, prop="officer+helmet", face="worried", anim="tilt", flip=True)], [pop("q", 0.25, 0.3, on="고민에")]))
sc(1, m("hwar", "hwar", [mark("hwaryeong", "blue", 0), unit([128.04, 36.43], "적 대대", "red", on="앞에는")], tilt=28))
sc(1, m("hwar", "hwar", [mark("hwaryeong", "blue", 0), unit([128.04, 36.43], "적 대대", "red", 0), unit("galryeong", "적 연대 본대", "red", on="뒤에서는", pulse=True)], tilt=28))
sc(1, m("hwar", "hwar", [unit([128.04, 36.43], "적 대대", "red", 0), unit("galryeong", "적 연대 본대", "red", 0), blue_a([[127.988, 36.443], [128.03, 36.435]], 0.2)], tilt=28), callouts=low("적 사이에 끼인 행군", "red"))
sc(1, black("대대장은", "다른 길을 골랐다"))
sc(1, text("이 자리에 숨어 기다린다", "yellow"))
sc(1, text("매복", "red", "숨어 기다렸다가 기습하는 싸움"))
next_act()

# ===== 제3막 상곡리의 저녁 =====
MID = [nid()]
sc(1, m("sanggok", "sanggok", [groad(0.1), LOCK("sanggok", 0.4)], tilt=34), pauseBefore=0.5, chapter={"num": "제3막", "title": "상곡리의 저녁"}, callouts=top("상곡리 · 위치 개략"))
sc(2, m("sanggok", "sanggok", [groad(0), badge("sg_w", "숲", "#2b5d34", 0.3, -40), badge("sg_e", "숲", "#2b5d34", 0.4, -40)], tilt=40), callouts=low("구불구불한 골짜기 길"))
sc(1, m("sanggok", "sanggok", [groad(0), unit("sg_w", "제1대대", "blue", 0.2), unit("sg_e", "제1대대", "blue", 0.4)], tilt=36), callouts=low("길 양쪽 능선 · 위치 개략"))
sc(1, ai("crest_wait"), label=DRAMA)
sc(1, checklist("매복 규칙", [{"text": "적이 다 들어올 때까지", "on": "다"}, {"text": "아무도 쏘지 않는다", "on": "쏘지", "checkOn": "내려졌습니다"}]))
sc(1, text("오발 한 발 = 실패", "red"))
sc(1, text("오후 3시 · 준비 완료", "blue", "1950. 7. 17"))
sc(1, black("그리고", "기다림"))
sc(1, ph("rok_m1"), label=plabel("rok_m1"), callouts=top("칠월 한여름"))
sc(1, stage([C("kr_idle", 0.5, 470, prop="helmet", face="sweat", anim="shake")], [pop("label", 0.5, 0.15, "움직이면 안 돼", on="움직일", color="dark")]))
sc(2, text("땀 · 모기 · 정적", "dark", "산 아래 길은 조용했다"))
sc(1, m("sanggok", "sanggok", [groad(0), LOCK("galryeong", 0.3, "갈령 쪽", RED)], tilt=34), sfx=PING(0.3))
sc(1, text("덜컹 덜컹", "yellow", "수레바퀴 소리"))
sc(1, m("sanggok", "sanggok", [groad(0), swarm(GAL_ROAD[:4], 0.2, 80, 0.3), unit("galryeong", "제48연대 본대", "red", 0.4, True)], tilt=34))
sc(1, text("앞장선 우마차", "red", "소가 끄는 수레"))
sc(1, bars("상곡리 · 북한군 우마차", [{"label": "우마차", "value": 40, "display": "40여 대", "color": "red", "on": "마흔"}]))
sc(1, checklist("수레에 실린 것", [{"text": "박격포", "on": "박격포와"}, {"text": "대전차포", "on": "대전차포"}, {"text": "탄약 상자", "on": "탄약"}]))
sc(1, stage([C("nk_idle", 0.5, 470, prop="nkcap+pipe", face="smug", anim="bounce", flip=True)], [pop("label", 0.5, 0.15, "여긴 안전해", on="느슨했습니다", color="red")]))
sc(1, text("“이 산골에 국군은 없다”", "red", "북한군의 착각"))
sc(1, ai("oxcart_rest"), label=DRAMA)
sc(1, m("sanggok", "sanggok", [groad(0), unit("sg_mid", "제48연대 · 휴식", "red", 0.2)], tilt=34), callouts=low("수레를 세우고 쉬는 적"))
sc(1, text("저녁밥 짓는 연기", "dark", "해 질 무렵의 골짜기"))
sc(1, m("sanggok", "sanggok", [groad(0), unit("sg_mid", "한곳에 모인 적", "red", 0.1, True), unit("sg_w", "국군", "blue", 0.3), unit("sg_e", "국군", "blue", 0.3)], tilt=36))
sc(1, stage([C("kr_idle", 0.5, 470, prop="helmet+headband", face="determined", flip=True)], [pop("label", 0.5, 0.15, "방아쇠 위의 손가락", on="방아쇠에", color="dark")]))
sc(2, black("조금만 더", "적이 가장 많이 모일 때까지"))
sc(1, text("사격!", "red"))
sc(1, ai("jindong_ambush"), label=DRAMA, sfx=FAR(0.1))
sc(1, m("sanggok", "sanggok", [groad(0), unit("sg_mid", "제48연대", "red", 0), shock(SG_FIRE, 0.1, 0.6), clash("sg_mid", 0.2)], tilt=36))
sc(1, text("날뛰는 소 · 흩어지는 수레", "dark"))
sc(1, stage([C("nk_shock", 0.5, 470, prop="nkcap", face="shock", anim="shake")], [pop("ex", 0.75, 0.28, on="틈도")]))
sc(1, stage([C("nk_shrug", 0.5, 470, prop="nkcap", face="coldsweat", anim="tilt", flip=True)], [pop("q", 0.25, 0.3, on="어디서")]))
sc(1, ai("mangil_ambush"), label=DRAMA)
sc(1, m("sanggok", "sanggok", [groad(0), red_a(FLEE1, 0.1), red_a(FLEE2, 0.3)], tilt=34), callouts=low("산속으로 흩어진 적"))
sc(1, text("7. 17 밤 ~ 7. 18", "dark", "이튿날까지 이어진 소탕전"))
sc(1, m("hwar", "hwar", [badge([127.94, 36.49], "마을", "#111", 0.1, -40), badge([127.95, 36.48], "마을", "#111", 0.2, -40), badge([127.966, 36.474], "마을", "#111", 0.3, -40),
                         badge([127.972, 36.46], "마을", "#111", 0.4, -40), badge([127.945, 36.465], "마을", "#111", 0.5, -40), badge([127.98, 36.45], "마을", "#111", 0.6, -40)], tilt=32), callouts=low("6개 마을 · 위치 개략"))
sc(1, black("이틀 동안의", "전과"))
sc(1, bars("상곡리 전투 · 북한군", [{"label": "사살", "value": 250, "display": "250여 명", "color": "red", "on": "이백오십"}]))
sc(1, bars("상곡리 전투 · 북한군", [{"label": "사살", "value": 250, "display": "250여 명", "color": "red", "at": 0}, {"label": "포로", "value": 30, "display": "30여 명", "color": "dark", "on": "삼십여"}]))
sc(1, ph("captured_equip"), label=plabel("captured_equip"))
sc(3, checklist("상곡리 노획 무기", [{"text": "박격포 20문", "on": "스무"}, {"text": "45mm 대전차포 7문", "on": "일곱"}, {"text": "소총 1,200여 정", "on": "천이백"}]))
sc(1, text("적 1개 연대의 중화기", "yellow", "거의 통째로 국군 손에"))
sc(1, m("sanggok", "sanggok", [groad(0), badge("sg_mid", "제48연대 · 전투력 상실", RED, 0.2, -60)], tilt=34))
sc(1, stage([C("kr_shock", 0.5, 480, prop="officer+helmet", face="determined", anim="tilt")], [pop("label", 0.5, 0.15, "아직 끝나지 않았다", on="놓지", color="dark")]))
sc(1, m("sobaek", "sobaek", [unit("sanggok", "제48연대", "red", 0), unit([127.83, 36.62], "제15사단 나머지?", "red", 0.4, True)], tilt=22), callouts=low("사단의 일부일 뿐"))
sc(1, stage([C("kr_shrug", 0.5, 470, prop="officer", face="worried", flip=True)], [pop("q", 0.25, 0.3, on="어디에")]))
sc(1, text("또 한 대의 자전거", "yellow"), hudCta={"at": 0, "dur": 7.0})
next_act()

# ===== 제4막 적 사단장의 편지 =====
sc(1, m("hwar", "hwar", [groad(0.1)], tilt=28), chapter={"num": "제4막", "title": "적 사단장의 편지"}, callouts=top("1950. 7. 18"))
sc(1, text("정보 주임 유창훈 대위", "yellow", "제17연대"))
sc(1, m("hwar", "hwar", [groad(0), LOCK("galryeong", 0.3, "갈령 고갯길")], tilt=32, hud=True), callouts=low("자전거를 탄 북한군 두 명"), sfx=PING(0.4))
sc(1, stage([C("kr_salute", 0.5, 470, prop="helmet+notebook", face="smug", anim="bounce", flip=True)], [pop("label", 0.5, 0.15, "또 잡았다!", on="사로잡았습니다", color="blue")]))
sc(1, ai("letters_table"), label=DRAMA)
sc(1, text("북한군 제15사단장 박성철 소장", "red", "보낸 사람"))
sc(1, text("→ 제48연대장", "dark", "받을 사람"))
sc(2, doc("제15사단장 → 제48연대장 (요지)", ["왜 아직 중간 보고가 없는가"], "督促", "북한군 제15사단", "1950. 7 · 재구성"))
sc(2, doc("작전 명령 (요지)", ["제45연대와 함께", "김천 방향 진출 준비"], "命令", "북한군 제15사단", "1950. 7 · 재구성"))
sc(1, black("두 장의 편지가", "말해 주는 것"))
sc(2, reasons("편지가 알려 준 것", [{"text": "적 사단장은 제48연대 궤멸을 모른다", "on": "모른다"}, {"text": "제45연대가 곧 이 길로 온다", "on": "둘째"}]))
sc(1, text("적의 다음 수", "yellow", "국군 손에 들어오다"))
sc(1, stage([C("kr_idle", 0.5, 470, prop="officer+glasses", face="smug", anim="tilt")], [pop("label", 0.5, 0.15, "다음 수가 보인다", on="훔쳐본", color="blue")]))
sc(1, m("mid", "mid", [blue_a(CHEONGJU_HW, 0.2)], tilt=16), callouts=top("청주 → 화령장 · 나머지 대대 도착"))
sc(1, troops(26, side="kr", cols=13, title="제17연대 집결", labels=[{"x": 0.5, "y": 0.74, "text": "연대 전체가 한곳에", "on": "마침내", "color": "blue"}]))
sc(1, ai("kim_alert"), label=DRAMA, callouts=top("연대장 대리 김희준 중령"))
sc(1, stage([C("kr_plead", 0.5, 470, prop="officer+notebook", face="determined", anim="enter")], [pop("label", 0.5, 0.15, "적이라면 어디로?", on="처지가", color="dark")]))
sc(1, m("hwar", "hwar", [groad(0), dash_r(GAL_ROAD, 0.2)], tilt=30), callouts=low("갈령을 넘어올까?"))
sc(1, m("hwar", "hwar", [groad(0), dash_r(GAL_ROAD, 0), droad(0.1), dash_r(DONG_ROAD, 0.3)], tilt=30), callouts=low("다른 골짜기로 올까?"))
sc(1, m("hwar", "hwar", [dash_r(GAL_ROAD, 0), dash_r(DONG_ROAD, 0), badge("sanggok", "차단", TC, 0.3, -50), badge("dongkwan", "차단", TC, 0.5, -50)], tilt=30), callouts=top("두 길을 모두 막는다"))
sc(1, m("hwar", "hwar", [unit("sanggok", "제1대대", "blue", on="제일대대는")], tilt=30))
sc(1, text("제48연대 잔병 대비", "dark", "상곡리 원위치"))
sc(1, m("hwar", "hwar", [unit("sanggok", "제1대대", "blue", 0), unit("hwaryeong", "제3대대 · 예비", "blue", on="제삼대대는")], tilt=30))
sc(1, text("제3대대장 오익경 소령", "dark"))
sc(1, black("그리고", "제2대대"))
sc(1, text("제2대대장 송호림 소령", "yellow", "새 매복의 주인공"))
sc(1, m("hwar", "hwar", [unit("sanggok", "제1대대", "blue", 0), unit("hwaryeong", "제3대대", "blue", 0), blue_a(HW_BONG, 0.2), LOCK("bonghwang", 0.5)], tilt=30), callouts=top("봉황산 북쪽 · 위치 개략"))
sc(1, m("hwar", "hwar", [mark("bonghwang", "blue", 0), droad(0), dash_r(DONG_ROAD, 0.2)], tilt=30), callouts=low("적 연대가 지나갈 길목"))
sc(1, text("7. 19 오후", "dark"))
sc(1, m("dongkwan", "dongkwan", [red_a(SUPPLY, 0.2), unit([127.9, 36.45], "보급 행렬", "red", 0.4)], tilt=32))
sc(1, bars("7. 19 · 북한군 보급 우마차", [{"label": "우마차", "value": 10, "display": "10여 대", "color": "red", "on": "열"}]))
sc(1, m("dongkwan", "dongkwan", [red_a(SUPPLY, 0), clash([127.912, 36.442], 0.2)], tilt=32), callouts=low("기습 · 우마차 격파"))
sc(1, checklist("적 연대의 보급", [{"text": "탄약", "on": "탄약과", "bad": True}, {"text": "식량", "on": "식량이", "bad": True}]))
sc(1, black("진짜 싸움은", "아직이었다"))
sc(1, m("dongkwan", "dongkwan", [droad(0), unit("dk_n", "제2대대", "blue", 0.2), unit("dk_s", "제2대대", "blue", 0.4)], tilt=36), callouts=top("동관리 계곡 · 위치 개략"))
sc(1, m("dongkwan", "dongkwan", [droad(0), badge("dk_n", "능선", "#111", 0.1, -40), badge("dk_s", "능선", "#111", 0.2, -40)], tilt=42), callouts=low("깊고 좁은 골짜기"))
sc(1, m("dongkwan", "dongkwan", [droad(0.1), badge([127.906, 36.434], "개울과 길", TC, 0.3, -40)], tilt=42))
sc(1, text("들어오면 빠져나갈 수 없는 곳", "red"))
sc(1, ai("trench_wait"), label=DRAMA)
sc(1, text("이틀 밤의 기다림", "dark", "7. 19 ~ 7. 21"))
next_act()

# ===== 제5막 동관리 계곡 =====
MID.append(nid())
sc(1, m("dongkwan", "dongkwan", [droad(0)], tilt=36), pauseBefore=0.5, chapter={"num": "제5막", "title": "동관리 계곡"}, callouts=top("1950. 7. 21 새벽"))
sc(1, ai("misty_gorge"), label=DRAMA, sfx=WIND(0))
sc(1, ai("op_post"), label=DRAMA, callouts=top("제2대대 관측소"))
sc(1, stage([C("kr_point", 0.5, 480, prop="officer+helmet+glasses", face="angry", anim="shake", flip=True)], [pop("label", 0.5, 0.15, "중대장들에게", on="중대장들에게", color="dark")]))
sc(2, doc("제2대대장 지시", ["수시로 보고하라", "나의 명령 없이는 절대 사격하지 말라"], "命令", "국군 제17연대 제2대대", "1950. 7. 21 · 재구성"))
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD[:2], 0.2, 60, 0.25)], tilt=36), callouts=low("계곡 입구의 행렬"))
sc(1, ai("column_in_mist"), label=DRAMA)
sc(1, stage([C("kr_shock", 0.5, 470, prop="helmet", face="worried", anim="tilt", flip=True)], [pop("label", 0.5, 0.15, "아군? 피난민?", on="피난민일", color="dark")]))
sc(1, text("피아 식별", "yellow", "적인지 아군인지 확실히 가려라"))
sc(1, text("제7중대장 조경학 중위", "dark", "관측 보고"))
sc(3, checklist("관측 보고", [{"text": "배낭 같은 것", "on": "배낭"}, {"text": "총에 송곳 같은 것", "on": "송곳"}, {"text": "바퀴 달린 기관총", "on": "바퀴"}]))
sc(1, text("송곳 = 소련식 대검", "red"))
sc(1, black("피난민은", "대검을 꽂지 않는다"))
sc(1, ph("dshk"), label=plabel("dshk"))
sc(1, text("북한군 제45연대", "red", "틀림없는 적"))
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD, 0.1, 120, 0.25), red_a(DONG_ROAD, 0.2)], tilt=36))
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD, 0, 150, 0.25), badge(DONG_ROAD[-1], "선두", RED, 0.2, -40), badge(DONG_ROAD[0], "후미", RED, 0.5, -40)], tilt=36))
sc(1, ai("red_flag"), label=DRAMA)
sc(1, text("사격 개시!", "red"))
sc(1, ai("pass_defense"), label=DRAMA, sfx=FAR(0.1))
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD, 0, 150, 0.25), line([[127.913, 36.437], [127.905, 36.434]], 0.1, "#ffb000"), line([[127.918, 36.423], [127.92, 36.43]], 0.2, "#ffb000")], tilt=36))
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD, 0, 150, 0.25), shock(DK_FIRE, 0.1, 0.6)], tilt=36))
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD, 0, 120, 0.25), badge(DONG_ROAD[-1], "✕", RED, 0.2, -40), badge(DONG_ROAD[0], "✕", RED, 0.4, -40)], tilt=36), callouts=low("앞도 뒤도 막힌 길", "red"))
sc(1, m("dongkwan", "dongkwan", [droad(0), badge("dk_n", "가파른 비탈", "#111", 0.1, -40), badge("dk_s", "가파른 비탈", "#111", 0.2, -40)], tilt=44))
sc(1, text("계곡 바닥에 갇힌 적", "red"))
sc(1, stage([C("nk_shock", 0.5, 470, prop="nkcap", face="sweat+shock", anim="shake", flip=True)], [pop("ex", 0.25, 0.28, on="버티지")]))
sc(1, black("1시간 남짓", "총소리가 멎다"))
sc(1, text("제6중대 · 잔적 소탕", "dark"))
sc(1, stage([C("kr_salute", 0.5, 470, prop="officer", face="determined", anim="enter")], [pop("label", 0.5, 0.15, "연대장 도착", on="달려왔습니다", color="blue")]))
sc(1, black("믿기 어려운", "광경"))
sc(1, ai("valley_quiet"), label=DRAMA)
sc(1, m("dongkwan", "dongkwan", [droad(0), blue_a([[127.913, 36.437], [127.912, 36.432]], 0.2), blue_a([[127.918, 36.423], [127.92, 36.428]], 0.3)], tilt=36), callouts=low("1개 중대의 소탕 작전"))
sc(1, text("오후 2시 · 소탕 종료", "blue", "1950. 7. 21"))
sc(1, black("이날 하루의", "전과"))
sc(1, bars("동관리 전투 · 북한군", [{"label": "사살", "value": 356, "display": "356명", "color": "red", "on": "삼백오십육"}]))
sc(1, bars("동관리 전투 · 북한군", [{"label": "사살", "value": 356, "display": "356명", "color": "red", "at": 0}, {"label": "포로", "value": 26, "display": "26명", "color": "dark", "on": "이십육"}]))
sc(5, checklist("동관리 노획", [{"text": "박격포 16문", "on": "열여섯"}, {"text": "대전차포 2문", "on": "대전차포"}, {"text": "기관총 53정", "on": "쉰세"}, {"text": "소총 186정", "on": "백팔십육"}, {"text": "무전기 1대", "on": "무전기"}]))
sc(1, bars("국군 피해", [{"label": "전사", "value": 4, "display": "4명", "color": "blue", "on": "네"}, {"label": "부상", "value": 30, "display": "30명", "color": "dark", "on": "서른"}]))
sc(1, black("콜드 오프닝의", "그 숫자"))
sc(1, cmp("북한군 사살", "356", "국군 전사", "4", "red", "blue"))
sc(1, text("노획 무기만 트럭 한 대 분량", "yellow"))
sc(1, text("한 노병의 말", "dark", "전해지는 이야기"))
sc(1, text("“30년 군 생활에 이렇게 통쾌한 전투는 처음”", "yellow", "전해지는 말"))
sc(1, m("hwar", "hwar", [badge("sanggok", "제48연대 ✕", RED, 0.1, -50), badge("dongkwan", "제45연대 ✕", RED, on="잇따라", dy=-50)], tilt=30))
next_act()

# ===== 제6막 시간을 산 닷새 =====
sc(1, m("hwar", "hwar", [unit([127.92, 36.5], "북한군 제15사단", "red", 0.2, True)], tilt=28), chapter={"num": "제6막", "title": "시간을 산 닷새"}, callouts=top("물러서지 않은 제15사단", "red"))
sc(1, m("hwar", "hwar", [red_a(COUNTER, 0.1), shock([[127.97, 36.455], [127.985, 36.448]], 0.3, 0.8)], tilt=28), sfx=FAR(0.1))
sc(1, black("이번에는", "혼자가 아니었다"))
sc(1, ph("us24_sangju"), label=plabel("us24_sangju"))
sc(1, flags("화령장 방어", [{"flag": "kr", "name": "국군 제17연대", "at": 0}, {"flag": "us", "name": "미 제25사단 제24연대", "on": "함께"}]))
sc(1, m("sobaek", "sobaek", [blue_a([[128.18, 36.56], [128.08, 36.5], [127.99, 36.45]], 0.2), unit("hwaryeong", "국군 제1사단", "blue", on="제일사단이")], tilt=22), callouts=top("1950. 7. 25"))
sc(1, ph("rok_march_aug"), label=plabel("rok_march_aug"), callouts=top("임무 인계"))
sc(1, text("1950. 7. 17 ~ 7. 21", "yellow", "화령장 전투의 닷새"))
sc(1, black("닷새 동안의", "전과"))
sc(2, bars("화령장 전투 합계 · 북한군", [{"label": "사살", "value": 600, "display": "600여 명", "color": "red", "on": "육백여"}, {"label": "포로", "value": 50, "display": "50여 명", "color": "dark", "on": "오십여"}]))
sc(1, text("기록에 따라 사살 625명 · 포로 56명", "dark", "수치는 기록마다 조금씩 다름"))
sc(1, text("국군 전사 · 손에 꼽을 정도", "blue"))
sc(3, checklist("제17연대에 없던 것", [{"text": "포병 지원", "on": "포병의", "bad": True}, {"text": "전차 · 비행기", "on": "전차도", "bad": True}, {"text": "중화기는 박격포뿐", "on": "박격포가"}]))
sc(1, black("숫자보다", "중요한 것"))
sc(1, text("시간", "yellow"))
sc(1, m("south", "south", [dash_r(SANGJU_DAEGU[:3], 0.1), mark("gimcheon", "red", 0.3)], tilt=14), callouts=low("제15사단의 계획 · 상주 → 김천", "red"))
sc(1, m("hwar", "hwar", [badge("sanggok", "제48연대 ✕", RED, 0, -50), badge("dongkwan", "제45연대 ✕", RED, 0, -50), unit([127.92, 36.5], "발이 묶인 사단", "red", 0.3)], tilt=28))
sc(1, text("흘러간 귀중한 날들", "dark"))
sc(1, m("south", "south", [unit("sangju", "미 제25사단", "blue", on="제이십오사단이")], tilt=14))
sc(1, m("south", "south", [unit("sangju", "미 제25사단", "blue", 0), unit("hamchang", "국군 제1사단", "blue", on="제일사단도")], tilt=14))
sc(1, ai("walker_map"), label=DRAMA)
sc(1, ph("naktong_map"), label=plabel("naktong_map"), callouts=top("1950. 8월 초"))
sc(1, m("naktong", "naktong", [line(PUSAN, 0.1, "#7fd3ff"), line(PUSAN_E, 0.3, "#7fd3ff")], tilt=12), callouts=low("남은 마지막 방어선"))
sc(1, text("화령장의 닷새 = 방어선을 세울 시간", "yellow"))
sc(1, black("이 승리의", "세 가지 비밀"))
SECRETS = lambda a, b, c: reasons("화령장의 세 가지 비밀", [dict({"text": "정보"}, **a), dict({"text": "지형"}, **b), dict({"text": "참을성"}, **c)])
sc(1, SECRETS({"on": "정보였습니다"}, {"later": True}, {"later": True}))
sc(3, checklist("정보의 세 고리", [{"text": "주민 엄봉림의 신고", "on": "엄봉림의"}, {"text": "자전거 탄 전령", "on": "자전거"}, {"text": "적 사단장의 편지", "on": "편지가"}]))
sc(1, text("적보다 적을 더 잘 안 국군", "blue"))
sc(1, SECRETS({"at": 0}, {"on": "지형이었습니다"}, {"later": True}))
sc(1, m("hwar", "hwar", [badge("sanggok", "상곡리 골짜기", TC, 0.1, -50), badge("dongkwan", "동관리 골짜기", TC, 0.3, -50)], tilt=38))
sc(1, text("숨을 곳도 빠져나갈 곳도 없다", "red"))
sc(1, text("숫자의 열세 → 산과 골짜기로", "yellow"))
sc(1, checklist("적이 가장 약한 순간", [{"text": "행군할 때", "on": "행군하거나"}, {"text": "쉬고 있을 때", "on": "쉬고"}]))
sc(1, text("바로 그 순간을 노렸다", "yellow"))
sc(1, SECRETS({"at": 0}, {"at": 0}, {"on": "참을성이었습니다"}))
sc(1, m("sanggok", "sanggok", [groad(0), unit("sg_mid", "밥 먹으러 모인 적", "red", 0.2)], tilt=34), callouts=low("상곡리 · 저녁 집결까지"))
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD, 0.1, 140, 0.25)], tilt=36), callouts=low("동관리 · 대열이 다 들어올 때까지"))
sc(1, text("“나의 명령 없이는 절대 쏘지 마라”", "yellow"))
sc(1, text("계곡을 함정으로 만든 한마디", "dark"))
sc(1, doc("특별 포상 (요지)", ["제17연대 장병 전원", "1계급 특진"], "表彰", "대한민국 정부", "1950. 7 · 재구성"))
sc(1, text("연대장 대리 김희준 중령 외 전원", "yellow"))
sc(1, troops(26, side="kr", cols=13, title="제17연대 1계급 특진", labels=[{"x": 0.5, "y": 0.74, "text": "2,600여 명 전원", "on": "이천육백여", "color": "yellow"}]))
sc(1, text("건군 이래 두 번째", "blue", "부대 전원 특진 기록"))
sc(1, stage([C("kr_salute", 0.5, 480, prop="helmet+medal", face="sparkle", anim="bounce", flip=True)], [pop("label", 0.5, 0.15, "귀한 희소식", on="희소식이었습니다", color="yellow")]))
next_act()

# ===== 제7막 화령장이 남긴 것 =====
MID.append(nid())
sc(1, m("naktong", "naktong", [line(PUSAN, 0, "#7fd3ff"), line(PUSAN_E, 0, "#7fd3ff")], tilt=12), pauseBefore=0.5, chapter={"num": "제7막", "title": "화령장이 남긴 것"}, callouts=top("1950. 8월 · 낙동강"))
sc(1, m("naktong", "naktong", [line(PUSAN, 0, "#7fd3ff"), line(PUSAN_E, 0, "#7fd3ff"), mark("dabudong", "blue", on="다부동과"), mark("yeongcheon", "blue", on="영천"), mark("pohang", "blue", on="포항")], tilt=12))
sc(1, ai("dabu_night"), label=DRAMA)
sc(1, m("south", "south", [red_a(SANGJU_FIGHT, 0.1), mark("sangju", "blue", 0.3)], tilt=14), callouts=top("상주 · 7월 말까지"))
sc(1, text("화령장에서 꺾인 그 사단", "red", "북한군 제15사단"))
sc(1, ai("tide_dawn"), label=DRAMA, callouts=top("1950. 9. 15 · 인천"))
sc(1, black("상륙 부대 속의", "낯익은 이름"))
sc(1, ph("inchon_embark"), label=plabel("inchon_embark"), callouts=top("국군 제17연대"))
sc(1, flat([127.6, 36.3], 5.5, [fpin([129.04, 35.12], "부산", at=0.1, flag="kr", side="right"), fpin([126.62, 37.47], "인천", on="인천으로", flag="kr", side="left")],
           [route([129.04, 35.12], [126.62, 37.47], "바닷길", on="배를", bend=0.45)], [{"ll": [125.6, 35.6], "text": "서해", "style": "sea"}]))
sc(1, m("korea", "korea", [mark("ongjin", "blue", 0.1), mark("incheon", "blue", 0.4)]), callouts=low("옹진 → 바다 → 인천"))
sc(1, ph("rok17_7th"), label=plabel("rok17_7th"))
sc(1, text("석 달 전 쫓겨났던 연대", "dark", "옹진반도 → 서울 탈환"))
sc(1, black("이제", "처음의 질문으로"))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05, "kicker": "■ 처음의 질문 ■"}})
sc(1, text("한 사람의 영웅이 아니었다", "dark"))
sc(1, ai("elder_runs"), label=DRAMA)
sc(1, ph("pow_19th"), label=plabel("pow_19th"))
sc(1, ai("letters_table"), label=DRAMA)
sc(1, ai("crest_wait"), label=DRAMA)
sc(1, m("dongkwan", "dongkwan", [droad(0), swarm(DONG_ROAD, 0, 120, 0.25), unit("dk_n", "국군", "blue", 0.2), unit("dk_s", "국군", "blue", 0.3)], tilt=36), callouts=low("좁은 골짜기 = 거대한 함정"))
sc(1, text("적이 우리를 모를 때 · 우리는 적을 알았다", "yellow"))
sc(1, text("화령장의 비밀", "red"))
sc(1, black("숫자가 적어도", "이길 수 있다"))
sc(1, ai("dawn_victory"), label=DRAMA)
sc(1, ai("withdraw"), label=DRAMA)
sc(1, text("모든 곳에서 진 것은 아니었다", "blue"))
sc(1, text("국군 단독 최대의 승리 가운데 하나", "yellow", "화령장 전투 · 1950"))
SOMBER = nid()
sc(1, ai("memorial_hall"), label=DRAMA, callouts=top("상주시 화서면 · 화령장전투전승기념관"))
sc(1, text("2018년 10월 개관", "dark", "화령장전투전승기념관"))
sc(1, text("해마다 열리는 전승 기념행사", "dark", "상주시 화서면"))
sc(1, ph("rok_kp"), label=plabel("rok_kp"), callouts=top("백발이 된 참전 용사들"))
sc(1, text("그해 여름의 2,600명", "dark", "이제 대부분 세상을 떠난 병사들"))
sc(1, m("sobaek", "sobaek", [line(BOEUN_SANGJU, 0.1, "#ffd400"), mark("hwaryeong", "blue", 0.3)], tilt=22), callouts=low("지금도 상주와 보은을 잇는 길"))
sc(1, ai("valley_today"), label=DRAMA)
sc(1, ai("yuhak_dawn"), label=DRAMA)
sc(1, ph("rok_m1"), label=plabel("rok_m1"))
sc(1, text("참아 낸 몇 시간 · 벌어 준 몇 달", "yellow"))
sc(2, {"type": "endcard", "title": "화령장의 골짜기를 지킨\n모든 이들을 기억하며", "q": pin("rok_july")}, tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 =====
# 재사용 (파일·서명 복사, 추가 비용 0)
REUSE = {
    "dawn_rain": "chuncheon", "nk_plan": "chuncheon", "kim_alert": "chuncheon", "withdraw": "chuncheon",
    "t34_column": "dabudong", "dabu_night": "dabudong", "yuhak_dawn": "dabudong",
    "trucks": "yeongcheon", "dawn_victory": "yeongcheon",
    "walker_map": "naktong", "tide_dawn": "naktong",
    "nk766_infiltrate": "ep28-pohang",
    "crest_wait": "ep27-tongyeong", "jindong_ambush": "ep27-tongyeong", "mangil_ambush": "ep27-tongyeong", "trench_wait": "ep27-tongyeong", "pass_defense": "ep27-tongyeong",
}
# 새 그림 (Cloudflare Workers AI 무료 · 사람이 나오는 장면은 국기 볼 없이 작은 실루엣 위주로 — 국적 표시 오류 방지)
TAIL = ", painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no flags, no text, no letters."
NEW = {
    "misty_gorge": "A deep narrow mountain valley in Korea at dawn in July 1950, a small stream and a dirt road winding along the bottom between steep forested slopes, thick low morning mist filling the valley, silent and tense, no people visible" + TAIL,
    "column_in_mist": "A long column of soldiers in plain khaki 1950 uniforms and soft caps with backpacks and bayonets fixed on their rifles, dragging small wheeled machine guns, marching into a misty narrow mountain valley road at dawn, seen from high above on a ridge through tree branches, small distant figures" + TAIL,
    "red_flag": "A hand raising a small plain red signal flag high on a rocky hilltop above a misty mountain valley at dawn, close-up of the arm in an olive drab sleeve and the flag, the flag is the only red color in the image" + TAIL,
    "valley_quiet": "A quiet narrow Korean mountain valley in late morning after a battle, drifting gunsmoke over the dirt road, abandoned small wheeled machine guns, scattered backpacks and overturned wooden carts, no bodies, no people visible" + TAIL,
    "bicycle_courier": "A lone soldier in a plain khaki 1950 uniform and soft field cap riding an old black bicycle down a dusty winding mountain dirt road between green forested hills in Korea on a hot July 1950 morning, seen from behind roadside bushes, tense" + TAIL,
    "village_school": "A small one-story 1950 rural Korean elementary school building of wood with a dark tiled roof and a dirt playground with a few old trees, rifles stacked in small tripods in the yard, green mountains behind, hot July afternoon, no people visible" + TAIL,
    "elder_runs": "An elderly Korean farmer in white 1950 hanbok clothes and a straw hat hurrying along a narrow path between green rice paddies toward a small village of thatched houses, pointing back urgently at a mountain pass, hot July day" + TAIL,
    "oxcart_rest": "A long column of wooden ox carts loaded with mortars, small anti-tank guns and wooden ammunition boxes halted along a narrow dirt road at the bottom of a deep green mountain valley in Korea at dusk in July 1950, oxen unhitched and grazing, small distant figures of soldiers in khaki uniforms and soft caps gathering around cooking fires with thin smoke rising, seen from high on a forested ridge through leaves" + TAIL,
    "letters_table": "Two folded handwritten military letters on faded yellowish paper with a round red ink stamp, lying on a rough wooden field table beside a folded paper map, a compass and an oil lamp, July 1950, close-up, the handwriting blurred and unreadable" + TAIL,
    "op_post": "A rocky hilltop observation post at dawn above a misty narrow mountain valley in Korea, a pair of old binoculars resting on a sandbag beside a 1950 field telephone and a folded plain red signal flag, July 1950, no people visible" + TAIL,
    "memorial_hall": "A modern war memorial hall with a tall granite memorial tower in a quiet park of a Korean rural town surrounded by green mountains in summer, flower beds, soft morning light, no people visible" + TAIL,
    "valley_today": "A peaceful Korean mountain valley in summer today with green rice paddies, a small village of modern farmhouses and a quiet two-lane road along a stream, soft golden evening light, no people visible" + TAIL,
}
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
board = {"title": "협곡에 갇힌 정예 사단", "subtitle": "화령장 전투 · 국군 제17연대 단독 매복전 · 1950", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         "target_sec": 1230, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap],
      "ai", len(AI), "pins", len(PINS), "stage", len(stages), "photo", sum(1 for s in S if s["visual"]["type"] == "photo"))
print("char uses", dict(cnt))
