# EP26 승호리 철교 폭파작전 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 연출 스타일 v2("style": 2) + 화면 업그레이드 2단계 첫 적용: stage(종이 무대·볼 캐릭터) · flatmap · flaggrid · checklist · reasons · 사진 tag/marks
# 지도 새 아이템(EP26): plane — 편대 비행 궤적(n대, hit=끝점 폭발)
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

# 자막 숫자 표기 (사용자 지시: 숫자는 숫자로)
SUBS = [
    ("천구백오십이 년 일월 십오일", "1952년 1월 15일"), ("천구백오십이 년 일월 십이일", "1952년 1월 12일"), ("천구백오십이 년 일월 초", "1952년 1월 초"),
    ("천구백오십일 년 겨울", "1951년 겨울"), ("천구백오십일 년 여름", "1951년 여름"), ("천구백오십일 년 가을", "1951년 가을"), ("천구백오십 년 유월", "1950년 6월"),
    ("일월 십이일", "1월 12일"), ("일월 십오일", "1월 15일"), ("이월 이십일일", "2월 21일"),
    ("오전 여덟 시 이십오 분", "오전 8시 25분"), ("아침 일곱 시 사십 분", "아침 7시 40분"), ("오후 두 시", "오후 2시"),
    ("미 제오공군", "미 제5공군"), ("제일전투비행단", "제1전투비행단"), ("제십전투비행전대", "제10전투비행전대"), ("제이차 세계대전", "제2차 세계대전"),
    ("제일편대장", "제1편대장"), ("제이편대장", "제2편대장"), ("제일편대", "제1편대"), ("제이편대", "제2편대"), ("이번기", "2번기"), ("삼번기", "3번기"),
    ("F 오십일", "F-51"), ("오백 파운드", "500파운드"),
    ("팔천 피트", "8,000피트"), ("사천 피트", "4,000피트"), ("삼천 피트", "3,000피트"), ("이천 피트", "2,000피트"), ("천오백 피트", "1,500피트"),
    ("약 이천사백 미터", "약 2,400m"), ("약 구백 미터", "약 900m"), ("구백 미터", "900m"), ("약 사백오십 미터", "약 450m"), ("사백오십 미터", "450m"),
    ("이백 미터", "200m"), ("이삼십 미터", "20~30m"), ("몇십 미터", "수십 m"), ("약 삼백 킬로미터", "약 300km"), ("육백 킬로미터", "600km"),
    ("오백 번 가까이", "500번 가까이"), ("오백 번을", "500번을"), ("오백 번 대 열네 번", "500번 대 14번"), ("오백 번과 열네 번", "500번과 14번"), ("오백 번이", "500번이"),
    ("오백 대 열넷", "500 대 14"), ("약 오백 회", "약 500회"), ("열네 번", "14번"), ("여덟 번", "8번"), ("여섯 번", "6번"), ("백 회", "100회"),
    ("팔천사백구십오 회", "8,495회"), ("칠천팔백여 회", "7,800여 회"), ("서른아홉 명", "39명"), ("스물네 살", "24살"), ("스물두 대", "22대"),
    ("폭탄 열두 발", "폭탄 12발"), ("로켓탄 스무 발", "로켓탄 20발"), ("기관총탄 사천칠백 발", "기관총탄 4,700발"), ("폭탄 열 발", "폭탄 10발"),
    ("포진지 여섯 곳", "포진지 6곳"), ("보급품 집적소 한 곳", "보급품 집적소 1곳"), ("벙커 세 곳", "벙커 3곳"), ("건물 한 동", "건물 1동"),
    ("교각 열 개", "교각 10개"), ("무스탕 열 대", "무스탕 10대"), ("조종사 열 명", "조종사 10명"), ("전투기 여섯 대", "전투기 6대"), ("무스탕 여섯 대", "무스탕 6대"),
    ("여섯 대", "6대"), ("다섯 대", "5대"), ("세 대", "3대"), ("여섯 명", "6명"), ("두 사람", "2명"), ("두 곳", "2곳"), ("두 개", "2개"),
    ("일 년", "1년"), ("칠십여 년", "70여 년"), ("천오백.", "1,500."), ("천오백이", "1,500이"), ("천오백", "1,500"), ("삼팔선", "38선"),
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
def C(c, x, h=480, on=None, at=None, flip=False, y=0.9):
    d = {"c": c, "x": x, "y": y, "h": h}
    if on:
        d["on"] = on
    else:
        d["at"] = at or 0
    if flip:
        d["flip"] = True
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


FILL = {"410": "#f1e4c6", "408": "#e8b6a5", "156": "#dcc9a3", "392": "#e6d9bd", "643": "#dcc9a3"}


def flat(center, span, pins=None, routes=None, labels=None, title=None, pops=None, zoomTo=0.92):
    v = {"type": "flatmap", "center": center, "span": span, "fill": FILL, "pins": pins or [], "routes": routes or [], "labels": labels or [], "zoomTo": zoomTo}
    if title:
        v["title"] = title
    if pops:
        v["pops"] = pops
    return v


SEA = [{"ll": [130.4, 39.3], "text": "동해", "style": "sea"}, {"ll": [124.2, 37.6], "text": "황해", "style": "sea"}]


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


def doc(head, rows, stamp="軍 秘", org="대한민국 공군", note="재구성 · 내용 요약"):
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


# 사진: 스카우트 catalog.json 설명으로 확인한 파일 (미 국립문서기록관리청·미 공군·스미스소니언 공공 저작물)
KNOWN = sorted({v for f in glob.glob(str(HERE.parent / "*" / "photo_pins.json")) if EP not in f for v in json.load(open(f, encoding="utf-8")).values()})
PH = json.loads((HERE / "photo_keys.json").read_text(encoding="utf-8")) if (HERE / "photo_keys.json").exists() else {}


def pin(key):
    sid = nid()
    if key in PH:
        PINS[f"{sid}-photo#0"] = PH[key]["file"]
    return f"{sid}-photo"


def ph(key, pos=None, marks=None):
    v = {"type": "photo", "kb": "in", "q": pin(key)}
    if key in PH and PH[key].get("tag"):
        v["tag"] = PH[key]["tag"]
    if pos:
        v["pos"] = pos
    if marks:
        v["marks"] = marks
    return v


def plabel(key, default):
    return PH.get(key, {}).get("label", default)


DRAMA = "재연 일러스트"
NOTE = "위치 개략"
P = {
    "pyongyang": [125.754, 39.02, "평양"], "bridge": [125.955, 39.008, "승호리 철교"], "seungho": [125.98, 39.03, "승호리"],
    "gangneung": [128.944, 37.753, "강릉 기지"], "sinuiju": [124.4, 40.1, "신의주"], "wonsan": [127.44, 39.15, "원산"], "seoul": [126.978, 37.566, "서울"],
    "panmun": [126.677, 37.956, "판문점"], "daegu": [128.6, 35.87, "대구"],
}
V = {
    "korea": {"center": [127.3, 38.3], "span": 6.6}, "north": {"center": [126.6, 39.1], "span": 4.2}, "route": {"center": [127.4, 38.5], "span": 4.4},
    "pyong": {"center": [125.9, 39.02], "span": 0.62}, "valley": {"center": [125.955, 39.01], "span": 0.16}, "bridge": {"center": [125.955, 39.008], "span": 0.1},
}
# 1951~52 겨울 전선 (개략)
MLR = [[126.1, 37.72], [126.6, 37.92], [127.0, 38.15], [127.4, 38.32], [127.8, 38.33], [128.15, 38.3], [128.4, 38.55]]
front = {"k": "front", "path": MLR, "at": 0}
RAIL = [[125.74, 39.012], [125.8, 39.0], [125.86, 38.998], [125.92, 39.0], [125.955, 39.008], [125.99, 39.025], [126.05, 39.05], [126.14, 39.08]]
rail = lambda at=0: {"k": "line", "path": RAIL, "color": "#ffb020", "glow": True, "at": at}
LOCK = lambda at=0.3, text="승호리 철교", color=None: dict({"k": "lock", "p": "bridge", "at": at, "text": text}, **({"color": color} if color else {}))
AA_PTS = [[125.94, 39.018], [125.968, 39.02], [125.945, 38.998], [125.972, 38.999], [125.957, 39.025]]
flak = lambda at=0.2, period=0.6: {"k": "shock", "pts": AA_PTS, "at": at, "period": period}
badge = lambda p, t, c="#111", at=0.3, dy=-70: {"k": "badge", "p": p, "text": t, "color": c, "at": at, "dy": dy}
RUN_SE = [[126.03, 38.96], [125.995, 38.985], [125.97, 39.0], [125.955, 39.008]]  # 남동쪽에서 계곡으로 진입 (개략)
RUN_E = [[126.05, 39.02], [126.0, 39.012], [125.975, 39.01], [125.955, 39.008]]
FLY = [[128.944, 37.753], [128.3, 38.1], [127.5, 38.55], [126.7, 38.85], [126.1, 38.98], [125.955, 39.008]]
plane = lambda path, at=0.1, n=1, dur=3.0, hit=False, size=1.0, color=None: dict({"k": "plane", "path": path, "at": at, "n": n, "dur": dur, "hit": hit, "size": size}, **({"color": color} if color else {}))
red_a = lambda path, at=0.3, w=1.0: {"k": "arrow", "path": path, "color": "red", "at": at, "width": w}
blue_a = lambda path, at=0.3, w=1.0: {"k": "arrow", "path": path, "color": "blue", "at": at, "width": w}
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]
BOOM = lambda at=0.2, v=0.45: [{"id": "boom", "at": at, "volume": v}]
KR_FLAT = [127.4, 38.6]

