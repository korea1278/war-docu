# EP28 포항 안강·기계 전투 & 형산강 방어선 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 연출 스타일 v2 + 화면 업그레이드 2단계 + 롱폼 표준(LONGFORM_STANDARD: 막 단위 TTS · 절제된 효과음 · BGM -24dB · 자막 28자 · 싱크 ±0.5초)
# + 캐릭터 반복 방지 규칙: stage chars[].face / prop / anim (Stage.tsx), 같은 조합 연속·3회 초과 금지 assert
import collections
import glob
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
EP = HERE.name
raw = (HERE / "script.md").read_text(encoding="utf-8")
ACTS = []
for a in raw.split("\n## ")[1:]:
    body = [l for l in a.split("\n")[1:] if l and not l.startswith((">", "#"))]
    ACTS.append([s for l in body for s in re.split(r"(?<=[.?])\s+", l.strip()) if s])


# 자막 숫자 표기 (사용자 지시: 숫자는 숫자로) — 긴 것부터
SUBS = [
    ("천구백오십년 팔월 십일일 새벽 네 시", "1950년 8월 11일 새벽 4시"), ("천구백오십칠년 팔월 십일일", "1957년 8월 11일"), ("천구백오십년 구월 십오일", "1950년 9월 15일"),
    ("천구백오십년 팔월 초", "1950년 8월 초"), ("팔월 십일일 새벽 네 시", "8월 11일 새벽 4시"), ("구월 십칠일 새벽 네 시", "9월 17일 새벽 4시"),
    ("팔월 십칠일 아침 일곱 시", "8월 17일 아침 7시"), ("팔월 구일부터 구월 이십이일까지 사십사 일", "8월 9일부터 9월 22일까지 44일"),
    ("팔월 십일일", "8월 11일"), ("팔월 이십육일", "8월 26일"), ("팔월 이십일", "8월 20일"), ("팔월 십구일", "8월 19일"), ("팔월 십칠일", "8월 17일"),
    ("팔월 십육일", "8월 16일"), ("팔월 십오일", "8월 15일"), ("팔월 십삼일", "8월 13일"), ("팔월 십일", "8월 10일"), ("팔월 구일", "8월 9일"),
    ("팔월 초", "8월 초"), ("팔월 공세", "8월 공세"), ("구월 십팔일", "9월 18일"), ("구월 십이일", "9월 12일"), ("구월 육일", "9월 6일"), ("구월 오일", "9월 5일"),
    ("구월 이일", "9월 2일"), ("구월 공세", "9월 공세"), ("새벽 네 시", "새벽 4시"), ("새벽 세 시", "새벽 3시"), ("오후 세 시", "오후 3시"),
    ("일흔한 명", "71명"), ("마흔여덟 명", "48명"), ("마흔일곱 명", "47명"), ("열한 시간", "11시간"), ("열세 명", "13명"), ("열 명", "10명"),
    ("엠원", "M1"), ("제칠백육십육 독립연대", "제766 독립연대"), ("칠백육십육 연대", "766연대"), ("제십이사단", "제12사단"), ("제오사단", "제5사단"),
    ("제삼사단", "제3사단"), ("제팔군", "제8군"), ("제십칠연대", "제17연대"), ("제이십오연대", "제25연대"), ("제이십이연대", "제22연대"), ("제오공군", "제5공군"),
    ("이백오십 발", "250발"), ("사십오 대", "45대"), ("구천여 명", "9,000여 명"), ("천이백여 명", "1,200여 명"), ("천여 명", "1,000여 명"),
    ("이천삼백여 명", "2,300여 명"), ("만 오천여 명", "1만 5,000여 명"), ("이백팔십구 미터", "289m"), ("십이 킬로미터", "12km"), ("삼 학년", "3학년"),
    ("두 개 중대", "2개 중대"), ("두 개 소대", "2개 소대"), ("한 개 대대", "1개 대대"), ("일 년 남짓", "1년 남짓"),
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


SEAV = {"coast", "pohang", "city", "river", "corridor", "gonje"}


def m(fr, to=None, items=None, **kw):
    v = {"type": "map", "from": fr, "to": to or fr, "items": items or []}
    # demSea는 pohang_sea 래스터 안쪽 뷰에서만 (넓은 뷰에 켜면 래스터 사각 경계가 비침)
    if all(k in SEAV for k in [fr, to or fr] + kw.get("flight", [])):
        v["demSea"] = True
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


def doc(head, rows, stamp="軍 秘", org="국군 제3사단", note="재구성 · 내용 요약"):
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


# 사진: 스카우트 catalog.json 설명으로 확인한 파일 (미 국립문서기록관리청·미 해군·미 육군·국방부·NASA 공개 자료, CC 일부)
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
NOTE = "위치 개략"
# 좌표는 개략 (포항여중·곤제봉·운제산·독석리·기관총 진지는 현재 지명 기준 근사)
P = {
    "pohang": [129.365, 36.032, "포항"], "school": [129.357, 36.041, "포항여중"], "airfield": [129.42, 35.988, "영일 비행장"],
    "gigye": [129.215, 36.062, "기계"], "angang": [129.225, 35.99, "안강"], "gonje": [129.215, 35.947, "곤제봉"], "gyeongju": [129.225, 35.856, "경주"],
    "heunghae": [129.345, 36.11, "흥해"], "bihak": [129.17, 36.135, "비학산"], "unje": [129.335, 35.977, "운제산"],
    "yeongdeok": [129.365, 36.415, "영덕"], "ganggu": [129.385, 36.36, "강구"], "dokseok": [129.375, 36.235, "독석리"], "guryongpo": [129.555, 35.99, "구룡포"],
    "cheongsong": [129.057, 36.435, "청송"], "daegu": [128.6, 35.87, "대구"], "yeongcheon": [128.94, 35.973, "영천"], "busan": [129.04, 35.18, "부산"],
    "masan": [128.57, 35.21, "마산"], "seoul": [126.978, 37.566, "서울"], "incheon": [126.62, 37.47, "인천"],
}
V = {
    "korea": {"center": [127.6, 36.4], "span": 4.6}, "perimeter": {"center": [128.75, 35.75], "span": 1.9},
    "ne": {"center": [129.22, 36.2], "span": 1.0}, "east": {"center": [129.2, 36.0], "span": 0.85}, "coast": {"center": [129.32, 36.22], "span": 0.6},
    "pohang": {"center": [129.3, 36.02], "span": 0.32}, "corridor": {"center": [129.225, 36.0], "span": 0.24}, "river": {"center": [129.31, 35.995], "span": 0.24},
    "city": {"center": [129.365, 36.025], "span": 0.12}, "gonje": {"center": [129.22, 35.955], "span": 0.12},
}
# 1950년 8월 낙동강 방어선 (개략)
PERIM = [[128.36, 35.04], [128.38, 35.25], [128.45, 35.4], [128.42, 35.6], [128.38, 35.85], [128.42, 36.02], [128.62, 36.12], [128.95, 36.16], [129.3, 36.2], [129.42, 36.12]]
front = {"k": "front", "path": PERIM, "at": 0}
# 형산강 (개략 — 경주 → 안강 → 포항 남쪽 바다)
RIVER = [[129.215, 35.86], [129.222, 35.92], [129.232, 35.972], [129.255, 35.99], [129.29, 36.0], [129.325, 36.008], [129.36, 36.015], [129.395, 36.02]]
RIVER_S = [[129.255, 35.985], [129.29, 35.995], [129.325, 36.003], [129.36, 36.01], [129.39, 36.014]]
river = lambda at=0: {"k": "line", "path": RIVER, "color": "#00E5FF", "glow": True, "at": at}
NK5_COAST = [[129.365, 36.415], [129.385, 36.36], [129.37, 36.25], [129.35, 36.15], [129.345, 36.11], [129.36, 36.05]]
NK12_MTN = [[129.057, 36.435], [129.1, 36.3], [129.15, 36.18], [129.215, 36.065]]
NK12_SOUTH = [[129.215, 36.062], [129.22, 36.02], [129.225, 35.99], [129.222, 35.93], [129.225, 35.86]]
NK766 = [[129.33, 36.38], [129.28, 36.25], [129.25, 36.13], [129.24, 36.07]]
ROAD_DAEGU = [[129.365, 36.03], [129.2, 36.0], [128.94, 35.973], [128.6, 35.87]]
ROAD_BUSAN = [[129.36, 36.02], [129.225, 35.86], [129.2, 35.6], [129.04, 35.18]]
EVAC = [[129.375, 36.235], [129.48, 36.2], [129.58, 36.08], [129.555, 35.99]]
TO_GIGYE_S = [[129.225, 35.99], [129.22, 36.025], [129.215, 36.055]]
TO_GIGYE_W = [[129.13, 36.1], [129.17, 36.08], [129.205, 36.065]]
OUT_SOUTH = [[129.36, 36.035], [129.37, 36.0], [129.39, 35.97]]
CAPLINE = [[129.17, 36.035], [129.2, 36.03], [129.24, 36.035]]
MG = [129.355, 36.02]  # 형산강 건너 기관총 진지 (개략)
plug = None
LOCK = lambda p, at=0.3, text=None, color=None, on=None: dict({"k": "lock", "p": p, "text": text or P[p][2]}, **({"on": on} if on else {"at": at}), **({"color": color} if color else {}))
badge = lambda p, t, c="#111", at=0.3, dy=-70, on=None: dict({"k": "badge", "p": p, "text": t, "color": c, "dy": dy}, **({"on": on} if on else {"at": at}))
red_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "red", "width": w}, **({"on": on} if on else {"at": at}))
blue_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "blue", "width": w}, **({"on": on} if on else {"at": at}))
dash_r = lambda path, at=0.2: {"k": "arrow", "path": path, "color": "red", "dash": True, "at": at}
mark = lambda p, color="red", at=0, text=None, on=None: dict({"k": "marker", "p": p, "color": color}, **({"text": text} if text else {}), **({"on": on} if on else {"at": at}))
unit = lambda p, t, color="red", at=0.1, pulse=False: dict({"k": "unit", "p": p, "text": t, "color": color, "at": at}, **({"pulse": True} if pulse else {}))
obj = lambda n, p, text, at=0, takenAt=None, takenOn=None: dict({"k": "obj", "n": n, "p": p, "text": text, "at": at}, **({"takenAt": takenAt} if takenAt is not None else {}), **({"takenOn": takenOn} if takenOn else {}))
clash = lambda p, at=0.3, size=1.0: {"k": "clash", "p": p, "at": at, "period": 0.9, "size": size}
shock = lambda pts, at=0.2, period=0.7: {"k": "shock", "pts": pts, "at": at, "period": period}
swarm = lambda path, at=0.1, n=120, width=None: dict({"k": "swarm", "path": path, "at": at, "n": n}, **({"width": width} if width else {}))
plane = lambda path, at=0.1, n=1, dur=3.0, hit=False, size=1.0: {"k": "plane", "path": path, "at": at, "n": n, "dur": dur, "hit": hit, "size": size}
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]
SW = lambda at=0: [{"id": "whoosh", "at": at}]
FAR = lambda at=0.1: [{"id": "artillery_far", "at": at}]
PING = lambda at=0.6: [{"id": "ping", "at": at}]
WATER = lambda at=0.1: [{"id": "water", "at": at}]
WIND = lambda at=0: [{"id": "wind", "at": at}]
NKC = "nkcap"
CTA_TEXT = "구독 · 좋아요로 다음 이야기까지 함께해 주세요"

