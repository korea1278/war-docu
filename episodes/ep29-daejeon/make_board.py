# EP29 대전 전투 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 연출 스타일 v2 + 화면 업그레이드 2단계 + 롱폼 표준(LONGFORM_STANDARD) + 캐릭터 반복 방지 규칙
# + ★ 초반 후킹 표준(docs/HOOK_STANDARD.md) 첫 적용: 장면 필드 hook {hud[], neg, question} (remotion/Hook.tsx) · 화면 troops
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
    ("천구백오십일년 일월 구일", "1951년 1월 9일"), ("천구백오십삼년 구월 사일", "1953년 9월 4일"), ("천구백오십년 유월 이십사일", "1950년 6월 24일"),
    ("천구백오십년 칠월 이십일", "1950년 7월 20일"), ("칠월 오일 아침 일곱 시", "7월 5일 아침 7시"), ("오후 다섯 시 오십오 분", "오후 5시 55분"),
    ("유월 이십오일", "6월 25일"), ("칠월 이십이일", "7월 22일"), ("칠월 이십일", "7월 20일"), ("칠월 십구일", "7월 19일"), ("칠월 십팔일", "7월 18일"),
    ("칠월 십육일", "7월 16일"), ("칠월 십사일", "7월 14일"), ("칠월 십이일", "7월 12일"), ("칠월 십일", "7월 10일"), ("칠월 팔일", "7월 8일"),
    ("칠월 오일", "7월 5일"), ("칠월 사일", "7월 4일"), ("팔월 이십오일", "8월 25일"), ("팔월 초", "8월 초"),
    ("오전 열한 시", "오전 11시"), ("오후 두 시", "오후 2시"), ("오후 세 시", "오후 3시"), ("여섯 시 무렵", "6시 무렵"),
    ("삼천구백삼십삼 명", "3,933명"), ("천백오십 명", "1,150명"), ("만천사백 명", "1만 1,400명"), ("만오천 명", "1만 5,000명"), ("천사백 명", "1,400명"),
    ("천백 명", "1,100명"), ("백오십삼 명", "153명"), ("백오십 명", "150명"), ("팔백칠십사 명", "874명"), ("이백이십팔 명", "228명"), ("사십팔 명", "48명"),
    ("백칠 명", "107명"), ("오백 명", "500명"), ("세 명 중 한 명", "3명 중 1명"),
    ("서른다섯 대", "35대"), ("서른네 대", "34대"), ("서른세 대", "33대"), ("서른 대", "30대"), ("열다섯 대", "15대"), ("열 대", "10대"),
    ("여덟 대", "8대"), ("여섯 대", "6대"), ("두 대는", "2대는"), ("전차 세 대", "전차 3대"), ("스물두 발", "22발"),
    ("백오십오 밀리 곡사포 다섯 문", "155mm 곡사포 5문"), ("이점삼육인치 약 육 센티미터", "2.36인치 약 6cm"), ("삼점오인치 약 구 센티미터", "3.5인치 약 9cm"),
    ("이점삼육인치", "2.36인치"), ("삼점오인치", "3.5인치"), ("팔 파운드 반 약 사 킬로그램", "8.5파운드 약 4kg"), ("육십 센티미터", "60cm"),
    ("사 센티미터 반", "4.5cm"), ("백구십 파운드", "190파운드"), ("백삼십 파운드", "130파운드"), ("약 팔십육 킬로그램에서 오십구 킬로그램", "약 86kg에서 59kg"),
    ("약 일 킬로미터 반", "약 1.5km"), ("약 삼 킬로미터", "약 3km"), ("약 십 킬로미터", "약 10km"),
    ("삼십육 일", "36일"), ("십칠 일", "17일"), ("일곱 시간", "7시간"), ("이 년 전", "2년 전"), ("삼 년 동안", "3년 동안"), ("쉰 살", "50세"), ("이 층짜리", "2층짜리"),
    ("제이십일연대 일대대", "제21연대 1대대"), ("제이십일연대", "제21연대"), ("제이십사사단", "제24사단"), ("제이십오사단", "제25사단"), ("제삼십사연대", "제34연대"),
    ("제십구연대", "제19연대"), ("제일기병사단", "제1기병사단"), ("제사사단", "제4사단"), ("제삼사단", "제3사단"), ("제팔군", "제8군"),
    ("두 개 연대", "2개 연대"), ("케이 중대", "K중대"), ("엘 중대", "L중대"), ("삼팔선", "38선"), ("이차 세계 대전", "2차 세계 대전"), ("티삼십사", "T-34"),
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


def doc(head, rows, stamp="軍 秘", org="미 제24사단", note="재구성 · 내용 요약"):
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
# 좌표는 개략 (1950년 대전 시가지·비행장·서쪽 교차로·터널 구간은 현재 지형 기준 근사)
P = {
    "daejeon": [127.425, 36.33, "대전"], "station": [127.434, 36.332, "대전역"], "airfield": [127.375, 36.365, "대전 비행장"],
    "westx": [127.395, 36.343, "서쪽 교차로"], "downtown": [127.423, 36.327, "시내 중심가"], "tunnel": [127.488, 36.321, "터널 구간"],
    "okcheon": [127.571, 36.306, "옥천"], "geumsan": [127.488, 36.108, "금산"], "yeongdong": [127.783, 36.175, "영동"], "jinan": [127.425, 35.792, "진안"],
    "osan": [127.077, 37.15, "오산"], "jukmi": [127.04, 37.19, "죽미령"], "pyeongtaek": [127.09, 36.99, "평택"], "cheonan": [127.152, 36.815, "천안"],
    "jeonui": [127.2, 36.68, "전의"], "jochiwon": [127.295, 36.6, "조치원"], "gongju": [127.12, 36.465, "공주"], "daepyeong": [127.27, 36.49, "대평리"],
    "yuseong": [127.34, 36.36, "유성"], "seoul": [126.978, 37.566, "서울"], "busan": [129.04, 35.18, "부산"], "pohang": [129.365, 36.032, "포항"],
    "sangju": [128.16, 36.41, "상주"], "daegu": [128.6, 35.87, "대구"],
}
V = {
    "korea": {"center": [127.6, 36.4], "span": 4.6}, "south": {"center": [128.3, 35.95], "span": 3.4},
    "corridor": {"center": [127.25, 36.75], "span": 2.3}, "north": {"center": [127.12, 37.0], "span": 1.0}, "osan": {"center": [127.06, 37.17], "span": 0.35},
    "geum": {"center": [127.28, 36.42], "span": 0.7}, "djwide": {"center": [127.48, 36.24], "span": 0.95}, "dj": {"center": [127.42, 36.335], "span": 0.3},
    "city": {"center": [127.42, 36.335], "span": 0.14}, "east": {"center": [127.5, 36.32], "span": 0.2}, "retreat": {"center": [127.6, 36.05], "span": 1.3},
}
# 1950년 8월 낙동강 방어선 (개략 — EP28과 같은 선)
PERIM = [[128.36, 35.04], [128.38, 35.25], [128.45, 35.4], [128.42, 35.6], [128.38, 35.85], [128.42, 36.02], [128.62, 36.12], [128.95, 36.16], [129.3, 36.2], [129.42, 36.12]]
perim = {"k": "front", "path": PERIM, "at": 0}
# 금강 (개략 — 대청 → 부강 → 공주 → 부여)
GEUM = [[127.48, 36.47], [127.38, 36.5], [127.3, 36.49], [127.22, 36.475], [127.12, 36.465], [127.03, 36.4], [126.93, 36.29]]
geum = lambda at=0: {"k": "line", "path": GEUM, "color": "#00E5FF", "glow": True, "at": at}
NK_ADV = [[127.04, 37.2], [127.09, 36.99], [127.15, 36.82], [127.2, 36.68], [127.29, 36.6], [127.3, 36.5], [127.4, 36.36]]
NK_SEOUL = [[126.98, 37.56], [127.03, 37.3], [127.04, 37.2]]
NK4_CROSS = [[127.1, 36.53], [127.12, 36.46], [127.15, 36.4]]
NK3_CROSS = [[127.27, 36.55], [127.27, 36.49], [127.3, 36.44]]
NK4_FLANK = [[127.13, 36.42], [127.22, 36.33], [127.33, 36.23], [127.43, 36.2], [127.46, 36.24]]
NK4_WEST = [[127.15, 36.4], [127.28, 36.37], [127.37, 36.36]]
NK3_NORTH = [[127.3, 36.47], [127.38, 36.41], [127.42, 36.36]]
GEUMSAN_RD = [[127.425, 36.32], [127.44, 36.25], [127.47, 36.18], [127.488, 36.108]]
OKCHEON_RD = [[127.435, 36.33], [127.47, 36.325], [127.5, 36.318], [127.571, 36.306]]
YD_RD = [[127.571, 36.306], [127.66, 36.25], [127.783, 36.175]]
WANDER = [[127.47, 36.2], [127.46, 36.1], [127.45, 35.98], [127.43, 35.86], [127.425, 35.795]]
CAV = [[129.365, 36.032], [128.9, 36.0], [128.4, 36.1], [127.95, 36.15], [127.783, 36.175]]
TO_CITY = [[127.375, 36.365], [127.395, 36.345], [127.415, 36.333]]
CHASE = [[127.432, 36.336], [127.427, 36.331], [127.423, 36.327], [127.419, 36.324]]
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
line = lambda path, at=0.1, color="#ffd400", on=None: dict({"k": "line", "path": path, "color": color, "glow": True}, **({"on": on} if on else {"at": at}))
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]
SW = lambda at=0: [{"id": "whoosh", "at": at}]
FAR = lambda at=0.1: [{"id": "artillery_far", "at": at}]
PING = lambda at=0.6: [{"id": "ping", "at": at}]
WIND = lambda at=0: [{"id": "wind", "at": at}]
NKC = "nkcap"
HUD = lambda big, sub=None, sub2=None, at=0.0, color=None, count=None, on=None: dict({"big": big}, **({"sub": sub} if sub else {}), **({"sub2": sub2} if sub2 else {}),
                                                                                      **({"on": on} if on else {"at": at}), **({"color": color} if color else {}), **({"count": count} if count is not None else {}))

