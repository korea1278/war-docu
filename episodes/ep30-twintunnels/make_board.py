# EP30 원주·쌍터널 전투 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 연출 스타일 v2 + 화면 업그레이드 2단계 + 롱폼 표준(LONGFORM_STANDARD) + 캐릭터 반복 방지 규칙 + 초반 후킹 표준(docs/HOOK_STANDARD.md)
# 프랑스 캐릭터(fr_*)는 그림 없이 Stage.tsx SVG 볼(프랑스 삼색기)로 대체 — 추가 비용 0
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
    ("천구백오십일년 이월 일일", "1951년 2월 1일"), ("천구백오십일년 일월 일일", "1951년 1월 1일"), ("천구백오십년 십일월 말", "1950년 11월 말"),
    ("일월 삼십일일 아침 여섯 시 반", "1월 31일 아침 6시 반"), ("십이월 이십삼일", "12월 23일"), ("십일월 이십구일", "11월 29일"),
    ("일월 이십구일", "1월 29일"), ("일월 이십오일", "1월 25일"), ("일월 십칠일", "1월 17일"), ("일월 십이일", "1월 12일"), ("일월 십일", "1월 10일"),
    ("일월 팔일", "1월 8일"), ("일월 칠일", "1월 7일"), ("이월 십일일", "2월 11일"), ("이월 십삼일", "2월 13일"), ("이월 십오일", "2월 15일"),
    ("이월 십사일", "2월 14일"), ("이월 삼일", "2월 3일"), ("이월 일일", "2월 1일"),
    ("오후 다섯 시 반", "오후 5시 반"), ("밤 열 시 반", "밤 10시 반"), ("새벽 세 시 반", "새벽 3시 반"), ("오후 세 시", "오후 3시"),
    ("천삼백 구", "1,300구"), ("삼천육백 명", "3,600명"), ("사천오백 명", "4,500명"), ("삼천오백 명", "3,500명"), ("팔천 명", "8,000명"),
    ("이천 명", "2,000명"), ("천백 명", "1,100명"), ("병력은 천 명", "병력은 1,000명"), ("이백칠 명", "207명"), ("이백 명", "200명"), ("백육십칠 명", "167명"),
    ("백십사 명", "114명"), ("사십오 명", "45명"), ("실종 네 명", "실종 4명"), ("스무 명", "20명"), ("마흔다섯에서 예순 명", "45~60명"),
    ("열 명 중 여덟 명", "10명 중 8명"), ("마흔세 살", "43세"),
    ("지프 아홉 대와 무기 운반차 두 대", "지프 9대와 무기 운반차 2대"), ("열네 대", "14대"), ("여든 번", "80번"), ("다섯 번이나", "5번이나"),
    ("칠십오 퍼센트", "75%"), ("칠십오 년 전", "75년 전"), ("별 세 개", "별 3개"), ("두 개 대대", "2개 대대"), ("세 개 연대", "3개 연대"),
    ("네 개 대대", "4개 대대"), ("한 개 연대", "1개 연대"), ("두 개의 터널", "2개의 터널"), ("산줄기 두 개", "산줄기 2개"),
    ("수백 미터에서 천 미터", "수백 m에서 1,000m"),
    ("제삼십칠야전포병대대", "제37야전포병대대"), ("제삼백칠십오연대", "제375연대"), ("제삼백칠십사연대", "제374연대"), ("제삼백칠십삼연대", "제373연대"),
    ("제백이십오사단", "제125사단"), ("제사십이군", "제42군"), ("제이십삼연대", "제23연대"), ("제이십사사단", "제24사단"), ("제이사단", "제2사단"),
    ("제팔사단", "제8사단"), ("제팔군", "제8군"), ("제오군단", "제5군단"), ("제삼대대", "제3대대"), ("제이대대", "제2대대"), ("제일대대", "제1대대"),
    ("제일중대", "제1중대"), ("제사차 공세", "제4차 공세"), ("사백오십삼고지", "453고지"), ("이백사십칠고지", "247고지"), ("삼팔선", "38선"),
    ("이차 세계 대전", "2차 세계 대전"), ("일차 세계 대전", "1차 세계 대전"), ("씨 중대", "C중대"), ("에프 중대", "F중대"),
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


def doc(head, rows, stamp="軍 秘", org="미 제2사단", note="재구성 · 내용 요약"):
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