# ===== 제1막 (콜드 오프닝 → 질문 → 타이틀 → 배경) =====
sc(1, ai("mustang_formation"), label=DRAMA, callouts=top("1952. 1. 15 오전 8:25"))
sc(1, m("pyong", "valley", [LOCK(0.2), plane(RUN_E, 0.1, 6, 3.2)], tilt=30, hud=True))
sc(1, ai("taeguk_wing"), label=DRAMA)
sc(1, ai("bridge_intact"), label=DRAMA)
sc(1, m("valley", "bridge", [LOCK(0), flak(0.1, 0.5)], tilt=38, hud=True), sfx=BOOM(0.3))
sc(1, ai("dive_start"), label=DRAMA, sfx=[{"id": "whoosh", "at": 0.2, "volume": 0.5}])
sc(1, ai("dive_flak"), label=DRAMA, sfx=BOOM(0.4))
sc(1, stage([C("us_shrug", 0.5, 520)], [pop("label", 0.5, 0.22, "약 500번 폭격", on="오백 번", color="red")]))
sc(1, stage([C("us_idle", 0.32, 480), C("us_point", 0.7, 480, flip=True)], [pop("bubble", 0.5, 0.3, "세계 최강 미 공군도..", at=0.2)]))
sc(1, stage([C("us_point", 0.3, 460), C("us_shrug", 0.72, 460, flip=True)], [pop("label", 0.5, 0.2, "누가 먼저 끊나? 내기", on="내기", color="yellow")]))
sc(1, stage([C("kr_plead", 0.5, 500)], [pop("label", 0.5, 0.18, "전투기 0대로 시작한 공군", on="단 한 대도", color="dark")]))
sc(1, stage([C("kr_salute", 0.5, 520)], [pop("label", 0.5, 0.2, "단 14번 출격", on="열네 번", color="red"), pop("ex", 0.75, 0.3, on="출격")]))
sc(1, cmp("미 공군", "약 500번", "한국 공군", "14번", "red", "blue"), sfx=[{"id": "hit", "at": 0.6, "volume": 0.4}])
sc(1, stage([C("us_shrug", 0.3, 440), C("kr_idle", 0.7, 440)], [pop("q", 0.5, 0.3, at=0.2, size=220)]))
sc(1, black("답은", "숫자 하나에"))
sc(1, text("1,500", "red", "이 숫자의 뜻은 영상 끝에서"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(1, black("1,500의 뜻은", "끝까지 보시면 알게 됩니다"))
sc(1, {"type": "titlecard", "title": "승호리 철교 폭파작전", "sub": "미군 500번 실패한 다리 · 1952", "at": 0, "q": pin("rokaf_f51")}, flash=True, sfx=BOOM(0, 0.5))
sc(1, black("1951년 겨울"), chapter={"num": "제1막", "title": "500번을 버틴 다리"})
sc(1, m("korea", "korea", [front, {"k": "marker", "p": "panmun", "color": "red", "at": 0.6}]), callouts=top("1951년 겨울 · 38선 부근 전선 고착 · " + NOTE))
sc(1, ph("talks"), label=plabel("talks", "판문점 휴전 회담"))
sc(1, stage([C("un_point", 0.5, 480)], [pop("label", 0.5, 0.2, "땅 → 하늘의 싸움", on="하늘에서", color="blue")]))
sc(1, m("korea", "north", [front, red_a([[124.4, 40.1], [125.75, 39.02], [126.6, 38.4]], 0.2, 1.2)]), callouts=top("적의 보급로", "red"))
sc(1, text("1951년 여름 시작", "yellow", "유엔 공군의 보급로 차단 작전"))
sc(1, text("교살 작전", "red", "Operation Strangle · 목을 조르다"), sfx=[{"id": "hit", "at": 0.3, "volume": 0.4}])
sc(1, stage([C("un_idle", 0.3, 440), C("cn_shock", 0.72, 440, flip=True)], [pop("label", 0.3, 0.18, "철길 · 도로 차단", at=0.2, color="blue"), pop("bubble", 0.72, 0.3, "보급이..!", on="말려")]))
sc(1, ph("supply_train"), label=plabel("supply_train", "한국 전쟁기의 철도 수송"))
sc(1, flat([125.7, 39.25], 5.4, [fpin([124.4, 40.1], "신의주", at=0, flag="cn", side="right"), fpin([125.754, 39.02], "평양", on="평양", side="left"), fpin([126.9, 38.4], "전선", on="전선", color="#111")],
           [route([124.4, 40.1], [125.754, 39.02], on="압록강", bend=0.05, color="#D32F2F"), route([125.754, 39.02], [126.9, 38.4], on="평양을", bend=-0.1, color="#D32F2F")],
           [{"ll": [124.0, 38.6], "text": "황해", "style": "sea"}, {"ll": [124.95, 40.35], "text": "압록강", "size": 40}]))
sc(1, stage([C("cn_shock", 0.35, 460), C("nk_shock", 0.68, 460)], [pop("label", 0.5, 0.18, "식량 ↓ 탄약 ↓", on="굶고", color="red")]))
sc(1, ai("rail_repair"), label=DRAMA)
sc(1, ai("rail_repair"), label=DRAMA, callouts=low("하룻밤이면 복구"))
sc(1, stage([C("un_point", 0.5, 480)], [pop("q", 0.78, 0.3, at=0.3)]))
sc(1, ph("bridge_strike"), label=plabel("bridge_strike", "폭격으로 끊긴 북한의 철교"), callouts=top("목표 = 철교", "yellow"))
sc(1, checklist("철교가 표적인 이유", [{"text": "부수기 어렵다", "at": 0, "checkOn": "부수기도"}, {"text": "다시 짓기는 더 어렵다", "on": "다시 짓기는", "checkOn": "더 어렵"}]))
sc(1, m("north", "pyong", [{"k": "marker", "p": "pyongyang", "color": "red", "at": 0}, LOCK(0.8)], flight=["north", "pyong"]), callouts=top("승호리 철교"))
sc(1, m("pyong", "pyong", [{"k": "marker", "p": "pyongyang", "color": "red", "at": 0}, LOCK(0.2)], tilt=24))
sc(1, m("pyong", "pyong", [{"k": "marker", "p": "pyongyang", "color": "red", "at": 0}, badge([125.86, 38.97], "대동강", "#1E8FFF", 0.3, 0), badge([126.0, 38.97], "남강", "#1E8FFF", 0.6, 0), LOCK(0.8)], tilt=26), callouts=low("평양 동쪽 · 남강 철교 · " + NOTE))
sc(1, m("pyong", "pyong", [rail(0), LOCK(0), red_a([[125.76, 39.03], [125.955, 39.03], [126.15, 39.1]], 0.4, 0.8)], tilt=26), callouts=top("평양 → 동부·중부 전선", "red"))
sc(1, stage([C("nk_point", 0.5, 480)], [pop("label", 0.5, 0.18, "보급의 혈관", on="혈관", color="red")]))
sc(1, ph("f51_us"), label=plabel("f51_us", "미 공군 F-51 전폭기"))
sc(1, {"type": "bars", "note": "국방부 군사편찬연구소 기준 · 기록에 따라 다름", "items": [{"label": "미 제5공군 출격", "value": 500, "display": "약 500회", "color": "red", "at": 0.2}]})
sc(1, m("bridge", "bridge", [{"k": "marker", "p": [125.953, 39.006], "color": "red", "at": 0, "text": "옛 철교"}], tilt=34), callouts=low("원래 철교 · 끊김"))
sc(1, m("bridge", "bridge", [{"k": "marker", "p": [125.953, 39.006], "color": "red", "at": 0, "text": "옛 철교"}, LOCK(0.4, "새 철교"), badge([125.955, 39.01], "약 200m", "#111", 0.7, -110)], tilt=34), callouts=low("하류 쪽 새 철교 · " + NOTE))
sc(1, stage([C("nk_salute", 0.5, 500)], [pop("bubble", 0.5, 0.3, "이번엔 단단히!", at=0.2)]))
sc(1, ai("crib_pier"), label=DRAMA, callouts=low("교각 10개 · 井 자 침목 + 모래주머니"))
sc(1, checklist("침목 교각의 비밀", [{"text": "폭탄 충격 흡수", "on": "충격을", "checkOn": "흡수"}, {"text": "기관총 탄 막기", "on": "기관총", "checkOn": "막아"}]))
sc(1, m("valley", "valley", [LOCK(0), flak(0.3, 0.7), badge([125.94, 39.02], "대공포", "#c9242c", 0.4, -50), badge([125.972, 38.998], "대공포", "#c9242c", 0.7, 50)], tilt=36, hud=True))
sc(1, ai("flak_valley"), label=DRAMA, sfx=BOOM(0.3))
sc(1, m("valley", "valley", [LOCK(0), plane([[126.03, 39.05], [125.98, 39.03], [125.93, 39.03], [125.88, 39.05]], 0.1, 3, 3.5, False, 0.7)], tilt=20), callouts=top("미군 · 높은 고도 투하", "blue"))
sc(1, stage([C("us_shrug", 0.5, 480)], [pop("bubble", 0.5, 0.3, "대공포는 피해야지..", at=0.2)]))
sc(1, ai("bomb_miss"), label=DRAMA)
sc(1, ai("bomb_miss"), label=DRAMA, callouts=low("강물 · 모래톱에 빗나간 폭탄"))
sc(1, black("끊어지지 않는", "다리"))
next_act()

# ===== 제2막 빨간 마후라의 탄생 =====
MID = [nid()]
sc(1, stage([C("kr_idle", 0.5, 480)], [pop("q", 0.72, 0.3, at=0.3)], title="이 다리를 끊은 공군은?"), pauseBefore=0.5, chapter={"num": "제2막", "title": "빨간 마후라의 탄생"})
sc(1, black("1950년 6월"))
sc(1, stage([C("kr_shock", 0.5, 500)], [pop("label", 0.5, 0.18, "전투기 0대", on="한 대도", color="red")]))
sc(1, checklist("1950년 6월 25일 · 한국 공군 보유 항공기", [{"text": "연락기·훈련기 등 경항공기 22대", "at": 0, "checkOn": "스물두"}, {"text": "전투기 0대", "on": "전부", "checkOn": "전부", "bad": True}]))
sc(1, ai("hand_bomb"), label=DRAMA)
sc(1, flat([131.0, 36.0], 9, [fpin([126.9, 37.5], "서울", at=0, flag="kr", side="left"), fpin([130.43, 33.58], "이타즈케 (일본)", on="일본", flag="us", side="right")], [route([126.9, 37.5], [130.43, 33.58], on="일본으로", bend=0.15, color="#2e66d8")]))
sc(1, ph("f51_bout"), label=plabel("f51_bout", "한국 공군이 넘겨받은 F-51 (1950)"))
sc(1, stage([C("kr_shock", 0.5, 480)], [pop("label", 0.5, 0.2, "훈련 단 며칠", on="며칠", color="yellow")]))
sc(1, flat([129.5, 35.0], 6, [fpin([130.43, 33.58], "이타즈케", at=0, side="right"), fpin([128.6, 35.87], "대구", on="대구로", flag="kr", side="left")], [route([130.43, 33.58], [128.6, 35.87], on="바다를", bend=-0.2, color="#2e66d8")]))
sc(1, text("이근석 대령 전사", "red", "1950. 7. 4 · 첫 출격 다음 날"))
sc(1, black("피로 시작된", "한국 공군 전투기의 역사"))
sc(1, ph("rok_capt", marks=[{"text": "미 공군과 함께 · 1년", "x": 0.5, "y": 0.12, "on": "일 년", "color": "yellow"}]), label=plabel("rok_capt", ""))
sc(1, black("1951년 가을", "혼자 설 기회"))
sc(1, flat(KR_FLAT, 6.8, [fpin([128.944, 37.753], "강릉 기지", on="강릉", flag="kr", side="right")], [], SEA))
sc(1, text("제1전투비행단 제10전투비행전대", "blue", "강릉 기지 · 1951년 가을부터"))
sc(1, stage([C("kr_point", 0.5, 500)], [pop("label", 0.5, 0.18, "첫 단독 작전", on="스스로 출격", color="yellow")]))
sc(1, stage([C("us_point", 0.3, 460), C("kr_idle", 0.7, 400, flip=True)], [pop("label", 0.3, 0.16, "미군 지휘", at=0.2, color="blue")]))
sc(1, stage([C("kr_point", 0.5, 500)], [pop("label", 0.5, 0.16, "한국인 지휘관 · 한국인 편대장", on="한국인 지휘관", color="yellow")]))
sc(1, black("신생 공군의", "시험대"))
sc(1, ph("kim_shin"), label=plabel("kim_shin", "김신 대령"), callouts=low("제10전투비행전대장 김신 대령"))
sc(1, text("백범 김구의 둘째 아들", "yellow"))
sc(1, ai("red_scarf"), label=DRAMA)
sc(1, ai("red_scarf"), label=DRAMA, callouts=top("빨간 마후라", "red"))
sc(1, flat(KR_FLAT, 5.2, [fpin([128.944, 37.753], "빨간 마후라의 고향 · 강릉", at=0, flag="kr", side="left")], [], SEA))
sc(1, ai("paper_flowers"), label=DRAMA)
sc(1, ai("paper_flowers"), label=DRAMA, callouts=low("흰 종이에 물감을 들인 꽃"))
sc(1, ph("f51_ww2"), label=plabel("f51_ww2", "F-51(P-51) 무스탕"))
sc(1, stage([C("us_idle", 0.5, 460)], [pop("label", 0.5, 0.18, "제트기의 시대", on="제트기", color="dark")]))
sc(1, stage([C("kr_idle", 0.5, 460)], [pop("q", 0.72, 0.3, on="이유가")]))
sc(1, checklist("무스탕이 불려 나온 이유", [{"text": "오래 떠 있을 수 있다", "on": "오래", "checkOn": "오래"}, {"text": "거친 활주로에서도 뜬다", "on": "거친", "checkOn": "거친"}]))
sc(1, ph("f51_ground"), label=plabel("f51_ground", "지상 공격에 나선 F-51"))
sc(1, reasons("무스탕의 약점", [{"text": "느리다", "at": 0}, {"text": "낡았다", "on": "낡았고"}, {"text": "엔진 고장", "on": "엔진이"}]))
sc(1, ph("f51_mud", "50% 50%"), label=plabel("f51_mud", "F-51 무스탕"), callouts=low("동체 아래 냉각 장치 = 급소"))
sc(1, stage([C("kr_shock", 0.5, 480)], [pop("label", 0.5, 0.18, "지상 사격 = 치명적", on="치명적", color="red")]))
sc(1, ph("rok_crew"), label=plabel("rok_crew", "출격 준비"))
sc(1, black("1952년 1월 초"))
sc(1, stage([C("us_point", 0.5, 500)], [pop("label", 0.5, 0.18, "미 제5공군 명령", at=0.2, color="blue")]))
sc(1, doc("작전 명령", ["발신: 미 제5공군", "수신: 강릉 기지 (한국 공군)", "", "승호리 철교를 차단하라"], "긴급", "미 제5공군"))
sc(1, m("korea", "pyong", [LOCK(0.6, "승호리 철교 · 약 500번 실패", "red")], flight=["korea", "north", "pyong"]))
next_act()

# ===== 제3막 1월 12일, 첫 번째 실패 =====
sc(1, flat([127.4, 38.4], 5.2, [fpin([128.944, 37.753], "강릉 기지", at=0, flag="kr", side="right"), fpin([125.955, 39.008], "승호리 철교", on="승호리", side="left", color="#111")],
           [route([128.944, 37.753], [125.955, 39.008], on="직선", label="직선 약 300km", bend=-0.16)], SEA), chapter={"num": "제3막", "title": "1월 12일, 첫 번째 실패"})
sc(1, m("route", "route", [front, plane(FLY, 0.1, 1, 4.0, False, 0.8)]), callouts=top("적진 횡단", "red"))
sc(1, stage([C("kr_shock", 0.5, 460)], [pop("label", 0.5, 0.18, "왕복 600km", on="육백", color="yellow"), pop("bubble", 0.5, 0.36, "연료가..", on="연료")]))
sc(1, ai("winter_cockpit"), label=DRAMA)
sc(1, ai("snow_ridges"), label=DRAMA, callouts=low("엔진이 멈추면 = 적진 한가운데"))
sc(1, stage([C("kr_salute", 0.5, 500)], [pop("label", 0.5, 0.18, "김두만 소령", at=0.1, color="dark")]))
sc(1, text("한국 공군 첫 100회 출격", "yellow", "김두만 소령"))
sc(1, black("1952년 1월 12일", "아침 7시 40분"))
sc(1, ai("takeoff_dawn"), label=DRAMA, callouts=top("F-51 5대 이륙"))
sc(1, m("valley", "valley", [LOCK(0), plane(RUN_SE, 0.1, 5, 3.0), flak(0.4)], tilt=30, hud=True), sfx=BOOM(0.8))
sc(1, m("bridge", "bridge", [LOCK(0), {"k": "shock", "pts": [[125.948, 39.004], [125.962, 39.002], [125.951, 39.013], [125.96, 39.014]], "at": 0.3, "period": 0.9}], tilt=36), callouts=top("500파운드 폭탄 10발"))
sc(1, black("결과는", "실패"), sfx=[{"id": "hit", "at": 0.5, "volume": 0.4}])
sc(1, ai("bomb_miss"), label=DRAMA, callouts=low("교각 사이 모래바닥 · 강물"))
sc(1, ai("bridge_intact"), label=DRAMA)
sc(1, ai("crib_pier"), label=DRAMA)
sc(1, stage([C("kr_shrug", 0.5, 480)], [pop("bubble", 0.5, 0.28, "정확히 맞혀야 한다..", at=0.3)]))
sc(1, black("오후 2시", "윤응렬 대위 · F-51 3대"))
sc(1, m("bridge", "bridge", [LOCK(0), plane(RUN_E, 0.1, 3, 2.6, True, 0.8)], tilt=36), callouts=top("철로 명중"))
sc(1, stage([C("kr_shrug", 0.5, 480)], [pop("label", 0.5, 0.18, "철로만 손상", on="철로만", color="red")]))
sc(1, cmp("1월 12일 출격", "8번", "철교", "그대로", "blue", "red"))
sc(1, stage([C("kr_shock", 0.35, 440), C("us_shrug", 0.7, 440, flip=True)], [pop("bubble", 0.7, 0.28, "그것 봐..", at=0.3)]))
sc(1, black("문제는", "폭격 방식 그 자체"))
sc(1, text("미군 표준 방식", "blue"))
sc(1, {"type": "profile", "pts": [[0, 2400], [0.35, 2400], [0.55, 1500], [0.7, 900], [0.8, 1100], [1, 1800]], "grid": [900, 1500, 2400], "yMin": 0, "yMax": 2800,
       "title": "미군 방식", "note": "모식도 · 피트는 근사 환산", "left": "강하 시작 8,000피트 (약 2,400m)", "right": "",
       "marks": [{"x": 0.35, "text": "강하 시작", "style": "yellow", "at": 0, "lift": 60, "size": 40}]})
sc(1, {"type": "profile", "pts": [[0, 2400], [0.35, 2400], [0.55, 1500], [0.7, 900], [0.8, 1100], [1, 1800]], "grid": [900, 1500, 2400], "yMin": 0, "yMax": 2800,
       "title": "미군 방식", "note": "모식도 · 피트는 근사 환산", "left": "강하 시작 8,000피트", "right": "투하 3,000피트 (약 900m)",
       "marks": [{"x": 0.35, "text": "강하 시작", "style": "yellow", "at": 0, "lift": 60, "size": 40}, {"x": 0.7, "text": "투하", "style": "red", "at": 0.3, "lift": 60, "size": 44}]})
sc(1, stage([C("us_idle", 0.5, 480)], [pop("label", 0.5, 0.18, "조종사는 안전", on="안전한", color="blue")]))
sc(1, stage([C("us_shrug", 0.5, 480)], [pop("label", 0.5, 0.18, "다리는 너무 좁다", on="좁은", color="red")]))
sc(1, reasons("폭탄이 빗나간 이유", [{"text": "바람 한 줄기", "on": "바람"}, {"text": "손끝 흔들림", "on": "흔들림"}, {"text": "수십 m 오차", "on": "몇십"}]))
sc(1, black("이 방식으로는", "몇 번을 가도 같다"))
sc(1, ai("ops_room_night"), label=DRAMA)
sc(2, {"type": "cta", "title": "구독 · 좋아요로 다음 이야기까지 함께해 주세요", "at": 0}, sfx=[{"id": "pop", "at": 0.2, "volume": 0.45}])
next_act()

# ===== 제4막 김신의 결단, 1,500피트 =====
MID.append(nid())
sc(1, ai("ops_room_night"), label=DRAMA, pauseBefore=0.5, chapter={"num": "제4막", "title": "김신의 결단, 1,500피트"})
sc(1, ph("briefing", "50% 30%"), label=plabel("briefing", ""), callouts=low("작전처장 강호륜 · 출격 편대와 폭격 방법 재설계"))
sc(1, black("그리고", "결론"))
sc(1, doc("작전 회의 결론", ["미군 방식(고고도 투하)으로는", "승호리 철교를 끊을 수 없다"], "결론"))
sc(1, stage([C("kr_idle", 0.5, 480)], [pop("q", 0.72, 0.3, at=0.2)]))
sc(1, text("더 낮게", "red"), sfx=[{"id": "whoosh", "at": 0, "volume": 0.5}])
sc(1, cmp("강하 시작 · 미군", "8,000피트", "강하 시작 · 한국 공군", "4,000피트", "blue", "red"))
sc(1, cmp("투하 · 미군", "3,000피트", "투하 · 한국 공군", "1,500피트", "blue", "red"), sfx=[{"id": "hit", "at": 0.7, "volume": 0.45}])
sc(1, text("1,500", "red", "영상 처음의 그 숫자"))
sc(1, text("1,500피트 ≈ 450m", "yellow"))
sc(1, stage([C("kr_point", 0.3, 440)], [pop("label", 0.68, 0.3, "남산서울타워 꼭대기 높이", on="남산", color="yellow")]))
sc(1, {"type": "profile", "pts": [[0, 1200], [0.3, 1200], [0.5, 800], [0.62, 450], [0.72, 650], [1, 1100]], "grid": [450, 900, 1200], "yMin": 0, "yMax": 2800,
       "title": "한국 공군 방식", "note": "모식도 · 피트는 근사 환산", "left": "강하 시작 4,000피트 (약 1,200m)", "right": "투하 1,500피트 (약 450m)",
       "marks": [{"x": 0.62, "text": "투하 = 절반 높이", "style": "red", "at": 0, "lift": 60, "size": 44}]})
sc(1, checklist("높이가 절반이 되면", [{"text": "폭탄이 날아가는 거리 ↓", "on": "날아가는", "checkOn": "짧아지고"}, {"text": "빗나갈 여유 ↓", "on": "빗나갈", "checkOn": "줄어듭"}]))
sc(1, text("명중률 ↑", "yellow"))
sc(1, stage([C("kr_point", 0.5, 480)], [pop("label", 0.5, 0.18, "= 다트 던지기", on="다트", color="yellow")]))
sc(1, stage([C("kr_idle", 0.25, 420), C("kr_idle", 0.75, 420)], [pop("label", 0.25, 0.2, "10걸음", on="열 걸음", color="dark"), pop("label", 0.75, 0.2, "5걸음", on="다섯 걸음", color="yellow"), pop("q", 0.5, 0.32, on="어느 쪽")]))
sc(1, stage([C("kr_salute", 0.5, 480)], [pop("label", 0.5, 0.18, "가까울수록 명중", on="가까이서", color="yellow")]))
sc(1, stage([C("kr_shock", 0.5, 480)], [pop("label", 0.5, 0.18, "총을 쏘는 과녁", on="쏘아 대는", color="red"), pop("ex", 0.78, 0.3, on="과녁")]))
sc(1, black("모두가", "알고 있었다"))
sc(1, reasons("1,500피트의 대가", [{"text": "대공포 노출", "on": "대공포에"}, {"text": "보병 사거리", "later": True}, {"text": "내 폭탄 파편", "later": True}]))
sc(1, reasons("1,500피트의 대가", [{"text": "대공포 노출", "at": 0}, {"text": "보병 사거리", "on": "보병의"}, {"text": "내 폭탄 파편", "later": True}]))
sc(1, reasons("1,500피트의 대가", [{"text": "대공포 노출", "at": 0}, {"text": "보병 사거리", "at": 0}, {"text": "내 폭탄 파편", "on": "파편과"}]))
sc(1, doc("윤응렬 장군의 회고", ["저공으로 내려가면", "대공포보다 무서운 것은", "적 보병의 소총 사격"], "증언", "공군본부 『6·25전쟁 증언록』", "요지 · 재구성"))
sc(1, stage([C("kr_shrug", 0.5, 480)], [pop("label", 0.5, 0.18, "저공 → 대공포는 별 소용 없다", on="대공포는", color="dark")]))
sc(1, stage([C("kr_shock", 0.5, 480)], [pop("label", 0.5, 0.18, "진짜 공포 = 적 보병", on="보병들", color="red")]))
sc(1, ai("infantry_barrage"), label=DRAMA, callouts=low("비행기 앞 20~30m 허공에 집중 사격"))
sc(1, ai("infantry_barrage"), label=DRAMA)
sc(1, ph("f51_mud", "50% 50%"), label=plabel("f51_mud", "F-51 무스탕"), callouts=low("냉각 장치 한 발 = 엔진 정지"))
sc(1, m("korea", "pyong", [front, LOCK(0.5, "평양 근처", "red")]), callouts=top("돌아올 방법이 없다", "red"))
sc(1, black("그럼에도", "실행"), sfx=[{"id": "hit", "at": 0.5, "volume": 0.45}])
sc(1, text("역할을 둘로", "yellow"))
sc(1, m("valley", "valley", [LOCK(0), plane(RUN_E, 0.1, 3, 2.6, False, 0.8, "#2e66d8"), badge([126.02, 39.03], "제1편대 · 대공포 제압", "#2e66d8", 0.3, -60), plane(RUN_SE, 2.0, 3, 2.8, True, 0.8, "#c9242c"), badge([126.02, 38.97], "제2편대 · 폭격", "#c9242c", 1.0, 60)], tilt=32, hud=True))
sc(1, stage([C("kr_point", 0.3, 440), C("kr_salute", 0.72, 440, flip=True)], [pop("label", 0.3, 0.16, "시선 끌기", on="시선을", color="blue"), pop("label", 0.72, 0.16, "가장 낮게", on="가장 낮게", color="red")]))
sc(1, black("출격 명단"))
sc(1, doc("제1편대", ["편대장 윤응렬 대위", "2번기 정주량 대위", "3번기 장성태 대위"]))
sc(1, doc("제2편대", ["편대장 옥만호 대위", "2번기 유치곤 대위", "3번기 박재호 대위"]))
sc(1, stage([C("kr_salute", 0.2, 380), C("kr_salute", 0.4, 380), C("kr_salute", 0.6, 380, flip=True), C("kr_salute", 0.8, 380, flip=True)], [pop("label", 0.5, 0.16, "6명", at=0.1, color="yellow")]))
sc(1, ai("dawn_base"), label=DRAMA)
sc(1, ai("pilots_map"), label=DRAMA)
sc(1, ai("pilots_map"), label=DRAMA, callouts=low("한 번의 실수도 허락되지 않는 비행"))
next_act()

# ===== 제5막 오전 8시 25분 =====
MID.append(nid())
sc(1, ai("frozen_runway"), label=DRAMA, pauseBefore=0.5, chapter={"num": "제5막", "title": "오전 8시 25분"}, callouts=top("1952. 1. 15 · 강릉"))
sc(1, ai("engine_start"), label=DRAMA)
sc(1, ai("bomb_load"), label=DRAMA)
sc(1, m("route", "route", [front, plane(FLY, 0.1, 6, 4.0, False, 0.75)]), callouts=top("적진 깊숙이", "red"))
sc(1, m("pyong", "valley", [LOCK(0.2), plane(RUN_E, 0.1, 6, 3.2, False, 0.8)], tilt=28, hud=True), callouts=top("오전 8:25 · 표적 상공", "red"))
sc(1, m("valley", "valley", [LOCK(0), flak(0, 0.45)], tilt=36, hud=True), sfx=BOOM(0.1, 0.5))
sc(1, ai("dive_start"), label=DRAMA, callouts=top("제1편대 · 윤응렬", "blue"))
sc(1, m("valley", "bridge", [LOCK(0), flak(0, 0.5), plane(RUN_E, 0.1, 3, 2.6, False, 0.85, "#2e66d8")], tilt=38, hud=True), sfx=[{"id": "whoosh", "at": 0.3, "volume": 0.5}])
sc(1, ai("rocket_fire"), label=DRAMA, sfx=[{"id": "whoosh", "at": 0.1, "volume": 0.5}])
sc(1, m("bridge", "bridge", [LOCK(0), {"k": "shock", "pts": [[125.952, 39.007], [125.958, 39.009]], "at": 0.1, "period": 0.7}], tilt=38), callouts=top("경간 2곳 불기둥", "red"), sfx=BOOM(0.2))
sc(1, black("하지만", "아직 끝이 아니었다"))
sc(1, ai("second_flight"), label=DRAMA, callouts=top("제2편대 · 옥만호", "red"))
sc(1, m("valley", "valley", [LOCK(0), plane([[125.99, 39.03], [125.96, 39.035], [125.935, 39.02], [125.94, 39.0]], 0.1, 3, 2.4, False, 0.8, "#2e66d8"), plane(RUN_SE, 0.6, 3, 2.8, False, 0.8, "#c9242c")], tilt=32, hud=True))
sc(1, m("valley", "valley", [LOCK(0), flak(0, 0.6), {"k": "shock", "pts": AA_PTS, "at": 0.4, "period": 0.35, "color": "#2e66d8"}], tilt=32, hud=True), callouts=top("제1편대 · 대공포 진지 제압", "blue"))
sc(1, stage([C("kr_point", 0.3, 440), C("kr_salute", 0.72, 440, flip=True)], [pop("bubble", 0.3, 0.26, "이쪽이다..!", at=0.2), pop("label", 0.72, 0.16, "동료를 위해", on="동료가", color="yellow")]))
sc(1, ai("dive_flak"), label=DRAMA, callouts=top("4,000피트 · 강하 시작"))
sc(1, text("3,000피트", "dark"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.45}])
sc(1, text("아직", "yellow"))
sc(1, text("2,000피트", "dark"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.45}])
sc(1, ai("flak_close"), label=DRAMA, sfx=BOOM(0.1, 0.5))
sc(1, text("1,500피트", "red"), sfx=[{"id": "hit", "at": 0.1, "volume": 0.5}])
sc(1, ai("bomb_release"), label=DRAMA, sfx=[{"id": "whoosh", "at": 0.1, "volume": 0.5}])
sc(1, ai("pull_up"), label=DRAMA)
sc(1, m("bridge", "bridge", [LOCK(0, "승호리 철교", "red"), plane(RUN_SE, 0, 1, 1.2, True, 1.0, "#c9242c")], tilt=40, hud=True), sfx=BOOM(1.2, 0.6))
sc(1, ai("bridge_explode"), label=DRAMA, sfx=BOOM(0.2, 0.6))
sc(1, ai("bridge_broken"), label=DRAMA, callouts=low("철교 한가운데 큰 구멍 2개"))
sc(1, black("승호리 철교", "끊어지다"), sfx=[{"id": "hit", "at": 0.5, "volume": 0.5}])
sc(1, {"type": "bars", "note": "1952. 1. 15 · F-51 6대 사용 탄약 (국방부 군사편찬연구소)", "items": [{"label": "폭탄", "value": 12, "display": "12발", "color": "red", "at": 0}, {"label": "로켓탄", "value": 20, "display": "20발", "color": "red", "at": 0.3}, {"label": "기관총탄", "value": 47, "display": "4,700발", "color": "blue", "at": 0.6}]})
sc(1, checklist("함께 부순 표적", [{"text": "포진지 6곳", "on": "포진지", "checkOn": "포진지"}, {"text": "보급품 집적소 1곳", "on": "집적소", "checkOn": "집적소"}, {"text": "벙커 3곳 · 건물 1동", "on": "벙커", "checkOn": "건물"}]))
sc(1, ph("gun_cam"), label=plabel("gun_cam", ""))
sc(1, black("누구도 부정할 수 없는", "증거"))
sc(1, m("route", "route", [front, plane(list(reversed(FLY)), 0.1, 6, 4.0, False, 0.75)]), callouts=top("귀환", "blue"))
sc(1, ai("landing"), label=DRAMA)
sc(1, ai("film_develop"), label=DRAMA)
sc(1, ph("seungho_ba", "50% 50%", marks=[{"text": "폭격 전", "x": 0.3, "y": 0.8, "at": 0, "color": "yellow"}, {"text": "폭격 후 · 경간 파괴", "x": 0.72, "y": 0.8, "at": 0.5, "color": "red"}]), label=plabel("seungho_ba", ""))
sc(1, {"type": "timeline", "items": [{"date": "1952. 1. 12", "text": "8번 출격 · 실패", "at": 0}, {"date": "1. 15", "text": "6번 출격 · 파괴", "at": 0.6}]})
sc(1, cmp("미 공군", "약 500번", "한국 공군", "14번", "red", "blue"), sfx=[{"id": "hit", "at": 0.7, "volume": 0.45}])
sc(1, stage([C("kr_idle", 0.5, 460)], [pop("q", 0.72, 0.3, at=0.2)], title="처음의 질문"))
sc(1, reasons("차이를 만든 것은?", [{"text": "더 좋은\n비행기", "at": 0, "xOn": "비행기도"}, {"text": "더 많은\n폭탄", "on": "더 많은", "xOn": "아니었"}]))
sc(1, text("1,500피트", "red"), sfx=[{"id": "hit", "at": 0.1, "volume": 0.5}])
sc(1, stage([C("kr_salute", 0.2, 360), C("kr_salute", 0.35, 360), C("kr_salute", 0.5, 360), C("kr_salute", 0.65, 360, flip=True), C("kr_salute", 0.8, 360, flip=True)], [pop("label", 0.5, 0.16, "절반의 높이 · 6명의 각오", at=0.2, color="yellow")]))
sc(1, black("그것이", "답이었다"))
next_act()