# ===== 콜드 오프닝 (초반 후킹 표준: 0~10초 절정 → 수치 HUD 누적 → 통념 X → 핵심 질문 카드 → 타이틀) =====
sc(1, ai("daejeon_burning"), label=DRAMA, hook={"hud": [HUD("1950. 7. 20", "대전", "불타는 시가지", count=False)]}, sfx=WIND(0.2))
sc(1, ai("dean_chase"), label=DRAMA, sfx=FAR(0.3))
sc(1, ph("walker_dean", pos="70% 30%", marks=[{"text": "딘 소장", "x": 0.68, "y": 0.2, "on": "윌리엄", "color": "yellow"}]), label=plabel("walker_dean"))
sc(1, troops(32, title="대전의 미군", labels=[{"x": 0.5, "y": 0.74, "text": "3,933명", "on": "삼천구백삼십삼", "color": "blue"}]), hook={"hud": [HUD("3,933명", "대전을 지킨 미군", "제24사단 투입 병력", on="삼천구백삼십삼")]})
sc(1, troops(32, keep=22, keepAt=0.35, title="단 이틀"), hook={"hud": [HUD("1,150명", "쓰러지거나 사라진 병력", "단 이틀 만에", color="#FF3B3B", on="천백오십")]})
sc(1, ph("dean_kill"), label=plabel("dean_kill"), hook={"hud": [HUD("10대", "새 무기로 부순 적 전차", "1950. 7. 20 하루", on="열 대")]})
sc(1, text("하루 만에 함락", "red", "1950. 7. 20 · 대전"))
sc(1, stage([C("us_salute", 0.5, 500, prop="officer+helmet", face="determined", anim="bounce")], [pop("label", 0.5, 0.15, "끝까지 남은 사단장", on="끝까지", color="yellow")]))
sc(1, m("djwide", "djwide", [line(GEUMSAN_RD, 0.1, "#ff3b3b"), mark("geumsan", "red", on="퇴각")], tilt=24), callouts=low("퇴로 · 개략"))
sc(1, ai("mountain_lost"), label=DRAMA, hook={"hud": [HUD("36일", "홀로 산속을 헤맨 시간", "그리고 포로", color="#FF3B3B", on="삼십육")]})
sc(2, black("누가 봐도", "참패"), hook={"neg": {"text": "참패", "at": 0.2, "xOn": "그랬을까요"}})
sc(1, doc("미 육군 공식 전사", ["대전 · 북한군의 큰 승리", "그러나 귀중한 시간을 벌었다"], "公刊", "애플먼 『낙동강에서 압록강까지』", "요지"))
sc(1, black(" "), hook={"question": {"text": "사단장까지 잃은 이 패배는\n어떻게 대한민국을 살렸나", "at": 0.05}})
sc(1, {"type": "titlecard", "title": "대전의 이틀", "sub": "3.5인치 바주카의 첫 일격과 딘 소장의 실종 · 1950", "at": 0, "q": pin("dean_kill")}, flash=True)
next_act()

# ===== 제1막 가장 가까이 있던 사단 =====
sc(1, flat([131.5, 34.6], 7, [fpin([130.88, 33.88], "고쿠라 (규슈)", at=0.2, flag="us", side="right")], [], [{"ll": [129.6, 33.2], "text": "대한해협", "style": "sea"}]),
   chapter={"num": "제1막", "title": "가장 가까이 있던 사단"}, callouts=top("1950. 6. 24 밤"))
sc(1, ai("masquerade"), label=DRAMA)
sc(1, stage([C("us_idle", 0.5, 500, prop="officer", face="smug", anim="tilt")], [pop("label", 0.5, 0.15, "사단장 딘 소장", on="딘 소장", color="dark")]))
sc(1, ai("dean_gat"), label=DRAMA)
sc(1, text("미군정 장관", "dark", "딘 소장 · 1947~1948"))
sc(1, doc("딘 소장 회고록", ["그날 밤 한국 옷을 입었지만", "한국 생각은 거의 하지 않았다"], "回顧", "윌리엄 딘 『딘 장군 이야기』", "요지"))
sc(1, black("한국 옷을 입고", "한국을 잊은 밤"))
sc(1, m("korea", "korea", [], tilt=10), callouts=top("몇 시간 뒤", "red"))
sc(1, m("korea", "korea", [{"k": "line", "path": [[124.6, 38.0], [126.5, 38.0], [128.6, 38.0]], "color": "#ffffff", "at": 0, "dash": True}, red_a([[126.9, 38.5], [126.98, 37.6]], 0.2), red_a([[127.8, 38.5], [127.75, 37.9]], 0.4), red_a([[128.6, 38.5], [128.9, 37.8]], 0.6)]), callouts=low("1950. 6. 25 새벽 · 38선"))
sc(1, ai("t34_column"), label=DRAMA)
sc(1, ph("t34_museum"), label=plabel("t34_museum"))
sc(1, m("korea", "korea", [red_a(NK_SEOUL[:1] + [[126.98, 37.75], [126.98, 37.6]], 0.1), mark("seoul", "red", on="서울이")]), callouts=top("사흘 만에 서울 함락", "red"))
sc(1, stage([C("us_point", 0.5, 480, prop="pipe", face="determined")], [pop("label", 0.5, 0.15, "지상군 파병", on="지상군을", color="blue")]))
sc(1, stage([C("un_shrug", 0.45, 470, prop="officer+glasses", face="worried", anim="tilt")], [pop("q", 0.75, 0.3, on="부대를")]))
sc(1, black("답은", "간단했다"))
sc(1, flat([130.0, 35.0], 8, [fpin([130.88, 33.88], "제24사단", at=0, flag="us", side="right"), fpin([127.4, 36.35], "한반도", at=0.3, flag="kr", side="left")], [route([130.88, 33.88], [129.05, 35.15], "가장 가까운 사단", on="가장", color="#2e66d8")]))
sc(1, text("미 제24보병사단", "blue", "일본 규슈 주둔"))
sc(1, black("문제는", "이 사단의 상태"))
sc(1, ai("occupation_life"), label=DRAMA)
sc(1, checklist("제24사단의 현실", [{"text": "정원 부족", "on": "정원이", "checkOn": "모자랐고", "bad": True}, {"text": "2차 대전 때 쓰던 낡은 장비", "on": "장비는", "checkOn": "낡은", "bad": True}]))
sc(1, stage([C("us_shock", 0.5, 460, prop="helmet", face="sweat", anim="shake")], [pop("label", 0.5, 0.15, "실전 경험 없음", on="한 번도", color="red")]))
sc(1, ph("tfs_station"), label=plabel("tfs_station"))
sc(1, text("스미스 특수임무부대", "yellow", "지휘관 찰스 스미스 중령"))
sc(1, troops(16, side="us", cols=6, title="약 500명", labels=[{"x": 0.5, "y": 0.74, "text": "보병 2개 중대 + 포병 일부", "at": 0.3, "color": "dark"}]))
sc(1, black("임무는", "단 하나"))
sc(1, stage([C("us_salute", 0.45, 470, prop="helmet", face="smug", flip=True)], [pop("bubble", 0.72, 0.28, "미군이 왔다!", on="미군이")]))
sc(1, stage([C("nk_idle", 0.55, 480, prop=NKC, face="smug", anim="tilt")], [pop("q", 0.25, 0.3, on="멈칫할")]))
sc(1, m("north", "osan", [LOCK("jukmi", 0.8)], flight=["corridor", "north", "osan"], flightDur=3.0, hud=True), callouts=top("1950. 7. 5 · 아침 7시"), sfx=SW(0) + PING(0.9))
sc(1, ai("jukmi_rain"), label=DRAMA, sfx=WIND(0))
sc(1, m("osan", "osan", [red_a([[127.07, 37.27], [127.05, 37.21], [127.04, 37.17]], 0.1, 1.2), swarm([[127.07, 37.27], [127.05, 37.2], [127.04, 37.15]], 0.2, 60, 0.4)], tilt=30), callouts=low("T-34 33대"))
sc(1, ai("bazooka_236"), label=DRAMA)
sc(1, text("2.36인치 바주카", "dark", "2차 대전 때의 휴대용 대전차 로켓포"))
sc(1, ai("rocket_hit"), label=DRAMA)
sc(1, black("그런데", "전차는 멈추지 않았다"))
sc(1, ai("rocket_bounce"), label=DRAMA)
sc(1, bars("같은 전차 한 대 · 병사 증언", [{"label": "쏜 로켓", "value": 22, "display": "22발", "color": "blue", "on": "스물두"}, {"label": "멈춘 전차", "value": 0.4, "display": "0대", "color": "red", "at": 0.7}]))
sc(1, stage([C("nk_shrug", 0.5, 470, prop=NKC, face="smug", flip=True)], [pop("label", 0.5, 0.15, "그대로 통과", on="지나갔습니다", color="red")]))
sc(1, ai("tfs_retreat"), label=DRAMA)
sc(1, ph("tfs_monument"), label=plabel("tfs_monument"))
sc(1, text("미군의 첫 전투", "red", "1950. 7. 5 · 오산 죽미령"))
sc(1, ai("rumor_campfire"), label=DRAMA)
sc(1, black("저 전차는", "우리 무기로 잡을 수 없다"))
next_act()