# ===== 콜드 오프닝 =====
sc(1, ai("school_dawn"), label=DRAMA, callouts=top("1950. 8. 11 · 새벽 4시"), sfx=WIND(0.2))
sc(1, m("coast", "city", [LOCK("school", 0.8)], flight=["coast", "pohang", "city"], flightDur=3.0, hud=True), sfx=SW(0) + PING(0.9))
sc(1, ai("wall_boys"), label=DRAMA)
sc(1, stage([C("kr_idle", 0.5, 480, prop="cap", face="worried")], [pop("label", 0.5, 0.16, "중학생 · 고등학생", on="중학생과", color="yellow")]))
sc(1, ai("red_eyes"), label=DRAMA, callouts=low("지급받은 M1 소총"))
sc(1, text("훈련은 며칠", "red", "총 쏘는 법 정도가 전부"))
sc(1, ai("fog_mountain"), label=DRAMA)
sc(1, stage([C("nk_point", 0.55, 480, flip=True, prop=NKC, face="angry", anim="enter")], [pop("label", 0.55, 0.15, "북한군 정규군", on="정규군이었습니다", color="red")]))
sc(1, text("71명", "yellow", "학도의용군"))
sc(1, checklist("그날 새벽 학도병에게 없던 것", [{"text": "지휘할 장교", "on": "장교도", "checkOn": "장교도", "bad": True}, {"text": "지원 병력", "on": "지원", "checkOn": "않았습니다", "bad": True}]))
sc(1, text("11시간", "blue", "1950. 8. 11 새벽 ~ 오후"))
sc(1, bars("기록 기준 · 자료에 따라 47명", [{"label": "학도병", "value": 71, "display": "71명", "color": "blue", "at": 0.1}, {"label": "전사", "value": 48, "display": "48명", "color": "red", "on": "마흔여덟"}]))
sc(1, stage([C("kr_shrug", 0.4, 460, prop="cap", face="sweat")], [pop("q", 0.7, 0.3, at=0.2, size=220)], title="왜 학생들이 그곳에?"))
sc(1, black("그 11시간은", "무엇을 바꿨나"))
sc(1, m("korea", "perimeter", [front], flight=["korea", "perimeter"], flightDur=3.0), sfx=SW(0))
sc(1, m("perimeter", "perimeter", [front, mark("pohang", "red", 0), {"k": "line", "path": ROAD_BUSAN, "color": "#ffd400", "glow": True, "on": "경주가"}, mark("busan", "blue", on="부산이")]))
sc(1, m("perimeter", "perimeter", [front, dash_r(ROAD_BUSAN, 0.2)]), callouts=top("동해안이 뚫리면", "red"))
sc(1, m("perimeter", "perimeter", [dict(front, glow=True), badge([129.42, 36.08], "마지막 문", "#c9242c", 0.3, -60)], tilt=22))
sc(1, cmp("학생들의", "11시간", "형산강의", "마지막 방어선", "blue", "red"))
sc(1, black("둘은 어떻게 이어질까", "끝까지 보시면 알게 됩니다"))
sc(1, {"type": "titlecard", "title": "포항 결전", "sub": "안강·기계 전투와 형산강 방어선 · 1950", "at": 0, "q": pin("student_train")}, flash=True)
next_act()

