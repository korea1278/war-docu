# EP25 수도고지·지형능선 전투 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# ⚠️ 2026-11-11 미리보기 뒤 storyboard.json을 손으로 고침(s29b·s86b·s114b·s144b 추가, 뷰·그림 프롬프트 수정) — 이 스크립트를 다시 돌리지 말 것
# 새 지도 기능(EP25): visual.flight(뷰 키 목록 → Catmull-Rom 카메라 비행) · visual.hud(전술 HUD) · 아이템 swarm(파티클 200개)
import glob
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
    ("천구백오십이 년 시월 육일", "1952년 10월 6일"), ("천구백오십이 년 시월 팔일", "1952년 10월 8일"), ("천구백오십이 년 사월", "1952년 4월"), ("천구백오십이 년 여름", "1952년 여름"),
    ("천구백오십이 년 가을", "1952년 가을"), ("천구백오십삼 년 유월", "1953년 6월"), ("천구백오십이 년", "1952년"),
    ("시월 육일", "10월 6일"), ("시월 십사일", "10월 14일"), ("시월 중순", "10월 중순"), ("구월 육일", "9월 6일"), ("구월 구일", "9월 9일"), ("구월 십삼일", "9월 13일"), ("구월 초", "9월 초"), ("구월 말", "9월 말"),
    ("칠월 칠일", "7월 7일"), ("칠월 말", "7월 말"), ("팔월 오일", "8월 5일"), ("팔월 십일", "8월 10일"), ("이듬해 칠월", "이듬해 7월"), ("이월", "2월"),
    ("새벽 한 시 십오 분", "새벽 1시 15분"),
    ("제이십육연대", "제26연대"), ("제일연대", "제1연대"), ("제일대대", "제1대대"), ("제삼중대", "제3중대"), ("제이군단", "제2군단"), ("제육사단", "제6사단"), ("제삼사단", "제3사단"), ("제구사단", "제9사단"),
    ("제십이군", "제12군"), ("제삼십오사단", "제35사단"), ("제삼십사사단", "제34사단"), ("제삼십팔군", "제38군"),
    ("육백육십삼 고지", "663고지"), ("육백 미터", "600m"), ("백오 밀리", "105mm"),
    ("삼백육십구 명", "369명"), ("사백오십 명", "450명"), ("마흔여덟 명", "48명"), ("백오십 명", "150명"), ("포탄 육천여 발", "포탄 6천여 발"), ("십사만 발", "14만 발"), ("사천 발", "4천 발"),
    ("전차 네 대", "전차 4대"), ("중기관총 세 정", "중기관총 3정"), ("중대 세 개", "중대 3개"), ("봉우리 세 개", "봉우리 3개"), ("아홉 개 대대", "9개 대대"), ("대대가 아홉 개", "대대가 9개"),
    ("여섯 차례", "6차례"), ("여섯 번", "6번"), ("열 번 남짓", "10번 남짓"), ("두 배", "2배"), ("일 년", "1년"), ("삼 년째", "3년째"), ("석 달", "3개월"), ("열흘", "10일"), ("나흘", "4일"), ("열이틀", "12일"), ("몇십 초", "수십 초"),
    ("에피소드 이십육", "EP 26"), ("스무 살", "20살"), ("수백 개", "수백 개"),
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
    assert len(out) == n, (CUR, n)
    CUR["i"] += n
    return [L(x) for x in out]


def next_act():
    assert CUR["i"] == len(ACTS[CUR["act"]]), ("남은 문장", CUR, ACTS[CUR["act"]][CUR["i"]:])
    CUR["act"] += 1
    CUR["i"] = 0


def nid():
    return f"s{NUM['n'] + 1:02d}"


def sc(n, visual, sid=None, **kw):
    i = sid
    if i is None:
        i = nid()
        NUM["n"] += 1
    d = {"id": i, "lines": take(n), "visual": visual}
    d.update(kw)
    S.append(d)


def m(fr, to=None, items=None, **kw):
    v = {"type": "map", "from": fr, "to": to or fr, "items": items or []}
    v.update(kw)
    return v


def ai(img, kb="in"):
    return {"type": "ai", "img": img, "kb": kb}


# 사진: 이전 에피소드에서 검증한 핀(파일명 앞부분으로 찾음) + 스카우트 목록(catalog.json) 설명으로 확인한 새 파일
KNOWN = sorted({v for f in glob.glob(str(HERE.parent / "*" / "photo_pins.json")) if EP not in f for v in json.load(open(f, encoding="utf-8")).values()})
PH = {
    "whitehorse": "Hill whitehorse", "talks": "80-G-436371", "kaesong": "Korean War Peace talks. Kaesong", "sunshine": "Sunshine Division in Korea Kumwha",
    "guard": "C-7267", "flare": "Trip flare", "f4u": "US Marine Corps F4U drops napalm in Korea in October 1952", "h105": "105mm-howitzer-korea-195008",
    "cap_wounded": "SC 407542", "training": "1952.11.5", "napalm": "Napalm bomb explosion in Korea c1952", "wh_wounded": "SC 418377", "dmz": "Imjin River with iron railing",
    # 새 파일 (스카우트 catalog 설명 확인 · 미 국립문서기록관리청 공공 저작물)
    "cav": "File:SC 383811 FEC-51-40055 - November 1951 (52564117551).jpg",  # 수도사단 기갑연대 제3대대 · 중공군 포로 (1951. 11)
    "rokaf": "File:NASM 4A 31753 - November 1953 (52564345424).jpg",  # 한국 공군 F-51 무스탕 · 김영환 대령 (1953. 11)
}