# ===== 제2막 밀리고 또 밀리다 =====
sc(1, ph("us_equip"), label=plabel("us_equip"), chapter={"num": "제2막", "title": "밀리고 또 밀리다"})
sc(1, m("corridor", "dj", [LOCK("daejeon", 0.8)], flight=["corridor", "geum", "dj"], flightDur=3.0), callouts=top("7. 4 · 대전에 사단 사령부"), sfx=SW(0) + PING(0.9))
sc(1, m("korea", "korea", [line([[126.98, 37.56], [127.15, 36.82], [127.425, 36.33], [128.6, 35.87], [129.04, 35.18]], 0.1), mark("daejeon", "blue", on="한가운데")]), callouts=low("서울 → 대전 → 부산"))
sc(1, m("corridor", "corridor", [line([[127.0, 37.2], [127.15, 36.82], [127.3, 36.55], [127.425, 36.33]], 0.1, on="경부선"), mark("daejeon", "blue", 0)]))
sc(1, m("djwide", "retreat", [line([[127.425, 36.33], [127.3, 36.1], [127.15, 35.82]], 0.3), badge("daejeon", "갈림길", "#111", 0.2, -60)]), callouts=low("호남 방면 · 개략"))
sc(1, m("retreat", "retreat", [dict(mark("daejeon", "red", 0)), dash_r([[127.425, 36.33], [127.6, 36.0], [127.9, 35.7]], 0.3)], tilt=22), callouts=top("대전을 잃으면", "red"))
sc(1, doc("작전 명령", ["지연전", "최대한 오래 버텨라"], "命令", "미 극동군 · 제24사단", "1950. 7 · 재구성"))
sc(1, text("이기라는 명령이 아니었다", "dark"))
sc(1, stage([C("us_plead", 0.5, 480, prop="officer+helmet", face="sweat")], [pop("label", 0.5, 0.15, "버텨라 · 발을 묶어라", on="발을", color="yellow")]))
sc(1, ph("boxer_f51"), label=plabel("boxer_f51"))
sc(1, black("버티는 일조차", "쉽지 않았다"))
sc(1, m("north", "north", [LOCK("cheonan", 0.3)], tilt=26), callouts=top("1950. 7. 8 · 천안"), sfx=PING(0.4))
sc(1, stage([C("us_shock", 0.4, 460, prop="helmet+glasses", face="coldsweat", flip=True)], [pop("label", 0.5, 0.15, "제34연대장 마틴 대령", on="마틴", color="dark")]))
sc(1, ai("martin_bazooka"), label=DRAMA)
sc(1, ai("martin_tank"), label=DRAMA)
sc(1, black("전차의 포탄이", "먼저 날아왔다"))
sc(1, text("마틴 대령 전사", "red", "1950. 7. 8 · 천안 시가지"))
sc(1, m("north", "north", [mark("cheonan", "red", 0), red_a([[127.12, 36.95], [127.15, 36.82], [127.18, 36.72]], 0.2)], tilt=24))
sc(1, m("corridor", "corridor", [unit("jochiwon", "제21연대", "blue", 0.1), mark("jeonui", "blue", 0.3), clash([127.25, 36.64], 0.5)]), callouts=low("전의 · 조치원 · 사흘"))
sc(1, bars("제21연대 · 오산부터 조치원까지", [{"label": "잃은 병력", "value": 1400, "display": "1,400명+", "color": "red", "on": "천사백"}]))
sc(1, bars("제21연대 · 남은 병사", [{"label": "남은 병사", "value": 1100, "display": "1,100명 남짓", "color": "blue", "on": "천백"}]))
sc(1, m("corridor", "geum", [geum(0.2), blue_a([[127.29, 36.6], [127.3, 36.52], [127.32, 36.45]], 0.3)], flight=["corridor", "geum"], flightDur=2.4), callouts=top("7. 12 · 금강 남쪽으로"), sfx=SW(0))
sc(1, m("geum", "geum", [geum(0), badge([127.3, 36.49], "금강", "#2e66d8", 0.3, -40)], tilt=24))
sc(1, ai("bridge_blow"), label=DRAMA)
sc(1, m("geum", "geum", [dict(geum(0)), badge("daejeon", "대전", "#111", 0.4, -50)], tilt=28), callouts=low("대전의 마지막 방패"))
sc(1, black("북한군은", "예상 못 한 방법으로"))
sc(1, m("geum", "geum", [geum(0), red_a(NK4_CROSS, 0.2), unit([127.06, 36.55], "북한군 제4사단", at=0.4)], tilt=26), callouts=top("7. 14 · 공주 방면", "red"))
sc(1, ai("geum_rafts"), label=DRAMA)
sc(1, ai("artillery_rifles"), label=DRAMA)
sc(1, m("geum", "geum", [geum(0), unit("daepyeong", "제19연대", "blue", 0.1)], tilt=26), callouts=top("7. 16 · 대평리"))
sc(1, m("geum", "geum", [geum(0), unit("daepyeong", "제19연대", "blue", 0), red_a(NK3_CROSS, 0.2), red_a([[127.2, 36.53], [127.22, 36.48], [127.25, 36.45]], 0.5)], tilt=28), callouts=low("북한군 제3사단 · 정면과 옆구리"))
sc(1, stage([C("us_idle", 0.5, 470, prop="officer+helmet", face="tears", anim="shake")], [pop("label", 0.5, 0.15, "제19연대장 멜로이 대령 부상", on="멜로이", color="red")]))
sc(1, m("geum", "geum", [geum(0), clash("daepyeong", 0.1), red_a([[127.3, 36.47], [127.32, 36.42]], 0.4)], tilt=28))
sc(1, text("금강의 사흘", "red", "쓰러진 미군 수백 명"))
sc(1, m("geum", "dj", [geum(0), unit([127.3, 36.43], "북한군", at=0.2, pulse=True), mark("daejeon", "blue", 0)], flight=["geum", "dj"], flightDur=2.4))
sc(1, troops(30, side="us", cols=8, title="한국에 들어올 때", labels=[{"x": 0.5, "y": 0.74, "text": "1만 5,000명+", "on": "만오천", "color": "blue"}]))
sc(1, troops(30, keep=23, keepAt=0.3, title="대전 앞에서", labels=[{"x": 0.5, "y": 0.74, "text": "1만 1,400명", "on": "만천사백", "color": "red"}]))
sc(1, ai("exhausted_gi"), label=DRAMA)
sc(1, stage([C("us_plead", 0.4, 470, prop="officer", face="worried", anim="tilt", flip=True)], [pop("q", 0.72, 0.3, at=0.3)]))
sc(1, black("병사들에게 필요한 것", "단 하나"))
sc(1, text("전차도 부서진다", "yellow", "눈으로 보여 줘야 한다"))
next_act()