# ===== 제1막 동해안의 문이 열리다 =====
sc(1, m("korea", "perimeter", [front], flight=["korea", "perimeter"], flightDur=3.0), chapter={"num": "제1막", "title": "동해안의 문이 열리다"}, callouts=top("1950년 8월 초 · 부산을 둘러싼 땅"))
sc(1, m("perimeter", "perimeter", [front, badge([128.28, 35.55], "낙동강", "#2e66d8", on="낙동강이", dy=0), badge([128.85, 36.3], "산줄기", "#111", on="산줄기가", dy=0)]))
sc(1, m("perimeter", "perimeter", [dict(front, glow=True), badge([128.4, 35.4], "낙동강 방어선", "#2e66d8", 0.3, 0)], tilt=22))
sc(1, m("perimeter", "east", [front, LOCK("pohang", 0.8)], flight=["perimeter", "east"], flightDur=2.4), sfx=PING(0.9))
sc(1, ph("cav_land"), label=plabel("cav_land"))
sc(1, text("세 개의 길", "yellow", "포항에 모인 길"))
sc(1, m("perimeter", "perimeter", [front, {"k": "line", "path": ROAD_DAEGU, "color": "#ffd400", "glow": True, "at": 0.2}, mark("daegu", "blue", on="대구로")]), callouts=top("① 대구로 가는 동서 도로"))
sc(1, text("낙동강 방어선의 심장 대구", "blue", "임시 정부 · 미 제8군 사령부"))
sc(1, m("perimeter", "perimeter", [front, red_a([[129.365, 36.03], [129.0, 35.98], [128.65, 35.88]], 0.2), mark("daegu", "blue", 0)]), callouts=low("포항을 잃으면 대구의 등 뒤가 열린다"))
sc(1, m("perimeter", "perimeter", [front, {"k": "line", "path": ROAD_BUSAN, "color": "#ffd400", "glow": True, "at": 0.2}, mark("gyeongju", "blue", on="경주를"), mark("busan", "blue", on="부산으로")]), callouts=top("② 경주 → 부산 직통로"))
sc(1, m("east", "east", [{"k": "line", "path": NK12_SOUTH, "color": "#ffd400", "glow": True, "at": 0.1}], tilt=30), callouts=low("산이 적은 평탄한 회랑"))
sc(1, text("③ 바다와 하늘", "yellow"))
sc(1, m("pohang", "pohang", [LOCK("airfield", 0.3)], tilt=28), sfx=PING(0.4))
sc(1, ph("f51_line"), label=plabel("f51_line"))
sc(1, checklist("포항이 쥔 것", [{"text": "길", "on": "길과", "checkOn": "길과"}, {"text": "항구", "on": "항구와", "checkOn": "항구와"}, {"text": "비행장", "on": "비행장을", "checkOn": "비행장을"}]))
sc(1, stage([C("nk_idle", 0.5, 480, prop=NKC, face="smug", anim="tilt")], [pop("label", 0.5, 0.15, "포항을 노려라", on="알고", color="red")]))
sc(1, m("perimeter", "perimeter", [front, red_a([[127.9, 35.5], [128.3, 35.5]], 0.1), red_a([[128.6, 36.55], [128.6, 36.17]], 0.3), red_a([[129.1, 36.55], [129.2, 36.25]], 0.5)]))
sc(1, text("8월 공세", "red", "1950년 8월 초 · 북한군 총공격"))
sc(1, m("ne", "ne", [red_a(NK5_COAST, 0.2), red_a(NK12_MTN, 0.5), red_a(NK766, 0.8)]), callouts=top("세 갈래의 칼끝", "red"))
sc(1, m("ne", "ne", [red_a(NK5_COAST, 0.1, 1.2), unit("yeongdeok", "북한군 제5사단", at=0.3)]))
sc(1, m("ne", "ne", [red_a(NK12_MTN, 0.1, 1.2), unit("cheongsong", "북한군 제12사단", at=0.3)]))
sc(1, m("ne", "ne", [red_a(NK766, 0.1, 1.0), unit([129.3, 36.3], "766독립연대", at=0.3)]))
sc(1, ai("nk766_infiltrate"), label=DRAMA)
sc(1, m("ne", "ne", [unit([129.37, 36.33], "국군 제3사단", "blue", 0.1), unit([129.0, 36.3], "국군 수도사단", "blue", 0.5)]))
sc(1, ph("yongdok_rest"), label=plabel("yongdok_rest"))
sc(1, black("문제는", "산 쪽"))
sc(1, m("ne", "ne", [swarm(NK12_MTN, 0.1, 140)], tilt=24), callouts=low("지키는 부대가 없던 산길 · 개략"))
sc(1, m("ne", "corridor", [LOCK("gigye", 0.8)], flight=["ne", "pohang", "corridor"], flightDur=3.0, hud=True), callouts=top("8월 9일 · 기계 점령", "red"), sfx=SW(0) + PING(0.9))
sc(1, m("corridor", "corridor", [mark("gigye", "red", 0), red_a([[129.215, 36.06], [129.222, 36.02], [129.225, 35.995]], on="고개"), badge("angang", "안강", "#111", on="안강이", dy=-60)], tilt=30))
sc(1, m("east", "east", [mark("gigye", "red", 0), red_a(NK12_SOUTH, 0.2), mark("gyeongju", "blue", on="경주가")]))
sc(1, m("perimeter", "perimeter", [front, dash_r([[129.225, 35.86], [129.2, 35.6], [129.04, 35.2]], 0.2), mark("busan", "blue", 0)]), callouts=top("경주 → 부산 · 막아설 지형이 없다", "red"))
sc(1, m("ne", "ne", [red_a(NK5_COAST, 0.1, 1.1), mark("ganggu", "red", on="강구를"), mark("heunghae", "red", on="흥해까지")]))
sc(1, m("pohang", "pohang", [mark("heunghae", "red", 0), mark("pohang", "blue", 0), red_a([[129.345, 36.11], [129.355, 36.06]], 0.3)], tilt=26))
sc(1, m("ne", "ne", [unit([129.37, 36.33], "제3사단", "blue", 0), red_a(NK5_COAST[2:], 0), clash([129.34, 36.16], 0.4)]), callouts=low("등 뒤가 끊긴 제3사단"))
sc(1, black("동해안의 문이", "열리기 직전"))
next_act()

# ===== 제2막 텅 빈 회랑 기계와 안강 =====
sc(1, ai("walker_map"), label=DRAMA, chapter={"num": "제2막", "title": "텅 빈 회랑 기계와 안강"})
sc(1, doc("긴급 보고", ["포항 북서쪽 산악 지대", "북한군 정규군 출현"], "緊急", "미 제8군 정보 보고"))
sc(1, stage([C("us_shrug", 0.5, 480, prop="officer", face="smug")], [pop("label", 0.5, 0.15, "게릴라겠지?", on="게릴라라고", color="dark")]))
sc(1, black("정찰 결과는", "달랐다"))
sc(1, text("사단 규모 정규군", "red", "북한군 제12사단"))
sc(1, stage([C("us_shock", 0.5, 480, prop="officer+glasses", face="coldsweat")], [pop("ex", 0.75, 0.3, at=0.3)]))
sc(1, m("east", "east", [mark("gigye", "red", 0), mark("angang", "red", at=0.4), mark("gyeongju", "red", on="경주")]))
sc(1, m("perimeter", "perimeter", [front, red_a([[129.215, 36.06], [129.225, 35.86], [129.0, 35.7]], 0.2), {"k": "line", "path": [[128.6, 35.87], [128.9, 35.7], [129.04, 35.2]], "color": "#ffd400", "glow": True, "at": 0}, clash([128.98, 35.72], 0.7)]), callouts=low("대구–부산 보급로 · 개략"))
sc(1, m("perimeter", "perimeter", [dict(front, glow=True), shock([[128.6, 35.9], [128.9, 36.1], [128.45, 35.5]], 0.2)], tilt=24), callouts=top("방어선 전체가 뒤에서 무너진다", "red"))
sc(1, m("corridor", "corridor", [badge("angang", "병력 없음", "#c9242c", 0.2, -70)], tilt=30))
sc(1, ph("rok_march"), label=plabel("rok_march"))
sc(1, doc("작전 명령", ["포항 지구 전투 사령부 편성", "기계 일대의 적을 몰아내라"], "命令", "미 제8군", "1950. 8. 10 · 재구성"))
sc(1, checklist("긁어모은 부대", [{"text": "제17연대", "on": "제십칠연대와", "checkOn": "제십칠연대와"}, {"text": "제25연대", "on": "제이십오연대", "checkOn": "제이십오연대"}, {"text": "경찰 · 해병대 대대", "on": "경찰과", "checkOn": "해병대"}]))
sc(1, text("실전 경험은 제17연대뿐", "yellow"))
sc(1, stage([C("kr_shock", 0.5, 460, prop="helmet", face="sweat", anim="shake")], [pop("label", 0.5, 0.15, "신병 부대", on="신병", color="dark")]))
sc(1, m("pohang", "pohang", [blue_a([[129.25, 35.93], [129.33, 35.955], [129.41, 35.985]], 0.2), LOCK("airfield", 0.6)], tilt=26))
sc(1, stage([C("us_salute", 0.5, 480, prop="helmet", face="determined")], [pop("label", 0.5, 0.15, "브래들리 특수 임무 부대", on="브래들리", color="blue")]))
sc(1, text("보병 1개 대대 중심", "blue", "미 제2사단 제9연대 제3대대 중심"))
sc(1, m("pohang", "pohang", [mark("airfield", "blue", 0), {"k": "radar", "p": "airfield", "at": 0.2, "size": 1.0, "color": "#2e9bff"}], tilt=28))
sc(1, black("비행장으로 가던 길", "사고"))
sc(1, ai("ambush_road"), label=DRAMA, callouts=top("8. 11 새벽 · 경주 북쪽 산길"))
sc(1, m("east", "east", [clash([129.24, 35.92], 0.2), red_a(NK766, 0, 0.8)]), callouts=low("766연대로 추정 · 위치 개략"))
sc(1, text("큰 피해", "red", "보병 1개 중대 · 포병 일부"))
sc(1, m("east", "east", [unit([129.24, 35.94], "북한군", at=0.2, pulse=True)]))
sc(1, m("corridor", "corridor", [mark("angang", "blue", 0)], tilt=28), callouts=top("안강", "dark"))
sc(1, m("corridor", "corridor", [blue_a(TO_GIGYE_S, 0.2), mark("gigye", "red", 0)], tilt=30), callouts=low("8. 11 · 기계 탈환 공격"))
sc(1, m("corridor", "corridor", [clash([129.22, 36.03], 0.1), red_a([[129.215, 36.055], [129.22, 36.025], [129.223, 36.0]], 0.5)], tilt=30))
sc(1, text("2개 중대 상실", "red", "제25연대 · 미 육군 공간사 기준"))
sc(1, m("corridor", "corridor", [mark([129.19, 36.02], "red", 0.1), mark([129.245, 36.025], "red", 0.4), mark([129.205, 36.003], "red", 0.7)], tilt=32), callouts=low("안강 북쪽 고지 · 위치 개략"))
sc(1, ph("kyongju_map"), label=plabel("kyongju_map"))
sc(1, m("pohang", "pohang", [red_a([[129.215, 36.06], [129.22, 36.0]], 0.2), unit("gigye", "제12사단", at=0)], tilt=24))
sc(1, m("pohang", "pohang", [unit("gigye", "제12사단", at=0), red_a([[129.345, 36.11], [129.36, 36.05]], 0.2), unit("heunghae", "제5사단", at=0.1)], tilt=24))
sc(1, m("pohang", "city", [LOCK("pohang", 0.7)], flight=["pohang", "city"], flightDur=2.4), sfx=SW(0))
sc(1, m("city", "city", [LOCK("school", 0.3)], tilt=30, hud=True), callouts=low("제3사단 후방 지휘소 · 위치 개략"), sfx=PING(0.4))
sc(1, ai("rear_cp"), label=DRAMA)
sc(1, black("지키는 전투 부대는", "사실상 없었다"))
sc(1, ai("boys_arrive"), label=DRAMA)
next_act()