# ===== 제6막 500 대 14가 남긴 것 =====
sc(1, black("1952년 2월 21일", "미 제5공군 지휘관 회의"), chapter={"num": "제6막", "title": "500 대 14가 남긴 것"})
sc(1, stage([C("us_idle", 0.22, 380), C("us_point", 0.45, 380), C("us_idle", 0.68, 380, flip=True), C("kr_salute", 0.88, 380, flip=True)], [pop("label", 0.5, 0.16, "박수", on="박수", color="yellow")]))
sc(1, ph("kim_shin"), label=plabel("kim_shin", "김신 대령"), callouts=low("김신 장군 증언 · 공군 『6·25전쟁 증언록』"))
sc(1, stage([C("us_point", 0.32, 460), C("kr_idle", 0.7, 440, flip=True)], [pop("bubble", 0.32, 0.26, "정말 반갑소!", on="반갑다", at=None)]))
sc(1, stage([C("kr_shrug", 0.5, 460)], [pop("q", 0.7, 0.3, at=0.2)]))
sc(1, stage([C("us_point", 0.3, 440), C("us_shrug", 0.7, 440, flip=True)], [pop("label", 0.5, 0.16, "한국 공군이 끊을까?", on="돈 내기", color="yellow")]))
sc(1, stage([C("us_shrug", 0.3, 440), C("us_point", 0.7, 440, flip=True)], [pop("label", 0.3, 0.16, "못 끊는다", on="못 끊는다", color="dark"), pop("label", 0.7, 0.16, "끊는다 (해병대)", on="끊는다는", color="yellow")]))
sc(1, stage([C("us_shock", 0.3, 440), C("us_salute", 0.7, 440, flip=True)], [pop("label", 0.7, 0.16, "내기 승리", on="이긴", color="yellow")]))
sc(1, ph("salute"), label=plabel("salute", ""), callouts=top("출격 조종사 6명 전원 표창"))
sc(1, text("윤응렬 대위 · 24살", "dark", "1927년생"))
sc(1, ai("pilots_map"), label=DRAMA)
sc(1, text("옥만호", "blue", "훗날 공군참모총장 · 대장 예편"))
sc(1, text("윤응렬", "blue", "훗날 공군사관학교 교장"))
sc(1, text("김신", "blue", "훗날 공군참모총장"))
sc(1, stage([C("kr_idle", 0.5, 460)], [pop("q", 0.72, 0.3, at=0.2)], title="500 대 14의 차이는?"))
sc(1, reasons("500 대 14를 가른 것", [{"text": "실패를\n인정하는 용기", "at": 0}, {"text": "역할을 나눈\n팀워크", "at": 0}, {"text": "실행한\n조종사의 각오", "at": 0}]))
sc(1, reasons("500 대 14를 가른 것", [{"text": "실패를\n인정하는 용기", "on": "용기"}, {"text": "역할을 나눈\n팀워크", "later": True}, {"text": "실행한\n조종사의 각오", "later": True}]))
sc(1, doc("1월 12일 이후", ["미군 교범: 3,000피트 투하", "김신 대령: 1,500피트로 바꾼다"], "변경"))
sc(1, black("통하지 않으면", "방식을 바꾼다"))
sc(1, reasons("500 대 14를 가른 것", [{"text": "실패를\n인정하는 용기", "at": 0}, {"text": "역할을 나눈\n팀워크", "on": "팀워크"}, {"text": "실행한\n조종사의 각오", "later": True}]))
sc(1, m("valley", "valley", [LOCK(0), plane([[125.99, 39.03], [125.96, 39.035], [125.935, 39.02], [125.94, 39.0]], 0.1, 3, 2.4, False, 0.8, "#2e66d8"), plane(RUN_SE, 0.5, 3, 2.6, True, 0.8, "#c9242c")], tilt=30, hud=True))
sc(1, stage([C("kr_point", 0.3, 440), C("kr_salute", 0.72, 440, flip=True)], [pop("label", 0.5, 0.16, "공격 = 동료를 지키는 일", on="지키기", color="yellow")]))
sc(1, reasons("500 대 14를 가른 것", [{"text": "실패를\n인정하는 용기", "at": 0}, {"text": "역할을 나눈\n팀워크", "at": 0}, {"text": "실행한\n조종사의 각오", "on": "각오"}]))
sc(1, ai("ops_map"), label=DRAMA)
sc(1, ai("dive_flak"), label=DRAMA, callouts=low("450m · 사람의 몫"))
sc(1, black("물론", "전쟁의 흐름이 바뀐 것은 아니다"))
sc(1, text("교살 작전의 한계", "dark", "적의 보급을 완전히 막지는 못했다"))
sc(1, black("하지만 남긴 것은", "다리 하나보다 컸다"))
sc(1, m("north", "pyong", [{"k": "marker", "p": "pyongyang", "color": "red", "at": 0}, plane([[126.4, 38.4], [126.1, 38.75], [125.85, 38.98], [125.76, 39.02]], 0.2, 6, 3.5, True, 0.7)]), callouts=top("1952년 여름 · 평양 일대 대규모 폭격", "red"))
sc(1, stage([C("us_idle", 0.32, 440), C("kr_salute", 0.68, 440, flip=True)], [pop("label", 0.5, 0.16, "보조가 아닌 한 몫", on="한 몫", color="yellow")]))
sc(1, stage([C("kr_salute", 0.5, 500)], [pop("label", 0.5, 0.16, "스스로 짜고 · 스스로 해냈다", on="스스로 해냈다", color="yellow")]))
sc(1, {"type": "bars", "note": "한국 공군 F-51 · 1950~1953 (공군 집계)", "items": [{"label": "F-51 총 출격", "value": 8495, "display": "8,495회", "color": "blue", "at": 0.2}]})
sc(1, text("62.9% = 후방 차단 작전", "yellow", "5,337회 · 공군 집계"))
sc(1, flat(KR_FLAT, 5.2, [fpin([128.944, 37.753], "강릉 기지 · 7,800여 회", on="강릉", flag="kr", side="left")], [], SEA))
sc(1, ai("snow_ridges"), label=DRAMA)
sc(1, black("그 대가도", "컸다"))
sc(1, text("조종사 39명", "red", "6·25전쟁 중 한국 공군 조종사 손실"))
sc(1, ai("paper_flowers"), label=DRAMA)
sc(1, ai("empty_slot"), label=DRAMA)
sc(1, ph("kf21"), label=plabel("kf21", "오늘의 한국 공군"))
sc(1, ai("red_scarf"), label=DRAMA)
sc(1, ai("mustang_sunset"), label=DRAMA)
sc(2, {"type": "endcard", "title": "1,500피트까지 내려간 여섯 명,\n돌아오지 못한 서른아홉 명을 기억하며", "q": pin("rokaf_f51")}, tail=1.0)
assert CUR["i"] == len(ACTS[5]), (CUR, len(ACTS[5]))