# ===== 제3막 상자 속의 새 무기 =====
MID = [nid()]
sc(1, black("그 답은", "이미 대전에 와 있었다"), pauseBefore=0.5, chapter={"num": "제3막", "title": "상자 속의 새 무기"})
sc(1, ai("travis_c54"), label=DRAMA, callouts=top("1950. 7. 8 · 미국 캘리포니아"))
sc(1, ai("long_crates"), label=DRAMA)
sc(1, text("3.5인치 로켓포", "yellow", "M20 로켓 발사기"))
sc(1, text("슈퍼 바주카", "blue"))
sc(1, m("dj", "dj", [plane([[127.2, 36.45], [127.3, 36.4], [127.375, 36.365]], 0.1, 1, 3.0), mark("airfield", "blue", 0.8)], tilt=26), callouts=low("7. 10 · 대전 비행장"))
sc(1, ai("bazooka_training"), label=DRAMA, callouts=top("7. 12부터 사격 교육"))
sc(1, cmp("옛 바주카", "2.36인치", "슈퍼 바주카", "3.5인치", "dark", "blue"))
sc(1, bars("로켓 지름", [{"label": "옛 바주카", "value": 6, "display": "약 6cm", "color": "dark", "on": "이점삼육인치"}]))
sc(1, bars("로켓 지름", [{"label": "옛 바주카", "value": 6, "display": "약 6cm", "color": "dark", "at": 0}, {"label": "슈퍼 바주카", "value": 9, "display": "약 9cm", "color": "blue", "on": "삼점오인치"}]))
sc(1, text("로켓 무게 약 4kg", "dark", "8.5파운드"))
sc(1, ai("shaped_charge"), label=DRAMA, callouts=low("성형 작약 · 개념도"))
sc(1, text("녹은 금속 줄기", "red", "송곳처럼 장갑을 뚫는다"))
sc(1, text("당시 어떤 전차든", "blue", "뚫을 수 있다는 무기"))
sc(1, ph("t34_knocked"), label=plabel("t34_knocked"), callouts=top("T-34 앞면 장갑 4.5cm"))
sc(1, text("경사 장갑", "dark", "비스듬히 눕혀 실제로는 훨씬 두꺼운 벽"))
sc(1, text("미끄러지거나 튕겨 나간다", "red", "옛 바주카 로켓 vs 경사 장갑"))
sc(1, black("문제는", "수량"))
sc(1, checklist("슈퍼 바주카의 약점", [{"text": "처음엔 몇 정뿐", "on": "몇 정에", "checkOn": "불과했고", "bad": True}, {"text": "넉넉하지 않은 탄약", "on": "탄약도", "checkOn": "않았습니다", "bad": True}]))
sc(1, checklist("슈퍼 바주카의 약점", [{"text": "처음엔 몇 정뿐", "at": 0, "checkAt": 0, "bad": True}, {"text": "넉넉하지 않은 탄약", "at": 0, "checkAt": 0, "bad": True}, {"text": "실전 경험 0회", "on": "실전에서", "checkOn": "없는", "bad": True}]))
sc(1, stage([C("us_shrug", 0.5, 470, prop="helmet+notebook", face="worried", flip=True)], [pop("q", 0.75, 0.28, at=0.2), pop("label", 0.5, 0.15, "정말 T-34를?", on="장담하지", color="dark")]))
sc(1, black("1950년 7월 18일", "오전"))
sc(1, m("south", "dj", [plane([[128.6, 35.87], [128.0, 36.1], [127.42, 36.33]], 0.1, 1, 2.6), LOCK("daejeon", 0.9)], flight=["south", "dj"], flightDur=2.6), callouts=top("미 제8군 사령관 워커 중장"), sfx=SW(0))
sc(1, ph("walker_dean"), label=plabel("walker_dean"))
sc(1, black("워커의", "무거운 이야기"))
sc(1, m("south", "south", [blue_a(CAV[:3], 0.2), mark("pohang", "blue", on="포항에"), badge("pohang", "제1기병사단 상륙", "#2e66d8", 0.4, -60)]), callouts=low("1950. 7. 18"))
sc(1, m("retreat", "retreat", [mark("yeongdong", "blue", 0.1), line(YD_RD, 0.3, "#7fd3ff"), badge("yeongdong", "영동", "#2e66d8", 0.2, -50)], tilt=22), callouts=top("자리 잡을 시간이 필요하다"))
sc(1, stage([C("us_point", 0.45, 490, prop="officer+helmet", face="determined", anim="bounce")], [pop("bubble", 0.75, 0.28, "이틀만 더!", on="이틀쯤")]))
sc(1, doc("워커 중장의 말 (요지)", ["대전을 이틀쯤 더 지켜 달라", "나빠지면 철수 · 책임은 내가"], "口頭", "미 제8군 사령관", "1950. 7. 18 · 재구성"))
sc(1, text("원래 계획 · 7월 19일 철수", "dark"))
sc(1, black("딘은", "하루를 미룬다"))
sc(1, text("철수 → 7월 20일", "yellow"))
sc(1, black("그리고", "또 하나의 결정"))
sc(1, m("retreat", "dj", [blue_a([[127.425, 36.33], [127.6, 36.27], [127.783, 36.175]], 0.1), badge("daejeon", "딘 소장은 잔류", "#c9242c", 0.6, -60)], flight=["retreat", "dj"], flightDur=2.4), callouts=low("사단 사령부 → 영동"))
sc(1, ai("dean_stays"), label=DRAMA)
sc(1, cmp("병사들에게", "큰 힘", "훗날", "두고두고 논란", "blue", "red"))
sc(1, stage([C("us_idle", 0.5, 470, prop="glasses+notebook", face="worried", flip=True)], [pop("label", 0.5, 0.15, "사단 전체는 누가 보나?", on="묶여", color="red")]), hudCta={"at": 0, "dur": 7.0})
next_act()

# ===== 제4막 칠월 이십일 새벽 =====
sc(1, m("geum", "dj", [red_a(NK4_WEST, 0.3), red_a(NK3_NORTH, 0.5)], flight=["geum", "dj"], flightDur=2.6), chapter={"num": "제4막", "title": "7월 20일 새벽"}, callouts=top("1950. 7. 19 · 공격 개시", "red"), sfx=SW(0))
sc(1, m("dj", "dj", [red_a(NK4_WEST, 0.1), unit([127.3, 36.37], "제4사단", at=0.2), red_a(NK3_NORTH, 0.4), unit([127.38, 36.42], "제3사단", at=0.5)], tilt=24))
sc(1, m("dj", "dj", [unit([127.3, 36.37], "전차 연대", at=0.1), unit([127.38, 36.42], "전차 연대", at=0.4)], tilt=26), callouts=low("사단마다 전차 연대 하나씩"))
sc(1, m("dj", "dj", [mark("airfield", "blue", 0), shock([[127.37, 36.37], [127.38, 36.36], [127.365, 36.355]], 0.2)], tilt=30), callouts=top("제34연대 · 비행장 앞"), sfx=FAR(0.2))
sc(1, black("진짜 위험은", "정면이 아니었다"))
sc(1, m("djwide", "djwide", [swarm(NK4_FLANK, 0.1, 160), red_a(NK4_FLANK, 0.3)], tilt=24), callouts=low("제4사단 2개 연대 · 산길 우회 · 개략"))
sc(1, m("djwide", "djwide", [line(GEUMSAN_RD, 0.1), LOCK("geumsan", 0.5)], tilt=24), callouts=top("노린 곳 · 금산 길", "red"), sfx=PING(0.6))
sc(1, m("djwide", "djwide", [line(GEUMSAN_RD, 0), {"k": "front", "path": [[127.41, 36.22], [127.45, 36.235], [127.49, 36.25]], "at": 0.3, "glow": True}, badge([127.45, 36.235], "차단선", "#c9242c", 0.6, -50)], tilt=26), callouts=low("7. 19 밤"))
sc(1, black("대전의 뒷문이", "조용히 닫히고 있었다"))
sc(1, stage([C("us_shrug", 0.5, 470, prop="helmet", face="smug", anim="tilt")], [pop("label", 0.5, 0.15, "아무것도 모른다", on="거의", color="dark")]))
sc(1, ai("radio_dead"), label=DRAMA)
sc(1, text("끊어진 전화선", "red", "북한군 침투조"))
sc(1, ai("refugee_column"), label=DRAMA)
sc(1, ai("white_clothes"), label=DRAMA, callouts=low("증언 · 흰옷 차림의 침투"))
sc(1, stage([C("us_point", 0.35, 450, prop="helmet+glasses", face="coldsweat", anim="shake"), C("kr_idle", 0.72, 400, flip=True, face="worried")], [pop("q", 0.53, 0.25, on="누가")]))
sc(1, black("1950년 7월 20일", "동이 트기 전"))
sc(1, m("dj", "city", [red_a(TO_CITY, 0.3)], flight=["dj", "city"], flightDur=2.6, hud=True), sfx=SW(0))
sc(1, m("city", "city", [LOCK("westx", 0.3)], tilt=32, hud=True), callouts=top("대전 서쪽 교차로 · 위치 개략"), sfx=PING(0.4))
sc(1, ai("first_aim"), label=DRAMA)
sc(1, ai("first_fire"), label=DRAMA)
sc(1, black("이번에는", "튕겨 나가지 않았다"))
sc(1, ai("first_kill"), label=DRAMA)
sc(1, text("불길", "red"))
sc(1, text("3.5인치 로켓포 첫 T-34 격파", "yellow", "1950. 7. 20 새벽 · 대전"))
sc(1, stage([C("us_salute", 0.35, 450, prop="helmet", face="sparkle", anim="bounce"), C("kr_point", 0.72, 410, flip=True, face="sparkle", prop="helmet")], [pop("ex", 0.53, 0.25, on="빠르게")]))
sc(1, black("전차도", "부서진다"))
sc(1, text("공포에 금이 가다", "blue", "보름 만의 첫 승전보"))
sc(1, m("city", "city", [mark("airfield", "blue", 0), swarm([[127.33, 36.38], [127.36, 36.37], [127.375, 36.365]], 0.1, 140)], tilt=30), sfx=FAR(0.2))
sc(1, m("city", "city", [unit("airfield", "K중대", "blue", 0.1, True), red_a([[127.35, 36.385], [127.37, 36.37]], 0.3), red_a([[127.36, 36.35], [127.372, 36.36]], 0.5)], tilt=32))
sc(1, ai("darr_cover"), label=DRAMA, callouts=top("로버트 데어 중사"))
sc(1, text("데어 중사 전사", "red", "소대가 빠져나갈 때까지"))
sc(1, m("city", "city", [red_a(TO_CITY, 0.1), mark("downtown", "red", on="시내까지")], tilt=32))
sc(1, ai("tank_street"), label=DRAMA)
next_act()