# ===== 제3막 교복을 입은 일흔한 명 =====
MID = [nid()]
sc(1, ai("classroom_1950"), label=DRAMA, pauseBefore=0.5, chapter={"num": "제3막", "title": "교복을 입은 71명"})
sc(1, stage([C("kr_idle", 0.3, 420, prop="cap+glasses", face="sparkle"), C("kr_point", 0.7, 420, flip=True, prop="cap", face="blush")], [pop("label", 0.5, 0.15, "중학생 · 고등학생", on="중학생과", color="yellow")]))
sc(1, ph("refugees_road"), label=plabel("refugees_road"))
sc(1, ph("student_train"), label=plabel("student_train"))
sc(1, text("학도의용군", "yellow", "나라를 지키겠다며 자원한 학생들"))
sc(1, text("학도병", "blue"))
sc(1, m("city", "city", [mark("school", "blue", 0.2, "포항여중")], tilt=30), callouts=top("8. 9 저녁 · 71명 도착"))
sc(1, text("제3사단 후방 지휘소", "dark", "포항여중 (지금의 포항여고)"))
sc(1, stage([C("kr_salute", 0.5, 500, prop="officer", face="determined")], [pop("label", 0.5, 0.15, "제3사단장 김석원 준장", on="김석원", color="dark")]))
sc(1, m("ne", "ne", [unit([129.37, 36.3], "제3사단", "blue", 0, True), red_a(NK5_COAST[2:], 0.2), clash([129.35, 36.17], 0.5)]), callouts=low("포위 위기의 제3사단"))
sc(1, ph("yongdok_m1"), label=plabel("yongdok_m1"))
sc(1, text("1인당 실탄 250발", "yellow", "전해지는 이야기 · 증언 기준"))
sc(1, black("군복은", "모자랐다"))
sc(1, ai("uniform_rifle"), label=DRAMA)
sc(1, checklist("이 부대에 없던 것", [{"text": "군번", "on": "군번도", "checkOn": "군번도", "bad": True}, {"text": "계급", "on": "계급도", "checkOn": "계급도", "bad": True}]))
sc(1, ai("vote"), label=DRAMA)
sc(1, text("2개 소대", "blue"))
sc(1, doc("부대 이름", ["제3사단 직할", "학도의용군 중대"], "學徒", "국군 제3사단", "재구성"))
sc(1, black("훈련은", "거의 없었다"))
sc(1, checklist("배운 것", [{"text": "분해", "on": "분해하고", "checkOn": "분해하고"}, {"text": "조립", "on": "조립하는", "checkOn": "조립하는"}, {"text": "사격", "on": "쏘는", "checkOn": "전부였죠"}]))
sc(1, stage([C("kr_plead", 0.5, 480, prop="cap", face="determined", anim="bounce")], [pop("label", 0.5, 0.15, "임무 · 학교를 지켜라", on="학교를", color="yellow")]))
sc(1, m("pohang", "pohang", [mark("heunghae", "red", 0), red_a([[129.345, 36.11], [129.35, 36.075], [129.355, 36.05]], 0.3)], tilt=26), callouts=top("8. 10 · 흥해에서 남쪽으로", "red"))
sc(1, ai("trucks"), label=DRAMA)
sc(1, ph("yongdok_ammo"), label=plabel("yongdok_ammo"))
sc(1, black("누군가는", "시간을 벌어야 했다"))
sc(1, m("city", "city", [badge("school", "학교 앞", "#2e66d8", 0.2, -60), badge([129.351, 36.047], "뒷산", "#2e66d8", on="뒷산에", dy=-40)], tilt=32, hud=True), callouts=low("배치 · 개략"))
sc(1, ai("first_contact"), label=DRAMA, callouts=top("8. 10 오후 · 첫 총격전"))
sc(1, ai("grenade_throw"), label=DRAMA)
sc(1, text("이우근", "yellow", "학도병"))
sc(1, text("서울 동성중학교 3학년", "dark"))
sc(1, ai("letter_write"), label=DRAMA, callouts=top("1950. 8. 10 밤"))
sc(1, text("부치지 못한 편지", "dark"))
sc(1, black("편지는", "이렇게 시작한다"))
sc(1, doc("어머니께", ["어머니 나는", "사람을 죽였습니다"], "1950", "학도병 이우근의 편지 (1950. 8. 10)", "첫 문장 · 원문 요지"))
sc(1, black("중학교 3학년 소년의", "첫 문장"))
sc(1, black("두려움과", "그리움"))
sc(1, stage([C("kr_shrug", 0.35, 440, prop="cap", face="tears"), C("kr_idle", 0.7, 400, flip=True, prop="headband", face="worried")], [pop("label", 0.5, 0.15, "너무 어린 동료들", on="어리다는", color="dark")]))
sc(1, ai("mother_home"), label=DRAMA)
sc(1, black("편지의 행방은", "잠시 뒤에"))
sc(1, ai("comrade_breathes"), label=DRAMA)
sc(1, m("city", "city", [swarm([[129.345, 36.08], [129.35, 36.06], [129.355, 36.045]], 0.1, 90, 0.6)], tilt=32, hud=True))
sc(1, {"type": "cta", "title": CTA_TEXT, "at": 0})
next_act()

# ===== 제4막 포항여중의 열한 시간 =====
sc(1, m("city", "city", [LOCK("school", 0.4)], tilt=34, hud=True), chapter={"num": "제4막", "title": "포항여중의 11시간"}, callouts=top("1950. 8. 11 · 새벽 4시"))
sc(1, m("city", "city", [red_a([[129.35, 36.07], [129.355, 36.047]], 0.1, 1.1), swarm([[129.348, 36.075], [129.355, 36.045]], 0, 120)], tilt=32), sfx=FAR(0.2))
sc(1, text("새벽 3시 기록도", "dark", "자료에 따라 다름"))
sc(1, m("pohang", "pohang", [unit([129.34, 36.07], "제5사단 · 766연대 일부", at=0.1)], tilt=26))
sc(1, ai("nk_column_coast"), label=DRAMA)
sc(1, ai("wall_fire"), label=DRAMA)
sc(1, text("1차 공격 격퇴", "blue"))
sc(1, stage([C("nk_shock", 0.5, 480, flip=True, prop=NKC, face="shock", anim="shake")], [pop("ex", 0.75, 0.3, on="놀라")]))
sc(1, black("곧", "두 번째 공격"))
sc(1, ai("mortar_school"), label=DRAMA)
sc(1, ai("window_defense"), label=DRAMA)
sc(1, text("2차 공격 격퇴", "blue"))
sc(1, m("city", "city", [obj(1, "school", "포항여중", 0)], tilt=30), callouts=top("날이 밝다"))
sc(1, m("pohang", "city", [plane([[129.42, 35.988], [129.4, 36.01], [129.37, 36.035]], 0.2, 3, 2.6)], flight=["pohang", "city"], flightDur=2.4), sfx=SW(0))
sc(1, ph("pohang_ruins"), label=plabel("pohang_ruins"))
sc(1, ph("refugee_woman"), label=plabel("refugee_woman"))
sc(1, m("city", "city", [blue_a([[129.36, 36.035], [129.37, 36.02], [129.375, 36.003]], 0.2), river(0)], tilt=28), callouts=low("후방 지휘소 · 형산강 남쪽으로"))
sc(1, stage([C("kr_salute", 0.5, 480, prop="cap", face="tears")], [pop("label", 0.5, 0.15, "자리를 지킨다", on="자리를", color="yellow")]))
sc(1, black("그리고", "세 번째 공격"))
sc(1, ai("armored_car"), label=DRAMA)
sc(1, stage([C("kr_shock", 0.45, 460, prop="cap", face="shock")], [pop("q", 0.75, 0.3, at=0.3)]))
sc(1, ai("empty_ammo"), label=DRAMA)
sc(1, bars("1인당 실탄 · 전해지는 이야기", [{"label": "처음", "value": 250, "display": "250발", "color": "blue", "at": 0.1}, {"label": "몇 시간 뒤", "value": 15, "display": "바닥", "color": "red", "on": "떨어져"}]))
sc(1, m("city", "city", [swarm([[129.35, 36.06], [129.357, 36.041]], 0, 150), clash("school", 0.4)], tilt=34))
sc(1, ai("bayonet"), label=DRAMA)
sc(1, ai("trench_melee"), label=DRAMA)
sc(1, text("총을 거꾸로 들고", "red"))
sc(1, text("돌까지 던졌다", "red"))
sc(1, black("그리고", "네 번째 공격"))
sc(1, text("증언", "dark", "적과 학도병이 겹쳐 쓰러진 운동장"))
sc(1, black("오후 3시 무렵", "총소리가 잦아들다"))
sc(1, m("city", "city", [{"k": "arrow", "path": [[129.357, 36.041], [129.35, 36.046], [129.344, 36.052]], "color": "blue", "width": 0.7, "at": 0.2}], tilt=30), callouts=low("뒷산을 넘어 · 개략"))
sc(1, text("11시간 넘게", "yellow", "기록에 따라 11시간 반"))
sc(1, bars("학도의용군 71명 · 기록 기준", [{"label": "학도병", "value": 71, "display": "71명", "color": "blue", "at": 0}, {"label": "전사", "value": 48, "display": "48명", "color": "red", "on": "전사했습니다"}]))
sc(1, text("47명 기록도", "dark", "자료에 따라 다름"))
sc(1, text("포로 10여 명", "dark", "나머지 대부분 부상 · 자료에 따라 다름"))
sc(1, text("탈출해 돌아온 포로들", "blue"))
sc(1, stage([C("kr_point", 0.4, 460, prop="helmet", face="worried", anim="tilt")], [pop("q", 0.72, 0.3, at=0.2)], title="11시간이 남긴 것은?"))
sc(1, m("pohang", "pohang", [blue_a(OUT_SOUTH, 0.2), river(0)], tilt=26), callouts=top("무사히 빠져나간 후방 부대", "blue"))
sc(1, ph("refugees_pohang"), label=plabel("refugees_pohang"))
sc(1, m("city", "city", [unit("pohang", "북한군", at=0.1), {"k": "arrow", "path": [[129.365, 36.035], [129.355, 36.05], [129.348, 36.065]], "color": "red", "width": 0.8, "on": "물러납니다"}], tilt=30))
sc(1, ph("helena"), label=plabel("helena"), sfx=FAR(0.2))
sc(1, m("city", "city", [badge("pohang", "무인지대", "#111", 0.3, -60)], tilt=28), callouts=low("누구의 것도 아닌 땅"))
sc(1, stage([C("nk_shrug", 0.5, 460, prop=NKC, face="sweat", anim="tilt")], [pop("label", 0.5, 0.15, "시간을 잃다", on="시간을", color="red")]))
sc(1, text("시간 = 승부", "yellow"))
next_act()

