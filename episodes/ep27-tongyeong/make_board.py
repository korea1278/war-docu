# EP27 통영상륙작전 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 연출 스타일 v2 + 화면 업그레이드 2단계 + 롱폼 표준(LONGFORM_STANDARD: 막 단위 TTS · 절제된 효과음 · BGM -24dB · 자막 28자 · 싱크 ±0.5초)
# + 캐릭터 반복 방지 규칙 첫 적용: stage chars[].face / prop / anim (Stage.tsx), 같은 조합 연속·3회 초과 금지 assert
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
    ("천구백오십년 팔월 십칠일 저녁 여섯 시", "1950년 8월 17일 저녁 6시"), ("천구백사십구년 사월 십오일", "1949년 4월 15일"),
    ("천구백오십년 구월 십오일", "1950년 9월 15일"), ("천구백오십년 팔월", "1950년 8월"),
    ("팔월 십칠일 오후 다섯 시쯤", "8월 17일 오후 5시쯤"), ("팔월 십칠일 새벽 세 시", "8월 17일 새벽 3시"), ("팔월 십육일 밤 열 시", "8월 16일 밤 10시"),
    ("팔월 십구일 오후 세 시 사십 분", "8월 19일 오후 3시 40분"), ("팔월 이십일 새벽 두 시 사십 분", "8월 20일 새벽 2시 40분"), ("팔월 십구일 오전 열 시", "8월 19일 오전 10시"),
    ("팔월 십팔일", "8월 18일"), ("팔월 십육일", "8월 16일"), ("팔월 십칠일", "8월 17일"), ("구월 이십이일", "9월 22일"), ("팔월 중순", "8월 중순"), ("팔월 초", "8월 초"), ("팔월이면", "8월이면"),
    ("오후 여섯 시", "오후 6시"), ("오후 두 시", "오후 2시"), ("이천칠년", "2007년"),
    ("삼백오십팔 년 전", "358년 전"), ("대대급 삼백여 명", "대대급 300여 명"), ("삼백여 명", "300여 명"), ("사백 명 남짓", "400명 남짓"),
    ("일 년 이 개월", "1년 2개월"), ("일 년 사 개월", "1년 4개월"), ("두 달도", "두 달도"),
    ("이백육십여 척", "260여 척"), ("일곱 척", "7척"), ("목선 세 척", "목선 3척"), ("소해정 두 척", "소해정 2척"),
    ("오백팔십 발", "580발"), ("세 시간 동안", "3시간 동안"), ("아홉 차례", "9차례"), ("아홉 번", "9번"),
    ("삼십칠 일", "37일"), ("사백육십구 명", "469명"), ("팔십삼 명", "83명"), ("사분의 삼", "4분의 3"),
    ("열다섯 명 부상 마흔일곱 명", "15명 부상 47명"), ("열다섯 명 혹은 열아홉 명", "15명 혹은 19명"), ("열아홉 명", "19명"),
    ("백여 명 가운데 쉰 명", "100여 명 가운데 50명"), ("스무 살", "스무 살"),
    ("제이중대와 제칠중대", "제2중대와 제7중대"), ("제이중대", "제2중대"), ("제칠중대", "제7중대"), ("이틀 만에", "이틀 만에"),
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


SEAV = {"south", "strait", "peninsula", "neck", "town"}


def m(fr, to=None, items=None, **kw):
    v = {"type": "map", "from": fr, "to": to or fr, "items": items or []}
    # demSea는 tongyeong_sea 래스터 안쪽 뷰에서만 (넓은 뷰에 켜면 래스터 사각 경계가 비침)
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


def doc(head, rows, stamp="軍 秘", org="대한민국 해병대", note="재구성 · 내용 요약"):
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


# 사진: 스카우트 catalog.json 설명으로 확인한 파일 (미 국립문서기록관리청·미 해군·미 해병대·국방부·문체부 공개 자료)
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
# 좌표는 개략 (망일봉·장평리·원문고개는 현재 지명 기준 근사)
P = {
    "tongyeong": [128.425, 34.846, "통영"], "wonmun": [128.418, 34.877, "원문고개"], "mangil": [128.43, 34.861, "망일봉"],
    "jangpyeong": [128.447, 34.875, "장평리"], "nammang": [128.431, 34.842, "남망산"], "sambong": [128.44, 34.882, "삼봉산"],
    "geoje": [128.62, 34.88, "거제도"], "gyeonnae": [128.468, 34.892, "견내량"], "goseong": [128.322, 34.973, "고성"],
    "masan": [128.57, 35.21, "마산"], "jinhae": [128.7, 35.135, "진해"], "jindong": [128.48, 35.108, "진동리"], "busan": [129.04, 35.18, "부산"],
    "hansan": [128.5, 34.79, "한산도"], "daegu": [128.6, 35.87, "대구"], "seoul": [126.978, 37.566, "서울"], "incheon": [126.62, 37.47, "인천"],
}
V = {
    "korea": {"center": [127.6, 36.4], "span": 4.6}, "perimeter": {"center": [128.7, 35.65], "span": 1.9}, "sw": {"center": [128.68, 35.08], "span": 0.95},
    "south": {"center": [128.5, 34.95], "span": 0.62}, "strait": {"center": [128.5, 34.84], "span": 0.3}, "peninsula": {"center": [128.43, 34.87], "span": 0.26},
    "neck": {"center": [128.43, 34.872], "span": 0.12}, "town": {"center": [128.428, 34.856], "span": 0.1},
}
# 1950년 8월 낙동강 방어선 (개략)
PERIM = [[128.36, 35.04], [128.38, 35.25], [128.45, 35.4], [128.42, 35.6], [128.38, 35.85], [128.42, 36.02], [128.62, 36.12], [128.95, 36.16], [129.3, 36.2], [129.42, 36.12]]
front = {"k": "front", "path": PERIM, "at": 0}
NECK = [[128.405, 34.879], [128.418, 34.877], [128.436, 34.874]]  # 원문고개를 가로지르는 '마개' 선 (개략)
plug = lambda at=0, on=None: dict({"k": "line", "path": NECK, "color": "#2e9bff", "glow": True}, **({"on": on} if on else {"at": at}))
LOCK = lambda p="wonmun", at=0.3, text=None, color=None, on=None: dict({"k": "lock", "p": p, "text": text or P[p][2]}, **({"on": on} if on else {"at": at}), **({"color": color} if color else {}))
badge = lambda p, t, c="#111", at=0.3, dy=-70, on=None: dict({"k": "badge", "p": p, "text": t, "color": c, "dy": dy}, **({"on": on} if on else {"at": at}))
red_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "red", "width": w}, **({"on": on} if on else {"at": at}))
blue_a = lambda path, at=0.3, w=1.0, on=None: dict({"k": "arrow", "path": path, "color": "blue", "width": w}, **({"on": on} if on else {"at": at}))
mark = lambda p, color="red", at=0, text=None, on=None: dict({"k": "marker", "p": p, "color": color}, **({"text": text} if text else {}), **({"on": on} if on else {"at": at}))
obj = lambda n, p, text, at=0, takenAt=None, takenOn=None: dict({"k": "obj", "n": n, "p": p, "text": text, "at": at}, **({"takenAt": takenAt} if takenAt is not None else {}), **({"takenOn": takenOn} if takenOn else {}))
clash = lambda p, at=0.3, size=1.0: {"k": "clash", "p": p, "at": at, "period": 0.9, "size": size}
HARBOR = [[128.424, 34.843], [128.432, 34.847], [128.419, 34.848], [128.428, 34.851]]
shock = lambda pts=HARBOR, at=0.2, period=0.7: {"k": "shock", "pts": pts, "at": at, "period": period}
PASS_PTS = [[128.413, 34.879], [128.421, 34.878], [128.416, 34.874], [128.425, 34.876], [128.41, 34.882]]
SEA_IN = [[128.52, 34.81], [128.47, 34.835], [128.44, 34.843]]          # 통영항 앞바다 → 항구 (양동 포격)
LAND_E = [[128.51, 34.89], [128.48, 34.881], [128.452, 34.876]]         # 견내량 쪽 → 장평리 해안 (개략)
TO_PASS = [[128.447, 34.875], [128.433, 34.878], [128.42, 34.877]]      # 장평리 → 원문고개
TO_PEAK = [[128.447, 34.875], [128.438, 34.868], [128.431, 34.862]]     # 장평리 → 망일봉
NK_IN = [[128.322, 34.973], [128.37, 34.93], [128.405, 34.892], [128.418, 34.877], [128.424, 34.855]]  # 고성 → 원문고개 → 통영 시내
NK_OUT = list(reversed(NK_IN))
NK_PASS = [[128.33, 34.96], [128.38, 34.915], [128.41, 34.888], [128.416, 34.88]]
COAST_W = [[128.39, 34.885], [128.4, 34.874], [128.408, 34.868]]       # 고개 서쪽 해안선 침투 (개략)
COAST_E = [[128.42, 34.892], [128.436, 34.884], [128.44, 34.879]]      # 고개 동쪽 해안선 침투 (개략)
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]
SW = lambda at=0: [{"id": "whoosh", "at": at}]
FAR = lambda at=0.1: [{"id": "artillery_far", "at": at}]
PING = lambda at=0.6: [{"id": "ping", "at": at}]
WATER = lambda at=0.1: [{"id": "water", "at": at}]
WIND = lambda at=0: [{"id": "wind", "at": at}]
MAR = "helmet"
NKC = "nkcap"