# 좌표는 개략 (쌍터널 일대 능선·453고지·신촌·이호리, 원주 247고지·섬강 지점은 현재 지형 기준 근사)
P = {
    "seoul": [126.978, 37.566, "서울"], "pyongyang": [125.75, 39.02, "평양"], "kunuri": [125.94, 39.58, "군우리"], "busan": [129.04, 35.18, "부산"],
    "wonju": [127.92, 37.342, "원주"], "h247": [127.935, 37.305, "247고지"], "hoengseong": [127.985, 37.49, "횡성"], "chungju": [127.926, 36.991, "충주"],
    "yangpyeong": [127.488, 37.492, "양평"], "yeoju": [127.637, 37.298, "여주"], "jipyeong": [127.636, 37.477, "지평리"], "chuncheon": [127.73, 37.88, "춘천"],
    "twin": [127.672, 37.443, "쌍터널"], "twin_e": [127.685, 37.446, "제3대대"], "twin_w": [127.659, 37.447, "프랑스 대대"], "h453": [127.667, 37.432, "453고지"],
    "h333": [127.688, 37.457, "333고지"], "nwr": [127.655, 37.457, "북서쪽 능선"], "sinchon": [127.676, 37.452, "신촌"], "ihori": [127.63, 37.37, "이호리"],
    "ridge_e": [127.679, 37.437, "동쪽 능선"], "arty": [127.668, 37.418, "포병"], "seom": [127.84, 37.37, "섬강"], "koksu": [127.598, 37.392, "곡수리"],
    "pw": [127.627, 37.477, "프랑스 대대"], "hongcheon": [127.888, 37.697, "홍천"],
}
V = {
    "nwide": {"center": [126.9, 38.7], "span": 6.0}, "kunuri": {"center": [125.95, 39.55], "span": 0.9}, "mid": {"center": [127.58, 37.3], "span": 2.1},
    "wonju": {"center": [127.9, 37.33], "span": 0.5}, "wonju_wide": {"center": [127.85, 37.38], "span": 0.8}, "jp_wide": {"center": [127.65, 37.405], "span": 0.4},
    "twin_jp": {"center": [127.656, 37.455], "span": 0.16}, "twin": {"center": [127.672, 37.444], "span": 0.1}, "jp_ring": {"center": [127.636, 37.472], "span": 0.13},
    "seom": {"center": [127.84, 37.38], "span": 0.45}, "korea": {"center": [127.6, 37.0], "span": 5.5},
}
RAIL = [[127.6, 37.478], [127.63, 37.463], [127.655, 37.452], [127.672, 37.443], [127.69, 37.434], [127.72, 37.42]]
ROAD = [[127.63, 37.37], [127.65, 37.4], [127.664, 37.424], [127.671, 37.436], [127.673, 37.445], [127.668, 37.458], [127.652, 37.47], [127.636, 37.477]]
PATROL = ROAD[:5]
RING = [[127.659, 37.447], [127.664, 37.455], [127.676, 37.456], [127.686, 37.45], [127.686, 37.44], [127.678, 37.436], [127.67, 37.433], [127.662, 37.437], [127.659, 37.447]]
CN375 = [[127.673, 37.478], [127.673, 37.466], [127.673, 37.457]]
CN374 = [[127.712, 37.472], [127.698, 37.462], [127.687, 37.453]]
CN373A = [[127.632, 37.466], [127.646, 37.457], [127.658, 37.45]]
CN373B = [[127.636, 37.42], [127.65, 37.43], [127.661, 37.438]]
TO453 = [[127.648, 37.425], [127.658, 37.429], [127.665, 37.431]]
CUT = [[127.664, 37.431], [127.667, 37.43]]
RETREAT = [[125.94, 39.58], [125.75, 39.02], [126.3, 38.45], [126.98, 37.62], [127.15, 37.5]]
CN_YALU = [[[125.3, 39.95], [125.7, 39.68]], [[126.0, 39.95], [126.0, 39.68]], [[126.8, 39.95], [126.45, 39.65]]]
L38 = {"k": "line", "path": [[124.6, 38.0], [126.5, 38.0], [128.6, 38.3]], "color": "#ffffff", "at": 0, "dash": True}
NEWYEAR = [[[126.9, 38.2], [126.98, 37.62]], [[127.7, 38.1], [127.9, 37.4]], [[128.3, 38.1], [128.2, 37.5]]]
NK_WONJU = [[127.93, 37.5], [127.925, 37.42], [127.92, 37.36]]
TO_SOUTH = [[127.92, 37.34], [127.93, 37.25], [127.94, 37.18]]
FLANK247 = [[127.9, 37.33], [127.905, 37.31], [127.925, 37.3]]
UP4 = [[[127.88, 37.2], [127.9, 37.27]], [[127.93, 37.19], [127.935, 37.27]], [[127.98, 37.21], [127.955, 37.28]], [[127.86, 37.25], [127.9, 37.3]]]
NK_OUT = [[127.92, 37.36], [127.93, 37.43], [127.95, 37.52]]
HSG_OUT = [[127.985, 37.49], [127.96, 37.42], [127.93, 37.36]]
SEOM_COL = [[127.76, 37.48], [127.8, 37.43], [127.84, 37.39]]
SEOM_COL2 = [[127.79, 37.49], [127.83, 37.44], [127.86, 37.4]]
SEOM_TURN = [[127.84, 37.39], [127.8, 37.36], [127.75, 37.35]]
CROMBEZ = [[127.598, 37.392], [127.615, 37.43], [127.63, 37.46], [127.636, 37.47]]
JP_RING = [[127.62, 37.477], [127.627, 37.487], [127.64, 37.489], [127.65, 37.482], [127.65, 37.47], [127.64, 37.464], [127.626, 37.467], [127.62, 37.477]]
FEB_OFF = [[[127.5, 37.75], [127.6, 37.55]], [[127.85, 37.75], [127.95, 37.55]], [[128.1, 37.7], [128.0, 37.5]]]
HIGHWATER = [[127.3, 37.42], [127.636, 37.47], [127.92, 37.36], [128.2, 37.3]]
LOCK = lambda p, at=0.3, text=None, color=None, on=None: dict({"k": "lock", "p": p, "text": text or P[p][2]}, **({"on": on} if on else {"at": at}), **({"color": color} if color else {}))
badge = lambda p, t, c="#111", at=0.3, dy=-70, on=None: dict({"k": "badge", "p": p, "text": t, "color": c, "dy": dy}, **({"on": on} if on else {"at": at}))
red_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "red", "width": w}, **({"on": on} if on else {"at": at}))
blue_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "blue", "width": w}, **({"on": on} if on else {"at": at}))
dash_r = lambda path, at=0.2: {"k": "arrow", "path": path, "color": "red", "dash": True, "at": at}
mark = lambda p, color="red", at=0, text=None, on=None: dict({"k": "marker", "p": p, "color": color}, **({"text": text} if text else {}), **({"on": on} if on else {"at": at}))
unit = lambda p, t, color="red", at=0.1, pulse=False, on=None: dict({"k": "unit", "p": p, "text": t, "color": color}, **({"on": on} if on else {"at": at}), **({"pulse": True} if pulse else {}))
obj = lambda n, p, text, at=0, takenAt=None, takenOn=None: dict({"k": "obj", "n": n, "p": p, "text": text, "at": at}, **({"takenAt": takenAt} if takenAt is not None else {}), **({"takenOn": takenOn} if takenOn else {}))
clash = lambda p, at=0.3, size=1.0: {"k": "clash", "p": p, "at": at, "period": 0.9, "size": size}
shock = lambda pts, at=0.2, period=0.7: {"k": "shock", "pts": pts, "at": at, "period": period}
swarm = lambda path, at=0.1, n=120, width=None: dict({"k": "swarm", "path": path, "at": at, "n": n}, **({"width": width} if width else {}))
plane = lambda path, at=0.1, n=1, dur=3.0, hit=False, size=1.0: {"k": "plane", "path": path, "at": at, "n": n, "dur": dur, "hit": hit, "size": size}
line = lambda path, at=0.1, color="#ffd400", on=None: dict({"k": "line", "path": path, "color": color, "glow": True}, **({"on": on} if on else {"at": at}))
radar = lambda p, at=0.2, size=1.0, color="blue", text=None: dict({"k": "radar", "p": p, "at": at, "size": size, "color": color}, **({"text": text} if text else {}))
rail = lambda at=0, on=None: line(RAIL, at, "#ffd400", on)
ring = lambda at=0.1, on=None: line(RING, at, "#7fd3ff", on)
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]
SW = lambda at=0: [{"id": "whoosh", "at": at}]
FAR = lambda at=0.1: [{"id": "artillery_far", "at": at}]
PING = lambda at=0.6: [{"id": "ping", "at": at}]
WIND = lambda at=0: [{"id": "wind", "at": at}]
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))
flags = lambda title, items: {"type": "flaggrid", "title": title, "items": items}
QUESTION = "도망치던 군대는 어떻게\n중공군을 막는 철벽이 됐나"
TC = "#2e66d8"

# ===== 콜드 오프닝 (초반 후킹 표준: 절정 → 수치 HUD 누적 → 통념 X → 핵심 질문 카드 → 타이틀) =====
sc(1, ai("twin_wave"), label=DRAMA, hook={"hud": [HUD("1951. 2. 1", "경기도 양평", "쌍터널 · 동트기 전", count=False)]}, sfx=WIND(0.2))
sc(1, m("twin", "twin", [rail(0.1), LOCK("twin", 0.5)], tilt=30, hud=True), sfx=PING(0.6))
sc(1, m("twin", "twin", [rail(0), ring(0.2, on="둥글게"), unit("twin_e", "미군", "blue", 0.3), unit("twin_w", "프랑스군", "blue", 0.4)], tilt=30),
   hook={"hud": [HUD("2개 대대", "쌍터널을 지킨 보병", "미군 1 · 프랑스군 1", on="두 개 대대")]})
sc(1, ai("bugle_night"), label=DRAMA, sfx=FAR(0.3))
sc(1, m("twin", "twin", [ring(0), red_a(CN375, 0.1), red_a(CN374, 0.25), red_a(CN373A, 0.4), red_a(CN373B, 0.5), swarm(CN374, 0.3, 80, 0.3)], tilt=32),
   hook={"hud": [HUD("3개 연대", "사방에서 덮친 중공군", "제125사단", color="#FF3B3B", on="세 개 연대")]})
sc(1, checklist("최악의 조건", [{"text": "탄약 바닥", "on": "탄약은", "checkOn": "바닥나고", "bad": True}, {"text": "구름 · 비행기 못 뜸", "on": "하늘은", "checkOn": "없었죠", "bad": True}]))
sc(1, ai("monclar"), label=DRAMA, hook={"hud": [HUD("★★★", "프랑스 대대장", "원래 별 3개의 장군", on="별 세 개", count=False)]})
sc(1, stage([C("fr_salute", 0.5, 500, prop="officer", face="determined", anim="bounce")], [pop("label", 0.5, 0.15, "중장 → 중령", on="중령", color="yellow")]))
sc(1, ai("night_walk"), label=DRAMA)
sc(3, black("중공군은", "막을 수 없다"), hook={"neg": {"text": "막을 수 없다", "at": 0.2, "xOn": "그랬을까요"}})
sc(1, m("twin", "twin", [ring(0), shock([[127.673, 37.459], [127.69, 37.452], [127.656, 37.452], [127.662, 37.438]], 0.2, 0.9)], tilt=30),
   hook={"hud": [HUD("1,300구", "진지 앞에 남은 중공군", "미군이 직접 센 숫자", color="#FF3B3B", on="천삼백")]})
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05}})
sc(1, {"type": "titlecard", "title": "쌍터널의 철벽", "sub": "원주·쌍터널 전투 · 미 제2사단 23연대와 프랑스 대대 · 1951", "at": 0, "q": pin("french_mg")}, flash=True)
next_act()