# ===== 제5막 사단장의 전차 사냥 =====
MID.append(nid())
sc(1, m("city", "city", [LOCK("downtown", 0.4, "제34연대 지휘소")], tilt=30, hud=True), pauseBefore=0.5, chapter={"num": "제5막", "title": "사단장의 전차 사냥"})
sc(1, stage([C("us_shrug", 0.5, 480, prop="officer+helmet", face="sweat", anim="tilt")], [pop("q", 0.76, 0.3, at=0.2)]))
sc(1, checklist("끊어진 눈과 귀", [{"text": "무전", "on": "무전은", "checkOn": "끊겼고", "bad": True}, {"text": "전령", "on": "전령은", "checkOn": "돌아오지", "bad": True}]))
sc(1, black("가장 단순한", "방법"))
sc(1, text("직접 보고 직접 싸운다", "yellow"))
sc(1, ai("dean_out"), label=DRAMA, callouts=top("50세 · 딘 소장과 부관 클라크 중위"))
sc(1, ai("dean_hunt"), label=DRAMA)
sc(1, bars("오전 11시까지 · 북한군 전차 격파", [{"label": "격파", "value": 8, "display": "8대", "color": "blue", "on": "여덟"}]))
sc(1, bars("오전 11시까지 · 누가 잡았나", [{"label": "슈퍼 바주카", "value": 6, "display": "6대", "color": "blue", "on": "여섯"}, {"label": "포병", "value": 2, "display": "2대", "color": "dark", "on": "두 대는"}]))
sc(1, black("그런데도", "전차는 계속 들어왔다"))
sc(1, m("city", "city", [LOCK("downtown", 0.3, "전차 1대", "#c9242c")], tilt=32, hud=True), callouts=top("오후 · 시내 중심가"), sfx=PING(0.4))
sc(1, m("city", "city", [red_a(CHASE, 0.1, 0.7), blue_a([[127.436, 36.338], [127.43, 36.333], [127.425, 36.329]], 0.4, 0.6)], tilt=34))
sc(1, ai("alley_chase"), label=DRAMA)
sc(1, text("1시간 넘는 추격", "yellow"))
sc(1, ai("tank_stops"), label=DRAMA)
sc(1, text("2층 상가 건물", "yellow", "창문 아래로 전차가 보이는 자리"))
sc(1, ai("backblast"), label=DRAMA, callouts=top("후폭풍 · 뒤를 비워야 한다"))
sc(1, text("창가에 자리를", "yellow", "등 뒤를 비운 채"))
sc(1, ai("window_view"), label=DRAMA)
sc(1, black("오후 2시", "무렵"))
sc(1, ai("window_shot"), label=DRAMA)
sc(1, text("두 번째 · 세 번째", "red"))
sc(1, ai("tank_burning"), label=DRAMA)
sc(1, black("딘은 나중에", "짧게 말했다"))
sc(1, doc("딘 소장", ["내가 전차 한 대 잡았지"], "1950", "딘 소장의 말", "전해지는 말 · 요지"))
sc(1, bars("1950. 7. 20 · 대전에서 부서진 북한군 전차", [{"label": "모두", "value": 10, "display": "10대", "color": "red", "on": "열 대"}]))
sc(1, bars("그중", [{"label": "모두", "value": 10, "display": "10대", "color": "red", "at": 0}, {"label": "3.5인치 로켓포", "value": 8, "display": "8대", "color": "blue", "on": "여덟"}]))
sc(1, text("적어도 15대", "yellow", "공중 공격 포함 · 미 육군 공간사 기준"))
sc(1, cmp("오산", "22발에도 통과", "대전", "3.5인치로 격파", "red", "blue"))
sc(1, black("전차를 잡아도", "도시는 지킬 수 없었다"))
sc(1, m("dj", "dj", [swarm(NK4_FLANK[2:], 0.1, 100), swarm(NK3_NORTH, 0.2, 100), mark("daejeon", "blue", 0)], tilt=26), callouts=low("거의 포위된 대전"))
sc(1, m("city", "city", [swarm([[127.4, 36.37], [127.415, 36.345], [127.423, 36.33]], 0.1, 120)], tilt=32), callouts=top("제3사단 · 시내로 스며들다", "red"))
sc(1, ai("sniper_city"), label=DRAMA)
sc(1, black("오후 3시 무렵", "또 하나의 비보"))
sc(1, stage([C("us_shock", 0.5, 470, prop="officer+helmet", face="shock", anim="shake", flip=True)], [pop("label", 0.5, 0.15, "제34연대장 뷰챔프 대령 연락 두절", on="뷰챔프", color="red")]))
sc(1, black("지휘관을 잃은 연대", "흔들리다"))
sc(1, black("오후 5시 55분"))
sc(1, ai("watch_check"), label=DRAMA)
sc(1, text("약속한 시간은 지켰다", "blue", "워커와의 약속"))
sc(1, m("city", "east", [blue_a(OKCHEON_RD, 0.2)], flight=["city", "east"], flightDur=2.4), callouts=top("오후 6시 무렵 · 철수 시작"), sfx=SW(0))
sc(1, black("그때는 이미", "늦어 있었다"))
next_act()