# ===== 제5막 바다로 빠져나간 사단 =====
MID.append(nid())
sc(1, m("pohang", "pohang", [mark("school", "blue", 0)], tilt=26), pauseBefore=0.5, chapter={"num": "제5막", "title": "바다로 빠져나간 사단"})
sc(1, black("더 큰 위기가", "기다리고 있었다"))
sc(1, m("pohang", "pohang", [LOCK("airfield", 0.2)], tilt=28), callouts=top("첫 번째 위기"), sfx=PING(0.3))
sc(1, doc("명령", ["영일 비행장을 비워라"], "命令", "미 제5공군", "1950. 8. 13 · 재구성"))
sc(1, stage([C("us_point", 0.5, 480, prop="cap", face="sweat")], [pop("label", 0.5, 0.15, "적이 너무 가깝다!", on="가까이", color="dark")]))
sc(1, flat([131.0, 34.9], 7, [fpin([129.42, 35.99], "영일 비행장", at=0, flag="kr", side="left"), fpin([131.04, 33.68], "규슈 쓰이키 기지", on="규슈로", side="right")], [route([129.42, 35.99], [131.04, 33.68], "F-51 45대", on="옮겨", bend=0.2, color="#2e66d8")], [{"ll": [130.6, 36.2], "text": "동해", "style": "sea"}]))
sc(1, stage([C("us_plead", 0.5, 500, prop="pipe+glasses", face="angry", anim="shake")], [pop("label", 0.5, 0.15, "맥아더 · 비행장을 지켜라!", on="화를", color="red")]))
sc(1, m("pohang", "pohang", [mark("airfield", "blue", 0), badge("airfield", "브래들리 부대", "#2e66d8", 0.3, -70)], tilt=28))
sc(1, text("비행장 사수", "blue", "지상 부대는 끝까지 지켰다"))
sc(1, ph("f51_arm"), label=plabel("f51_arm"))
sc(1, m("ne", "ne", [unit([129.37, 36.3], "제3사단", "blue", 0.1, True)]), callouts=top("두 번째 위기", "red"))
sc(1, m("coast", "coast", [unit([129.37, 36.27], "제3사단", "blue", 0), {"k": "front", "path": [[129.3, 36.2], [129.35, 36.19], [129.39, 36.2]], "at": 0.2}], tilt=22), callouts=low("8. 10부터 갇힌 사단"))
sc(1, m("coast", "coast", [unit([129.37, 36.27], "제3사단", "blue", 0), red_a([[129.34, 36.38], [129.36, 36.31]], 0.2), badge([129.5, 36.27], "바다", "#2e66d8", on="바다", dy=0)], tilt=24))
sc(1, m("coast", "coast", [unit([129.37, 36.27], "제3사단", "blue", 0), clash([129.35, 36.17], 0.2), red_a([[129.32, 36.14], [129.36, 36.2]], 0.4)], tilt=24))
sc(1, text("사단 전체 고립", "red"))
sc(1, black("8월 15일", "결단"))
sc(1, doc("미 제8군 명령", ["제3사단을", "바다로 철수시켜라"], "命令", "미 제8군", "1950. 8. 15 · 재구성"))
sc(1, m("coast", "coast", [LOCK("dokseok", 0.3)], tilt=28, hud=True), sfx=PING(0.4))
sc(1, ai("ship_evac"), label=DRAMA, callouts=top("8. 16 밤 · 독석리 해변"), sfx=WATER(0.2))
sc(1, ai("boarding_night"), label=DRAMA)
sc(1, m("coast", "coast", [shock([[129.37, 36.235], [129.38, 36.242], [129.372, 36.228]], 0.1)], tilt=26), sfx=FAR(0.2))
sc(1, m("coast", "coast", [blue_a([[129.55, 36.25], [129.42, 36.24]], 0.1), badge([129.52, 36.22], "순양함 헬레나", "#2e66d8", 0.4, 0)], tilt=26))
sc(1, ai("night_ring"), label=DRAMA)
sc(1, text("8월 17일 아침 7시", "yellow", "마지막 배 출항"))
sc(3, bars("독석리 해상 철수 · 미 육군 공간사 기준", [{"label": "병사", "value": 9000, "display": "9,000여 명", "color": "blue", "on": "병사"}, {"label": "경찰", "value": 1200, "display": "1,200여 명", "color": "blue", "on": "경찰"}, {"label": "노무자 · 피란민", "value": 1000, "display": "1,000여 명", "color": "dark", "on": "노무자와"}]))
sc(1, text("장비 · 차량까지", "blue"))
sc(1, stage([C("kr_salute", 0.5, 500, prop="helmet", face="sparkle", anim="bounce")], [pop("label", 0.5, 0.15, "사단이 살아 나왔다", on="살아", color="blue")]))
sc(1, m("ne", "ne", [{"k": "arrow", "path": EVAC, "color": "blue", "at": 0.2, "width": 1.1}, mark("guryongpo", "blue", on="구룡포에")]))
sc(1, ph("yongdok_57"), label=plabel("yongdok_57"))
sc(1, black("같은 시각", "산 쪽에서도"))
sc(1, m("corridor", "corridor", [blue_a(TO_GIGYE_S, 0.2)], tilt=30), callouts=top("8. 17 · 기계 반격"))
sc(1, text("이번에는 달랐다", "blue"))
sc(1, m("corridor", "corridor", [blue_a(TO_GIGYE_S, 0), blue_a(TO_GIGYE_W, 0.2), LOCK("gigye", 0.6)], tilt=32, hud=True), sfx=PING(0.7))
sc(1, m("corridor", "corridor", [{"k": "arrow", "path": [[129.24, 36.06], [129.25, 36.085], [129.26, 36.1]], "color": "red", "width": 0.8, "at": 0.2}]), callouts=low("766연대 · 산속으로"))
sc(1, m("east", "east", [{"k": "arrow", "path": [[129.215, 36.06], [129.19, 36.1], [129.17, 36.13]], "color": "red", "at": 0.2}, mark("bihak", "red", on="비학산으로")]), callouts=top("8. 19 · 비학산으로", "red"))
sc(1, m("city", "city", [mark("pohang", "blue", 0.2), blue_a([[129.375, 36.0], [129.37, 36.02], [129.365, 36.033]], 0.1)], tilt=28), callouts=top("8. 19 · 포항 재진입", "blue"))
sc(1, doc("미 제8군 발표", ["동해안 위기", "일단 해소"], "8. 20", "미 제8군", "재구성"))
sc(1, black("놀라운 일이", "하나 있었다"))
sc(1, stage([C("nk_salute", 0.5, 460, prop=NKC, face="sweat", anim="exit")], [pop("label", 0.5, 0.15, "766연대 소멸", on="사라집니다", color="red")]))
sc(1, text("다른 사단에 흡수", "dark", "북한군 제12사단으로"))
sc(1, text("창설 1년 남짓", "dark", "1949. 4 ~ 1950. 8"))
sc(1, stage([C("nk_point", 0.5, 480, prop="officer", face="angry", anim="bounce")], [pop("label", 0.5, 0.15, "아직 끝나지 않았다", on="포기하지", color="red")]))
sc(1, black("진짜 결전은", "아직"))
next_act()