# ===== 제1막 도망치는 군대 =====
sc(1, m("kunuri", "kunuri", [mark("kunuri", "blue", 0.2)], tilt=26), chapter={"num": "제1막", "title": "도망치는 군대"}, callouts=top("1950. 11월 말 · 군우리"), sfx=WIND(0.1))
sc(1, m("nwide", "nwide", [red_a(CN_YALU[0], 0.1), red_a(CN_YALU[1], 0.25), red_a(CN_YALU[2], 0.4), swarm([[126.0, 39.95], [126.0, 39.7]], 0.2, 120)]), callouts=low("중공군 수십만 명", "red"))
sc(1, ph("kunuri_map"), label=plabel("kunuri_map"))
sc(1, black("퇴로를", "마지막까지 지킨 부대"))
sc(1, ph("freeman", marks=[{"text": "폴 프리먼", "x": 0.5, "y": 0.18, "on": "프리먼", "color": "yellow"}]), label=plabel("freeman"))
sc(1, text("43세 · 은발의 연대장", "dark", "제23연대장 폴 프리먼 대령"))
sc(1, m("nwide", "nwide", [blue_a(RETREAT, 0.1, 1.1)]), callouts=low("1950. 12 · 남쪽으로"))
sc(1, m("nwide", "nwide", [L38, blue_a(RETREAT, 0), mark("pyongyang", "red", on="평양을")]), callouts=top("38선 아래로"))
sc(1, black("병사들 사이에 퍼진", "이상한 말"))
sc(1, text("버그아웃", "red", "bug-out · 일단 도망치기"))
sc(1, stage([C("us_shock", 0.5, 480, prop="helmet", face="sweat", anim="exit")], [pop("label", 0.5, 0.15, "짐 싸서 달아나라", on="달아난다는", color="red")]))
sc(1, ai("night_march"), label=DRAMA)
sc(1, ai("gauntlet_fire"), label=DRAMA)
sc(1, stage([C("us_shrug", 0.5, 470, prop="helmet", face="worried", anim="tilt")], [pop("q", 0.76, 0.3, on="몰랐습니다")]))
sc(1, text("워커 중장 사망", "dark", "1950. 12. 23 · 교통사고"))
sc(1, black("사흘 뒤", "새 사령관"))
sc(1, ph("ridgway", marks=[{"text": "리지웨이", "x": 0.5, "y": 0.16, "on": "리지웨이", "color": "yellow"}]), label=plabel("ridgway"))
sc(1, text("가슴에 수류탄을 단 장군", "yellow", "2차 세계 대전 공수부대 지휘관"))
sc(1, m("nwide", "nwide", [L38, dash_r([[126.98, 37.5], [127.3, 36.6]], 0.1), dash_r([[127.9, 37.3], [128.2, 36.5]], 0.3), dash_r([[128.6, 37.6], [128.9, 36.8]], 0.5)]), callouts=low("싸울 의지를 잃은 군대", "red"))
sc(1, stage([C("un_shrug", 0.5, 470, prop="officer+glasses", face="worried", flip=True)], [pop("label", 0.5, 0.15, "어디까지 물러나지?", on="물러날지만", color="dark")]))
sc(1, black("리지웨이는", "질문을 바꾼다"))
sc(1, cmp("어디까지", "물러날 것인가", "얼마나", "쓰러뜨릴 것인가", "dark", "red"))
sc(1, text("땅보다 적의 병력", "yellow", "리지웨이의 새 싸움법"))
sc(1, flat([128.3, 35.6], 5, [fpin([129.04, 35.12], "부산항", at=0.2, flag="fr", side="right")], [], [{"ll": [129.6, 34.9], "text": "대한해협", "style": "sea"}]), callouts=top("1950. 11. 29"))
sc(1, text("프랑스 자원병 대대", "blue", "1950. 11. 29 · 부산 도착"))
sc(1, ph("french_radio"), label=plabel("french_radio"), callouts=top("병력 1,000명 남짓"))
sc(1, ph("french_mg"), label=plabel("french_mg"))
sc(1, text("미 제2사단 제23연대 배속", "blue"))
sc(1, checklist("제23연대", [{"text": "제1대대", "at": 0}, {"text": "제2대대", "at": 0}, {"text": "제3대대", "at": 0}, {"text": "프랑스 대대 · 네 번째 대대", "on": "네 번째", "checkOn": "셈이었죠"}]))
sc(1, flags("프랑스 대대", [{"flag": "fr", "name": "프랑스 병사", "at": 0}, {"flag": "kr", "name": "한국인 중대", "on": "한국인"}]))
sc(1, black("이 대대를 이끄는 사람이", "문제였다"))
sc(1, text("랄프 몽클라르", "yellow"))
sc(1, ph("monclar", marks=[{"text": "본명 라울 마그랭베르느레", "x": 0.5, "y": 0.14, "on": "라울", "color": "yellow"}]), label=plabel("monclar"))
sc(1, text("외인부대의 전설", "yellow", "1차 세계 대전부터 싸워 온 군인"))
sc(1, text("★★★ 중장", "yellow", "프랑스 육군 · 군단장급 장군"))
sc(1, stage([C("fr_point", 0.45, 480, prop="officer+medal", face="determined", flip=True)], [pop("bubble", 0.74, 0.28, "한국에 가겠다!", on="가겠다고")]))
sc(1, text("대대장 = 중령", "dark"))
sc(1, stage([C("fr_salute", 0.5, 480, prop="helmet", face="smug", anim="tilt", flip=True)], [pop("label", 0.5, 0.15, "★★★ 내려놓다", on="내려놓았습니다", color="red")]))
sc(1, text("★★★ → 중령", "red", "스스로 계급을 낮춘 장군"))
sc(1, stage([C("us_idle", 0.5, 470, prop="officer+glasses", face="smug", flip=True)], [pop("q", 0.25, 0.3, on="반신반의했습니다")]))
sc(1, black("그 의심이 풀리는 데", "한 달도 걸리지 않았다"))
sc(1, m("mid", "mid", [LOCK("wonju", 0.4)], tilt=20), callouts=top("첫 무대 · 원주"), sfx=PING(0.5))
next_act()