# ===== 콜드 오프닝 =====
sc(1, ai("naval_feint_dusk"), label=DRAMA, callouts=top("1950. 8. 17 · 저녁 6시"), sfx=FAR(0.3))
sc(1, m("south", "peninsula", [mark("tongyeong", "red", 0.3), blue_a(SEA_IN, 0.5), badge([128.5, 34.82], "해군 함정", "#2e66d8", 0.9, 0)], flight=["south", "peninsula"], flightDur=3.0), sfx=SW(0))
sc(1, m("peninsula", "peninsula", [mark("tongyeong", "red", 0), shock(HARBOR, 0.2, 0.6), blue_a(SEA_IN, 0)], tilt=26), callouts=top("통영항 · 양동 포격", "red"))
sc(1, stage([C("nk_shock", 0.62, 480, flip=True, prop=NKC, face="sweat", anim="shake")], [pop("ex", 0.3, 0.32, on="항구"), pop("label", 0.62, 0.17, "항구 쪽이다!", on="쏠립니다", color="red")]))
sc(1, m("neck", "neck", [blue_a(LAND_E, 0.3), badge("jangpyeong", "반대편 조용한 해안", "#2e66d8", 0.8, -70)], tilt=30, hud=True), sfx=WATER(0.4))
sc(1, ai("landing_dusk"), label=DRAMA, callouts=low("대한민국 해병대"))
sc(1, black("그런데", "이상한 점 하나"))
sc(1, black("받은 명령은", "통영이 아니었다"))
sc(2, doc("작전 명령", ["통영은 포기한다", "거제도를 지켜라"], "命令", "해군 지휘부"))
sc(1, m("south", "south", [mark("geoje", "blue", 0, "명령: 거제도"), mark("tongyeong", "red", 0, "적 점령: 통영"), blue_a([[128.6, 34.86], [128.52, 34.86], [128.45, 34.86]], on="통영으로", w=1.2)]))
sc(1, text("대대급 300여 명", "yellow", "김성은 부대 · 기록에 따라 330명 등"))
sc(1, stage([C("kr_salute", 0.5, 500, prop=MAR, face="determined")], [pop("label", 0.5, 0.16, "한국군 첫 단독 상륙작전", on="혼자서", color="yellow")]))
sc(1, ai("nk_column_coast"), label=DRAMA)
sc(1, black("그런데", "결과는 놀라웠다"))
sc(1, m("town", "town", [mark("tongyeong", "blue", 0.1), obj(1, "mangil", "망일봉", 0, 0.5)], tilt=24), callouts=top("이틀 만에 탈환", "blue"))
sc(1, text("한 달 넘게 사수", "blue", "1950. 8. 17 ~ 9. 22"))
sc(1, ph("higgins"), label=plabel("higgins"))
sc(1, text("귀신도 잡을 해병", "red"))
sc(1, stage([C("kr_shrug", 0.4, 460, prop=MAR, face="worried")], [pop("q", 0.68, 0.32, at=0.2, size=220)], title="왜 명령과 다른 길을?"))
sc(1, stage([C("nk_plead", 0.5, 440, prop=NKC, face="tears", anim="shake")], [pop("label", 0.5, 0.16, "독 안에 갇힌 적?", on="독 안에", color="red")]))
sc(1, m("peninsula", "neck", [LOCK("wonmun", 0.6)], flight=["peninsula", "neck"], flightDur=2.6, hud=True), sfx=SW(0) + PING(0.7))
sc(1, m("neck", "neck", [LOCK("wonmun", 0), badge("wonmun", "원문고개", "#c9242c", 0.2, -110)], tilt=36))
sc(1, black("이 고개가 왜 모든 것을 갈랐는지", "끝까지 보시면 알게 됩니다"))
sc(1, {"type": "titlecard", "title": "통영상륙작전", "sub": "귀신 잡는 해병의 탄생 · 1950", "at": 0, "q": pin("kmc_pusan")}, flash=True)

# ===== 제1막 반도의 목을 노려라 =====
sc(1, ph("pusan_105"), label=plabel("pusan_105"), chapter={"num": "제1막", "title": "반도의 목을 노려라"})
sc(1, ph("refugees"), label=plabel("refugees"))
sc(1, m("korea", "perimeter", [front, red_a([[127.0, 37.4], [127.5, 36.6], [128.1, 35.95]], 0.2, 1.3)], flight=["korea", "perimeter"], flightDur=3.0), callouts=top("1950년 8월 · 낙동강까지", "red"), sfx=SW(0))
sc(1, m("perimeter", "perimeter", [front, mark("busan", "blue", on="부산을")]), callouts=low("부산을 둘러싼 마지막 땅 · " + NOTE))
sc(1, text("임시 수도 부산", "yellow", "1950년 8월 · 정부 부산 이전"))
sc(1, black("부산이 무너지면", "대한민국도 끝"))
sc(1, m("perimeter", "perimeter", [dict(front, glow=True), badge([128.42, 35.55], "낙동강 방어선", "#2e66d8", 0.3, 0)], tilt=22))
sc(1, ph("rok_hills"), label=plabel("rok_hills"))
sc(1, stage([C("kr_shock", 0.5, 460, prop=MAR, face="worried")], [pop("ex", 0.75, 0.3, on="따로")]))
sc(1, m("perimeter", "sw", [front, LOCK("masan", 0.8)], flight=["perimeter", "sw"], flightDur=2.4), sfx=PING(0.9))
sc(1, m("sw", "sw", [front, mark("masan", "red", 0), mark("busan", "blue", 0), red_a([[128.57, 35.21], [128.8, 35.2], [129.0, 35.18]], 0.3, 1.0)]), callouts=top("마산 → 부산", "red"))
sc(1, ph("usmc_aug"), label=plabel("usmc_aug"))
sc(1, ph("masan_mortar"), label=plabel("masan_mortar"))
sc(1, m("sw", "sw", [front, mark("jindong", "blue", 0), red_a([[128.25, 35.15], [128.38, 35.12], [128.45, 35.11]], 0.1), clash("jindong", 0.5)]), callouts=low("진동리에서 막힌 북한군 · " + NOTE))
sc(1, stage([C("nk_point", 0.5, 480, prop=NKC, face="smug", anim="bounce")], [pop("label", 0.5, 0.16, "정면이 막히면 옆으로!", at=0.2, color="red")]))
sc(1, m("sw", "south", [front, red_a([[128.3, 35.12], [128.3, 35.03], [128.322, 34.973], [128.39, 34.9]], 0.2, 1.1)], flight=["sw", "south"], flightDur=2.6), callouts=top("고성을 거쳐 남쪽 바닷가로", "red"))
sc(1, m("south", "south", [mark("goseong", "red", 0), LOCK("tongyeong", 0.3, "통영", "#c9242c")]), sfx=PING(0.4))
sc(1, ai("tongyeong_1950"), label=DRAMA, callouts=low("지키는 병력이 거의 없던 항구"))
sc(1, m("peninsula", "peninsula", [mark("tongyeong", "red", 0.2)], tilt=28))
sc(1, m("peninsula", "peninsula", [mark("tongyeong", "red", 0), badge([128.43, 34.85], "머리", "#111", on="머리처럼", dy=0)], tilt=28))
sc(1, m("peninsula", "peninsula", [badge([128.43, 34.85], "머리", "#111", 0, 0), badge([128.41, 34.9], "몸통", "#111", on="몸통을", dy=0), plug(on="목이")], tilt=28))
sc(1, m("neck", "neck", [plug(0), LOCK("wonmun", 0.4)], tilt=34, hud=True), sfx=PING(0.5))
sc(1, m("south", "south", [mark("tongyeong", "red", 0), red_a([[128.45, 34.86], [128.53, 34.87], [128.6, 34.88]], 0.3)]), callouts=low("통영 → 거제도"))
sc(1, ph("navy_chinhae"), label=plabel("navy_chinhae"))
sc(1, m("sw", "sw", [mark("jinhae", "blue", 0), mark("masan", "blue", 0), mark("busan", "blue", 0), red_a([[128.45, 34.87], [128.6, 35.0], [128.7, 35.12]], 0.3)]), callouts=top("남쪽 바닷길이 흔들린다", "red"))
sc(1, m("peninsula", "peninsula", [{"k": "swarm", "path": NK_IN, "at": 0.1, "n": 120}, red_a(NK_IN, 0.3)], tilt=26), callouts=top("8월 중순 · 통영 진입", "red"))
sc(1, ai("tongyeong_occupied"), label=DRAMA)
sc(1, text("통영 함락", "red", "1950년 8월 중순"))
next_act()