def full(key):
    if PH[key].startswith("File:"):
        return PH[key]
    hit = [k for k in KNOWN if k[5:].startswith(PH[key])]
    assert len(hit) == 1, (key, hit)
    return hit[0]


def pin(key):
    sid = nid()
    PINS[f"{sid}-photo#0"] = full(key)
    return f"{sid}-photo"


def ph(key, pos=None):
    v = {"type": "photo", "kb": "in", "q": pin(key)}
    if pos:
        v["pos"] = pos
    return v


def black(a, b):
    return {"type": "black", "text": a, "accent": b, "accentAt": 0.5}


def text(big, style="yellow", sub=None):
    v = {"type": "text", "big": big, "style": style}
    if sub:
        v.update(sub=sub, subAt=0.4)
    return v


def cmp(lt, lb, rt, rb, lc="blue", rc="red"):
    return {"type": "compare", "left": {"title": lt, "big": lb, "icon": "none", "color": lc}, "right": {"title": rt, "big": rb, "icon": "none", "color": rc, "at": 0.6}}


DRAMA = "재연 일러스트"
NOTE = "위치 개략"
P = {
    "seoul": [126.978, 37.566, "서울"], "panmun": [126.677, 37.956, "판문점"], "cheorwon": [127.212, 38.248, "철원"], "gimhwa": [127.47, 38.298, "김화"],
    "baengma": [127.197, 38.296, "백마고지"], "snp": [127.4853, 38.3289, "저격능선"], "kumsong": [127.585, 38.445, "금성"], "jiri": [127.73, 35.34, "지리산"],
    # 수도고지·지형능선 좌표: 미군 그리드 CT 905493 · CT 878498 (Korean War Educator 전초 목록) — 663고지·좌수동·합류부는 개략
    "capital": [127.746, 38.389, "수도고지"], "finger": [127.715, 38.393, "지형능선"], "h663": [127.752, 38.378, "663고지"], "jwasu": [127.742, 38.412, "좌수동 계곡"],
    "confl": [127.754, 38.357, "금성천·북한강 합류"], "f1": [127.706, 38.396], "f2": [127.715, 38.393], "f3": [127.724, 38.391],
    "pyongyang": [125.754, 39.02, "평양"], "seungho": [125.97, 39.02, "승호리"],
}
V = {
    "korea": {"center": [127.6, 37.4], "span": 5.6}, "central": {"center": [127.5, 38.33], "span": 1.1}, "salient": {"center": [127.66, 38.39], "span": 0.42},
    "area": {"center": [127.735, 38.386], "span": 0.16}, "close": {"center": [127.742, 38.39], "span": 0.1}, "finger": {"center": [127.716, 38.394], "span": 0.1},
    "capital": {"center": [127.748, 38.388], "span": 0.1}, "jwasu": {"center": [127.745, 38.402], "span": 0.1}, "confl": {"center": [127.752, 38.37], "span": 0.14},
    "west": {"center": [127.48, 38.34], "span": 0.75}, "pyong": {"center": [125.9, 39.0], "span": 1.0},
}
MLR = [[127.45, 38.36], [127.52, 38.4], [127.585, 38.415], [127.65, 38.405], [127.7, 38.385], [127.75, 38.377], [127.8, 38.37], [127.88, 38.36]]
front = {"k": "front", "path": MLR, "at": 0}
U = lambda p, t, c="blue", at=0.2, **kw: dict({"k": "unit", "p": p, "color": c, "text": t, "at": at}, **kw)
red_a = lambda path, at=0.3, w=0.9: {"k": "arrow", "path": path, "color": "red", "at": at, "width": w}
blue_a = lambda path, at=0.3, w=0.9: {"k": "arrow", "path": path, "color": "blue", "at": at, "width": w}
OBJ_C = lambda at=0, taken=None, c="red": dict({"k": "obj", "p": "capital", "n": "C", "text": "수도고지", "at": at, "color": c}, **({"takenAt": taken} if taken is not None else {}))
FINGERS = lambda at=0, taken=None: [dict({"k": "obj", "p": f"f{j}", "n": str(j), "r": 24, "at": at + 0.15 * j}, **({"takenAt": taken} if taken is not None else {})) for j in (1, 2, 3)]
FLBL = {"k": "badge", "p": "finger", "text": "지형능선", "color": "red", "at": 0.3, "dy": -95}
# 중공군 접근 축선 (북·북동에서 수도고지·지형능선으로) — 모두 개략
AX_C = [[127.738, 38.43], [127.741, 38.415], [127.744, 38.402], [127.746, 38.391]]
AX_C2 = [[127.775, 38.42], [127.765, 38.408], [127.753, 38.396], [127.747, 38.39]]
AX_F = [[127.712, 38.428], [127.714, 38.413], [127.715, 38.4], [127.715, 38.394]]
SOUTH = [[127.744, 38.37], [127.745, 38.378], [127.746, 38.387]]
swarm = lambda path, at=0.2, n=200, **kw: dict({"k": "swarm", "path": path, "at": at, "n": n}, **kw)
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]