# ===== 제6막 형산강까지 밀리다 =====
sc(1, ai("rain_attack"), label=DRAMA, chapter={"num": "제6막", "title": "형산강까지 밀리다"})
sc(1, m("perimeter", "perimeter", [front, red_a([[127.95, 35.2], [128.33, 35.25]], 0.1), red_a([[128.0, 35.55], [128.37, 35.5]], 0.2), red_a([[128.3, 36.35], [128.5, 36.05]], 0.3), red_a([[128.8, 36.4], [128.9, 36.12]], 0.4), red_a([[129.2, 36.3], [129.25, 36.15]], 0.5), mark("masan", "red", on="마산부터")]), callouts=top("다섯 갈래 동시 공격", "red"))
sc(1, text("9월 공세", "red", "1950. 9 · 북한군 총공격"))
sc(1, m("east", "east", [unit("bihak", "제12사단", at=0.1, pulse=True)]))
sc(1, m("corridor", "corridor", [mark("gigye", "red", 0.2)], tilt=30), callouts=top("8. 26 밤 · 기계 재점령", "red"))
sc(1, ai("tank_break"), label=DRAMA, callouts=top("9. 2 · 전차를 앞세운 공격"))
sc(1, m("corridor", "corridor", [{"k": "front", "path": CAPLINE, "at": 0.1, "glow": True}, badge([129.205, 36.03], "수도사단", "#2e66d8", 0.4, 60)], tilt=30))
sc(1, m("corridor", "corridor", [{"k": "front", "path": CAPLINE, "at": 0}, red_a([[129.15, 36.06], [129.14, 36.02], [129.17, 36.0]], 0.2)], tilt=30), callouts=low("옆으로 돌아 우회 · 개략"))
sc(1, stage([C("kr_shrug", 0.5, 460, prop="helmet", face="coldsweat", anim="shake")], [pop("ex", 0.75, 0.3, on="위태로워졌죠")]))
sc(1, m("pohang", "pohang", [red_a([[129.345, 36.12], [129.355, 36.07]], 0.2), unit("heunghae", "제5사단", at=0)], tilt=24))
sc(1, ph("rok_hills"), label=plabel("rok_hills"))
sc(1, m("pohang", "pohang", [clash([129.22, 36.02], 0.2), unit([129.35, 36.06], "제3사단", "blue", 0)], tilt=24), callouts=low("안강 쪽이 흔들리다"))
sc(1, m("pohang", "pohang", [blue_a([[129.36, 36.05], [129.37, 36.025], [129.38, 36.0]], 0.2), river(0.4)], tilt=26), callouts=top("9. 5 · 형산강 남쪽으로"))
sc(1, ph("hyeongsan_map"), label=plabel("hyeongsan_map"))
sc(1, black("이제 남은 것은", "강 하나"))
sc(1, ph("hyeongsan_today"), label=plabel("hyeongsan_today"))
sc(1, m("east", "river", [river(0.1)], flight=["east", "river"], flightDur=3.0), sfx=SW(0))
sc(1, m("perimeter", "perimeter", [front, dash_r([[129.3, 36.0], [129.225, 35.86], [129.04, 35.2]], 0.2), mark("airfield", "blue", on="비행장")]), callouts=top("강 뒤로 열리는 길", "red"))
sc(1, m("river", "river", [river(0), {"k": "front", "path": RIVER_S, "at": 0.1, "glow": True}, badge([129.33, 35.99], "마지막 방어선", "#2e66d8", 0.5, 60)], tilt=30, hud=True))
sc(1, black("그 무렵 안강 남쪽", "또 하나의 결전"))
sc(1, m("corridor", "gonje", [LOCK("gonje", 0.8)], flight=["corridor", "gonje"], flightDur=2.4, hud=True), sfx=PING(0.9))
sc(1, {"type": "profile", "pts": [[0, 40], [0.3, 110], [0.5, 289], [0.7, 120], [1, 35]], "grid": [100, 200], "yMin": 0, "yMax": 360,
       "title": "곤제봉 (모식도)", "note": "모식도 · 실제 지형과 다름", "left": "안강 · 형산강", "right": "경주 쪽",
       "marks": [{"x": 0.5, "text": "곤제봉 289m", "style": "red", "at": 0.2, "lift": 40, "size": 44}]})
sc(1, m("east", "east", [mark("gonje", "blue", 0), dash_r([[129.215, 35.947], [129.225, 35.86]], 0.2), mark("gyeongju", "blue", 0)]), callouts=low("곤제봉 → 경주 약 12km"))
sc(1, stage([C("us_idle", 0.5, 460, prop="officer", face="worried")], [pop("label", 0.5, 0.15, "경주가 눈앞", on="눈앞이었습니다", color="red")]))
sc(1, m("gonje", "gonje", [obj(1, "gonje", "곤제봉", 0)], tilt=34), callouts=top("9. 6 · 쟁탈전 시작", "red"), sfx=FAR(0.2))
sc(1, m("gonje", "gonje", [obj(1, "gonje", "곤제봉", 0), clash("gonje", 0.1, 1.1)], tilt=34), callouts=low("일주일 동안 뺏고 뺏기다"))
sc(1, black("하늘도", "국군 편이 아니었다"))
sc(1, ai("rain_trench"), label=DRAMA, sfx=WIND(0))
sc(1, m("gonje", "gonje", [obj(1, "gonje", "곤제봉", 0), swarm([[129.215, 36.0], [129.215, 35.97], [129.215, 35.95]], 0.1, 120)], tilt=34))
sc(1, m("river", "river", [red_a([[129.25, 35.97], [129.29, 35.972], [129.325, 35.976]], 0.2), mark("unje", "red", on="운제산까지")], tilt=28))
sc(1, m("river", "river", [mark("unje", "red", 0), mark("airfield", "blue", on="비행장이")], tilt=28))
sc(1, ph("macarthur_walker"), label=plabel("macarthur_walker"))
sc(1, doc("워커 중장 명령", ["운제산을 되찾아라"], "命令", "미 제8군", "재구성"))
sc(1, m("river", "river", [mark("unje", "red", 0), blue_a([[129.3, 35.94], [129.32, 35.965]], 0.2), blue_a([[129.38, 35.96], [129.355, 35.972]], 0.4)], tilt=28))
sc(1, text("참호마다 빗물", "dark"))
sc(1, ph("capital_howitzer"), label=plabel("capital_howitzer"))
sc(1, black("9월 12일", "밤"))
sc(1, ai("night_climb"), label=DRAMA)
sc(1, m("gonje", "gonje", [obj(1, "gonje", "곤제봉", 0, takenOn="되찾습니다")], tilt=34, hud=True), sfx=PING(0.6))
sc(1, m("corridor", "corridor", [{"k": "front", "path": [[129.15, 35.955], [129.215, 35.947], [129.27, 35.96], [129.32, 35.975]], "at": 0.1, "glow": True}], tilt=28), callouts=low("안강 남쪽 방어선 회복 · 개략"))
sc(1, black("그리고 바로 그때", "서해에서 날아온 소식"))
next_act()