# ===== 제2막 창설 일 년 사 개월의 해병대 =====
MID = [nid()]
sc(1, ph("kmc_flag"), label=plabel("kmc_flag"), pauseBefore=0.5, chapter={"num": "제2막", "title": "창설 1년 4개월의 해병대"})
sc(1, stage([C("kr_salute", 0.5, 520, prop=MAR, face="smug")], [pop("label", 0.5, 0.15, "대한민국 해병대", at=0.1, color="blue")]))
sc(1, text("아주 젊은 군대", "yellow"))
sc(2, text("1949. 4. 15 창설", "blue", "경상남도 진해 덕산 비행장"))
sc(1, text("약 400명", "yellow", "창설 당시 장교·병사 합계"))
sc(1, text("창설 1년 2개월 만에 전쟁", "red"))
sc(2, checklist("1950년 6월의 해병대", [{"text": "상륙작전 경험", "on": "상륙작전은", "checkOn": "없었죠", "bad": True}, {"text": "상륙함", "on": "상륙함도", "checkOn": "상륙함도", "bad": True}, {"text": "상륙 장갑차", "on": "장갑차도", "checkOn": "없었습니다", "bad": True}]))
sc(1, stage([C("kr_point", 0.5, 480, prop="officer", face="determined")], [pop("label", 0.5, 0.15, "지휘관 김성은", on="김성은", color="dark")]))
sc(1, text("김성은", "blue", "해병대 창설 멤버 · 1924년생"))
sc(1, ph("kmc_amtrac"), label=plabel("kmc_amtrac"))
sc(1, black("통영 직전", "큰 싸움"))
sc(1, m("sw", "sw", [front, LOCK("jindong", 0.3, "진동리")]), callouts=top("8월 초 · 진동리 전투"), sfx=PING(0.4))
sc(1, ai("jindong_ambush"), label=DRAMA)
sc(1, stage([C("kr_salute", 0.5, 500, prop="officer+medal", face="smug")], [pop("label", 0.5, 0.15, "1계급 특진", on="특진", color="yellow")]))
sc(2, text("대령 김성은", "yellow", "중령으로 적은 자료도 있음 · 8월 초 특진 기록 기준"))
sc(1, black("쉴 틈은", "없었다"))
sc(1, doc("긴급 보고", ["북한군 통영 진입", "다음 목표는 거제도?"], "緊急", "해군 지휘부"))
sc(1, m("peninsula", "peninsula", [{"k": "unit", "p": "tongyeong", "text": "북한군", "color": "red", "pulse": True, "at": 0.1}], tilt=24))
sc(1, m("south", "south", [mark("tongyeong", "red", 0), red_a([[128.45, 34.86], [128.53, 34.87], [128.6, 34.88]], 0.2, 1.0), badge("geoje", "거제도?", "#c9242c", 0.6, -60)]))
sc(1, m("sw", "sw", [mark("geoje", "red", 0), mark("jinhae", "blue", 0), red_a([[128.62, 34.92], [128.66, 35.04], [128.7, 35.12]], 0.3)]), callouts=low("거제도 → 진해 앞바다"))
sc(1, ph("sohn"), label=plabel("sohn"))
sc(1, doc("작전 명령", ["김성은 부대는 거제도로 이동", "적이 바다를 건너오지 못하게 막아라"], "命令", "해군참모총장"))
sc(1, text("상식적인 명령", "dark"))
sc(2, checklist("거제 방어가 안전해 보인 이유", [{"text": "병력이 적다", "on": "병력은", "checkOn": "병력은"}, {"text": "장비가 모자라다", "on": "장비는", "checkOn": "모자랐"}, {"text": "섬을 지키면 바다가 방패", "on": "섬을", "checkOn": "안전한"}]))
sc(1, ai("strait_night"), label=DRAMA, callouts=top("8. 16 밤 10시 · 출동"))
sc(1, m("south", "strait", [mark("gyeonnae", "blue", 0.6), blue_a([[128.7, 34.98], [128.56, 34.93], [128.47, 34.895]], 0.3)], flight=["south", "strait"], flightDur=2.4), sfx=SW(0))
sc(1, m("strait", "strait", [badge("gyeonnae", "견내량", "#2e66d8", 0.2, -60)], tilt=28))
sc(1, ai("hansan_1592"), label=DRAMA, callouts=top("1592년 · 견내량"))
sc(1, m("strait", "strait", [mark("hansan", "blue", 0), blue_a([[128.468, 34.892], [128.49, 34.85], [128.5, 34.81]], 0.2, 1.1)], tilt=24), callouts=low("견내량 → 한산도 앞바다"))
sc(1, text("한산도대첩", "yellow", "1592년 · 이순신"))
sc(1, m("strait", "strait", [blue_a([[128.56, 34.93], [128.5, 34.91], [128.468, 34.892]], 0.2), badge("gyeonnae", "김성은 부대", "#2e66d8", 0.7, -60)], tilt=28))
sc(1, m("neck", "neck", [badge([128.445, 34.9], "작은 섬 도착 · 개략", "#2e66d8", 0.3, 0)], tilt=26), callouts=top("8. 17 새벽 3시"))
sc(1, ai("recon_boat"), label=DRAMA)
sc(1, ai("kim_map"), label=DRAMA)
sc(1, m("peninsula", "peninsula", [badge([128.43, 34.85], "머리", "#111", on="머리가", dy=0), plug(on="목이")], tilt=26))
sc(1, m("peninsula", "peninsula", [plug(0), red_a(NK_IN, on="들어온")], tilt=26))
sc(1, m("peninsula", "peninsula", [plug(0), {"k": "arrow", "path": NK_OUT, "color": "red", "width": 0.9, "on": "나가는"}], tilt=26))
sc(1, stage([C("kr_point", 0.4, 480, prop=MAR, face="determined")], [pop("q", 0.72, 0.3, on="막으면")]))
sc(1, m("neck", "neck", [plug(0.1), LOCK("wonmun", 0.2), badge("tongyeong", "독 안의 쥐", "#c9242c", on="독 안에", dy=-60)], tilt=30, hud=True), sfx=PING(0.3))
sc(1, m("peninsula", "peninsula", [plug(0), red_a(NK_PASS, 0.2), clash("wonmun", 0.6)], tilt=26), callouts=low("뒤따르는 적 지원군 차단"))
sc(1, cmp("거제도 방어", "기다리는 싸움", "통영 상륙", "가두는 싸움", "dark", "blue"))
sc(1, reasons("위험 요소", [{"text": "명령에 없는 공격", "on": "명령에"}, {"text": "첫 적전 상륙", "later": True}, {"text": "실패하면 고립", "later": True}]))
sc(1, reasons("위험 요소", [{"text": "명령에 없는 공격", "at": 0}, {"text": "첫 적전 상륙", "on": "적전"}, {"text": "실패하면 고립", "later": True}]))
sc(1, reasons("위험 요소", [{"text": "명령에 없는 공격", "at": 0}, {"text": "첫 적전 상륙", "at": 0}, {"text": "실패하면 고립", "on": "실패하면"}]))
sc(1, stage([C("kr_plead", 0.5, 480, prop="officer", face="determined", anim="tilt")], [pop("bubble", 0.5, 0.3, "통영으로 가겠습니다!", on="건의")]))
sc(1, doc("김성은 부대 건의", ["거제를 지키는 가장 좋은 방법은", "통영을 되찾는 것"], "建議", "해병대 김성은 부대"))
sc(1, black("8월 17일", "오후 5시쯤"))
sc(1, doc("회신", ["통영 상륙작전 승인"], "承認", "해군 지휘부"))
sc(1, text("상륙까지 1시간", "red"))
next_act()