# ===== 제6막 불타는 퇴로 =====
sc(1, m("djwide", "djwide", [line(OKCHEON_RD, 0.2), line(GEUMSAN_RD, 0.4)], tilt=24), chapter={"num": "제6막", "title": "불타는 퇴로"}, callouts=top("빠져나갈 길은 두 갈래"))
sc(1, m("djwide", "djwide", [line(OKCHEON_RD, 0), line(GEUMSAN_RD, 0), badge("okcheon", "옥천", "#2e66d8", on="옥천으로", dy=-50), badge("geumsan", "금산", "#2e66d8", on="금산으로", dy=-50)], tilt=24))
sc(1, m("djwide", "djwide", [line(OKCHEON_RD, 0), line(GEUMSAN_RD, 0, "#ff3b3b"), {"k": "front", "path": [[127.41, 36.22], [127.45, 36.235], [127.49, 36.25]], "at": 0, "glow": True}], tilt=24), callouts=low("금산 길 · 전날 밤부터 차단", "red"))
sc(1, m("djwide", "djwide", [line(OKCHEON_RD, 0.1), mark("okcheon", "blue", 0.3)], tilt=24), callouts=top("남은 길 · 옥천 길 하나"))
sc(1, ai("convoy_out"), label=DRAMA)
sc(1, m("east", "east", [line(OKCHEON_RD, 0), LOCK("tunnel", 0.4, "대전 동쪽 약 3km")], tilt=32, hud=True), sfx=PING(0.5))
sc(1, m("east", "east", [line(OKCHEON_RD, 0), {"k": "front", "path": [[127.475, 36.323], [127.488, 36.321], [127.5, 36.318]], "at": 0.2, "glow": True}], tilt=32), callouts=low("철도 터널 · 도로 터널 · 약 1.5km 구간"))
sc(1, black("기다리고 있던 것은", "매복"))
sc(1, m("east", "east", [shock([[127.48, 36.326], [127.49, 36.317], [127.497, 36.325]], 0.1, 0.6), mark([127.485, 36.33], "red", 0.3), mark([127.495, 36.313], "red", 0.4)], tilt=34), sfx=FAR(0.1))
sc(1, ai("ambush_tunnel"), label=DRAMA)
sc(1, black("병사들은", "도랑으로 몸을 던졌다"))
sc(1, text("조지 리비 중사", "dark", "공병대"))
sc(1, ai("libby_truck"), label=DRAMA)
sc(1, text("총에 맞으면서도", "red", "멈추지 않았다"))
sc(1, black("리비 중사", "그날 밤 숨지다"))
sc(1, text("명예훈장 추서", "yellow", "조지 리비 중사"))
sc(1, m("djwide", "djwide", [line(OKCHEON_RD, 0), red_a(GEUMSAN_RD[:3], 0.2, 0.7), badge([127.44, 36.3], "길목을 놓치다", "#c9242c", 0.4, -50)], tilt=26), callouts=low("딘 소장의 지프 · 경로 개략"))
sc(1, m("djwide", "djwide", [line(GEUMSAN_RD, 0, "#ff3b3b"), mark([127.455, 36.24], "red", 0.2, "막힌 길")], tilt=26))
sc(1, m("djwide", "djwide", [line(GEUMSAN_RD, 0, "#ff3b3b"), shock([[127.44, 36.27], [127.45, 36.24], [127.46, 36.255]], 0.1, 0.6)], tilt=26), sfx=FAR(0.1))
sc(1, ai("jeep_abandon"), label=DRAMA)
sc(1, text("부상병 몇 명과 함께", "dark"))
sc(1, ai("night_mountain"), label=DRAMA, sfx=WIND(0))
sc(1, text("목이 마르다", "dark", "부상병의 신음"))
sc(1, ai("dean_water"), label=DRAMA)
sc(1, black("그 순간", "발을 헛디뎠다"))
sc(1, ai("dean_fall"), label=DRAMA)
sc(1, black("깨어났을 때", "혼자였다"))
sc(1, checklist("딘 소장의 부상", [{"text": "머리가 찢어짐", "on": "머리가", "checkOn": "찢어졌고", "bad": True}, {"text": "어깨뼈 골절", "on": "어깨뼈가", "checkOn": "부러져", "bad": True}]))
sc(1, text("부관 클라크 중위", "dark", "날이 밝기 전 남은 병사들과 하산"))
sc(1, m("retreat", "retreat", [blue_a([[127.47, 36.22], [127.62, 36.2], [127.783, 36.175]], 0.2), mark("yeongdong", "blue", on="영동의")], tilt=22), callouts=top("사흘 뒤 · 제1기병사단 진지"))
sc(1, black("사단장은", "그 안에 없었다"))
sc(1, m("retreat", "retreat", [{"k": "arrow", "path": WANDER[:3], "color": "blue", "dash": True, "at": 0.2, "width": 0.7}], tilt=22), callouts=low("딘 소장의 길 · 개략"))
sc(1, ai("hide_forest"), label=DRAMA)
sc(1, checklist("홀로 남은 사단장", [{"text": "먹을 것 없음", "on": "먹을", "checkOn": "거의", "bad": True}, {"text": "치료 못 받은 어깨", "on": "어깨는", "checkOn": "못했습니다", "bad": True}]))
sc(1, ai("farmer_rice"), label=DRAMA)
sc(1, text("36일", "yellow", "1950. 7. 20 ~ 8. 25"))
sc(1, bars("딘 소장의 몸무게", [{"label": "전쟁 전", "value": 190, "display": "190파운드", "color": "blue", "at": 0.1}, {"label": "36일 뒤", "value": 130, "display": "130파운드", "color": "red", "on": "백삼십"}]))
sc(1, bars("딘 소장의 몸무게 (킬로그램)", [{"label": "전쟁 전", "value": 86, "display": "약 86kg", "color": "blue", "at": 0}, {"label": "36일 뒤", "value": 59, "display": "약 59kg", "color": "red", "on": "오십구"}]))
sc(1, doc("딘 소장 회고", ["팔다리가 막대기 같았다"], "回顧", "윌리엄 딘 『딘 장군 이야기』", "요지"))
sc(1, m("retreat", "retreat", [{"k": "arrow", "path": WANDER, "color": "blue", "dash": True, "at": 0, "width": 0.7}, LOCK("jinan", 0.4, "진안 근처")], tilt=22), callouts=top("1950. 8. 25 · 전라북도 진안 근처"), sfx=PING(0.5))
sc(1, ai("betrayal"), label=DRAMA)
sc(1, ai("capture_struggle"), label=DRAMA)
sc(1, text("가장 계급이 높은 포로", "red", "한국전쟁 미군 포로 가운데"))
sc(1, black("윌리엄 딘", "북한의 포로가 되다"))
sc(1, black("살아 있는지조차", "알 수 없었다"))
sc(1, black("1951년 1월 9일", "백악관"))
sc(1, doc("명예훈장 공적서 (요지)", ["윌리엄 F. 딘 소장", "1950. 7. 20~21 대전", "전차 공격을 직접 지휘"], "名譽", "미국 대통령", "1951. 1. 9 수여 · 요지"))
sc(1, text("명예훈장", "yellow", "미군 최고의 무공 훈장"))
sc(1, text("실종자 명단", "dark", "훈장의 주인은 행방불명"))
next_act()