# ===== 제2막 눈보라 속의 원주 =====
sc(1, m("nwide", "nwide", [L38]), chapter={"num": "제2막", "title": "눈보라 속의 원주"}, callouts=top("1951. 1. 1"))
sc(1, m("nwide", "nwide", [L38, red_a(NEWYEAR[0], 0.1), red_a(NEWYEAR[1], 0.3), red_a(NEWYEAR[2], 0.5)]), callouts=low("중공군·북한군 신정 공세", "red"))
sc(1, m("mid", "mid", [red_a([[127.0, 37.8], [126.98, 37.6]], 0.1), mark("seoul", "red", on="서울이")], tilt=18), callouts=top("1951. 1. 4 · 서울 다시 함락", "red"))
sc(1, stage([C("us_plead", 0.5, 480, prop="officer+helmet", face="worried")], [pop("q", 0.76, 0.3, on="걱정한")]))
sc(1, m("mid", "mid", [LOCK("wonju", 0.3, on="원주였습니다")], tilt=20), sfx=PING(0.4))
sc(1, m("mid", "mid", [mark("wonju", "blue", 0), line([[127.92, 37.342], [127.5, 37.45], [126.98, 37.566]], 0.2, "#7fd3ff"), line([[127.92, 37.342], [127.926, 36.991]], 0.4, "#7fd3ff"), line([[127.92, 37.342], [128.4, 37.45]], 0.6, "#7fd3ff")]), callouts=low("길이 모이는 곳 · 개략"))
sc(1, m("mid", "mid", [mark("wonju", "blue", 0), badge("seoul", "서울", TC, 0, -50), badge("chungju", "충주", TC, 0, -50, on="충주"), badge([128.3, 37.45], "동해안 방면", TC, 0, -50, on="동해안으로")]))
sc(1, m("mid", "mid", [mark("wonju", "red", 0), dash_r([[127.92, 37.6], [127.92, 37.34], [127.9, 37.05]], 0.2)], tilt=22), callouts=low("가운데가 갈라진다면", "red"))
sc(1, doc("리지웨이 (요지)", ["원주는 서울 다음으로 중요하다"], "回顧", "미 제8군 사령관 리지웨이", "요지"))
sc(1, ph("r23_1950"), label=plabel("r23_1950"))
sc(1, text("군우리의 상처", "dark", "아직 아물지 않은 미 제2사단"))
sc(1, m("wonju", "wonju", [red_a(NK_WONJU, 0.2), unit([127.93, 37.45], "북한군 제5군단", at=0.3)], tilt=26), callouts=top("1951. 1. 7"))
sc(1, text("피난민 옷차림의 침투병", "red", "1951. 1. 7 · 원주"))
sc(1, bars("붙잡힌 위장 침투병", [{"label": "생포", "value": 114, "display": "114명", "color": "red", "on": "백십사"}]))
sc(1, m("wonju_wide", "wonju_wide", [mark("wonju", "red", 0), blue_a(TO_SOUTH, 0.2)], tilt=22), callouts=low("원주를 버리고 남쪽으로"))
sc(1, ph("almond", marks=[{"text": "알몬드 중장", "x": 0.3, "y": 0.2, "on": "알몬드", "color": "yellow"}]), label=plabel("almond"), callouts=top("사수 명령을 어긴 철수", "red"))
sc(1, stage([C("us_point", 0.5, 480, prop="officer+helmet", face="angry", anim="shake")], [pop("bubble", 0.76, 0.28, "원주를 되찾아라!", on="되찾으라고")]))
sc(1, m("wonju", "wonju", [LOCK("h247", 0.2, on="이백사십칠고지로")], tilt=28, hud=True), callouts=top("1951. 1. 8 · 원주 남쪽 · 위치 개략"), sfx=PING(0.5))
sc(1, m("wonju", "wonju", [blue_a([[127.93, 37.25], [127.935, 37.3]], 0.1), clash("h247", 0.3)], tilt=28), callouts=low("북한군 약 200명 쓰러뜨림"))
sc(1, m("wonju", "wonju", [red_a(FLANK247, 0.1), blue_a([[127.935, 37.3], [127.94, 37.25]], 0.5)], tilt=28))
sc(1, m("wonju", "wonju", [blue_a(UP4[0], 0.1), blue_a(UP4[1], 0.2), blue_a(UP4[2], 0.3), blue_a(UP4[3], 0.4)], tilt=26), callouts=top("1. 9 · 4개 대대 다시 진격"))
sc(1, flags("1. 9 · 원주로", [{"flag": "us", "name": "미 제23·38연대", "at": 0}, {"flag": "fr", "name": "프랑스 대대", "on": "프랑스"}, {"flag": "nl", "name": "네덜란드 대대", "on": "네덜란드"}]))
sc(1, text("영하의 추위", "blue", "얼어붙은 병사들"))
sc(1, text("눈구름 · 공중 지원 없음", "dark"))
sc(1, ai("snow_column"), label=DRAMA, sfx=WIND(0))
sc(1, text("프랑스 대대의 첫 전투", "blue", "1951. 1. 10 · 247고지"))
sc(1, m("wonju", "wonju", [mark("h247", "blue", 0), red_a([[127.95, 37.27], [127.938, 37.3]], 0.1), red_a([[127.91, 37.28], [127.93, 37.3]], 0.3), red_a([[127.96, 37.31], [127.94, 37.305]], 0.5), clash("h247", 0.6)], tilt=30), callouts=low("눈보라 속 북한군의 반복 공격", "red"))
sc(1, ph("french_mg"), label=plabel("french_mg"))
sc(1, checklist("247고지 · 프랑스 대대", [{"text": "탄약", "on": "탄약이", "checkOn": "떨어집니다", "bad": True}]))
sc(1, stage([C("us_shrug", 0.5, 470, prop="helmet+glasses", face="sweat", flip=True)], [pop("label", 0.5, 0.15, "여기서 후퇴?", on="물러날", color="dark")]))
sc(1, ai("french_charge"), label=DRAMA)
sc(1, ai("twin_bayonet"), label=DRAMA)
sc(1, text("눈보라 속의 총검 돌격", "yellow", "프랑스 대대 · 247고지"))
sc(1, stage([C("nk_shock", 0.5, 470, prop="nkcap", face="shock", anim="exit")], [pop("ex", 0.75, 0.28, on="무너져")]))
sc(1, bars("1. 10 하루 · 북한군 손실 (추산)", [{"label": "손실", "value": 2000, "display": "약 2,000명", "color": "red", "on": "이천"}]))
sc(1, ph("f51"), label=plabel("f51"), callouts=top("1. 11 · 하늘이 열리다"))
sc(1, bars("1. 11~12 · 북한군 손실 (추산)", [{"label": "1. 10", "value": 2000, "display": "약 2,000명", "color": "dark", "at": 0}, {"label": "1. 11~12", "value": 1100, "display": "약 1,100명", "color": "red", "on": "천백"}]))
sc(1, m("wonju", "wonju", [obj(1, "h247", "247고지", 0, takenOn="들어왔습니다")], tilt=28), callouts=top("1951. 1. 12"))
sc(1, m("wonju", "wonju", [mark("h247", "blue", 0), radar("h247", 0.2, 1.3, "blue", "포병 사정거리 안의 원주")], tilt=24))
sc(1, m("wonju_wide", "wonju_wide", [red_a(NK_OUT, 0.2), mark("wonju", "blue", 0.5)]), callouts=low("1. 17 · 북한군 제5군단 철수"))
sc(1, ph("refugees_snow"), label=plabel("refugees_snow"))
sc(1, text("동상", "red", "적보다 무서운 추위"))
sc(1, text("원주를 지켜 내다", "blue", "1951. 1월"))
sc(1, ph("ridgway_jan"), label=plabel("ridgway_jan"))
sc(1, stage([C("us_salute", 0.5, 480, prop="officer+helmet", face="smug", anim="bounce")], [pop("label", 0.5, 0.15, "그 프랑스 부대!", on="프랑스 부대를", color="blue")]))
sc(1, doc("미 제8군 명령", ["썬더볼트 작전", "반격 개시"], "命令", "미 제8군 사령관 리지웨이", "1951. 1. 25 · 재구성"))
sc(1, ph("thunderbolt_map"), label=plabel("thunderbolt_map"))
sc(1, ph("cav_hill45"), label=plabel("cav_hill45"), callouts=top("다시 북쪽으로"))
sc(1, m("mid", "jp_wide", [LOCK("twin", 0.85)], flight=["mid", "jp_wide"], flightDur=3.0, hud=True), sfx=SW(0) + PING(0.9))
sc(1, text("쌍터널", "yellow", "미군 지도 표기 · Twin Tunnels"))
next_act()