# ===== 제3막 팔월 십칠일 저녁 여섯 시 =====
sc(1, m("south", "neck", [LOCK("wonmun", 0.8)], flight=["south", "peninsula", "neck"], flightDur=3.2, hud=True), chapter={"num": "제3막", "title": "8월 17일 저녁 6시"}, sfx=SW(0))
sc(1, m("peninsula", "peninsula", [blue_a(SEA_IN, 0.2), badge([128.47, 34.83], "양동", "#2e66d8", 0.6, 0)], tilt=24))
sc(1, ph("navy_gun"), label=plabel("navy_gun"))
sc(1, stage([C("nk_idle", 0.6, 460, flip=True, prop=NKC, face="sweat")], [pop("label", 0.6, 0.16, "항구로 쳐들어온다!", on="항구로", color="red")]))
sc(1, m("neck", "neck", [blue_a(LAND_E, 0.2)], tilt=30))
sc(1, m("neck", "neck", [blue_a(LAND_E, 0), LOCK("jangpyeong", 0.3)], tilt=30), callouts=low("장평리 해안 · " + NOTE))
sc(1, ph("tongyeong_air"), label=plabel("tongyeong_air"))
sc(1, m("neck", "neck", [mark("jangpyeong", "blue", 0), mark("wonmun", "red", 0.3)], tilt=30))
sc(1, m("neck", "neck", [mark("jangpyeong", "blue", 0), blue_a(TO_PASS, 0.2)], tilt=34))
sc(1, text("해군 함정 7척", "blue"))
sc(1, ph("navy_703"), label=plabel("navy_703"))
sc(1, doc("참가 함정 (기록 기준)", ["경비정 PC-703 · JMS-302 · JMS-307", "소해정 YMS-504 · YMS-512", "수송선 AKL-901 · 평택호"], "海軍", "국방부 군사편찬연구소 자료 요약", "기록에 따라 다름"))
sc(1, text("상륙함 0척", "red"))
sc(1, ph("inchon_lst"), label=plabel("inchon_lst"))
sc(2, cmp("인천상륙작전", "260여 척", "통영상륙작전", "7척", "dark", "blue"))
sc(1, black("맨손에 가까운", "상륙"))
sc(1, m("peninsula", "peninsula", [blue_a(SEA_IN, 0), shock(HARBOR, 0.1, 0.55)], tilt=26), callouts=top("오후 6시 · 통영항 포격", "red"), sfx=FAR(0.1))
sc(1, m("neck", "neck", [blue_a(LAND_E, 0.2, 1.2), badge("jangpyeong", "상륙", "#2e66d8", on="장평리", dy=-70)], tilt=32, hud=True), sfx=WATER(0.3))
sc(1, stage([C("nk_idle", 0.4, 460, prop=NKC, face="smug", anim="tilt")], [pop("q", 0.7, 0.28, at=0.4)]))
sc(1, ai("marines_climb"), label=DRAMA)
sc(1, m("neck", "neck", [obj(1, "sambong", "삼봉산", 0, takenOn="단숨에")], tilt=32))
sc(1, text("고지부터", "yellow", "해안을 내려다보는 산 = 상륙 지점의 방패"))
sc(1, black("그날 밤", "적에게 들키지 않고"))
sc(1, m("neck", "neck", [obj(1, "wonmun", "원문고개", 0.2), obj(2, "mangil", "망일봉", 0.5)], tilt=30, hud=True))
sc(1, text("목표 2곳", "yellow"))
sc(1, m("neck", "neck", [LOCK("wonmun", 0.1), blue_a(TO_PASS, 0.3)], tilt=32))
sc(1, m("neck", "town", [LOCK("mangil", 0.4), blue_a(TO_PEAK, 0.2)], tilt=30))
sc(1, text("상륙 성공", "blue"))
sc(1, black("진짜 싸움은", "이제부터"))
sc(1, ai("night_trail"), label=DRAMA)
sc(1, stage([C("kr_point", 0.32, 440, prop=MAR), C("kr_idle", 0.7, 400, flip=True, prop="headband", anim="bounce")], [pop("label", 0.7, 0.2, "길잡이", on="길잡이가", color="yellow")]))
sc(1, text("길잡이 = 마을 주민", "yellow"))
sc(1, ai("jige_porters"), label=DRAMA)
sc(1, doc("김성은 장군 증언 (요지)", ["주민들이 탄약을 나르며", "해병과 함께 싸웠다"], "證言", "통영신문 보도 요지", "요지 · 재구성"))
sc(1, m("neck", "neck", [obj(1, "wonmun", "원문고개", 0, takenOn="급소를"), obj(2, "mangil", "망일봉", 0, takenOn="급소를")], tilt=30, hud=True))
sc(1, m("neck", "neck", [obj(1, "wonmun", "원문고개", 0, 0), LOCK("wonmun", 0.2)], tilt=36), sfx=PING(0.3))
sc(1, ai("pass_dig"), label=DRAMA, callouts=top("제2중대 · 원문고개"))
sc(1, m("peninsula", "peninsula", [plug(0.1), red_a(NK_PASS, 0.3), {"k": "arrow", "path": [[128.424, 34.855], [128.42, 34.868], [128.418, 34.874]], "color": "red", "at": 0.5}, clash("wonmun", 0.8)], tilt=26))
sc(1, m("neck", "town", [LOCK("mangil", 0.3)], tilt=30))
sc(1, ai("peak_view"), label=DRAMA)
sc(1, m("town", "town", [obj(2, "mangil", "망일봉", 0, takenOn="꼭대기를"), badge("mangil", "제7중대", "#2e66d8", on="제칠중대", dy=-90)], tilt=30))
sc(1, text("고지 = 주도권", "yellow", "높은 곳을 쥔 쪽이 시가지 싸움을 이끈다"))
sc(1, stage([C("nk_point", 0.55, 480, flip=True, prop=NKC, face="determined")], [pop("label", 0.55, 0.15, "같은 생각", on="같은", color="red")]))
sc(1, m("town", "town", [red_a([[128.425, 34.848], [128.428, 34.855], [128.43, 34.86]], 0.2)], tilt=30), callouts=low("북한군도 망일봉으로"))
sc(1, text("북한군은 몰랐다", "red", "망일봉 꼭대기의 해병대"))
sc(1, m("town", "town", [badge("nammang", "남망산", "#c9242c", on="남망산", dy=-50), badge("mangil", "망일봉", "#c9242c", on="망일봉에", dy=-80)], tilt=28), callouts=top("북한군 진지 계획", "red"))
sc(1, m("town", "town", [{"k": "front", "path": [[128.41, 34.845], [128.42, 34.842], [128.43, 34.84], [128.44, 34.845]], "at": 0}, blue_a([[128.43, 34.82], [128.43, 34.835]], 0.3)], tilt=28), callouts=low("바다 쪽만 대비"))
sc(1, m("neck", "town", [blue_a([[128.44, 34.88], [128.435, 34.87], [128.43, 34.861]], 0.2, 1.2)], tilt=30), callouts=top("등 뒤의 산에서", "blue"))
sc(1, {"type": "cta", "title": "구독 · 좋아요로 다음 이야기까지 함께해 주세요", "at": 0})
next_act()