# ===== 제7막 패배가 번 시간 =====
MID.append(nid())
sc(1, ai("daejeon_night_fall"), label=DRAMA, pauseBefore=0.5, chapter={"num": "제7막", "title": "패배가 번 시간"})
sc(1, black("숫자로", "정리해 보면"))
sc(1, troops(32, title="대전 전투 투입", labels=[{"x": 0.5, "y": 0.74, "text": "3,933명", "on": "삼천구백삼십삼", "color": "blue"}]))
sc(1, troops(32, keep=23, keepAt=0.3, title="피해", labels=[{"x": 0.5, "y": 0.74, "text": "1,150명", "on": "천백오십", "color": "red"}]))
sc(1, bars("제24사단 · 대전 전투 피해 (미 육군 공간사 기준)", [{"label": "전사", "value": 48, "display": "48명", "color": "red", "on": "사십팔"}, {"label": "부상", "value": 228, "display": "228명", "color": "dark", "on": "이백이십팔"}]))
sc(1, bars("제24사단 · 대전 전투 피해 (미 육군 공간사 기준)", [{"label": "전사", "value": 48, "display": "48명", "color": "red", "at": 0}, {"label": "부상", "value": 228, "display": "228명", "color": "dark", "at": 0}, {"label": "실종", "value": 874, "display": "874명", "color": "red", "on": "팔백칠십사"}]))
sc(1, text("끝내 돌아오지 못한 실종자", "dark"))
sc(1, text("3명 중 1명", "red"))
sc(1, troops(30, keep=9, keepAt=0.4, cols=6, title="제34연대 L중대", labels=[{"x": 0.5, "y": 0.74, "text": "153명 중 107명 손실", "on": "백칠", "color": "red"}]))
sc(1, black("장비 손실은", "더 참담했다"))
sc(1, text("빠져나온 차량 35대 남짓", "dark", "제34연대"))
sc(1, checklist("잃어버린 장비", [{"text": "보급 중대 트럭 34대 중 30대", "on": "보급", "checkOn": "서른 대를", "bad": True}, {"text": "155mm 곡사포 5문 전부", "on": "곡사포", "checkOn": "모두", "bad": True}]))
sc(1, black("사단장까지", "사라졌다"))
sc(1, text("누가 봐도 참패", "red"))
sc(1, black("이제", "처음의 질문으로"))
sc(1, black(" "), hook={"question": {"text": "사단장까지 잃은 이 패배는\n어떻게 대한민국을 살렸나", "at": 0.05, "kicker": "■ 처음의 질문 ■"}})
sc(1, text("답은 날짜 속에", "yellow"))
sc(1, m("corridor", "corridor", [red_a(NK_ADV, 0.2), mark("osan", "blue", on="오산에서")]), callouts=top("1950. 7. 5 · 지연전 시작"))
sc(1, m("corridor", "corridor", [red_a(NK_ADV, 0), mark("daejeon", "red", on="칠월 이십일")]), callouts=low("1950. 7. 20 · 대전 함락"))
sc(1, bars("북한군 하루 진격 거리 (평균)", [{"label": "오산→대전 17일", "value": 10, "display": "약 10km", "color": "blue", "on": "십 킬로미터"}]))
sc(1, cmp("6월 · 서울까지", "사흘", "7월 · 오산→대전", "17일", "red", "blue"))
sc(1, text("워커가 부탁한 이틀", "yellow"))
sc(1, m("south", "south", [blue_a(CAV, 0.2, 1.1), mark("yeongdong", "blue", on="영동까지")]), callouts=top("제1기병사단 · 포항 → 영동"))
sc(1, ph("cav_withdraw"), label=plabel("cav_withdraw"), callouts=top("7. 22 · 영동 진지 인계"))
sc(1, ph("lst_25th"), label=plabel("lst_25th"))
sc(1, m("south", "south", [dict(perim, glow=True)], tilt=22), callouts=top("1950. 8월 초 · 마지막 방어선"))
sc(1, text("낙동강 방어선", "blue"))
sc(1, stage([C("us_plead", 0.4, 470, prop="helmet", face="worried", anim="tilt", flip=True)], [pop("q", 0.73, 0.3, at=0.2)], title="대전이 일주일 일찍 무너졌다면?"))
sc(1, m("south", "south", [dash_r([[127.425, 36.33], [128.0, 35.9], [128.6, 35.5], [129.04, 35.18]], 0.2), shock([[128.6, 35.5], [129.04, 35.18]], 0.6, 0.8)]), callouts=low("가정 · 자리 잡기 전에 쏟아져 내려오는 적", "red"))
sc(1, doc("미 육군 공식 전사 (요지)", ["대전 전투 · 북한군의 큰 승리"], "公刊", "애플먼 『낙동강에서 압록강까지』", "요지"))
sc(1, doc("미 육군 공식 전사 (요지)", ["대전 전투 · 북한군의 큰 승리", "딘 소장이 번 시간으로", "제8군은 증원군을 불러왔다"], "公刊", "애플먼 『낙동강에서 압록강까지』", "요지"))
sc(1, cmp("전술", "패배", "전략", "승리", "red", "blue"))
sc(1, text("대전 전투", "yellow", "전술에서 지고 전략에서 이긴 싸움"))
sc(1, black("대전이 남긴", "또 하나"))
sc(1, ai("superbazooka_flow"), label=DRAMA)
sc(1, m("retreat", "retreat", [mark("yeongdong", "blue", 0.1), clash("yeongdong", 0.4, 0.8)], tilt=24), callouts=top("사흘 뒤 · 영동 · 전차 3대 격파"))
sc(1, ph("rok_july"), label=plabel("rok_july"))
sc(1, ph("t34_knocked"), label=plabel("t34_knocked"))
sc(1, ph("dean_kill"), label=plabel("dean_kill"))
sc(1, ph("big_switch"), label=plabel("big_switch"), callouts=top("1953. 9. 4 · 판문점"))
sc(1, ai("dean_return"), label=DRAMA)
sc(1, text("명예훈장", "yellow", "3년 만에 안 사실"))
SOMBER = nid()
sc(1, black("그런데 딘은", "오히려"))
sc(1, doc("딘 소장 (요지)", ["나는 군사 재판에 설 줄 알았다"], "回顧", "타임 「The Dean Story」 1953", "요지"))
sc(1, doc("딘 소장 (요지)", ["나는 군사 재판에 설 줄 알았다", "나의 영웅담은 크게 부풀려졌다"], "回顧", "타임 「The Dean Story」 1953", "요지"))
sc(1, cmp("비판", "병사처럼 싸운 장군", "그는", "피하지 않았다", "red", "dark"))
sc(1, black("하지만 병사들은", "다르게 기억한다"))
sc(1, ai("dean_beside"), label=DRAMA)
sc(1, ai("memorial_daejeon"), label=DRAMA, callouts=top("해마다 7월 · 대전 전투 추모식"))
sc(1, text("함께 선 두 나라의 군인", "blue", "한국 · 미국"))
sc(1, text("대전의 이틀", "red", "사단장을 잃고 도시를 내준"))
sc(1, ph("naktong_24th"), label=plabel("naktong_24th"), callouts=top("낙동강 방어선의 첫 벽돌", "blue"))
sc(2, {"type": "endcard", "title": "대전의 거리에서 시간을 번\n모든 이들을 기억하며", "q": pin("dean_kill")}, tail=1.0)
assert CUR["i"] == len(ACTS[7]), (CUR, len(ACTS[7]))

# ===== 재연 일러스트 (Gemini · 새 그림 + 재사용) =====
CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
US = "American soldiers whose heads are round balls painted as the United States flag (stars and stripes), wearing 1950 M1 steel helmets and olive drab summer uniforms"
US1 = "an American soldier whose head is a round ball painted as the United States flag (stars and stripes), wearing a 1950 M1 steel helmet and an olive drab summer uniform"
DEAN = ("an American two-star general whose head is a round ball painted as the United States flag (stars and stripes), wearing an M1 steel helmet with two small silver stars, "
        "an olive drab summer field uniform, carrying an M1 Garand rifle")