# ===== 재연 일러스트 (Gemini) =====
CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
F51 = "a 1952 Republic of Korea Air Force F-51D Mustang propeller fighter-bomber, natural silver metal finish, with the South Korean roundel (red-and-blue taeguk circle) on the wings and fuselage"
F51S = "1952 Republic of Korea Air Force F-51D Mustang propeller fighter-bombers, natural silver metal finish, with South Korean red-and-blue taeguk roundels on the wings"
PIL = "a South Korean Air Force pilot whose head is a round ball painted as the South Korean Taegukgi flag, wearing a 1950s brown leather flight jacket, a red silk scarf around the neck and a leather flight helmet with goggles"
PILS = "South Korean Air Force pilots whose heads are round balls painted as the South Korean Taegukgi flag, wearing 1950s brown leather flight jackets and red silk scarves around their necks"
BR = "a long steel truss railway bridge on many wooden crib piers over a frozen river in a snowy North Korean valley in winter 1952"
END = ", leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic, dark desaturated winter palette, film grain, no people visible, no text, no letters."
AI = {
    "mustang_formation": "Six " + F51S + " flying in two tight formations over snowy mountains in North Korea on a cold clear winter morning in January 1952, low sun, " + LAND,
    "taeguk_wing": "Close-up of the silver wing of " + F51 + ", the red-and-blue taeguk roundel clearly visible, rockets and a bomb hanging under the wing, snowy mountains far below, winter morning, " + LAND,
    "bridge_intact": BR + ", countless bomb craters in the snow and ice around it but the bridge still standing, anti-aircraft gun positions on the hills on both sides, " + LAND,
    "dive_start": F51 + " rolling over and starting a steep dive toward a railway bridge in a snowy river valley far below, black flak bursts around it, dramatic angle from above and behind, " + LAND,
    "dive_flak": "View from just behind the cockpit of " + F51 + " diving steeply into a narrow snowy river valley toward a railway bridge, dense black anti-aircraft flak bursts and tracer fire all around, " + LAND,
    "crib_pier": "Close-up of a wooden railway bridge pier in North Korea 1952 built from railway sleepers stacked in a criss-cross square tic-tac-toe pattern, filled with sandbags, frozen river, bomb craters nearby, " + LAND,
    "flak_valley": "North Korean anti-aircraft gun crews with 37mm guns firing upward from snowy hillside sandbagged pits overlooking a railway bridge in a river valley, winter 1952, tracer streaks in the sky, silhouettes only, " + LAND,
    "bomb_miss": "Bombs exploding in a frozen river and on sandbars beside a long railway bridge in a snowy North Korean valley, tall water columns, the bridge itself untouched, " + LAND,
    "rail_repair": CB + "North Korean workers whose heads are round balls painted as the North Korean flag repairing a bombed railway track at night by lantern light, carrying rails and sleepers, winter 1951" + END,
    "hand_bomb": CB + PIL + " in the rear seat of a small yellow 1950 trainer airplane, holding a small hand-made bomb ready to drop over the side, summer 1950, determined" + END,
    "red_scarf": CB + PIL + " standing proudly beside a silver F-51 Mustang on a snowy airfield at Gangneung, the red scarf blowing in the wind, winter 1952" + END,
    "paper_flowers": CB + "Korean high school girls whose heads are round balls painted as the South Korean Taegukgi flag, in 1950s school uniforms, placing handmade paper flower garlands around the necks of " + PILS + " beside silver F-51 Mustangs on a winter airfield" + END,
    "winter_cockpit": CB + PIL + " in the cramped cockpit of an F-51 Mustang in flight, breath fogging in the freezing air, frost on the canopy, snowy mountains below" + END,
    "snow_ridges": "Endless snow-covered mountain ridges of North Korea seen from a fighter cockpit at altitude in winter, a silver propeller fighter wingtip at the edge of the frame, " + LAND,
    "takeoff_dawn": "Five " + F51S + " taking off one after another from a snowy coastal airfield at Gangneung at dawn in January 1952, the East Sea in the background, " + LAND,
    "ops_room_night": CB + "South Korean Air Force officers whose heads are round balls painted as the South Korean Taegukgi flag, in 1950s olive uniforms, leaning over a large map table with aerial photos of a railway bridge in a small wooden operations room at night, a single bulb, cigarette smoke" + END,
    "ops_map": "Close-up of a 1952 military operations map table with an aerial reconnaissance photo of a railway bridge over a river, pencil lines drawing a steep dive angle, a protractor and ruler, lamp light, no readable text, no letters, " + LAND,
    "infantry_barrage": CB + "North Korean infantry soldiers whose heads are round balls painted as the North Korean flag, lying on their backs in the snow on a hillside, all firing rifles and submachine guns straight up into the sky together at a low-flying propeller fighter" + END,
    "dawn_base": "A snowy airfield at Gangneung at dawn in January 1952 with a row of six silver F-51 Mustang fighters waiting, ground crew lanterns, frost, quiet, " + LAND,
    "pilots_map": CB + "six " + PILS[0].lower() + PILS[1:] + " gathered around a hand-drawn map of a river valley by lamplight in a barracks the night before a mission, serious faces" + END,
    "frozen_runway": "A frozen snowy airfield at Gangneung on a bitter cold January morning in 1952, ground crew in heavy coats, six silver F-51 Mustangs lined up with propellers, breath steam, " + LAND,
    "engine_start": "Close-up of the propeller and exhaust stacks of " + F51 + " starting up on a frozen airfield, blue exhaust smoke and blowing snow, winter morning, " + LAND,
    "bomb_load": CB + "South Korean Air Force ground crew whose heads are round balls painted as the South Korean Taegukgi flag, in heavy winter coats, loading a 500-pound bomb and rockets under the wing of a silver F-51 Mustang on a frozen airfield" + END,
    "rocket_fire": F51 + " firing rockets from under its wings in a steep dive toward a railway bridge in a snowy valley, rocket smoke trails, flak bursts, " + LAND,
    "second_flight": "Three " + F51S + " in a line rolling in one after another to dive on a railway bridge in a snowy river valley, while other Mustangs strafe hillside anti-aircraft positions, " + LAND,
    "flak_close": "Extreme close view from the cockpit of a diving F-51 Mustang, a black flak burst exploding just beside the wing, shrapnel streaks, the railway bridge rushing closer below, " + LAND,
    "bomb_release": F51 + " releasing a 500-pound bomb at very low altitude just above a railway bridge in a snowy valley, the bomb falling away, flak all around, " + LAND,
    "pull_up": F51 + " pulling up hard out of a narrow snowy river valley after a bomb run, vapor trails off the wingtips, flak bursts behind, " + LAND,
    "bridge_explode": "A huge explosion in the middle of a long steel railway bridge over a frozen river in a snowy North Korean valley, twisted steel girders flying into the air, " + LAND,
    "bridge_broken": "The broken railway bridge after the bombing, two big gaps in the middle with fallen spans in the frozen river, smoke drifting, snowy valley, " + LAND,
    "landing": "Silver F-51 Mustangs landing one after another on a snowy airfield at Gangneung in the late morning, ground crew waving, the East Sea in the background, " + LAND,
    "film_develop": CB + "a South Korean Air Force photo technician whose head is a round ball painted as the South Korean Taegukgi flag, holding up a strip of developed film to a red darkroom light, excited" + END,
    "empty_slot": "An empty parking spot on a snowy airfield at dusk where one fighter plane did not return, a single red scarf laid on the snow, a paper flower garland beside it, solemn, " + LAND,
    "mustang_sunset": "A lone silver F-51 Mustang propeller fighter flying over the East Sea coast near Gangneung at sunset, warm golden light, peaceful, " + LAND,
    "thumb_subject": "Photorealistic black-and-white 1952 Korean War documentary portrait of a young Korean fighter pilot, clearly East Asian Korean face with black hair, wearing a 1950s leather flight jacket, a scarf around the neck and a leather flight helmet with goggles pushed up on the forehead, resolute determined eyes looking into the distance, waist-up, face clearly visible and turned slightly toward the left of the frame, isolated on a plain pure white background, no shadows on the background, no text.",
}
used = {s["visual"]["img"] for s in S if s["visual"]["type"] == "ai"}
assert not used - set(AI), used - set(AI)
assert not set(AI) - used - {"thumb_subject"}, set(AI) - used

ids = [s["id"] for s in S]
chap = [i for i, s in enumerate(S) if s.get("chapter")]
sid = lambda i: S[i]["id"]
music = [{"id": "drone", "from": "s001", "to": sid(chap[0] - 1), "volume": 0.2},
         {"id": "theme", "from": sid(chap[0]), "to": sid(chap[2] - 1), "volume": 0.16},
         {"id": "tension", "from": sid(chap[2]), "to": sid(chap[3] - 1), "volume": 0.17},
         {"id": "analysis", "from": sid(chap[3]), "to": sid(chap[4] - 1), "volume": 0.16},
         {"id": "march", "from": sid(chap[4]), "to": sid(chap[5] - 1), "volume": 0.16},
         {"id": "somber", "from": sid(chap[5]), "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "승호리 철교 폭파작전", "subtitle": "1952. 1. 12 ~ 15", "style": 2, "target_sec": 1200, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID,
         "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap], "ai", len(AI), "pins", len(PINS), "photo scenes", sum(1 for s in S if s["visual"]["type"] == "photo"))