# ===== 제4막 망일봉과 독 안의 쥐 =====
MID.append(nid())
sc(1, ai("crest_wait"), label=DRAMA, pauseBefore=0.5, chapter={"num": "제4막", "title": "망일봉과 독 안의 쥐"}, callouts=top("1950. 8. 18 · 망일봉"))
sc(1, m("town", "town", [{"k": "swarm", "path": [[128.424, 34.852], [128.427, 34.857], [128.43, 34.861]], "at": 0.1, "n": 60, "width": 0.6}], tilt=32, hud=True))
sc(1, m("town", "town", [obj(2, "mangil", "망일봉", 0, 0), badge("mangil", "제7중대 대기", "#2e66d8", 0.2, -90)], tilt=32))
sc(1, ai("mangil_ambush"), label=DRAMA, sfx=FAR(0.2))
sc(1, m("town", "town", [clash("mangil", 0.1, 0.9), red_a([[128.43, 34.86], [128.427, 34.855], [128.424, 34.85]], 0.5)], tilt=32))
sc(1, m("town", "town", [clash("mangil", 0.1, 1.1), badge("mangil", "2차 교전", "#c9242c", on="다시", dy=-90)], tilt=32))
sc(1, bars("통영신문 보도 기준", [{"label": "올라온 적", "value": 100, "display": "약 100명", "color": "red", "at": 0.1}, {"label": "쓰러진 적", "value": 50, "display": "약 50명", "color": "dark", "on": "쉰"}]))
sc(1, stage([C("kr_shock", 0.5, 460, prop=MAR, face="coldsweat")], [pop("label", 0.5, 0.16, "할 말을 잃다", on="할 말을", color="dark")]))
sc(1, ai("boy_soldier"), label=DRAMA)
sc(1, ph("nk_captured"), label=plabel("nk_captured"))
sc(1, black("전쟁의", "잔인한 얼굴"))
sc(1, ph("kmc_search"), label=plabel("kmc_search"))
sc(1, stage([C("kr_shrug", 0.3, 440, prop=MAR, face="tears"), C("nk_plead", 0.7, 400, flip=True, prop=NKC, face="tears")], [pop("label", 0.5, 0.15, "어린 병사들끼리", on="어린", color="dark")]))
sc(2, m("town", "town", [red_a([[128.43, 34.86], [128.422, 34.852], [128.416, 34.848]], 0.1), red_a([[128.43, 34.86], [128.436, 34.852], [128.44, 34.846]], 0.2), badge([128.42, 34.866], "북신동 쪽", "#c9242c", on="북신동", dy=0)], tilt=30))
sc(1, m("town", "town", [obj(2, "mangil", "망일봉", 0, 0), {"k": "radar", "p": "mangil", "at": 0.2, "size": 1.0, "color": "#2e9bff"}], tilt=34, hud=True))
sc(1, ai("street_fight"), label=DRAMA, callouts=top("8. 18 오후 2시 · 시가전"))
sc(1, ph("kmc_hay"), label=plabel("kmc_hay"))
sc(1, m("town", "town", [{"k": "radar", "p": "mangil", "at": 0, "size": 1.2, "color": "#2e9bff"}, red_a([[128.42, 34.85], [128.425, 34.846]], 0.4, 0.7)], tilt=30), callouts=low("망일봉 = 관측소"))
sc(1, cmp("망일봉 위", "관측", "시가지 아래", "돌격", "blue", "yellow"))
sc(1, black("한 가지", "원칙"))
sc(1, ph("chungnyeolsa"), label=plabel("chungnyeolsa"))
sc(1, ai("shrine_pass"), label=DRAMA, callouts=low("전해지는 이야기"))
sc(1, text("지켜야 할 도시", "yellow", "전해지는 이야기"))
sc(1, m("peninsula", "peninsula", [plug(0), LOCK("wonmun", 0.1), {"k": "unit", "p": "tongyeong", "text": "고립된 적", "color": "red", "at": 0.3}], tilt=26))
sc(1, m("neck", "neck", [plug(0), red_a([[128.424, 34.852], [128.42, 34.866], [128.418, 34.875]], 0.2)], tilt=32), callouts=low("적 지휘부 차량 · 원문고개로"))
sc(1, m("neck", "neck", [plug(0), LOCK("wonmun", 0), clash("wonmun", 0.3)], tilt=34))
sc(1, ai("jeep_escape"), label=DRAMA)
sc(1, m("town", "town", [red_a([[128.425, 34.845], [128.43, 34.835], [128.44, 34.825]], 0.2)], tilt=26), callouts=low("바다로"))
sc(1, text("목선 3척", "red"))
sc(1, ph("navy_ship"), label=plabel("navy_ship"))
sc(1, ai("boats_sunk"), label=DRAMA, callouts=top("소해정 YMS-504 · 512"))
sc(1, m("peninsula", "peninsula", [plug(0.1), blue_a([[128.36, 34.84], [128.4, 34.82], [128.46, 34.82], [128.5, 34.85]], 0.3, 0.8), badge([128.47, 34.82], "해군 경계", "#2e66d8", 0.8, 0)], tilt=26))
sc(1, stage([C("nk_shrug", 0.5, 460, face="sweat", anim="shake")], [pop("label", 0.5, 0.15, "군복을 벗고 주민 옷으로", on="군복을", color="red")]))
sc(1, stage([C("nk_shock", 0.45, 440, face="coldsweat")], [pop("q", 0.72, 0.3, on="빈집에")]))
sc(1, stage([C("kr_idle", 0.3, 400, prop="headband", face="angry"), C("nk_plead", 0.72, 400, flip=True, face="sweat", anim="shake")], [pop("label", 0.3, 0.18, "신고!", on="신고로", color="yellow")]))
sc(1, black("1950. 8. 19", "오전 10시"))
sc(1, m("town", "town", [obj(1, "mangil", "망일봉", 0, 0), obj(2, "nammang", "남망산", 0, takenOn="모두"), mark("tongyeong", "blue", on="시내와")], tilt=28))
sc(1, ai("town_liberated"), label=DRAMA)
sc(1, text("통영 탈환", "blue", "상륙 약 40시간 만"))
sc(1, m("peninsula", "peninsula", [plug(0), LOCK("wonmun", 0), badge("tongyeong", "독 안의 쥐", "#c9242c", on="독 안에", dy=-60)], tilt=26))
sc(1, m("neck", "neck", [dict(plug(0), width=1.5), LOCK("wonmun", 0.2)], tilt=36, hud=True))
next_act()