# ===== 제7막 형산강의 기적 =====
MID.append(nid())
sc(1, ph("inchon_craft"), label=plabel("inchon_craft"), pauseBefore=0.5, chapter={"num": "제7막", "title": "형산강의 기적"})
sc(1, m("korea", "korea", [front, mark("incheon", "blue", 0), blue_a([[125.9, 37.3], [126.62, 37.47], [126.98, 37.56]], 0.2)]), callouts=top("1950. 9. 15 · 인천상륙작전", "blue"))
sc(1, m("korea", "korea", [front, blue_a([[126.62, 37.47], [127.2, 37.0], [127.6, 36.5]], 0.1), clash([127.5, 36.6], 0.5)]), callouts=low("허리가 끊긴 북한군"))
sc(1, m("perimeter", "perimeter", [front, blue_a([[128.4, 35.6], [128.2, 36.0]], 0.1), blue_a([[128.7, 36.1], [128.7, 36.4]], 0.2), blue_a([[129.3, 36.0], [129.35, 36.15]], 0.3)]), callouts=top("총반격 명령", "blue"))
sc(1, m("river", "river", [river(0), {"k": "front", "path": RIVER_S, "at": 0}, unit([129.37, 35.99], "제3사단", "blue", 0.2)], tilt=28))
sc(1, doc("명령", ["형산강을 건너", "포항을 되찾아라"], "命令", "국군 제3사단", "재구성"))
sc(1, m("river", "river", [river(0), mark([129.33, 36.015], "red", 0.1), mark([129.36, 36.022], "red", 0.3), mark([129.29, 36.008], "red", 0.5)], tilt=30), callouts=low("강 건너 북한군 진지 · 개략"))
sc(1, m("river", "river", [river(0), LOCK(MG, 0.3, "기관총 진지", "#c9242c")], tilt=34, hud=True), sfx=PING(0.4))
sc(1, ai("swollen_river"), label=DRAMA)
sc(1, black("9월 17일", "새벽 4시"))
sc(1, stage([C("kr_point", 0.5, 480, prop="helmet+headband", face="determined", anim="bounce")], [pop("label", 0.5, 0.15, "분대장 연제근 이등상사", on="연제근", color="dark")]))
sc(1, text("13명", "yellow", "연제근 분대 결사대"))
sc(1, ai("river_plunge"), label=DRAMA, sfx=WATER(0.2))
sc(1, m("river", "river", [river(0), LOCK(MG, 0, "기관총 진지", "#c9242c"), blue_a([[129.352, 35.998], [129.354, 36.014]], 0.2, 0.8)], tilt=36))
sc(1, m("river", "river", [river(0), LOCK(MG, 0, "기관총 진지", "#c9242c"), clash([129.353, 36.008], 0.2, 0.8)], tilt=36))
sc(1, text("총탄을 맞고도", "red"))
sc(1, ai("grenade_bunker"), label=DRAMA)
sc(1, black("진지가", "침묵했다"))
sc(1, m("river", "river", [river(0), blue_a([[129.345, 35.99], [129.352, 36.015], [129.36, 36.04]], 0.1, 1.2), blue_a([[129.31, 35.988], [129.315, 36.012], [129.32, 36.03]], 0.3), blue_a([[129.38, 35.995], [129.383, 36.017], [129.385, 36.035]], 0.5)], tilt=30), callouts=top("형산강 도하", "blue"))
sc(1, ai("napalm"), label=DRAMA)
sc(1, m("pohang", "pohang", [shock([[129.33, 36.015], [129.36, 36.025], [129.3, 36.01]], 0.1, 0.6), blue_a([[129.5, 36.06], [129.42, 36.04]], 0.1)], tilt=26), callouts=low("영일만 함포 지원"), sfx=FAR(0.2))
sc(1, text("불바다", "red"))
sc(1, text("13명 중 생존 1명", "dark", "전해지는 이야기"))
sc(1, m("east", "east", [blue_a([[129.36, 36.0], [129.36, 36.06]], 0.1), blue_a([[129.225, 35.96], [129.225, 36.0]], 0.3)]), callouts=top("전선 전체가 움직인다", "blue"))
sc(1, m("corridor", "corridor", [mark("angang", "blue", on="안강을")], tilt=28), callouts=top("9. 18 · 안강 탈환", "blue"))
sc(1, ph("pohang_return"), label=plabel("pohang_return"))
sc(1, m("east", "east", [{"k": "arrow", "path": [[129.36, 36.06], [129.36, 36.15]], "color": "red", "at": 0.1}, {"k": "arrow", "path": [[129.215, 36.07], [129.17, 36.13]], "color": "red", "at": 0.3}]))
sc(1, text("동해안의 문", "blue", "끝내 열리지 않았다"))
sc(1, text("44일", "yellow", "1950. 8. 9 ~ 9. 22 · 포항 지구 전투"))
sc(2, bars("포항 지구 전투 · 국내 전사 기록 기준", [{"label": "국군 전사", "value": 2300, "display": "2,300여 명", "color": "blue", "on": "이천삼백여"}, {"label": "북한군 사살", "value": 15300, "display": "1만 5,000여 명", "color": "red", "on": "만 오천여"}]))
SOMBER = nid()
sc(1, black("처음의", "질문"))
sc(1, stage([C("kr_plead", 0.4, 460, prop="officer", face="worried", anim="tilt")], [pop("q", 0.72, 0.3, at=0.2)], title="동해안이 뚫리면 왜 부산이 끝인가?"))
sc(1, m("perimeter", "perimeter", [front, {"k": "line", "path": [[129.215, 36.06], [129.225, 35.99], [129.225, 35.86], [129.2, 35.6], [129.04, 35.18]], "color": "#ffd400", "glow": True, "at": 0.1}]), callouts=top("부산으로 가는 가장 짧은 길"))
sc(1, m("perimeter", "perimeter", [front, mark("pohang", "blue", 0), mark("daegu", "blue", on="대구의")]))
sc(1, m("perimeter", "perimeter", [front, dash_r([[129.36, 36.03], [128.9, 35.95], [128.6, 35.88]], 0.1), shock([[128.6, 35.88], [128.45, 35.5]], 0.5, 0.8)]), callouts=low("가정 · 뒤에서 무너지는 방어선"))
sc(1, stage([C("kr_shock", 0.5, 460, prop="cap+medal", face="worried", anim="tilt")], [pop("q", 0.76, 0.3, at=0.2)], title="학생들의 11시간은 무엇을 바꿨나?"))
sc(1, m("pohang", "pohang", [blue_a(OUT_SOUTH, 0.1), river(0)], tilt=26), callouts=top("그 11시간 동안", "blue"))
sc(1, m("city", "city", [obj(1, "school", "포항여중", 0), clash("school", 0.2)], tilt=32, hud=True))
sc(1, m("ne", "ne", [{"k": "arrow", "path": EVAC, "color": "blue", "at": 0.1, "width": 1.1}]), callouts=low("며칠 뒤 · 제3사단 해상 철수"))
sc(1, text("11시간", "yellow"))
sc(1, text("하루보다 긴 11시간", "red"))
sc(1, ai("letter_found"), label=DRAMA)
sc(1, text("학도병 이우근의 편지", "yellow"))
sc(2, doc("편지의 끝 (요지)", ["다시 편지를 쓰겠습니다", "이것이 마지막 인사는 아닙니다"], "1950", "학도병 이우근의 편지", "요지 · 현대어"))
sc(1, black("그 다음 편지는", "끝내 쓰이지 않았다"))
sc(1, text("이우근", "dark", "포항여중 앞에서 전사"))
sc(1, ai("memorial"), label=DRAMA, callouts=top("1957. 8. 11 · 전몰학도 충혼탑"))
sc(1, text("학도의용군 전승기념관", "blue", "포항 북구 용흥동"))
sc(1, text("매년 8월 11일 추념식", "blue", "전몰 학도의용군을 기리며"))
sc(1, text("포항여중 → 포항여고", "dark"))
sc(1, ai("parade_boys"), label=DRAMA)
sc(1, ai("river_dawn"), label=DRAMA)
sc(1, m("east", "pohang", [river(0.3), LOCK("school", 0.9)], flight=["east", "pohang"], flightDur=2.8), sfx=SW(0))
sc(2, {"type": "endcard", "title": "군번도 계급도 없던 71명,\n형산강을 건넌 13명을 기억하며", "q": pin("student_train")}, tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 (Gemini · 새 그림 + 재사용) =====
CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
STU = ("young South Korean student soldiers whose heads are round balls painted as the South Korean Taegukgi flag (white with the red and blue taegeuk circle and black trigrams), "
       "wearing plain black high-school uniforms and mismatched steel helmets or black school caps, NO stars and NO red insignia anywhere")
STU1 = ("a young South Korean student soldier whose head is a round ball painted as the South Korean Taegukgi flag (white with the red and blue taegeuk circle and black trigrams), "
        "wearing a plain black high-school uniform and an old steel helmet, NO stars and NO red insignia anywhere")
ROK = ("South Korean soldiers whose heads are round balls painted as the South Korean taegukgi flag (white with the red and blue taegeuk circle and black trigrams), "
       "wearing 1950 M1 steel helmets and plain olive drab summer field uniforms with absolutely NO collar tabs, NO patches, NO red insignia")
NK = "North Korean soldiers whose heads are round balls painted as the North Korean flag (blue, red and white stripes with a red star in a white circle), wearing 1950 khaki uniforms and soft field caps"
US = "American soldiers whose heads are round balls painted as the United States flag, wearing 1950 M1 helmets and olive drab uniforms"
SCHOOL = "a 1950 Korean girls' middle school: a plain two-story wooden-and-brick school building with tall windows, a dirt schoolyard and a low stone wall, a wooded hill behind"
END = ", August 1950 summer, leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic, desaturated palette, film grain, no text, no letters."
AI = {
    "school_dawn": SCHOOL + " in the deep blue darkness just before dawn, small figures of boys in black school uniforms crouching behind the stone wall with rifles, faint mist, absolutely silent and tense, August 1950, " + LAND,
    "wall_boys": CB + STU + " lying flat behind a low stone schoolyard wall before dawn, gripping M1 rifles, wide frightened eyes, the dark school building behind them" + END,
    "nk766_infiltrate": CB + NK + " in light commando gear moving fast in single file along a narrow forested mountain ridge path at dusk, crouching low, the East Sea coast faintly visible far behind" + END,
    "ambush_road": CB + US + " in a column of jeeps and trucks ambushed on a narrow mountain road before dawn, muzzle flashes from the dark hillsides on both sides, soldiers diving into a ditch, a truck burning" + END,
    "rear_cp": CB + ROK + " hurriedly working in a school classroom turned into a division rear command post, maps on the blackboard, stacks of supply crates, wounded soldiers on stretchers in the hallway, lantern light at night" + END,
    "boys_arrive": CB + STU + " arriving at the gate of " + SCHOOL + " in the evening, tired, carrying small bundles, some still in school caps, looking up at the building" + END,
    "classroom_1950": "An empty 1950 Korean school classroom with old wooden desks and a blackboard, school caps and books left on the desks, afternoon light through tall windows, dust in the air, quiet and nostalgic, " + LAND,
    "uniform_rifle": CB + STU + " in black high-school uniforms receiving M1 rifles handed out from wooden crates in a schoolyard, some boys holding a rifle for the first time, serious faces" + END,
    "vote": CB + STU + " standing in a circle in a schoolyard at dusk, raising their hands to vote for their own squad leader, one tall boy stepping forward, rifles slung" + END,
    "first_contact": CB + STU + " firing rifles over a low stone wall at distant enemy scouts in the late afternoon, smoke from the muzzles, one boy flinching at the noise" + END,
    "grenade_throw": CB + STU1 + " throwing a hand grenade over a low stone schoolyard wall with his eyes squeezed shut, late afternoon, smoke beyond the wall" + END,
    "letter_write": CB + STU1 + " sitting alone against a classroom wall at night, writing a letter on a small piece of paper by faint candlelight, his rifle leaning beside him, sad and quiet" + END,
    "mother_home": "A Korean mother in a white 1950 hanbok standing alone at the twig gate of a small thatched-roof village house at dusk, looking down the empty road, waiting, soft golden light, " + LAND,
    "wall_fire": CB + STU + " firing all at once from behind the stone schoolyard wall at dawn as a line of " + NK + " charges across the dark field toward them, bright muzzle flashes" + END,
    "mortar_school": "Mortar shells exploding on the dirt schoolyard and against the wooden walls of " + SCHOOL + " at early dawn, windows shattering, dust and smoke, no visible bodies, " + LAND,
    "window_defense": CB + STU + " firing rifles from the shattered windows of a wooden school classroom at dawn, broken glass on the floor, smoke drifting in, determined faces" + END,
    "armored_car": "A 1950 Soviet-made BA-64 armored car followed by infantry advancing up a dusty road toward the stone wall of " + SCHOOL + " in morning light, smoke, " + LAND,
    "bayonet": CB + STU + " fixing bayonets to their M1 rifles behind the schoolyard wall, sweat and dust on their faces, the enemy coming close, harsh morning sun" + END,
    "boarding_night": CB + ROK + " climbing ladders and nets up the side of a grey US Navy LST from small boats at night, flares lighting the sky, waves, a long line of soldiers waiting on the beach" + END,
    "rain_trench": CB + ROK + " crouching in a muddy hillside trench in pouring rain, rainwater up to their boots, rifles wrapped in ponchos, grey sky, no aircraft in the sky" + END,
    "night_climb": CB + ROK + " climbing a steep wet rocky hillside in the dark rain toward a hilltop, bayonets fixed, one soldier pulling another up, faint flashes on the crest" + END,
    "swollen_river": "A wide brown swollen Korean river after days of rain in September 1950, fast muddy current, the far bank dark with low hills and a hidden machine gun nest, grey dawn, " + LAND,
    "river_plunge": CB + "thirteen " + ROK + " with grenades strapped to their chests wading and swimming across a fast swollen river in the dark before dawn, tracer bullets skimming the water" + END,
    "grenade_bunker": CB + "a wounded South Korean sergeant whose head is a round ball painted as the South Korean taegukgi flag, wearing a 1950 M1 steel helmet and a plain olive drab uniform with NO insignia, crawling up a muddy riverbank and throwing a grenade into a log-and-sandbag machine gun nest, dawn" + END,
    "napalm": "Four F-51 Mustang fighter-bombers swooping low over a river and dropping napalm on enemy positions on the far bank, huge orange fireballs and black smoke, September 1950, " + LAND,
    "letter_found": "A small folded blood-stained letter in faded paper sticking out of the breast pocket of a dusty black school uniform jacket lying on the ground, soft light, extreme close-up, solemn, no readable writing, no letters, " + LAND,
    "river_dawn": "A calm wide river flowing into the sea beside a quiet small Korean city at dawn, soft pink light, mist over the water, peaceful, " + LAND,
    "thumb_subject": "Photorealistic black-and-white 1950 Korean War documentary portrait of a very young South Korean student volunteer soldier, clearly East Asian Korean face with black hair, plain black high-school uniform with no insignia and an old American M1 steel helmet, soot and sweat on his face, fierce determined eyes, holding an M1 rifle across his chest, waist-up, face clearly visible and turned slightly toward the left of the frame, isolated on a plain pure white background, no shadows on the background, no text.",
}
# 재사용 그림 (파일·서명 복사, 추가 비용 0): 원래 프롬프트 그대로
REUSE = {"walker_map": "naktong", "ship_evac": "naktong", "rain_attack": "naktong", "tank_break": "naktong", "fog_mountain": "naktong", "trucks": "naktong",
         "empty_ammo": "ep23-jangsari", "trench_melee": "ep23-jangsari", "red_eyes": "ep23-jangsari", "comrade_breathes": "ep23-jangsari", "parade_boys": "ep23-jangsari", "night_ring": "ep23-jangsari",
         "nk_column_coast": "ep27-tongyeong", "memorial": "ep27-tongyeong"}
import hashlib
import shutil
AIDIR = ROOT / "public" / "ep" / EP / "ai"
AIDIR.mkdir(parents=True, exist_ok=True)
man = json.loads((AIDIR / "ai.json").read_text()) if (AIDIR / "ai.json").exists() else {}
for k, src in REUSE.items():
    AI[k] = json.loads((ROOT / "episodes" / src / "storyboard.json").read_text(encoding="utf-8"))["ai_images"][k]
    shutil.copyfile(ROOT / "public" / "ep" / src / "ai" / f"{k}.jpg", AIDIR / f"{k}.jpg")
    man[k] = hashlib.sha1(f"gpt-image-1|high|{AI[k]}".encode()).hexdigest()[:12]
(AIDIR / "ai.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
used = {s["visual"]["img"] for s in S if s["visual"]["type"] == "ai"}
assert not used - set(AI), used - set(AI)
assert not set(AI) - used - {"thumb_subject"}, set(AI) - used

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
         {"id": "theme", "from": sid(chap[0]), "to": sid(chap[2] - 1), "volume": 0.16},
         {"id": "somber", "from": sid(chap[2]), "to": sid(chap[3] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[3]), "to": sid(chap[4] - 1), "volume": 0.17},
         {"id": "march", "from": sid(chap[4]), "to": sid(chap[5] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[5]), "to": sid(chap[6] - 1), "volume": 0.17},
         {"id": "march", "from": sid(chap[6]), "to": prev_id(SOMBER), "volume": 0.16},
         {"id": "somber", "from": SOMBER, "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "포항 결전", "subtitle": "안강·기계 전투와 형산강 방어선 · 1950. 8 ~ 9", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         "target_sec": 1260, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap],
      "ai", len(AI), "new ai", len(set(AI) - set(REUSE)), "pins", len(PINS), "stage", len(stages), "photo", sum(1 for s in S if s["visual"]["type"] == "photo"))
print("char uses", dict(cnt))