# ===== 제3막 쌍터널의 정찰대 =====
MID = [nid()]
sc(1, m("jp_wide", "jp_wide", [mark("yangpyeong", "blue", 0.1), mark("wonju", "blue", 0.2)], tilt=24), pauseBefore=0.5, chapter={"num": "제3막", "title": "쌍터널의 정찰대"}, callouts=top("경기도 양평군 지제면"))
sc(1, m("twin_jp", "twin_jp", [rail(0.1, on="중앙선")], tilt=28), callouts=low("중앙선 철길 · 개략"))
sc(1, m("twin", "twin", [rail(0), badge([127.664, 37.4475], "터널", "#111", 0.1, -40), badge([127.68, 37.439], "터널", "#111", 0.3, -40), badge("twin", "철교", TC, 0.5, -40)], tilt=34), callouts=low("두 터널과 철교 · 위치 개략"))
sc(1, doc("미군 작전 지도", ["TWIN TUNNELS", "쌍터널"], "地圖", "미 제10군단", "1951. 1 · 재구성"))
sc(1, m("twin_jp", "twin_jp", [rail(0), line(ROAD[3:], 0.2, "#ffffff"), mark("jipyeong", "blue", on="지평리가")], tilt=26), callouts=low("북쪽 교차로 마을 · 지평리"))
sc(1, text("정찰 명령", "dark", "1951. 1. 29 새벽 · 제23연대"))
sc(1, stage([C("us_point", 0.45, 470, prop="officer+notebook", face="determined", flip=True)], [pop("q", 0.75, 0.3, on="적이")]))
sc(1, text("정찰대장 제임스 미첼 중위", "yellow", "C중대"))
sc(1, m("jp_wide", "jp_wide", [mark("ihori", "blue", on="이호리에서"), badge("ihori", "제24사단 병사 합류", TC, 0.5, -60)], tilt=22), callouts=top("이호리 · 위치 개략"))
sc(1, checklist("정찰대 장비", [{"text": "지프 9대", "on": "지프"}, {"text": "무기 운반차 2대", "on": "무기"}, {"text": "기관총 · 무반동총", "on": "기관총과"}]))
sc(1, troops(15, side="us", cols=5, title="쌍터널 정찰대", labels=[{"x": 0.5, "y": 0.74, "text": "45~60명 · 기록마다 다름", "on": "마흔다섯", "color": "blue"}]))
sc(2, text("보충병 약 20명", "red", "보병 훈련도 제대로 못 받은 신병"))
sc(1, m("twin", "twin", [blue_a(PATROL, 0.1), mark("sinchon", "blue", on="신촌")], tilt=30), callouts=top("정오 무렵 · 신촌 부근 · 위치 개략"))
sc(1, text("스타이 대위", "dark", "홀로 신촌 쪽으로"))
sc(1, black("그리고 다시는", "돌아오지 않았다"))
sc(1, m("twin", "twin", [line(PATROL, 0, "#7fd3ff"), shock([[127.671, 37.437], [127.673, 37.441]], 0.2)], tilt=30), sfx=FAR(0.2))
sc(1, m("twin", "twin", [line(PATROL, 0, "#7fd3ff"), LOCK("h453", 0.1, color="#c9242c"), red_a(TO453[::-1] + [[127.67, 37.434]], 0.4)], tilt=32, hud=True), sfx=PING(0.2))
sc(1, m("twin", "twin", [line(PATROL, 0, "#7fd3ff"), red_a([[127.66, 37.428], [127.667, 37.429]], 0.1), badge([127.664, 37.425], "퇴로 차단", "#c9242c", 0.3, -50)], tilt=32))
sc(1, ai("twin_ambush"), label=DRAMA)
sc(1, m("twin", "twin", [mark("ridge_e", "blue", 0.1, "동쪽 능선")], tilt=34), callouts=low("눈 덮인 좁은 능선 · 위치 개략"))
sc(1, ai("fox_hill"), label=DRAMA, sfx=WIND(0))
sc(1, m("twin", "twin", [mark("ridge_e", "blue", 0), red_a([[127.664, 37.432], [127.676, 37.436]], 0.1), red_a([[127.69, 37.43], [127.682, 37.436]], 0.3), red_a([[127.678, 37.447], [127.679, 37.44]], 0.5), clash("ridge_e", 0.6, 0.8)], tilt=32), callouts=low("오후 내내 · 대여섯 번의 돌격", "red"))
sc(1, ai("gunner"), label=DRAMA)
sc(1, text("“우리는 여기서 무사히 나갈 거야”", "yellow", "스트래턴 일병"))
sc(1, black("그 일병은", "끝내 내려가지 못했다"))
sc(1, m("twin", "twin", [mark("ridge_e", "blue", 0), plane([[127.64, 37.42], [127.67, 37.43], [127.7, 37.44]], 0.1, 1, 4.0, False, 0.6)], tilt=28), callouts=top("하늘 위의 정찰기"))
sc(1, m("twin", "twin", [mark("ridge_e", "blue", 0), plane([[127.65, 37.4], [127.672, 37.432], [127.69, 37.45]], 0.1, 4, 3.0, True)], tilt=28), callouts=top("오후 5시 반 무렵"), sfx=SW(0.1))
sc(1, ph("napalm"), label=plabel("napalm"))
sc(1, m("twin", "twin", [mark("ridge_e", "blue", 0), plane([[127.65, 37.43], [127.679, 37.437], [127.7, 37.445]], 0.1, 1, 3.5, False, 0.6), badge([127.688, 37.432], "탄약 투하 · 대부분 진지 밖", TC, 0.5, -50)], tilt=30))
sc(1, ai("wave_snow"), label=DRAMA)
sc(1, text("마틴슨 상사", "yellow", "5번 총에 맞고도"))
sc(1, stage([C("us_salute", 0.5, 470, prop="helmet+medal", face="angry", flip=True)], [pop("bubble", 0.24, 0.28, "항복은 없다!", on="거절했습니다")]))
sc(1, black("그 시각", "구조대가 오고 있었다"))
sc(1, text("F중대 167명", "blue", "지휘관 티렐 대위"))
sc(1, m("twin", "twin", [blue_a([[127.655, 37.41], [127.663, 37.425], [127.667, 37.431]], 0.1), obj(1, "h453", "453고지", 0, takenOn="빼앗았습니다")], tilt=30))
sc(1, stage([C("us_shock", 0.5, 460, prop="helmet", face="tears", anim="shake")], [pop("label", 0.5, 0.15, "정찰대 전멸?", on="전멸했다고", color="red")]))
sc(1, text("아침까지 기다린다", "dark", "구조대의 판단"))
sc(1, text("위생병의 소식", "blue"))
sc(1, text("아직 버티고 있다!", "yellow"))
sc(1, m("twin", "twin", [mark("h453", "blue", 0), blue_a([[127.667, 37.431], [127.673, 37.434], [127.678, 37.437]], 0.2)], tilt=30), callouts=top("밤 10시 반"))
sc(1, black("어둠 속의", "외침"))
sc(1, text("“로즈볼 경기는 누가 이겼지?”", "yellow", "어둠 속의 질문"))
sc(1, text("로즈볼", "dark", "미국 대학 미식축구 결승전 · 매년 1월 1일"))
sc(1, stage([C("cn_shrug", 0.5, 470, prop="cap", face="worried", anim="tilt")], [pop("q", 0.76, 0.3, on="대답할")]))
sc(1, text("구조!", "yellow", "능선 위의 환호"))
sc(1, ai("carry_dead"), label=DRAMA, callouts=top("새벽 3시 반 · 마지막 부상자까지"))
sc(1, troops(10, keep=2, keepAt=0.35, side="us", cols=5, title="쌍터널 정찰대", labels=[{"x": 0.5, "y": 0.74, "text": "10명 중 8명 넘게 손실", "on": "여덟", "color": "red"}]))
sc(1, black("정찰대가 알아낸", "중요한 사실"))
sc(1, m("jp_wide", "jp_wide", [mark("twin", "blue", 0), unit([127.7, 37.475], "중공군 제125사단", at=0.3, pulse=True)], tilt=24), callouts=top("쌍터널 뒤의 적", "red"))
sc(1, text("군단장 알몬드", "dark", "미 제10군단"))
sc(1, stage([C("un_point", 0.5, 480, prop="officer", face="angry", anim="bounce")], [pop("bubble", 0.78, 0.26, "찾아내 쳐부수라!", on="쳐부수라")]))
sc(1, text("임무 · 다시 제23연대", "blue", "쌍터널의 적을 찾아 섬멸하라"), hudCta={"at": 0, "dur": 7.0})
next_act()

# ===== 제4막 터널 속으로 =====
sc(1, m("jp_wide", "jp_wide", [mark("twin", "blue", 0.2)], tilt=22), chapter={"num": "제4막", "title": "터널 속으로"}, callouts=top("1951. 1. 31 · 아침 6시 반"))
sc(1, m("jp_wide", "jp_wide", [blue_a(PATROL, 0.2, 1.1)], tilt=24))
sc(1, flags("앞장선 두 대대", [{"flag": "us", "name": "제3대대", "on": "제삼대대와"}, {"flag": "fr", "name": "프랑스 대대", "on": "프랑스"}]))
sc(1, ph("howitzer"), label=plabel("howitzer"), callouts=top("제37야전포병대대"))
sc(1, text("제2대대 · 사단 예비", "dark"))
sc(1, m("jp_wide", "twin", [rail(0.6), LOCK("twin", 0.85)], flight=["jp_wide", "twin_jp", "twin"], flightDur=3.0, hud=True), sfx=SW(0))
sc(1, m("twin", "twin", [rail(0), badge("h333", "능선", "#111", 0.1, -40), badge("ridge_e", "능선", "#111", 0.25, -40), badge("nwr", "능선", "#111", 0.4, -40), badge("h453", "능선", "#111", 0.55, -40)], tilt=40), callouts=low("골짜기를 둘러싼 높은 능선"))
sc(1, ai("tunnel_inside"), label=DRAMA)
sc(1, m("twin", "twin", [rail(0), ring(0.3, on="둥근")], tilt=32), callouts=low("둥근 진지 · 위치 개략"))
sc(1, m("twin", "twin", [ring(0), unit("twin_e", "제3대대", "blue", on="동쪽")], tilt=32))
sc(1, m("twin", "twin", [ring(0), unit("twin_e", "제3대대", "blue", 0), unit("twin_w", "프랑스 대대", "blue", on="서쪽")], tilt=32))
sc(1, m("twin", "twin", [ring(0), LOCK("h453", 0.2)], tilt=32, hud=True), sfx=PING(0.3))
sc(1, text("정찰대의 퇴로를 끊었던 고지", "red", "453고지"))
sc(1, m("twin", "twin", [ring(0), unit("h453", "프랑스 제1중대", "blue", on="제일중대가", pulse=True)], tilt=32))
sc(1, text("외딴 진지", "dark", "옆 부대와 이어지지 않은"))
sc(1, m("twin", "twin", [ring(0), mark("sinchon", "blue", 0.1), badge("sinchon", "전차로 막은 빈틈", TC, 0, -50, on="전차로")], tilt=32))
sc(1, bars("중대마다 맡은 정면", [{"label": "정면 폭", "value": 1000, "display": "수백 m ~ 1,000m+", "color": "blue", "on": "수백"}]))
sc(1, checklist("쌍터널 진지", [{"text": "예비대 거의 없음", "on": "예비대는", "checkOn": "없었습니다", "bad": True}]))
sc(1, m("twin", "twin", [ring(0), dash_r([[127.7, 37.465], [127.686, 37.45], [127.672, 37.444]], 0.2)], tilt=32), callouts=low("능선 하나만 내줘도", "red"))
sc(1, stage([C("us_plead", 0.5, 480, prop="officer+helmet", face="determined", anim="tilt", flip=True)], [pop("label", 0.5, 0.15, "다른 길은 없다", on="방법이", color="dark")]))
sc(1, m("twin", "twin", [ring(0.1), mark("sinchon", "blue", 0.3)], tilt=26), callouts=top("해 질 무렵 · 진지 완성"))
sc(1, text("적의 흔적 없음", "dark", "1951. 1. 31 저녁"))
sc(1, ph("almond"), label=plabel("almond"))
sc(1, stage([C("un_idle", 0.5, 480, prop="officer", face="angry", anim="shake")], [pop("label", 0.5, 0.15, "적은 어디 있나?", on="실망했습니다", color="red")]))
sc(1, m("twin_jp", "twin_jp", [ring(0), mark("jipyeong", "red", 0.1), dash_r([[127.672, 37.455], [127.655, 37.468], [127.638, 37.476]], 0.3)], tilt=26), callouts=low("지평리까지 못 간 연대"))
sc(1, ph("stewart", marks=[{"text": "스튜어트 준장", "x": 0.22, "y": 0.2, "on": "스튜어트", "color": "yellow"}]), label=plabel("stewart"))
sc(1, doc("군단장 명령 (요지)", ["지평리에 사격을 가하라"], "命令", "미 제10군단장 알몬드", "1951. 1. 31 · 전해지는 말"))
sc(1, ai("masan_clash"), label=DRAMA)
sc(1, text("“지평리를 사격했음”", "dark", "스튜어트 준장의 보고"))
sc(1, doc("스튜어트 준장 회고 (요지)", ["터무니없는 명령이었다"], "回顧", "미 육군대학 전적 답사 교재 인용", "요지"))
sc(1, stage([C("us_idle", 0.5, 480, prop="officer+helmet", face="angry", anim="shake")], [pop("ex", 0.76, 0.28, on="화가")]))
sc(1, m("twin_jp", "twin_jp", [ring(0), radar("twin", 0.2, 1.1, "red", "적에게 알려진 위치")], tilt=26))
sc(1, black("그는 이렇게", "중얼거렸다고 전해진다"))
sc(1, text("“저들이 내 연대를 죽이려 한다”", "red", "프리먼 대령 · 전해지는 말"))
sc(1, black("그 말은", "곧 현실이 된다"))
sc(1, m("twin", "twin", [ring(0), unit("h453", "프랑스 제1중대", "blue", 0), clash("h453", 0.3, 0.8)], tilt=32), callouts=top("1. 31 밤"), sfx=FAR(0.2))
sc(1, text("중공군의 탐색전", "red", "453고지 · 신촌"))
sc(1, m("twin", "twin", [ring(0), clash("sinchon", 0.2, 0.7)], tilt=32))
sc(1, m("jp_wide", "jp_wide", [mark("twin", "blue", 0), swarm([[127.7, 37.5], [127.69, 37.47]], 0.1, 120), swarm([[127.64, 37.5], [127.65, 37.47]], 0.2, 120), swarm([[127.75, 37.48], [127.71, 37.46]], 0.3, 100)], tilt=26), callouts=low("어둠 속의 수천 명", "red"))
next_act()