# ===== 제5막 원문고개를 사수하라 =====
MID.append(nid())
sc(1, m("peninsula", "neck", [plug(0), LOCK("wonmun", 0.8)], flight=["peninsula", "neck"], flightDur=2.6), pauseBefore=0.5, chapter={"num": "제5막", "title": "원문고개를 사수하라"}, sfx=SW(0))
sc(1, m("south", "south", [{"k": "unit", "p": "goseong", "text": "북한군 본대", "color": "red", "pulse": True, "at": 0.2}, mark("tongyeong", "blue", 0)]))
sc(1, m("peninsula", "neck", [plug(0), {"k": "swarm", "path": NK_PASS, "at": 0.1, "n": 140}], tilt=30))
sc(1, stage([C("nk_salute", 0.5, 480, prop=NKC, face="angry", anim="shake")], [pop("label", 0.5, 0.15, "통영을 되찾아라!", at=0.2, color="red")]))
sc(1, black("8월 19일", "오후 3시 40분"))
sc(1, m("neck", "neck", [plug(0), {"k": "shock", "pts": PASS_PTS, "at": 0.1, "period": 0.5}], tilt=34, hud=True), sfx=FAR(0.1))
sc(1, text("포탄 580발", "red", "약 3시간 · 국내 언론 보도 기준"))
sc(1, m("neck", "neck", [plug(0), {"k": "swarm", "path": NK_PASS[1:] + [[128.418, 34.877]], "at": 0, "n": 160}], tilt=34))
sc(1, m("neck", "neck", [plug(0), badge([128.414, 34.879], "제2중대", "#2e66d8", 0.2, -60), badge([128.426, 34.874], "제7중대", "#2e66d8", 0.5, 60)], tilt=34))
sc(1, ai("trench_wait"), label=DRAMA, sfx=WIND(0))
sc(1, ai("pass_defense"), label=DRAMA, sfx=FAR(0.2))
sc(1, text("화력 부족", "red", "탄약을 아껴야 했다"))
sc(1, ai("trench_wait"), label=DRAMA, callouts=low("가까이 올 때까지"))
sc(1, text("한 발 한 발", "yellow"))
sc(1, m("neck", "neck", [plug(0), LOCK("wonmun", 0.1)], tilt=40, hud=True))
sc(1, {"type": "profile", "pts": [[0, 160], [0.3, 140], [0.42, 70], [0.58, 70], [0.7, 140], [1, 170]], "grid": [70, 140], "yMin": 0, "yMax": 220,
       "title": "원문고개 (모식도)", "note": "모식도 · 실제 지형과 다름", "left": "고성 쪽", "right": "통영 쪽",
       "marks": [{"x": 0.5, "text": "좁은 길목", "style": "red", "at": 0.2, "lift": 50, "size": 44}]})
sc(1, text("길목 하나만 막으면 된다", "yellow"))
sc(1, ai("kim_map"), label=DRAMA, callouts=low("지도에서 읽어 낸 원리"))
sc(1, text("고개 하나 > 병력 수백", "yellow"))
sc(1, stage([C("nk_point", 0.5, 480, prop=NKC, face="smug", anim="tilt")], [pop("label", 0.5, 0.15, "옆으로 돌아가자", on="꾀를", color="red")]))
sc(1, black("8월 20일", "새벽 2시 40분"))
sc(1, m("neck", "neck", [plug(0), red_a(COAST_W, 0.2, 0.8), red_a(COAST_E, 0.4, 0.8)], tilt=32), callouts=low("양쪽 해안선 침투 · " + NOTE))
sc(1, ai("coast_creep"), label=DRAMA)
sc(1, m("neck", "neck", [plug(0), clash([128.404, 34.871], 0.1, 0.8), clash([128.438, 34.881], 0.3, 0.8)], tilt=32))
sc(1, m("neck", "neck", [plug(0), {"k": "arrow", "path": list(reversed(COAST_W)), "color": "red", "width": 0.7, "at": 0.1}, {"k": "arrow", "path": list(reversed(COAST_E)), "color": "red", "width": 0.7, "at": 0.3}], tilt=32))
sc(1, m("neck", "neck", [plug(0), {"k": "shock", "pts": PASS_PTS[:3], "at": 0.1, "period": 0.8}], tilt=34), sfx=FAR(0.2))
sc(1, text("9차례 공격", "red", "약 한 달 · 국방부 군사편찬연구소 연구 기준"))
sc(1, text("9번 모두 격퇴", "blue", "원문고개 사수"))
sc(1, stage([C("kr_shock", 0.5, 480, prop=MAR, face="shock")], [pop("q", 0.76, 0.3, at=0.3)]))
sc(1, m("peninsula", "peninsula", [{"k": "arrow", "path": NK_IN, "color": "red", "at": 0.1, "dash": True}], tilt=26), callouts=top("가정 · 고개가 뚫렸다면", "dark"))
sc(1, m("south", "south", [{"k": "arrow", "path": [[128.45, 34.86], [128.53, 34.87], [128.6, 34.88]], "color": "red", "dash": True, "at": 0.1}, mark("geoje", "blue", 0)]), callouts=top("가정", "dark"))
sc(1, m("sw", "sw", [front, {"k": "arrow", "path": [[128.42, 34.9], [128.48, 35.05], [128.56, 35.18]], "color": "red", "dash": True, "at": 0.2}, mark("masan", "blue", 0)]), callouts=top("가정 · 마산의 등 뒤", "dark"))
sc(1, m("peninsula", "peninsula", [dict(plug(0), width=1.6), LOCK("wonmun", 0.1), badge("wonmun", "마개", "#2e66d8", on="마개였습니다", dy=-110)], tilt=28))
sc(1, ph("rok_move"), label=plabel("rok_move"))
sc(1, black("1950. 9. 15"))
sc(1, ph("inchon_craft"), label=plabel("inchon_craft"))
sc(1, m("korea", "korea", [front, mark("incheon", "blue", 0), blue_a([[125.9, 37.3], [126.62, 37.47], [126.98, 37.56]], 0.2), blue_a([[128.6, 35.9], [128.2, 36.6], [127.6, 37.2]], 0.5)]), callouts=top("허리가 끊긴 북한군", "blue"))
sc(1, m("south", "south", [{"k": "arrow", "path": [[128.33, 34.96], [128.3, 35.05], [128.28, 35.18]], "color": "red", "at": 0.2}, mark("tongyeong", "blue", 0)]), callouts=low("북쪽으로 물러나는 북한군"))
sc(1, text("작전 종료", "blue", "1950. 9. 22"))
sc(1, text("37일", "yellow", "1950. 8. 17 ~ 9. 22"))
sc(1, black("해병대 기록", "전과"))
sc(2, bars("해병대 기록 기준", [{"label": "적 사살", "value": 469, "display": "469명", "color": "red", "on": "사살"}, {"label": "포로", "value": 83, "display": "83명", "color": "dark", "on": "포로"}]))
sc(1, text("약 4분의 3", "red", "통영에 들어온 북한군 대비 · 일부 평가"))
sc(1, doc("노획 (해병대 기록)", ["따발총 128정 · 소총 107정", "박격포 2문 · 트럭 10대 · 지프 2대"], "戰果", "해병대 기록 요약"))
sc(1, stage([C("kr_idle", 0.5, 440, prop=MAR, face="worried")], [pop("q", 0.74, 0.3, at=0.3)]))
sc(1, bars("해병대 기록 기준", [{"label": "전사", "value": 15, "display": "15명", "color": "blue", "at": 0.1}, {"label": "부상", "value": 47, "display": "47명", "color": "blue", "on": "부상"}]))
sc(1, text("전사 15명 · 19명", "dark", "기록에 따라 다름"))
sc(1, cmp("해병대 전사", "15명", "적 사살", "469명", "blue", "red"))
sc(1, m("peninsula", "peninsula", [plug(0), LOCK("wonmun", 0.1, "원문고개", "#2e9bff")], tilt=26))
sc(1, ai("comrades_graves"), label=DRAMA)
next_act()