NK = "North Korean soldiers whose heads are round balls painted as the North Korean flag (blue, red and white stripes with a red star in a white circle), wearing 1950 khaki uniforms and soft field caps"
T34 = "a Soviet-made T-34/85 tank with a red star painted on its turret"
TOWN = "the streets of a small 1950 Korean provincial city with two-story brick and wooden shop buildings, tiled roofs and power poles"
END = ", July 1950 summer, leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic, desaturated palette, film grain, no text, no letters."
AI = {
    "daejeon_burning": CB + TOWN + " burning at dawn, " + T34 + " rolling through thick smoke between the buildings, a small group of " + US + " crouching behind a wall with a bazooka" + END,
    "dean_chase": CB + DEAN + " leading a small bazooka team of " + US + " running through a burning street after " + T34 + " disappearing around a corner" + END,
    "mountain_lost": "A lone exhausted figure in a torn olive drab uniform hiding among dark pine trees on a steep Korean mountainside at night, moonlight, mist in the valley below, lonely and desperate, " + LAND,
    "masquerade": CB + "American officers whose heads are round balls painted as the United States flag at a 1950 officers' club masquerade costume party in Kokura, Japan, wearing silly costumes, paper lanterns, a small band, drinks, festive mood at night" + END,
    "dean_gat": CB + "an American general whose head is a round ball painted as the United States flag, wearing a traditional Korean black horsehair gat hat that is too small for him and a white Korean dopo robe, at a costume party, other guests laughing" + END,
    "occupation_life": CB + "young " + US + " in a 1950 occupation barracks in Japan, playing cards and polishing shoes, old worn World War II rifles and a rusty jeep, relaxed and untrained" + END,
    "jukmi_rain": CB + US + " in rain ponchos dug into foxholes on a muddy rain-soaked ridge above a road at dawn, staring down at a column of tanks coming out of the mist, rain falling" + END,
    "bazooka_236": CB + "two " + US + " aiming an old slim 2.36-inch bazooka from a muddy roadside ditch in the rain at an approaching tank" + END,
    "rocket_hit": "A bazooka rocket striking the sloped front armor of " + T34 + " on a rainy muddy road, a bright small explosion flash, painterly realistic, cinematic, film grain, no text, no letters.",
    "rocket_bounce": "Close-up of a small bazooka rocket glancing off the thick sloped armor of " + T34 + ", sparks flying, the tank undamaged and still moving forward in the rain, painterly realistic, cinematic, film grain, no text, no letters.",
    "tfs_retreat": CB + "exhausted " + US + " retreating in small groups through flooded rice paddies in the rain, some helping wounded comrades, abandoned equipment behind them" + END,
    "rumor_campfire": CB + "frightened young " + US + " whispering to each other around a small dim fire at night in a Korean village, worried faces, rifles leaning on a wall" + END,
    "martin_bazooka": CB + "an American colonel whose head is a round ball painted as the United States flag, wearing an M1 helmet, holding an old 2.36-inch bazooka on his shoulder in a narrow street of a small Korean town at dawn, determined" + END,
    "martin_tank": CB + T34 + " turning its gun toward a bazooka team in a narrow Korean town street at dawn, the muzzle flashing, dust and debris" + END,
    "bridge_blow": "Army engineers blowing up a long concrete bridge over a wide brown Korean river in July 1950, a huge explosion in the middle span, smoke and debris, green hills on the far bank, " + LAND,
    "geum_rafts": CB + NK + " crossing a wide brown river at dawn on small wooden boats and log rafts, pushing with poles, mist over the water" + END,
    "artillery_rifles": CB + US + " artillerymen firing rifles and carbines from behind their 155mm howitzers as enemy infantry attack through the bushes, smoke, chaos" + END,
    "exhausted_gi": CB + "exhausted, sweating " + US + " sitting at the roadside in the hot July sun, empty canteens, thousand-yard stares, fearful glances toward the north" + END,
    "travis_c54": "A 1950 four-engine C-54 Skymaster transport plane taking off from a California air base at sunset, mechanics watching, " + LAND,
    "long_crates": "The inside of a 1950 military transport plane cabin packed with long olive green wooden crates stenciled only with plain stripes, two instructors in khaki sitting beside them, dim light, " + LAND,
    "bazooka_training": CB + "an instructor teaching " + US + " how to load and aim a large new 3.5-inch M20 rocket launcher on a dusty airfield in Korea, soldiers watching closely" + END,
    "shaped_charge": "A clean cutaway technical illustration of a 1950 shaped-charge anti-tank rocket hitting thick armor plate, a jet of molten metal piercing through like an awl, dark background, glowing orange, no text, no letters, no labels.",
    "dean_stays": CB + DEAN + " standing alone at night by a window in a small command post office lit by a lantern, maps on the table, looking out at the dark city" + END,
    "radio_dead": CB + "a frustrated " + US1 + " radio operator shaking a dead field radio in a dark room, cut telephone wires hanging outside the window" + END,
    "refugee_column": "A long column of Korean refugees in white clothes carrying bundles on their heads and A-frames on their backs, walking south along a dusty road out of a small city in hot July 1950, " + LAND,
    "white_clothes": CB + "a few " + NK + " partly disguised in white Korean civilian clothes, hiding rifles under bundles, slipping into a crowd of refugees on a road at dusk" + END,
    "first_aim": CB + "two " + US + " kneeling in the dark at a city crossroads before dawn, aiming a large new 3.5-inch bazooka at the silhouette of " + T34 + " approaching" + END,
    "first_fire": CB + "a large 3.5-inch bazooka firing at a dark city crossroads before dawn, a bright rocket flash and backblast lighting up two " + US + END,
    "first_kill": CB + T34 + " exploding from inside at a dark city crossroads before dawn, flames bursting out of the hatches, two " + US + " ducking behind rubble" + END,
    "darr_cover": CB + "a lone " + US1 + " sergeant firing his rifle from a hillside position near an airfield, covering his platoon as it withdraws behind him, enemy approaching through the grass" + END,
    "tank_street": CB + T34 + " rolling down " + TOWN + " in daylight, civilians fleeing, smoke rising from buildings" + END,
    "dean_out": CB + DEAN + " walking out of a command post with a young lieutenant and a few " + US + " carrying bazookas, smoke over the city behind them" + END,
    "dean_hunt": CB + DEAN + " pointing the way for a bazooka team of " + US + " moving carefully along " + TOWN + ", searching for tanks" + END,
    "alley_chase": CB + DEAN + " and a few " + US + " running through a narrow alley between brick buildings and climbing over a low wall, chasing a tank heard nearby" + END,
    "tank_stops": T34 + " stopped at the side of a street in a small 1950 Korean city, engine smoking, the commander's hatch closed, two-story buildings around it, afternoon light, painterly realistic, cinematic, film grain, no text, no letters.",
    "backblast": "A 3.5-inch bazooka firing inside a room with a huge backblast flame shooting out behind it, debris flying, dramatic, painterly realistic, cinematic, film grain, no text, no letters.",
    "window_view": "View from a second-floor window looking straight down at the turret of " + T34 + " stopped in the street right below, afternoon light, tense, painterly realistic, cinematic, film grain, no text, no letters.",
    "window_shot": CB + "a " + US1 + " corporal firing a large 3.5-inch bazooka from a second-floor window straight down at the turret of " + T34 + " in the street below, " + DEAN + " beside him pointing" + END,
    "tank_burning": T34 + " engulfed in flames and black smoke in a street of a small 1950 Korean city, burning, the turret hatch open, painterly realistic, cinematic, film grain, no text, no letters.",
    "sniper_city": CB + US + " ducking behind a wall as snipers fire from the windows of buildings in " + TOWN + ", dust kicking up, smoke" + END,
    "watch_check": CB + DEAN + " looking down at his wristwatch at dusk in a smoky city street, worried but resolute" + END,
    "convoy_out": CB + "a long column of trucks and jeeps full of " + US + " rushing out of a burning city along a road at dusk, dust and smoke" + END,
    "ambush_tunnel": CB + "a convoy of trucks and jeeps ambushed near a railway tunnel on a narrow road between steep hills at dusk, machine gun fire from both hillsides, the lead truck on fire, " + US + " jumping out" + END,
    "libby_truck": CB + "a wounded " + US1 + " sergeant standing on the running board of an army truck full of wounded soldiers, shielding the driver with his body as the truck speeds through a burning roadblock at dusk" + END,
    "jeep_abandon": CB + DEAN + " and a few " + US + " leaving their jeep and climbing up a dark hillside at night, helping wounded soldiers, burning vehicles on the road below" + END,
    "night_mountain": CB + "a small group of exhausted " + US + " with wounded comrades resting in the dark on a pine-covered Korean mountain at night, moonlight" + END,
    "dean_water": CB + DEAN + " carefully climbing down a steep dark slope alone at night, holding an empty canteen, the faint sound of a stream below in the moonlight" + END,
    "dean_fall": CB + DEAN + " slipping and tumbling down a steep rocky slope in the dark at night, his helmet flying off" + END,
    "hide_forest": CB + "a thin exhausted " + US1 + " in a torn uniform with a bandaged head and his arm in a sling, hiding under bushes in a Korean forest in daylight" + END,
    "farmer_rice": "An elderly Korean farmer in white clothes secretly handing a bowl of rice to a thin exhausted American man in a torn uniform behind a thatched farmhouse at night, lamplight, kindness and fear, " + LAND,
    "betrayal": CB + "two Korean men in white civilian clothes leading a thin exhausted " + US1 + " with a bandaged head along a mountain path at dusk, glancing at each other" + END,
    "capture_struggle": CB + "a thin, exhausted American general whose head is a round ball painted as the United States flag, struggling weakly as " + NK + " surround him on a mountain path at dusk" + END,
    "daejeon_night_fall": "A small 1950 Korean city burning at night seen from a distant hill, orange glow on the clouds, smoke columns, silhouettes of tanks entering, " + LAND,
    "superbazooka_flow": CB + US + " and South Korean soldiers whose heads are round balls painted as the South Korean taegukgi flag unloading many new 3.5-inch bazookas from trucks at a busy supply point" + END,
    "dean_return": CB + "a thin American general whose head is a round ball painted as the United States flag, in a plain uniform, stepping out of a truck at a prisoner exchange point in 1953, soldiers saluting, emotional" + END,
    "dean_beside": CB + DEAN + " crouching right beside young frightened " + US + " in a burning street, pointing at a tank and encouraging them" + END,
    "memorial_daejeon": "A modern memorial ceremony in Daejeon, South Korea, with South Korean and American soldiers in dress uniforms standing in formation before a war memorial, wreaths of white flowers, summer, " + LAND,
    "thumb_bg": "Cinematic photorealistic war film still, 16:9 wide shot: from the second-floor window of a burning 1950 Korean brick shop building, an American soldier fires a large 3.5-inch bazooka straight down at a Soviet T-34/85 tank in the street, the rocket exploding on the turret in a bright fireball, huge backblast flame, the burning city street at dusk, orange fire and black smoke, high contrast, dramatic, the lower third of the frame darker, no text, no letters, no logos.",
}
# 재사용 그림 (파일·서명 복사, 추가 비용 0): 원래 프롬프트 그대로
REUSE = {"t34_column": "dabudong"}
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
assert not set(AI) - used - {"thumb_bg"}, set(AI) - used

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
board = {"title": "대전의 이틀", "subtitle": "3.5인치 바주카의 첫 일격과 딘 소장의 실종 · 1950. 7", "style": 2, "tts_mode": "act", "sfx_policy": "doc", "bgm_rel_db": -24, "sub_max": 28, "sync_limit": 0.5,
         "target_sec": 1230, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap],
      "ai", len(AI), "new ai", len(set(AI) - set(REUSE)), "pins", len(PINS), "stage", len(stages), "photo", sum(1 for s in S if s["visual"]["type"] == "photo"))
print("char uses", dict(cnt))