# ===== 제5막 이월 일일 새벽 =====
MID.append(nid())
sc(1, black("1951년 2월 1일", "동트기 직전"), pauseBefore=0.5, chapter={"num": "제5막", "title": "2월 1일 새벽"})
sc(1, ai("bugle_gong"), label=DRAMA, sfx=WIND(0))
sc(1, m("twin", "twin", [ring(0), unit([127.68, 37.464], "중공군 제125사단", at=0.2, pulse=True)], tilt=32, hud=True))
sc(1, m("twin", "twin", [ring(0), red_a(CN375, 0.1), unit([127.673, 37.462], "제375연대", on="제삼백칠십오연대는")], tilt=32))
sc(1, m("twin", "twin", [ring(0), red_a(CN375, 0), red_a(CN374, 0.1), unit([127.7, 37.465], "제374연대", on="제삼백칠십사연대는")], tilt=32))
sc(1, ai("human_wave"), label=DRAMA)
sc(1, m("twin", "twin", [ring(0), red_a(CN375, 0), red_a(CN374, 0), red_a(CN373A, 0.2), red_a(CN373B, 0.4), unit([127.643, 37.46], "제373연대", at=0.3)], tilt=32))
sc(1, m("twin", "twin", [ring(0), red_a(CN375, 0), red_a(CN374, 0), red_a(CN373A, 0), red_a(CN373B, 0), swarm(CN375, 0.1, 80, 0.3), swarm(CN374, 0.1, 80, 0.3), swarm(CN373A, 0.2, 80, 0.3), LOCK("twin", 0.5, "포위", "#c9242c")], tilt=34, hud=True), sfx=PING(0.6))
sc(1, troops(32, side="cn", cols=8, title="공격에 나선 중공군", labels=[{"x": 0.5, "y": 0.74, "text": "약 8,000명 (추산)", "on": "팔천", "color": "red"}]))
sc(1, troops(8, side="us", cols=4, title="진지 안의 보병 · 2개 대대", vs={"n": 32, "side": "cn", "cols": 8}))
sc(1, ph("howitzer"), label=plabel("howitzer"))
sc(1, m("twin", "twin", [ring(0), shock([[127.673, 37.459], [127.69, 37.455], [127.652, 37.455], [127.66, 37.437]], 0.1, 0.8)], tilt=32), callouts=top("제37야전포병대대"), sfx=FAR(0.1))
sc(1, text("진지 바로 앞 비탈", "red", "포탄이 떨어진 곳"))
sc(1, ai("ridge_ambush"), label=DRAMA)
sc(1, m("twin", "twin", [ring(0), LOCK("h453", 0.2, "프랑스 제1중대", "#c9242c"), clash("h453", 0.4)], tilt=34, hud=True))
sc(1, m("twin", "twin", [ring(0), red_a(CN373B, 0), clash("h453", 0.1), badge("h453", "진지 일부 피탈", "#c9242c", 0.4, -60)], tilt=34))
sc(1, m("twin", "twin", [ring(0), LOCK("twin_w", 0.2, "프랑스 대대 지휘소", "#c9242c")], tilt=34, hud=True))
sc(1, ai("french_night"), label=DRAMA)
sc(1, black("문제는", "탄약"))
sc(1, bars("탄약 상자", [{"label": "남은 탄약", "value": 15, "display": "바닥", "color": "red", "on": "비어"}]))
sc(1, text("낮은 구름", "dark", "하늘이 막힌 날"))
sc(1, checklist("2월 1일 오전의 하늘", [{"text": "전투기", "on": "전투기도", "checkOn": "없는", "bad": True}, {"text": "수송기", "on": "수송기도", "checkOn": "없는", "bad": True}]))
sc(1, m("twin", "twin", [ring(0), swarm(CN374, 0.1, 100, 0.3), swarm(CN373A, 0.2, 100, 0.3)], tilt=32), callouts=top("정오 이후"))
sc(1, text("더 거세진 오후 공격", "red"))
sc(1, m("twin", "twin", [ring(0), mark("h333", "red", on="북동쪽과"), mark("nwr", "red", on="북서쪽의")], tilt=34), callouts=low("빼앗긴 능선 · 위치 개략", "red"))
sc(1, m("twin", "twin", [ring(0), mark("h333", "red", 0), mark("nwr", "red", 0), red_a([[127.688, 37.457], [127.678, 37.448]], 0.2), red_a([[127.655, 37.457], [127.665, 37.449]], 0.3)], tilt=40), callouts=low("진지 안이 내려다보이는 자리", "red"))
sc(1, stage([C("fr_shock", 0.5, 470, prop="helmet", face="coldsweat", anim="shake")], [pop("ex", 0.76, 0.28, on="뚫릴")]))
sc(1, black("그때 하늘에", "변화가 일어난다"))
sc(1, text("구름 사이의 틈", "yellow"))
sc(1, m("twin", "twin", [ring(0), plane([[127.62, 37.41], [127.66, 37.44], [127.69, 37.457]], 0.1, 4, 3.0, True)], tilt=30), sfx=SW(0.1))
sc(1, ph("napalm"), label=plabel("napalm"))
sc(1, ph("f51"), label=plabel("f51"))
sc(1, m("twin", "twin", [ring(0), plane([[127.72, 37.41], [127.69, 37.44], [127.655, 37.458]], 0.1, 3, 2.8, True), plane([[127.62, 37.47], [127.66, 37.46], [127.7, 37.45]], 0.5, 3, 2.8, True)], tilt=30))
sc(1, bars("2월 1일 · 쌍터널 공습", [{"label": "공습", "value": 80, "display": "80번+", "color": "blue", "on": "여든"}]))
sc(1, m("twin", "twin", [ring(0), shock([[127.688, 37.457], [127.655, 37.457], [127.673, 37.462]], 0.1, 0.6)], tilt=32), callouts=low("숨을 곳 없는 능선", "red"))
sc(1, ai("ranger_counter"), label=DRAMA)
sc(1, black("해가 기울며", "잦아든 나팔 소리"))
sc(1, text("공격 중지", "blue", "1951. 2. 1 해 질 녘"))
sc(1, cmp("미군·프랑스군", "2개 대대", "중공군", "3개 연대", "blue", "red"))
next_act()