# ===== 제6막 귀신 잡는 해병의 탄생 =====
sc(1, flat([132.5, 36.0], 14, [fpin([128.42, 34.85], "통영", at=0, flag="kr", side="left"), fpin([139.7, 35.7], "도쿄 · 외신 기자들", on="건너", side="right")], [route([128.42, 34.85], [139.7, 35.7], on="건너", bend=-0.2, color="#2e66d8")], [{"ll": [131.0, 37.6], "text": "동해", "style": "sea"}]), chapter={"num": "제6막", "title": "귀신 잡는 해병의 탄생"})
sc(1, stage([C("us_point", 0.5, 480, prop="notebook", face="sparkle", anim="enter")], [pop("label", 0.5, 0.15, "외국인 기자", on="기자의", color="dark")]))
sc(1, ph("higgins"), label=plabel("higgins"))
sc(1, text("최전선의 여성 종군기자", "yellow"))
sc(1, ph("higgins_flyer"), label=plabel("higgins_flyer"))
sc(1, stage([C("us_idle", 0.4, 460, prop="notebook+glasses", face="smug")], [pop("bubble", 0.4, 0.28, "한국 해병대는..", on="이렇게")]))
sc(1, doc("전해지는 말", ["They might capture", "even the devil."], "傳言", "마거리트 히긴스 (전해지는 말)", "원문 기사 미확인"))
sc(1, black("하나의", "이름"))
sc(1, text("귀신 잡는 해병", "red"))
sc(1, text("원문 기사 미확인", "dark", "히긴스가 쓴 기사 원문은 확인되지 않음"))
sc(1, black("전해지는", "이야기"))
sc(1, black("그래도 한 가지는", "분명하다"))
sc(1, ai("town_liberated"), label=DRAMA, callouts=low("통영에서 싸운 해병들"))
sc(1, ph("kmc_today"), label=plabel("kmc_today"))
sc(1, ai("summit_dawn"), label=DRAMA, callouts=top("1951 · 도솔산"))
sc(1, text("무적해병", "red", "1951년 도솔산 전투"))
sc(2, cmp("1950 통영", "귀신 잡는 해병", "1951 도솔산", "무적해병", "red", "blue"))
sc(1, black("처음의", "질문"))
sc(1, stage([C("kr_shrug", 0.4, 460, prop=MAR, face="worried", anim="tilt")], [pop("q", 0.7, 0.3, at=0.2)], title="왜 거제가 아니라 통영이었나?"))
sc(1, m("korea", "peninsula", [plug(0.8)], flight=["korea", "south", "peninsula"], flightDur=3.4, hud=True), sfx=SW(0))
sc(1, m("south", "south", [mark("geoje", "blue", 0), {"k": "arrow", "path": [[128.45, 34.86], [128.55, 34.86]], "color": "red", "dash": True, "at": 0.2}, {"k": "arrow", "path": [[128.42, 34.82], [128.52, 34.8]], "color": "red", "dash": True, "at": 0.4}, {"k": "arrow", "path": [[128.48, 34.93], [128.56, 34.93]], "color": "red", "dash": True, "at": 0.6}]), callouts=top("언제 · 어디로?", "dark"))
sc(1, m("peninsula", "peninsula", [plug(0), LOCK("wonmun", on="원문고개를")], tilt=28))
sc(1, m("neck", "neck", [plug(0), red_a(NK_PASS[2:], 0.1, 0.8), {"k": "arrow", "path": [[128.424, 34.855], [128.42, 34.868]], "color": "red", "at": 0.3}, clash("wonmun", 0.6)], tilt=32))
sc(1, text("숫자보다 지형", "yellow", "대대급 300여 명 · 고개 하나"))
sc(1, m("south", "south", [plug(0), mark("tongyeong", "blue", 0), mark("geoje", "blue", on="거제와"), mark("jinhae", "blue", on="진해를")]))
sc(1, doc("명령의 목적", ["글자: 거제도를 지켜라", "목적: 남쪽 바다를 지켜라"], "判斷", "재구성"))
sc(1, ph("sohn"), label=plabel("sohn"))
sc(1, ph("navy_chinhae2"), label=plabel("navy_chinhae2"))
sc(3, checklist("통영상륙작전의 기록", [{"text": "한국군 첫 단독 상륙작전", "on": "처음으로", "checkOn": "해낸"}, {"text": "낙동강 방어 시기의 공격작전", "on": "공격작전", "checkOn": "공격작전"}]))
sc(1, ph("refugees2"), label=plabel("refugees2"))
sc(2, doc("통영전선 회고기 (요지)", ["참 우리 통영의 은인이라", "해병대 기념탑이라도 세워야 된다"], "1950", "부산일보 1950. 11. 5", "요지 · 현대어"))
sc(1, ph("kmc_pusan"), label=plabel("kmc_pusan"))
sc(1, text("해병대 제1연대", "blue", "1950. 9 인천상륙작전"))
sc(1, ph("kmc_dukw"), label=plabel("kmc_dukw"))
sc(1, ph("kim_2007"), label=plabel("kim_2007"))
sc(1, text("김성은 1924 ~ 2007", "dark"))
sc(1, text("통영상륙작전 기념관", "blue", "김성은 장군 유품 전시"))
sc(1, ai("memorial"), label=DRAMA, callouts=low("원문고개 전적비"))
sc(1, text("통영상륙작전 기념관", "yellow", "2011년 개관 · 통영 원문공원"))
sc(1, text("매년 8월 전승 기념식", "blue", "통영 원문고개"))
sc(1, ai("temple_dusk"), label=DRAMA)
sc(1, black("명령을 따르는 것은", "쉽다"))
sc(1, black("목적을 생각하는 것은", "어렵다"))
sc(1, m("south", "south", [mark("geoje", "blue", 0), mark("jinhae", "blue", 0), mark("tongyeong", "blue", 0)]), callouts=top("목적 = 남쪽 바다", "blue"))
sc(1, m("strait", "neck", [blue_a(LAND_E, 0.2, 1.2), LOCK("wonmun", 0.7)], flight=["strait", "neck"], flightDur=2.8), sfx=SW(0))
sc(1, ai("peak_view"), label=DRAMA, callouts=low("귀신 잡는 해병"))
sc(3, {"type": "endcard", "title": "명령의 글자가 아닌 목적을 본 300여 명,\n돌아오지 못한 젊은 해병들을 기억하며", "q": pin("kmc_flag")}, tail=1.0)
assert CUR["i"] == len(ACTS[5]), (CUR, len(ACTS[5]))

# ===== 재연 일러스트 (Gemini · 새 그림 + 재사용) =====
CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
KM = ("South Korean marines whose heads are round balls painted as the South Korean taegukgi flag (white with the red and blue taegeuk circle and black trigrams), "
      "wearing 1950 M1 steel helmets and plain olive drab herringbone field uniforms with absolutely NO collar tabs, NO patches, NO red insignia")
KM1 = ("a South Korean marine whose head is a round ball painted as the South Korean taegukgi flag (white with the red and blue taegeuk circle and black trigrams), "
       "wearing a 1950 M1 steel helmet and a plain olive drab herringbone field uniform with absolutely NO collar tabs, NO patches, NO red insignia")
KIM = ("a young South Korean marine colonel whose head is a round ball painted as the South Korean taegukgi flag (white with the red and blue taegeuk circle and black trigrams), "
       "wearing a 1950 M1 steel helmet and a plain olive drab field jacket with absolutely NO collar tabs, NO patches, NO red insignia")