# ===== 제1막 (콜드 오프닝) =====
sc(2, ai("tanks_dusk"), label=DRAMA, callouts=top("1952. 10. 6 저녁 · 강원도 중부 전선"))
sc(1, m("area", "capital", [OBJ_C(), {"k": "shock", "pts": ["capital", [127.744, 38.393], [127.749, 38.386]], "at": 0.1, "period": 0.8}], hud=True, tilt=30), callouts=top("포탄 6천여 발", "red"), sfx=[{"id": "boom", "at": 0.2, "volume": 0.45}])
sc(2, m("central", "central", [{"k": "marker", "p": "baengma", "color": "red", "at": 0}, {"k": "marker", "p": "capital", "color": "red", "at": 0.5}, {"k": "shock", "pts": ["baengma", "capital"], "at": 0.6, "period": 0.9}]), callouts=top("같은 날 · 같은 밤"))
sc(2, ph("whitehorse"), label="백마고지 전적지 위령탑")
sc(2, black("이름 없는 봉우리", "병사들이 붙인 이름"))
sc(2, {"type": "titlecard", "title": "수도고지·지형능선 전투", "sub": "금성천의 방패 · 1952", "at": 0, "q": pin("sunshine")}, flash=True, sfx=[{"id": "boom", "at": 0, "volume": 0.5}])
sc(2, m("finger", "capital", [OBJ_C(), *FINGERS(0.4), FLBL], flight=["finger", "close", "capital"], hud=True, tilt=34))
sc(1, text("3개월 넘는 쟁탈전", "red", "1952년 7월 ~ 10월"))
sc(2, text("보병 9개 대대 전원 투입", "yellow", "당시 대대장 증언"))
sc(2, black("이름 없던 봉우리 하나가", "왜 그토록 많은 피를"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, ph("talks"), label="유엔군 휴전 회담 대표단 (1951. 11)", chapter={"num": "제1막", "title": "같은 날 같은 밤"})
sc(2, ph("kaesong"), label="휴전 회담 (개성 · 1951)")
sc(3, text("지금 선 자리 = 국경", "yellow", "휴전 회담 시기 양측의 계산"))
sc(2, ai("hill_night"), label=DRAMA)
sc(2, black("1952. 10. 8 회담 중단", "남은 건 대포뿐"), sfx=[{"id": "hit", "at": 0.5, "volume": 0.4}])
sc(2, m("central", "central", [front, red_a([[127.2, 38.5], [127.2, 38.33]], 0.2), red_a([[127.47, 38.5], [127.48, 38.36]], 0.5), red_a([[127.74, 38.55], [127.745, 38.4]], 0.8)]), callouts=top("1952년 가을 · 중공군 공세", "red"))
sc(1, m("central", "salient", [front, {"k": "badge", "p": [127.62, 38.43], "text": "금성 돌출부", "color": "#111", "at": 0.5, "dy": -40}]))
sc(2, m("salient", "salient", [front, red_a([[127.62, 38.53], [127.62, 38.43]], 0.1), red_a([[127.47, 38.47], [127.55, 38.42]], 0.4), red_a([[127.82, 38.47], [127.73, 38.4]], 0.7)]), callouts=top("세 방향의 위협 · " + NOTE, "red"))
sc(1, cmp("적에게", "잘라 낼 혹", "우리에게", "전진 기지", "red", "blue"))
sc(1, m("salient", "capital", [front, {"k": "lock", "p": "capital", "at": 0.5, "text": "수도고지"}], flight=["salient", "confl", "area", "capital"], hud=True, tilt=32))
next_act()

# ===== 제2막 =====
sc(2, m("central", "confl", [front], flight=["central", "salient", "confl"], tilt=28), chapter={"num": "제2막", "title": "육백 미터의 덫"})
sc(2, m("confl", "confl", [{"k": "badge", "p": [127.775, 38.345], "text": "북한강", "color": "#1E8FFF", "at": 0, "dy": 0}, {"k": "badge", "p": [127.715, 38.348], "text": "금성천", "color": "#1E8FFF", "at": 0.4, "dy": 0}, {"k": "marker", "p": "capital", "color": "red", "at": 0.8}], hud=True, tilt=26))
sc(2, text("국군 제2군단", "blue", "1952. 4. 5 재창설"))
sc(2, m("salient", "salient", [front, U([127.58, 38.395], "제6사단"), U([127.72, 38.36], "수도사단", at=0.5, pulse=True), U([127.845, 38.345], "제3사단", at=0.8)]), callouts=top("국군 제2군단 배치 · " + NOTE, "blue"))
sc(2, black("한 치도", "물러서지 말 것"))
sc(3, ai("capital_march"), label=DRAMA)
sc(1, m("korea", "korea", [{"k": "marker", "p": "jiri", "color": "blue", "at": 0}, blue_a([[127.73, 35.4], [127.6, 36.6], [127.7, 38.3]], 0.3, 1.2)]), callouts=top("1952년 봄 · 지리산 → 중부 전선", "blue"))
sc(1, m("area", "close", [front], tilt=30, hud=True))
sc(3, m("close", "capital", [front, OBJ_C(), {"k": "marker", "p": "h663", "color": "blue", "at": 0.6}, {"k": "badge", "p": "capital", "text": "약 600m", "color": "red", "at": 1.0, "dy": -100}], tilt=36, hud=True), callouts=low("663고지 옆 무명 봉우리 · " + NOTE))
sc(3, m("capital", "jwasu", [OBJ_C(), {"k": "lock", "p": "jwasu", "at": 0.4, "text": "좌수동 계곡"}], flight=["capital", "close", "jwasu"], tilt=40, hud=True), callouts=top("관측의 요충지", "yellow"))
sc(3, {"type": "profile", "pts": [[0, 330], [0.1, 360], [0.2, 400], [0.3, 445], [0.4, 495], [0.5, 545], [0.58, 595], [0.62, 600], [0.66, 590], [0.72, 470], [0.8, 380], [0.9, 340], [1, 320]], "grid": [400, 500, 600], "yMin": 250, "yMax": 680,
       "title": "수도고지 남북 단면", "note": "모식도 (높이·경사 과장 · 개략)", "left": "북 · 완만한 능선 여러 갈래", "right": "남 · 가파른 능선 하나",
       "marks": [{"x": 0.62, "text": "수도고지", "style": "yellow", "at": 0, "lift": 80, "size": 42}],
       "arrows": [{"from": 0.05, "to": 0.55, "color": "red", "at": 1.0, "lift": 40}, {"from": 0.12, "to": 0.57, "color": "red", "at": 1.6, "lift": 90}, {"from": 0.95, "to": 0.68, "color": "blue", "at": 3.0, "lift": 50}]})
sc(3, ai("single_trail"), label=DRAMA)
sc(2, m("close", "finger", [OBJ_C(), *FINGERS(0.3), FLBL], tilt=34, hud=True), callouts=top("손가락 모양 능선 · 봉우리 3개 · " + NOTE))
sc(1, ph("cav"), label="수도사단 기갑연대 제3대대와 중공군 포로 (1951. 11)")
sc(2, ai("cavalry_dig"), label=DRAMA)
sc(2, ph("guard", "50% 20%"), label="판문점 길목을 지키는 국군 병사 (1952. 3)")
sc(2, m("area", "area", [front, OBJ_C(), *FINGERS(0), {"k": "badge", "p": [127.73, 38.405], "text": "주저항선 앞 두 개의 방패", "color": "#111", "at": 0.5, "dy": 0}], tilt=28, hud=True))
sc(2, m("salient", "area", [front, U([127.735, 38.425], "중공군 제35사단", "red", 0.1), U([127.7, 38.475], "제34사단 (예비)", "red", 0.6)]), callouts=top("중공군 제12군", "red"))
sc(2, {"type": "timeline", "items": [{"date": "1952. 7. 7", "text": "첫 충돌", "at": 0}, {"date": "8. 5 밤", "text": "초소 2곳 기습", "at": 0.6}, {"date": "8. 10", "text": "중공군 후퇴", "at": 1.2}]})
sc(2, m("close", "capital", [OBJ_C(0, 0.2), blue_a(SOUTH, 0), {"k": "clash", "p": "capital", "at": 0.6}], tilt=32), callouts=top("1952. 8. 5 밤 · 제26연대", "blue"))
sc(2, {"type": "bars", "note": "1952. 8. 5~10 · 미군 기록 기준", "items": [{"label": "중공군 확인 전사", "value": 369, "display": "369명", "color": "red", "at": 0}, {"label": "중공군 추정 전사", "value": 450, "display": "450명", "color": "red", "at": 0.3}, {"label": "제26연대 전사", "value": 48, "display": "48명", "color": "blue", "at": 1.0}, {"label": "제26연대 부상", "value": 150, "display": "150명", "color": "blue", "at": 1.3}]})
sc(2, black("8월 10일 중공군 후퇴", "그러나 서막일 뿐"))
sc(2, ai("monsoon_wait"), label=DRAMA)
next_act()

# ===== 제3막 =====
MID = [nid()]
sc(1, black("제3막", "야간 파상공세"), pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, m("area", "area", [front, OBJ_C(), *FINGERS(0)], tilt=28, hud=True), chapter={"num": "제3막", "title": "야간 파상공세"}, callouts=top("1952. 9. 6 밤", "red"))
sc(1, m("area", "area", [OBJ_C(), *FINGERS(0), {"k": "shock", "pts": ["capital", "f1", "f2", "f3", [127.744, 38.393]], "at": 0, "period": 0.7}], tilt=28, hud=True), sfx=[{"id": "boom", "at": 0.2, "volume": 0.45}])
sc(3, ai("shell_storm"), label=DRAMA)
sc(2, ai("bugle_tunnel"), label=DRAMA)
sc(3, ai("human_wave"), label=DRAMA)
sc(2, ph("f4u"), label="미 해병대 F4U 코르세어의 네이팜 공격 (1952. 10)")
sc(1, black("어둠은", "가장 좋은 엄폐물"))
sc(2, ph("flare"), label="전선의 조명탄 (1951 · 참고 사진)")
sc(1, ai("rok_mg_flare"), label=DRAMA)
sc(2, ai("flare_dark"), label=DRAMA)
sc(1, ai("wire_cut"), label=DRAMA)
sc(2, m("finger", "finger", [*FINGERS(0), swarm(AX_F, 0.1), FLBL], tilt=36, hud=True), callouts=top("지형능선 · 기갑연대 전초 피탈", "red"))
sc(2, m("finger", "finger", [*FINGERS(0), blue_a([[127.712, 38.378], [127.714, 38.386], [127.715, 38.391]], 0.1, 0.7), U("finger", "중공군 증원", "red", 0.6, pulse=True)], tilt=36, hud=True), callouts=top("기갑연대 역습 → 철수", "blue"))
sc(2, m("close", "capital", [OBJ_C(), swarm(AX_C, 0.1, 120), swarm(AX_C2, 0.4, 120), {"k": "clash", "p": "capital", "at": 1.2}], tilt=38, hud=True), callouts=top("같은 밤 · 수도고지", "red"))
sc(1, m("capital", "capital", [{"k": "marker", "p": "capital", "color": "red", "at": 0}, {"k": "lock", "p": "capital", "at": 0.1, "text": "정상 피탈", "color": "red"}], tilt=40, hud=True), sfx=[{"id": "hit", "at": 0.3, "volume": 0.4}])
sc(2, m("area", "capital", [front, {"k": "marker", "p": "capital", "color": "red", "at": 0}], flight=["area", "close", "capital"], tilt=42, hud=True))
sc(2, m("capital", "close", [front, {"k": "radar", "p": "capital", "at": 0.2, "size": 1.2, "color": "red", "text": "적의 관측"}], tilt=32, hud=True))
sc(2, {"type": "cta", "title": "지도 위에서 그날 밤을 끝까지 따라갑니다", "at": 0}, pauseBefore=0.3, sfx=[{"id": "pop", "at": 0.3, "volume": 0.45}])
sc(1, black("다시", "그날 밤으로"))
sc(2, ai("slope_cling"), label=DRAMA)
sc(2, cmp("물러서면", "고지 상실", "버티면", "전멸 위기", "red", "red"))
sc(1, black("사단은", "선택해야 했다"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
next_act()

# ===== 제4막 =====
sc(1, ai("command_bunker"), label=DRAMA, chapter={"num": "제4막", "title": "진내사격의 결단"})
sc(1, black("진내사격", "우리 진지 위로"), sfx=[{"id": "boom", "at": 0.5, "volume": 0.45}])
sc(1, ai("vt_burst"), label=DRAMA)
sc(2, black("끔찍하지만", "원리는 단순하다"))
sc(2, ai("bunker_cover"), label=DRAMA)
sc(2, m("capital", "capital", [{"k": "marker", "p": "capital", "color": "red", "at": 0}, {"k": "shock", "pts": ["capital", [127.744, 38.392], [127.749, 38.387], [127.742, 38.388]], "at": 0.3, "period": 0.6}], tilt=40, hud=True), callouts=top("공중 폭발 사격 · 파편은 위에서 아래로"))
sc(1, text("1952. 10 · 미 해병대 전초", "yellow", "방어 병사들이 직접 머리 위 공중 폭발 사격 요청 · 미 해병대 기록"))
sc(3, ai("radio_call"), label=DRAMA)
sc(1, text("수도고지의 진내사격", "yellow", "횟수·시각까지는 기록이 자세하지 않음"))
sc(2, black("버티기만 하는", "방어가 아니었다"))
sc(3, text("빼앗기면 바로 되찾는다", "blue", "역습으로 지키는 방어"))
sc(1, ph("h105"), label="105mm 곡사포 사격 (1950. 8 · 참고 사진)")
sc(2, m("close", "capital", [{"k": "marker", "p": "capital", "color": "red", "at": 0}, {"k": "radar", "p": [127.746, 38.381], "at": 0, "size": 0.8, "color": "#00E5FF", "text": "사전 사격 구역"}, {"k": "shock", "pts": ["capital"], "at": 0.6, "period": 0.8}], tilt=34, hud=True), hudCta={"at": 0, "dur": 7.5})
sc(2, m("close", "capital", [{"k": "marker", "p": "capital", "color": "red", "at": 0}, U([127.738, 38.372], "제26연대", at=0.1), U([127.756, 38.371], "제1연대", at=0.4), blue_a([[127.738, 38.375], [127.743, 38.383], [127.746, 38.388]], 0.8, 0.7)], tilt=34, hud=True), callouts=top("1952. 9. 9 · 역습", "blue"))
sc(1, ai("counterattack"), label=DRAMA)
sc(1, m("capital", "capital", [OBJ_C(0, 0.3, "red"), {"k": "badge", "p": "capital", "text": "탈환", "color": "blue", "at": 0.5, "dy": -110}], tilt=40, hud=True), sfx=[{"id": "hit", "at": 0.4, "volume": 0.4}])
sc(2, m("close", "capital", [OBJ_C(0, 0), swarm(AX_C, 0.1, 90, speed=0.2), {"k": "clash", "p": [127.745, 38.396], "at": 1.0, "period": 0.9}], tilt=36, hud=True), callouts=top("최대 3개 중대 규모 · 거듭된 공격", "red"))
sc(2, text("다시는 밀려나지 않았다", "blue", "미 육군 공간사"))
sc(3, ai("green_flare"), label=DRAMA, callouts=top("1952. 9. 13 새벽 1시 15분", "red"))
sc(2, ai("gong_mg"), label=DRAMA, callouts=top("제26연대 제1대대 · 공해동 하사"))
sc(2, ai("gong_wounded"), label=DRAMA)
sc(1, ph("cap_wounded"), label="참호를 따라 후송되는 부상병 · 수도고지 (1952. 9)")
sc(1, ai("trigger_hand"), label=DRAMA, callouts=top("전해지는 이야기 · 왜관지구전적기념관"))
sc(2, black("수도고지의", "얼"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
next_act()

# ===== 제5막 =====
MID.append(nid())
sc(1, black("제5막", "뺏고 뺏기는 백병전"), pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, m("area", "finger", [*FINGERS(0), FLBL, {"k": "clash", "p": "f2", "at": 0.8}], tilt=36, hud=True), chapter={"num": "제5막", "title": "뺏고 뺏기는 백병전"}, callouts=top("1952. 9월 말 ~ 10월 중순"))
sc(3, text("주인이 바뀐 횟수는?", "yellow", "기록마다 다르거나 없음 · 미 공간사는 '여러 차례'"))
sc(3, text("제1연대 · 6차례 투입", "red", "지형능선 쟁탈전 · 당시 대대장 증언"))
sc(2, text("9개 대대 × 10번 남짓", "red", "당시 대대장 증언 (2차 인용)"))
sc(2, ph("training"), label="교육훈련 중인 국군 (1952. 11 · 참고 사진)")
sc(1, cmp("고참 병사", "1배", "신병", "2배", "blue", "red"), callouts=low("사상률 · 당시 대대장 증언"))
sc(3, ai("narrow_trench"), label=DRAMA)
sc(2, ai("grenade_duel"), label=DRAMA)
sc(1, ai("rok_bayonet"), label=DRAMA)
sc(1, ph("napalm"), label="네이팜 폭격 (1952 · 참고 사진)")
sc(1, ai("chinese_wave"), label=DRAMA)
sc(2, m("finger", "finger", [*FINGERS(0), blue_a([[127.716, 38.378], [127.716, 38.389]], 0.1, 0.7), red_a([[127.714, 38.412], [127.715, 38.398]], 0.9, 0.7), {"k": "clash", "p": "f1", "at": 0.6}, {"k": "clash", "p": "f3", "at": 1.4}], tilt=36, hud=True), callouts=top("낮에는 되찾고 · 밤에는 빼앗기고"))
sc(2, black("1952. 10. 6 저녁", "영상 처음의 그날"))
sc(1, m("central", "central", [{"k": "marker", "p": "baengma", "color": "red", "at": 0}, {"k": "marker", "p": "capital", "color": "red", "at": 0}, {"k": "shock", "pts": ["baengma", "capital"], "at": 0.1, "period": 0.8}]), callouts=top("백마고지 · 중공군 제38군 공세 시작", "red"))
sc(1, m("close", "capital", [OBJ_C(0, 0), {"k": "shock", "pts": ["capital", [127.743, 38.392], [127.749, 38.386], [127.741, 38.387], [127.747, 38.394]], "at": 0, "period": 0.6}], tilt=38, hud=True), callouts=top("전차 4대 · 포탄 6천여 발", "red"))
sc(2, ai("kim_rifle"), label=DRAMA, callouts=top("제26연대 제1대대 제3중대 · 김재호 일병"))
sc(2, ai("alone_trench"), label=DRAMA)
sc(3, ai("kim_melee"), label=DRAMA)
sc(2, text("을지무공훈장", "yellow", "1953. 7. 15 금성 지구 전투에서 전사"))
next_act()

# ===== 제6막 =====
sc(2, m("area", "area", [front, OBJ_C(0, 0), *FINGERS(0, 1)], tilt=30, hud=True), chapter={"num": "제6막", "title": "금성천의 방패"}, callouts=top("1952. 10월 중순", "blue"))
sc(2, m("finger", "finger", [*FINGERS(0, 0), {"k": "badge", "p": "finger", "text": "재확보", "color": "blue", "at": 0.6, "dy": -95}], tilt=36, hud=True), callouts=top("미 육군 공간사 기준", "blue"))
sc(1, m("close", "capital", [OBJ_C(0, 0), U([127.745, 38.372], "수도사단", at=0.2, pulse=True)], tilt=34))
sc(1, ph("wh_wounded"), label="백마고지 전투에서 부상한 국군 제9사단 병사들 (1952. 10)")
sc(2, m("west", "west", [{"k": "marker", "p": "baengma", "color": "blue", "at": 0}, {"k": "marker", "p": "snp", "color": "red", "at": 0.5}, {"k": "marker", "p": "capital", "color": "blue", "at": 0.2}]), callouts=top("1952년 가을 · 중부 전선 고지전", "red"))
sc(2, m("salient", "area", [front, OBJ_C(0, 0)], flight=["salient", "confl", "area"], tilt=30, hud=True))
sc(2, m("salient", "salient", [front, red_a([[127.746, 38.39], [127.745, 38.37]], 0.1, 0.8), red_a([[127.75, 38.37], [127.77, 38.3]], 0.7, 1.0)]), callouts=top("가정 · 두 고지가 무너졌다면", "red"))
sc(1, m("salient", "salient", [front, {"k": "badge", "p": [127.735, 38.405], "text": "금성 돌출부의 방패", "color": "blue", "at": 0.3, "dy": -40}]))
sc(2, text("한 달 14만여 발", "red", "왜관지구전적기념관 기록"))
sc(1, text("하루 4천 발 이상", "red", "단순 환산"))
sc(2, {"type": "document", "org": "국방부", "head": "장관 특별 담화", "stamp": "전공 치하", "rows": ["대상: 수도사단 장병", "내용: 수도고지 전투 전공"], "note": "요지 · 재구성 화면"})
sc(2, black("수도사단은 어떻게", "지켜 냈을까"))
sc(3, {"type": "factors", "head": "수도고지를 지킨 세 가지", "items": ["즉각 역습", "포병·보병 협동", "사람"], "at": 0})
sc(2, text("기동방어", "blue", "예비 병력을 뚫린 곳으로 재빨리 투입"))
sc(3, m("close", "capital", [U("capital", "중공군", "red", 0, pulse=True), blue_a([[127.736, 38.372], [127.742, 38.382], [127.745, 38.388]], 0.6, 0.7), blue_a([[127.758, 38.374], [127.751, 38.383], [127.747, 38.388]], 1.0, 0.7)], tilt=36, hud=True), callouts=top("적이 가장 약한 몇 시간", "blue"))
sc(2, ai("arty_infantry"), label=DRAMA, callouts=top("둘째 · 포병과 보병의 협동", "blue"))
sc(2, ai("gong_mg", "out"), label=DRAMA, callouts=top("셋째 · 사람", "blue"))
sc(2, ai("wooden_marker"), label=DRAMA)
next_act()

# ===== 제7막 =====
MID.append(nid())
sc(1, black("제7막", "피로 지킨 이름"), pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(1, m("area", "area", [front, OBJ_C(0, 0), *FINGERS(0, 0)], tilt=28), chapter={"num": "제7막", "title": "피로 지킨 이름"}, callouts=top("이듬해 · 다른 사단이 이어받음"))
sc(2, m("salient", "salient", [front, red_a([[127.7, 38.5], [127.72, 38.39]], 0.1, 1.2), red_a([[127.6, 38.52], [127.6, 38.42]], 0.4, 1.2), red_a([[127.8, 38.48], [127.75, 38.39]], 0.7, 1.2), {"k": "marker", "p": "capital", "color": "red", "at": 1.0}]), callouts=top("1953. 6 · 중공군 공세 · 두 고지 상실", "red"))
sc(2, m("salient", "central", [{"k": "badge", "p": [127.6, 38.36], "text": "1953. 7 금성 전투", "color": "red", "at": 0.5, "dy": 0}]), callouts=top("EP 17 금성 전투 편"))
sc(2, black("헛된 피였을까", "그렇지 않다"))
sc(2, m("salient", "salient", [front, {"k": "line", "path": [[127.45, 38.3], [127.55, 38.33], [127.65, 38.33], [127.75, 38.31], [127.88, 38.3]], "color": "#FF4B4B", "at": 0.3}]), callouts=top("가정 · 1년 일찍 밀려났다면", "red"))
sc(1, ph("dmz"), label="오늘의 비무장지대 철책 (임진강)")
sc(2, ai("peak_today"), label=DRAMA)
sc(2, ai("dmz_dawn"), label=DRAMA)
sc(2, ai("young_letters"), label=DRAMA)
sc(1, ai("quiet_ridge"), label=DRAMA)
sc(2, text("그 고지의 이야기를", "yellow", "댓글로 남겨 주세요"))
sc(1, black("다음 이야기", "하늘의 싸움"))
sc(2, m("korea", "pyong", [{"k": "marker", "p": "pyongyang", "color": "red", "at": 0.3}, {"k": "lock", "p": "seungho", "at": 0.9, "text": "승호리 철교"}]), callouts=low("위치 개략"))
sc(1, ai("bridge_intact"), label=DRAMA)
sc(2, ph("rokaf"), label="한국 공군 F-51 무스탕과 김영환 대령 (1953. 11)")
sc(2, black("EP 26", "승호리 철교 폭파 작전"), sfx=[{"id": "boom", "at": 0.5, "volume": 0.4}])
sc(2, {"type": "cta", "title": "구독 · 알림으로 다음 편에서 만나요", "at": 0}, sfx=[{"id": "pop", "at": 0.2, "volume": 0.45}])
sc(1, {"type": "endcard", "title": "1952년 가을, 수도고지.\n이름 없이 쓰러진 이들을 기억하며.", "q": pin("sunshine")}, tail=1.0)
assert CUR["i"] == len(ACTS[6])

# ===== 재연 일러스트 =====
CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
KR = "South Korean soldiers whose heads are round balls painted as the South Korean Taegukgi flag, wearing plain olive American-style 1952 field uniforms and M1 steel helmets, absolutely NO collar tabs, NO shoulder patches, NO arm patches, NO stars, and NO red anywhere on the uniform"
KR1 = "a South Korean soldier whose head is a round ball painted as the South Korean Taegukgi flag, wearing a plain olive American-style 1952 field uniform and M1 steel helmet, absolutely NO collar tabs, NO shoulder patches, NO arm patches, NO stars, and NO red anywhere on the uniform"
OF = "a South Korean army officer whose head is a round ball painted as the South Korean Taegukgi flag, wearing a plain olive field uniform and M1 steel helmet with no collar tabs, no shoulder boards, no stars, no medals and absolutely no red on the uniform"
CN = "Chinese soldiers whose heads are round balls painted as the flag of the People's Republic of China, wearing padded mustard-khaki 1952 uniforms and soft caps"
END = ", leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no people visible, no text, no letters."
AI = {
    "tanks_dusk": CB + "four Soviet-made T-34 tanks with plain dark green hulls and NO markings, crewed by " + CN + ", raising their gun barrels toward a distant bare mountain peak at dusk, autumn Korean mountains, orange sky" + END,
    "capital_march": CB + KR + " marching proudly in a long column along a mountain road in spring 1952, a plain unmarked olive regimental flag on a pole, determined" + END,
    "single_trail": CB + KR + " climbing in single file up one steep narrow rocky ridge path toward a bare hilltop, sheer slopes on both sides, dusk" + END,
    "cavalry_dig": CB + KR + " digging a deep zigzag trench with shovels on a narrow bare mountain ridge, an old cavalry saddle resting on sandbags nearby, autumn 1952" + END,
    "monsoon_wait": CB + KR + " standing in a rain-flooded trench under ponchos during the summer monsoon, watching a misty enemy-held ridge across the valley" + END,
    "rok_mg_flare": CB + KR + " firing a machine gun from a sandbagged trench at night under the harsh white light of a parachute flare, tracers streaking down the slope" + END,
    "flare_dark": "A dying parachute flare sinking over a dark Korean hillside at night, shadowy silhouettes of many crouching figures much closer to a trench line than before, eerie, painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no text, no letters.",
    "wire_cut": "Shredded barbed wire, broken stakes and empty ammunition boxes in front of a collapsed hilltop trench at night, smoke drifting, " + LAND,
    "slope_cling": CB + KR + " clinging to a very steep rocky slope just below a hilltop crest at night, enemy grenades rolling down toward them, desperate" + END,
    "command_bunker": CB + OF + " gripping a field telephone inside a cramped log-and-sandbag command bunker at night, dust falling from the ceiling, grim decision on his face" + END,
    "bunker_cover": CB + KR + " crouching safely inside a covered log bunker with a thick roof of logs and sandbags, while outside in the open trench enemy silhouettes stand exposed, night" + END,
    "radio_call": CB + KR1 + " shouting into a radio handset inside a covered bunker at night, the ceiling shaking, bright airbursts visible through the firing slit" + END,
    "green_flare": "A single green signal flare rising high over a dark bare mountain peak in central Korea at 1 a.m., the green glow lighting a trench line on the crest, starry autumn sky, " + LAND,
    "gong_mg": CB + KR1 + " a sergeant firing a light machine gun over the parapet of a hilltop trench at night, upper body exposed, fierce and steady, muzzle flash" + END,
    "gong_wounded": CB + KR1 + " a wounded sergeant with a bandaged shoulder still firing his light machine gun at night, refusing to stop, smoke and tracers" + END,
    "trigger_hand": "Close-up of a soldier's hand still resting on the trigger of an old light machine gun on a sandbag parapet at grey dawn, no blood, dust and spent cartridges, solemn, painterly realistic digital illustration, cinematic, dark desaturated palette, film grain, no face visible, no text, no letters.",
    "narrow_trench": CB + KR + " pressed against the wall of a very narrow zigzag trench on a ridge at night, no room to aim rifles, grenades in hand" + END,
    "kim_rifle": CB + "a young " + KR1[2:] + " a rifleman crouching in a trench under a heavy artillery barrage at night, clutching his M1 rifle, explosions all around" + END,
    "alone_trench": CB + "a young " + KR1[2:] + " lifting his head in a smoking trench after a barrage, his comrades lying still around him covered in dust, no blood, he is alone" + END,
    "kim_melee": CB + "a lone " + KR1[2:] + " fighting hand to hand with rifle butt and bayonet against " + CN + " jumping into his trench at night, fierce" + END,
    "arty_infantry": CB + KR + " firing 105mm howitzers at night in a valley while far away on a ridge other soldiers climb toward the shelled hilltop, coordinated" + END,
    "peak_today": "A quiet bare mountain peak in Gangwon Province, Korea at dawn today, autumn grass and silver reeds, an old rusted 1950s steel helmet among stones, soft golden light, " + LAND,
    "young_letters": CB + "young " + KR + " sitting in a trench writing letters by candlelight, one holding a small photograph, quiet moment" + END,
    "bridge_intact": "A long steel railway bridge over a wide river in North Korea in 1952, surrounded by countless bomb craters but still standing, anti-aircraft gun positions on the hills around, " + LAND,
    "thumb_subject": "Photorealistic black-and-white 1952 Korean War documentary portrait of a young Korean man, clearly East Asian Korean face with black hair, a South Korean army soldier of the Capital Division in a plain olive field jacket with no insignia and an M1 steel helmet with chin strap, dirt and sweat on his face, resolute determined eyes looking into the distance, waist-up, face clearly visible and turned slightly toward the left of the frame, isolated on a plain pure white background, no shadows on the background, no text.",
}
# 이전 에피소드 그림 재사용 (프롬프트·서명·파일을 그대로 복사 → 재생성 비용 0)
REUSE = {"hill_night": "ep19-sniper-ridge", "shell_storm": "ep19-sniper-ridge", "human_wave": "ep19-sniper-ridge", "grenade_duel": "ep19-sniper-ridge", "rok_bayonet": "ep19-sniper-ridge",
         "quiet_ridge": "ep19-sniper-ridge", "wooden_marker": "ep19-sniper-ridge", "vt_burst": "ep22-pork-chop-hill", "bugle_tunnel": "ep22-pork-chop-hill",
         "counterattack": "ep17-kumsong", "chinese_wave": "ep17-kumsong", "dmz_dawn": "ep17-kumsong"}
out_ai = ROOT / "public" / "ep" / EP / "ai"
out_ai.mkdir(parents=True, exist_ok=True)
man_p = out_ai.parent / "ai.json"
man = json.loads(man_p.read_text()) if man_p.exists() else {}
for name, src in REUSE.items():
    AI[name] = json.load(open(HERE.parent / src / "storyboard.json", encoding="utf-8"))["ai_images"][name]
    shutil.copy(ROOT / "public" / "ep" / src / "ai" / f"{name}.jpg", out_ai / f"{name}.jpg")
    man[name] = json.load(open(ROOT / "public" / "ep" / src / "ai.json"))[name]
man_p.write_text(json.dumps(man, ensure_ascii=False, indent=1))

used = {s["visual"]["img"] for s in S if s["visual"]["type"] == "ai"}
assert not used - set(AI), used - set(AI)
assert not set(AI) - used - {"thumb_subject"}, set(AI) - used

ids = [s["id"] for s in S]
chap = [i for i, s in enumerate(S) if s.get("chapter")]
sid = lambda i: S[i]["id"]
music = [{"id": "drone", "from": "s01", "to": sid(chap[0] - 1), "volume": 0.2},
         {"id": "theme", "from": sid(chap[0]), "to": sid(chap[2] - 2), "volume": 0.16},
         {"id": "tension", "from": MID[0], "to": sid(chap[3] - 1), "volume": 0.17},
         {"id": "march", "from": sid(chap[3]), "to": sid(chap[4] - 2), "volume": 0.15},
         {"id": "somber", "from": MID[1], "to": sid(chap[5] - 1), "volume": 0.17},
         {"id": "analysis", "from": sid(chap[5]), "to": sid(chap[6] - 2), "volume": 0.16},
         {"id": "somber", "from": MID[2], "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "수도고지·지형능선 전투", "subtitle": "1952. 7 ~ 10", "target_sec": 1230, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap], "ai new", len(set(AI) - set(REUSE)), "reuse", len(REUSE), "pins", len(PINS))