# ===== 제6막 시체 천삼백 구 =====
sc(1, m("jp_wide", "jp_wide", [mark("twin", "blue", 0), blue_a(PATROL, 0.2)], tilt=24), chapter={"num": "제6막", "title": "시체 1,300구"})
sc(1, text("제1대대 도착", "blue", "오후 내내 걸어서"))
sc(1, ph("airdrop"), label=plabel("airdrop"), callouts=top("대형 수송기 14대 · 보급 투하"))
sc(1, checklist("하늘에서 온 보급", [{"text": "탄약", "on": "탄약과", "checkOn": "탄약과"}, {"text": "식량", "on": "식량", "checkOn": "식량"}, {"text": "의약품", "on": "의약품이었습니다", "checkOn": "의약품이었습니다"}]))
sc(1, ai("frozen_night"), label=DRAMA)
sc(1, stage([C("fr_idle", 0.5, 470, prop="helmet", face="worried", anim="tilt")], [pop("q", 0.76, 0.3, on="밤에")]))
sc(1, black("그날 밤", "공격은 오지 않았다"))
sc(1, text("새벽의 정찰", "dark", "1951. 2. 2"))
sc(1, text("중공군은 사라졌다", "yellow"))
sc(1, ai("pva_withdraw"), label=DRAMA)
sc(1, bars("진지 둘레에서 센 중공군 시신", [{"label": "시신", "value": 1300, "display": "1,300구", "color": "red", "on": "천삼백"}]))
sc(1, bars("중공군 손실 (미군 추산)", [{"label": "센 시신", "value": 1300, "display": "1,300구", "color": "dark", "at": 0}, {"label": "전체 사상자", "value": 3600, "display": "약 3,600명", "color": "red", "on": "삼천육백"}]))
sc(1, ph("cn_pow"), label=plabel("cn_pow"))
sc(1, text("중공군 제42군 제125사단", "red"))
sc(1, black("연대도", "대가를 치렀다"))
sc(1, bars("제23연대 손실 (미 육군 공간사 기준)", [{"label": "전사", "value": 45, "display": "45명", "color": "red", "on": "사십오"}, {"label": "부상", "value": 207, "display": "207명", "color": "dark", "on": "이백칠"}, {"label": "실종", "value": 4, "display": "4명", "color": "red", "on": "네 명"}]))
sc(1, m("twin", "twin", [ring(0), unit("h453", "프랑스 제1중대", "blue", 0), badge("h453", "가장 큰 고비", "#c9242c", 0.4, -60)], tilt=32))
sc(1, black("그래도 숫자가 말하는 것은", "분명했다"))
sc(1, text("밀려오는 중공군도 무너진다", "yellow"))
sc(1, black("이 싸움의", "세 가지 비밀"))
R3 = "쌍터널의 세 가지 비밀"
sc(1, reasons(R3, [{"text": "물러서지 않는 둥근 진지", "on": "둥근"}]))
sc(1, m("twin", "twin", [ring(0.1), unit("twin_e", "제3대대", "blue", 0.2), unit("twin_w", "프랑스 대대", "blue", 0.3), unit("h453", "프랑스 제1중대", "blue", 0.4)], tilt=30), callouts=low("등을 맞댄 원형 진지"))
sc(1, reasons(R3, [{"text": "물러서지 않는 둥근 진지", "at": 0}, {"text": "포병과 공군", "on": "포병과"}]))
sc(1, cmp("중공군", "병력의 수", "미군", "불의 양", "red", "blue"))
sc(1, reasons(R3, [{"text": "물러서지 않는 둥근 진지", "at": 0}, {"text": "포병과 공군", "at": 0}, {"text": "사람", "sub": "끝까지 자리를 지킨 병사들", "on": "사람이었습니다"}]))
sc(1, ph("french_mortar"), label=plabel("french_mortar"))
sc(1, ph("r23_1950"), label=plabel("r23_1950"))
sc(1, ph("ridgway"), label=plabel("ridgway"))
sc(1, text("땅을 내주지 않고 적을 깎아 낸다", "blue", "리지웨이의 싸움"))
sc(1, text("쌍터널", "yellow", "그 첫 본보기"))
sc(1, black("승리의 기쁨은", "오래가지 않았다"))
sc(1, troops(20, keep=15, keepAt=0.3, side="us", cols=5, title="제23연대 전력", labels=[{"x": 0.5, "y": 0.74, "text": "약 75%", "on": "칠십오", "color": "red"}]))
sc(1, m("twin_jp", "twin_jp", [blue_a([[127.672, 37.444], [127.668, 37.458], [127.652, 37.47], [127.638, 37.476]], 0.2)], tilt=26), callouts=top("1951. 2. 3"))
sc(1, m("twin_jp", "twin_jp", [LOCK("jipyeong", 0.3)], tilt=28, hud=True), sfx=PING(0.4))
sc(1, stage([C("cn_idle", 0.5, 470, prop="cap", face="smug", anim="tilt", flip=True)], [pop("label", 0.5, 0.15, "들어와라…", on="순순히", color="red")]))
sc(1, black("너무 쉽게", "내준 마을"))
sc(1, ph("winget"), label=plabel("winget"), callouts=top("지평리"))
sc(1, m("jp_wide", "jp_wide", [mark("jipyeong", "blue", 0), red_a([[127.7, 37.53], [127.65, 37.49]], 0.1), red_a([[127.56, 37.52], [127.62, 37.485]], 0.2), red_a([[127.72, 37.43], [127.655, 37.468]], 0.3), badge("jipyeong", "덫", "#c9242c", 0.5, -60)], tilt=24))
sc(1, ai("dig_in"), label=DRAMA)
sc(1, text("쌍터널에서 배운 그대로", "blue", "다시 둥근 진지"))
sc(1, stage([C("us_idle", 0.5, 470, prop="officer", face="worried", anim="tilt", flip=True)], [pop("label", 0.5, 0.15, "이번엔 군 전체", on="알고", color="red")]))
sc(1, m("mid", "mid", [mark("jipyeong", "blue", 0), swarm([[127.4, 37.85], [127.6, 37.52]], 0.1, 200), swarm([[127.9, 37.85], [127.75, 37.55]], 0.2, 200)]), callouts=low("중공군 여러 개 군", "red"))
next_act()