NK = "North Korean soldiers whose heads are round balls painted as the North Korean flag (blue, red and white stripes with a red star), wearing 1950 olive-brown uniforms and soft field caps"
VIL = "Korean villagers whose heads are round balls painted as the South Korean taegukgi flag, wearing white 1950 hanbok work clothes"
TOWN = "a small 1950 Korean harbor town of dark tile-roofed and thatched houses on a hillside around a narrow harbor full of wooden fishing boats, green hills behind, southern coast"
END = ", August 1950 summer, leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic, desaturated summer palette, film grain, no text, no letters."
AI = {
    "naval_feint_dusk": "Three small grey 1950 South Korean navy patrol boats and minesweepers firing their deck guns toward " + TOWN + " at dusk, orange muzzle flashes over dark water, smoke over the harbor, August 1950, " + LAND,
    "landing_dusk": CB + KM + " jumping from a small wooden-hulled transport boat into knee-deep water on a quiet rocky cove at dusk and wading ashore with rifles held high, dark wooded hills just behind the beach" + END,
    "nk_column_coast": CB + "a long column of " + NK + " marching along a dusty coastal dirt road beside rice paddies toward a southern harbor town, a few trucks, confident and fast, hot summer haze" + END,
    "tongyeong_1950": TOWN + ", quiet and tense under a hazy summer sky, empty streets, a few people hurrying, distant smoke on the hills, August 1950, " + LAND,
    "tongyeong_occupied": CB + NK + " entering the narrow streets of " + TOWN + ", North Korean national flags (blue-red-blue stripes with a white circle and red star) hung from a building, absolutely NO hammer and sickle, NO Soviet flags, frightened villagers hiding behind doors" + END,
    "jindong_ambush": CB + KM + " springing an ambush from a wooded hillside above a dusty road and rice paddies on a hot summer day, firing rifles and a machine gun down at a startled column of " + NK + " on the road below, smoke and dust" + END,
    "strait_night": "Two small 1950 South Korean navy ships moving silently through a narrow dark strait between rocky islands at night, no lights, faint moonlight on calm water, soldiers' helmets silhouetted on deck, " + LAND,
    "hansan_1592": "A historical 1592 naval battle off Hansan island in Korea: a crescent crane-wing formation of large Korean Joseon panokseon warships (flat-bottomed two-deck wooden oared ships with a high fortress-like upper deck and plain square sails) and one geobukseon turtle ship with a spiked armored roof and a dragon head firing cannons at a fleet of Japanese wooden atakebune warships, smoke, dramatic sky, absolutely NO modern flags, NO taegukgi, NO European galleons, only plain cloth banners, painterly realistic historical illustration, no text, no letters.",
    "recon_boat": CB + KIM + " crouching in a small wooden fishing boat rowed by an old Korean fisherman in white hanbok before dawn, looking through binoculars toward a dark hilly peninsula and a harbor town across calm water" + END,
    "kim_map": CB + KIM + " pointing firmly at the narrow neck of a hand-drawn peninsula map spread on an ammunition crate by lantern light at night, other marine officers leaning in with serious faces, a tense moment of realization" + END,
    "marines_climb": CB + KM + " climbing quickly up a steep wooded hillside from a cove at last light, rifles slung, the sea and a small boat behind them below" + END,
    "night_trail": CB + KM + " moving in single file along a narrow dark mountain trail at night, guided by " + VIL + " carrying wooden A-frame backpacks (jige) loaded with ammunition boxes and water jars, faint moonlight" + END,
    "pass_dig": CB + KM + " digging foxholes and stacking stones at dawn on a low mountain pass where a dirt road crosses the narrow neck of a peninsula, the sea visible on both sides, a machine gun being set up facing the road" + END,
    "peak_view": CB + KM + " crouching on a rocky hilltop at sunrise looking down over " + TOWN + " and the harbor below, one marine with binoculars, a taegukgi flag on a pole" + END,
    "crest_wait": CB + KM + " lying silently in shallow foxholes along a hill crest at early morning, rifles aimed down the grassy slope, one marine raising a hand to hold fire, tense silence" + END,
    "mangil_ambush": CB + KM + " firing down from a hill crest at a group of " + NK + " climbing the slope below, muzzle flashes, the enemy soldiers scattering and tumbling down the slope, harbor town in the background" + END,
    "boy_soldier": CB + "a very young boy soldier whose head is a round ball painted as the North Korean flag, wearing an oversized 1950 olive-brown uniform and soft cap, sitting on the ground exhausted and frightened after surrendering, " + KM1 + " kneeling and offering him a canteen of water, somber and humane mood" + END,
    "street_fight": CB + KM + " advancing carefully through a narrow alley between tile-roofed houses of a harbor town, one marine peeking around a stone wall corner with a rifle, smoke in the street" + END,
    "shrine_pass": CB + KM + " walking carefully past the old wooden gate and stone steps of a traditional Korean Joseon-era shrine in a harbor town, rifles lowered, one marine signaling the others not to fire, respectful mood" + END,
    "jeep_escape": CB + "a military jeep full of panicked North Korean officers whose heads are round balls painted as the North Korean flag, abandoned and stopped askew on a dusty mountain pass road with bullet holes in the windshield, the officers jumping out and running into a tall sorghum field beside the road" + END,
    "boats_sunk": "A small grey 1950 South Korean navy minesweeper firing its deck gun at three small wooden fishing boats fleeing across a calm bay at dusk, one boat sinking and splintering, water splashes, " + LAND,
    "town_liberated": CB + KM + " walking down the main street of " + TOWN + " while relieved " + VIL + " come out of their houses waving small taegukgi flags, morning light" + END,
    "trench_wait": CB + KM + " crouching in a dug-in trench on a mountain pass, holding fire and waiting with grim faces as enemy soldiers creep closer up the slope below, a few grenades lined up on the parapet, dusk" + END,
    "pass_defense": CB + KM + " in trenches on a mountain pass throwing grenades and firing rifles down at waves of " + NK + " charging up the slope along a dirt road, explosions and dust, dusk" + END,
    "coast_creep": CB + NK + " creeping at night along a rocky shoreline below a dark hill, crouching low between rocks at the water's edge, a parachute flare suddenly lighting them up from above" + END,
    "memorial": "A modern granite war memorial monument with a bronze statue of soldiers on a small green park on a hill pass beside a road in a Korean coastal city, bouquets of white chrysanthemums laid in front, soft evening light, no readable text, no letters, painterly realistic, cinematic.",
    "temple_dusk": "A small quiet Korean Buddhist temple hall on a wooded hillside at dusk, lanterns glowing, incense smoke, the sea faintly visible below, peaceful and solemn, painterly realistic digital illustration, no text, no letters.",
    "thumb_subject": "Photorealistic black-and-white 1950 Korean War documentary portrait of a young South Korean marine, clearly East Asian Korean face with black hair, M1 steel helmet with chin strap, plain herringbone field uniform with no insignia, sweat and dust on his face, fierce determined eyes, rifle sling on shoulder, waist-up, face clearly visible and turned slightly toward the left of the frame, isolated on a plain pure white background, no shadows on the background, no text.",
}
# 재사용 그림 (파일·서명 복사, 추가 비용 0): 원래 프롬프트 그대로
REUSE = {"jige_porters": "dabudong", "comrades_graves": "ep16-dosolsan", "summit_dawn": "ep16-dosolsan"}
for k, src in REUSE.items():
    AI[k] = json.loads((ROOT / "episodes" / src / "storyboard.json").read_text(encoding="utf-8"))["ai_images"][k]
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
music = [{"id": "drone", "from": "s001", "to": sid(chap[0] - 1), "volume": 0.2},
         {"id": "theme", "from": sid(chap[0]), "to": sid(chap[2] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[2]), "to": sid(chap[3] - 1), "volume": 0.17},
         {"id": "march", "from": sid(chap[3]), "to": sid(chap[4] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[4]), "to": sid(chap[5] - 1), "volume": 0.17},
         {"id": "somber", "from": sid(chap[5]), "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "통영상륙작전", "subtitle": "1950. 8. 17 ~ 9. 22", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         "target_sec": 1170, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap],
      "ai", len(AI), "new ai", len(set(AI) - set(REUSE)), "pins", len(PINS), "stage", len(stages), "photo", sum(1 for s in S if s["visual"]["type"] == "photo"))
print("char uses", dict(cnt))