# ===== 제7막 철벽의 의미 =====
MID.append(nid())
sc(1, m("mid", "mid", [red_a(FEB_OFF[0], 0.1), red_a(FEB_OFF[1], 0.3), red_a(FEB_OFF[2], 0.5)]), pauseBefore=0.5, chapter={"num": "제7막", "title": "철벽의 의미"}, callouts=top("1951. 2. 11 밤 · 2월 공세", "red"))
sc(1, text("제4차 공세", "red", "중공군 2월 공세"))
sc(1, ph("hoengsong_map"), label=plabel("hoengsong_map"))
sc(1, m("wonju_wide", "wonju_wide", [mark("hoengseong", "red", 0), blue_a(HSG_OUT, 0.2), mark("wonju", "blue", 0.5)], tilt=22), callouts=low("횡성 → 원주"))
sc(1, m("jp_wide", "jp_wide", [LOCK("jipyeong", 0.2, color="#c9242c"), swarm([[127.7, 37.52], [127.65, 37.485]], 0.3, 100), swarm([[127.58, 37.42], [127.63, 37.47]], 0.4, 100)], tilt=24, hud=True), sfx=PING(0.3))
sc(1, m("jp_ring", "jp_ring", [line(JP_RING, 0, "#7fd3ff"), {"k": "front", "path": [[127.6, 37.5], [127.66, 37.5], [127.67, 37.455], [127.605, 37.452], [127.6, 37.5]], "at": 0.3, "glow": True}], tilt=28), callouts=top("1951. 2. 13 · 포위", "red"))
sc(1, stage([C("un_plead", 0.5, 470, prop="officer", face="sweat")], [pop("label", 0.5, 0.15, "철수하겠습니다", on="건의했지만", color="dark")]))
sc(1, doc("리지웨이 명령 (요지)", ["지평리를 지켜라"], "命令", "미 제8군 사령관", "1951. 2. 13 · 재구성"))
sc(1, ph("freeman"), label=plabel("freeman"), callouts=top("제23연대장 프리먼 대령"))
sc(1, text("“우리는 포위됐다 그러나 여기 남아 싸운다”", "yellow", "프리먼 대령 · 전해지는 말"))
sc(1, troops(18, side="us", cols=6, title="지평리의 제23연대 + 프랑스 대대", labels=[{"x": 0.5, "y": 0.74, "text": "약 4,500명", "on": "사천오백", "color": "blue"}]))
sc(1, troops(10, side="us", cols=5, title="지평리", vs={"n": 40, "side": "cn", "cols": 10}, labels=[{"x": 0.7, "y": 0.8, "text": "중공군 여러 개 사단", "on": "여러", "color": "red"}]))
sc(1, ai("basin_night"), label=DRAMA, sfx=FAR(0.2))
sc(1, m("jp_ring", "jp_ring", [line(JP_RING, 0, "#7fd3ff"), unit("pw", "프랑스 대대", "blue", on="서쪽을")], tilt=28))
sc(1, ai("siren"), label=DRAMA, callouts=low("전해지는 이야기"))
sc(1, stage([C("us_plead", 0.5, 470, prop="officer+helmet", face="sweat+determined", anim="shake")], [pop("label", 0.5, 0.15, "다리를 다치고도 지휘", on="다치고도", color="yellow")]))
sc(1, ai("tank_run"), label=DRAMA, callouts=top("1951. 2. 15 · 크롬베즈 특수임무부대"))
sc(1, m("jp_ring", "jp_ring", [line(JP_RING, 0, "#7fd3ff"), red_a([[127.645, 37.49], [127.66, 37.51]], 0.1), red_a([[127.62, 37.465], [127.6, 37.45]], 0.3)], tilt=26))
sc(1, text("중공군의 첫 뚜렷한 패배", "blue", "1951. 2. 15 · 지평리"))
sc(1, black("같은 무렵", "원주에서도"))
sc(1, m("seom", "seom", [LOCK("seom", 0.3)], tilt=24, hud=True), callouts=top("1951. 2. 14 · 원주 북서쪽"), sfx=PING(0.4))
sc(1, m("seom", "seom", [red_a(SEOM_COL, 0.1), red_a(SEOM_COL2, 0.2), swarm(SEOM_COL, 0.2, 100, 0.3), plane([[127.7, 37.35], [127.8, 37.42], [127.9, 37.47]], 0.5, 1, 3.5, False, 0.6)], tilt=26))
sc(1, m("seom", "seom", [red_a(SEOM_COL, 0), red_a(SEOM_COL2, 0), shock([[127.8, 37.43], [127.83, 37.41], [127.85, 37.4]], 0.1), plane([[127.95, 37.3], [127.84, 37.4], [127.75, 37.48]], 0.3, 4, 3.0, True)], tilt=26), sfx=FAR(0.1))
sc(1, m("seom", "seom", [red_a(SEOM_TURN, 0.2), mark("wonju", "blue", 0)], tilt=24))
sc(1, text("오후 3시 · 멈춘 공세", "yellow", "원주로 향하던 중공군"))
sc(1, text("원주 사격전", "red", "Wonju Shoot"))
sc(1, cmp("지평리", "2. 13~15", "원주", "2. 14", "blue", "blue"))
sc(1, text("한국전쟁의 게티즈버그", "yellow"))
sc(1, m("mid", "mid", [line(HIGHWATER, 0.1, "#ffd400"), mark("jipyeong", "blue", 0.3), mark("wonju", "blue", 0.4)], tilt=18), callouts=low("중공군 공세가 꺾인 선"))
sc(1, black("이제", "처음의 질문으로"))
sc(1, black(" "), hook={"question": {"text": QUESTION, "at": 0.05, "kicker": "■ 처음의 질문 ■"}})
sc(1, text("답은 한 번에 오지 않았다", "dark"))
sc(1, ai("twin_bayonet"), label=DRAMA, callouts=top("1951. 1. 10 · 원주 247고지"))
sc(1, ai("twin_ambush"), label=DRAMA, callouts=top("1951. 1. 29 · 쌍터널 정찰대"))
sc(1, m("twin", "twin", [ring(0), red_a(CN375, 0), red_a(CN374, 0), red_a(CN373A, 0), red_a(CN373B, 0), LOCK("twin", 0.5, "2개 대대 vs 3개 연대", "#2e66d8")], tilt=30))
sc(1, text("작은 승리들이 쌓은 철벽", "blue"))
sc(1, black("중공군도", "막을 수 있다"))
sc(1, ph("cav_hill45"), label=plabel("cav_hill45"), callouts=top("다시 북쪽으로"))
sc(1, doc("리지웨이 미국 의회 연설 (요지)", ["프리먼 대령의 제23연대", "그리고 프랑스 대대"], "演說", "1952. 5 · 미국 의회 합동 회의", "요지"))
sc(1, flags("리지웨이가 꼽은 부대", [{"flag": "us", "name": "제23연대", "at": 0}, {"flag": "fr", "name": "프랑스 대대", "on": "프랑스"}]))
sc(1, doc("미국 대통령 부대 표창", ["미 제23연대", "프랑스 대대"], "表彰", "미국 대통령", "재구성 · 요지"))
SOMBER = nid()
sc(1, ph("monclar"), label=plabel("monclar"), callouts=top("다시 장군의 자리로"))
sc(1, text("파리 앵발리드", "dark", "몽클라르가 잠든 곳"))
sc(1, text("프랑스 병사 약 3,500명", "blue", "한국전쟁 참전 · 교대 병력 포함"))
sc(1, ph("monument"), label=plabel("monument"))
sc(1, m("twin", "twin", [rail(0.1)], tilt=26), callouts=low("오늘도 달리는 중앙선 · 개략"))
sc(1, ai("basin_dawn"), label=DRAMA)
sc(1, ph("french_radio"), label=plabel("french_radio"))
sc(1, text("철벽 위에서 바뀐 전쟁의 흐름", "yellow"))
sc(2, {"type": "endcard", "title": "쌍터널과 원주의 철벽을 쌓은\n모든 이들을 기억하며", "q": pin("french_mg")}, tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트: 전부 재사용 (2026-11-18 Gemini 선불 크레딧 소진 — 새 그림 0장, 파일·서명 복사, 추가 비용 0) =====
REUSE = {
    "twin_wave": "chipyongni", "monclar": "chipyongni", "twin_ambush": "chipyongni", "gunner": "chipyongni", "wave_snow": "chipyongni",
    "dig_in": "chipyongni", "masan_clash": "chipyongni", "twin_bayonet": "chipyongni", "ranger_counter": "chipyongni", "pva_withdraw": "chipyongni",
    "basin_night": "chipyongni", "siren": "chipyongni", "french_charge": "chipyongni", "basin_dawn": "chipyongni", "tank_run": "chipyongni",
    "night_walk": "ep18-kunuri", "gauntlet_fire": "ep18-kunuri", "frozen_night": "ep18-kunuri", "carry_dead": "ep18-kunuri", "ridge_ambush": "ep18-kunuri", "snow_column": "ep18-kunuri",
    "bugle_night": "ep20-imjin-river", "human_wave": "ep20-imjin-river", "bugle_gong": "ep21-gapyeong", "night_march": "ep24-hyeonri",
    "tunnel_inside": "ep19-sniper-ridge", "fox_hill": "jangjin", "french_night": "heartbreak",
}
AI = {}
AIDIR = ROOT / "public" / "ep" / EP / "ai"
AIDIR.mkdir(parents=True, exist_ok=True)
MAN = AIDIR.parent / "ai.json"  # ai_images.py가 읽는 위치 (public/ep/<ep>/ai.json)
man = json.loads(MAN.read_text()) if MAN.exists() else {}
for k, src in REUSE.items():
    AI[k] = json.loads((ROOT / "episodes" / src / "storyboard.json").read_text(encoding="utf-8"))["ai_images"][k]
    shutil.copyfile(ROOT / "public" / "ep" / src / "ai" / f"{k}.jpg", AIDIR / f"{k}.jpg")
    man[k] = hashlib.sha1(f"gpt-image-1|high|{AI[k]}".encode()).hexdigest()[:12]
MAN.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
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
board = {"title": "쌍터널의 철벽", "subtitle": "원주·쌍터널 전투 · 미 제2사단 23연대와 프랑스 대대 · 1951", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         "target_sec": 1230, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap],
      "ai", len(AI), "pins", len(PINS), "stage", len(stages), "photo", sum(1 for s in S if s["visual"]["type"] == "photo"))
print("char uses", dict(cnt))
