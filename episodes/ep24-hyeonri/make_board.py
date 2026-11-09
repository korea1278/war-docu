# EP24 현리 전투 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
import glob
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
raw = (HERE / "script.md").read_text(encoding="utf-8")
ACTS = []
for a in raw.split("\n## ")[1:]:
    body = [l for l in a.split("\n")[1:] if l and not l.startswith((">", "#"))]
    ACTS.append([s for l in body for s in re.split(r"(?<=[.?])\s+", l.strip()) if s])

SUBS = [
    ("천구백오십일 년 오월 십칠일", "1951년 5월 17일"), ("천구백오십일 년 오월 십육일", "1951년 5월 16일"), ("천구백오십일 년 사월 이십이일", "1951년 4월 22일"), ("천구백오십일 년 팔월", "1951년 8월"), ("천구백오십일 년", "1951년"), ("천구백오십 년 칠월", "1950년 7월"), ("천구백오십이 년", "1952년"),
    ("오월 십육일", "5월 16일"), ("십칠일 새벽", "17일 새벽"), ("열두 시간", "12시간"), ("열세 시간 반", "13시간 반"), ("오천 명", "5천 명"), ("오월 초", "5월 초"), ("오월 중순", "5월 중순"), ("오월 이십일일", "5월 21일"), ("오월 이십육일", "5월 26일"), ("오월 이십칠일", "5월 27일"), ("오월 이십일", "5월 20일"), ("오월 십구일", "5월 19일"), ("오월 십칠일", "5월 17일"),
    ("오후 다섯 시 삼십 분", "오후 5시 30분"), ("새벽 네 시", "새벽 4시"), ("오후 네 시", "오후 4시"), ("오후 한 시", "오후 1시"), ("오후 여섯 시", "오후 6시"), ("저녁 여덟 시", "저녁 8시"), ("아침 일곱 시", "아침 7시"),
    ("제백칠십팔연대", "제178연대"), ("제육십사단", "제60사단"), ("제이십칠군", "제27군"), ("제이십군", "제20군"), ("제삼십연대", "제30연대"), ("제십팔연대", "제18연대"), ("제이대대", "제2대대"),
    ("제십군단", "제10군단"), ("제삼군단", "제3군단"), ("제일군단", "제1군단"), ("제이군단", "제2군단"), ("제오군단", "제5군단"), ("제팔군", "제8군"), ("제오연대", "제5연대"),
    ("제삼사단", "제3사단"), ("제구사단", "제9사단"), ("제칠사단", "제7사단"), ("제오사단", "제5사단"), ("제이사단", "제2사단"), ("제일사단", "제1사단"),
    ("천사백삼십육 미터", "1,436미터"), ("천사백 미터", "1,400미터"), ("이십팔 킬로미터", "28km"), ("삼십 킬로미터", "30km"), ("칠십 킬로미터", "70km"), ("삼십일 번 국도", "31번 국도"), ("칠십 리", "70리"),
    ("십삼만 팔천", "13만 8천"), ("삼만 팔천", "3만 8천"), ("삼십만 명", "30만 명"), ("이만 오천 명", "2만 5천 명"), ("일만 사천여 명", "1만 4천여 명"),
    ("삼십사 점 이 퍼센트", "34.2%"), ("사십 퍼센트", "40%"), ("삼십 퍼센트", "30%"), ("칠십 퍼센트", "70%"), ("삼백구십오 고지", "395고지"), ("구십구 일", "99일"), ("팔 주", "8주"), ("일 년 오 개월", "1년 5개월"), ("팔 개월", "8개월"), ("다섯 달", "5개월"),
    ("여섯 개 사단", "6개 사단"), ("세 개 사단", "3개 사단"), ("세 개 군단", "3개 군단"), ("두 개 사단", "2개 사단"), ("한 개 중대", "1개 중대"), ("한 개 연대", "1개 연대"), ("한 개 대대", "1개 대대"), ("일곱 번", "7번"),
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


# 사진은 이전 에피소드에서 검증한 핀만 재사용 (파일명 앞부분으로 찾음)
KNOWN = sorted({v for f in glob.glob(str(HERE.parent / "*" / "photo_pins.json")) if "ep24" not in f for v in json.load(open(f, encoding="utf-8")).values()})
PH = {
    "offensive_map": "Chinese Spring Offensive, April to May 1951", "peng": "General Peng Dehuai", "soyang": "Soyang River to the North from the Bottleneck",
    "almond": "Briefing, Generals Almond", "rok_gun": "SC 348631", "wreck": "Knocked out US truck and 155mm howitzer", "napalm": "Napalm bomb explosion in Korea c1952",
    "vanfleet": "General James A. Van Fleet", "chosin": "Chosin.jpg", "training": "1952.11.5", "whitehorse": "Hill whitehorse",
    "lt": "ROK Artillery Taegu", "long_tom": "Artillerymen-firing-Long-Tom", "rok_chow": "SC 348636",
}


def full(key):
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


def black(a, b, **kw):
    return {"type": "black", "text": a, "accent": b, "accentAt": 0.5}


def text(big, style="yellow", sub=None):
    v = {"type": "text", "big": big, "style": style}
    if sub:
        v.update(sub=sub, subAt=0.4)
    return v


def cmp(lt, lb, rt, rb, lc="blue", rc="red"):
    return {"type": "compare", "left": {"title": lt, "big": lb, "icon": "none", "color": lc}, "right": {"title": rt, "big": rb, "icon": "none", "color": rc, "at": 0.6}}


def quote(title, t):
    return {"type": "quotes", "title": title, "items": [{"text": t, "at": 0}]}


DRAMA = "재연 일러스트"
P = {
    "seoul": [126.978, 37.566, "서울"], "yanggu": [127.99, 38.11, "양구"], "inje": [128.17, 38.07, "인제"], "hongcheon": [127.888, 37.697, "홍천"], "gangneung": [128.9, 37.75, "강릉"],
    "hyeonri": [128.317, 37.957, "현리"], "omachi": [128.285, 37.925, "오마치고개"], "chimgyo": [128.255, 37.89, "침교"], "bangtae": [128.36, 37.895, "방태산"], "sangnam": [128.22, 37.85, "상남"],
    "hajinbu": [128.56, 37.637, "하진부리"], "soksa": [128.495, 37.638, "속사리"], "daehwa": [128.45, 37.5, "대화"], "yeongwol": [128.46, 37.18, "영월"], "gimhwa": [127.46, 38.27, "금화"], "baekma": [127.22, 38.31, "395고지"],
}
V = {
    "korea": {"center": [127.8, 36.9], "span": 5.6}, "east": {"center": [128.2, 37.85], "span": 1.9}, "bt": {"center": [128.28, 38.05], "span": 0.95},
    "zoom": {"center": [128.3, 37.94], "span": 0.17}, "bang": {"center": [128.33, 37.93], "span": 0.32}, "cut": {"center": [128.29, 37.91], "span": 0.24}, "koreaN": {"center": [127.8, 37.6], "span": 5.6}, "cw": {"center": [127.7, 38.0], "span": 1.6}, "flee": {"center": [128.45, 37.72], "span": 0.85}, "south": {"center": [128.4, 37.35], "span": 1.7},
}
FR = [[127.7, 38.02], [127.95, 38.08], [128.12, 38.12], [128.33, 38.17], [128.5, 38.25], [128.62, 38.4]]
ROAD = [[128.37, 38.1], [128.33, 38.02], [128.317, 37.957], [128.285, 37.925], [128.255, 37.89], [128.22, 37.85]]
PATH = [[128.15, 38.13], [128.19, 38.05], [128.23, 37.99], [128.285, 37.925]]
BND = [[128.24, 38.15], [128.25, 38.03], [128.33, 37.95], [128.37, 37.88]]
front = {"k": "front", "path": FR, "at": 0}
road = {"k": "line", "path": ROAD, "color": "#FFD000", "at": 0, "glow": True}
inf = {"k": "arrow", "path": PATH, "color": "red", "at": 0.3, "width": 0.7}
HR = {"k": "marker", "p": "hyeonri", "color": "blue", "at": 0}
OM = {"k": "marker", "p": "omachi", "color": "red", "at": 0}
lock = {"k": "lock", "p": "omachi", "at": 0.3, "text": "오마치고개"}
U = lambda p, t, c="blue", at=0.2, **kw: dict({"k": "unit", "p": p, "color": c, "text": t, "at": at}, **kw)
D3 = U([128.47, 38.14], "제3사단"); D9 = U([128.33, 38.1], "제9사단"); D7 = U([128.13, 38.07], "제7사단"); D5 = U([127.93, 38.03], "제5사단")
red_a = lambda path, at=0.3, w=0.9: {"k": "arrow", "path": path, "color": "red", "at": at, "width": w}
NOTE = "위치·경로 개략"
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]

# ===== 콜드 오프닝 (제1막 전반) =====
sc(2, ai("pass_night"), label=DRAMA, callouts=top("1951. 5. 17 새벽 4시 · 강원도 인제"))
sc(2, ai("pva_company"), label=DRAMA)
sc(1, m("east", "zoom", [lock, HR]))
sc(2, m("bt", "bt", [front, D3, D9, HR, OM]), callouts=top("국군 제3군단 (제3·9사단)", "blue"))
sc(1, ai("trucks_left"), label=DRAMA)
sc(1, black("지도에서 사라진", "제3군단"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(1, {"type": "titlecard", "title": "현리 전투", "sub": "오마치고개의 비극 · 1951", "at": 0, "q": pin("soyang")}, flash=True, sfx=[{"id": "boom", "at": 0, "volume": 0.5}])
sc(2, text("병력도 장비도 멀쩡했다", "yellow", "그런데 왜"))
sc(1, black("고개 하나에", "무너진 군대"))
sc(1, m("zoom", "zoom", [road, HR, lock], tilt=26))
# ===== 제1막 =====
sc(3, m("koreaN", "koreaN", [{"k": "front", "path": [[126.5, 37.85], [127.2, 38.1], [128.0, 38.05], [128.6, 38.4]], "at": 0}, {"k": "marker", "p": "seoul", "color": "yellow", "at": 0.5}, red_a([[126.9, 38.5], [126.95, 38.0], [127.0, 37.65]], 1.0, 1.4)]),
   chapter={"num": "제1막", "title": "섬멸의 표적"}, callouts=top("1951. 4. 22 · 약 30만 명 (4월 공세)", "red"))
sc(2, ph("offensive_map"), label="1951년 중공군 춘계 공세 상황도")
sc(2, ph("peng", "50% 45%"), label="중공군 사령관 펑더화이")
sc(1, text("국군만 골라서", "red", "미군보다 화력이 약한 부대"))
sc(1, ai("pva_east"), label=DRAMA)
sc(1, cmp("중공군", "13만 8천", "북한군", "3만 8천", "red", "red"), callouts=[{"text": "서방 측 집계", "style": "dark", "at": 1, "pos": "lower"}])
sc(1, text("기록마다 다른 규모", "yellow", "우리 쪽 기록은 훨씬 크게 적음"))
sc(3, ai("recon_map"), label=DRAMA)
sc(2, m("east", "east", [front, D5, D7]), callouts=top("미 제10군단 (제5·7사단 포함) · " + NOTE, "blue"))
sc(2, m("east", "bt", [front, D5, D7, D9, D3]), callouts=top("국군 제3군단 구역 · 인제", "blue"))
sc(2, m("east", "east", [front, {"k": "arrow", "path": [[128.3, 38.15], [128.33, 38.32]], "color": "blue", "at": 0.3, "width": 0.8}, {"k": "arrow", "path": [[128.5, 38.25], [128.55, 38.42]], "color": "blue", "at": 0.6, "width": 0.8}]), callouts=top("5월 초 · 미주리선으로 북진", "blue"))
sc(1, text("국군만으로 충분하다", "yellow", "당시 동부 전선 판단"))
sc(1, black("그 판단이", "적의 계산과 맞았다"))
sc(2, m("east", "bt", [front, D9, D3, U([128.2, 38.21], "중공군 제20군", "red"), U([127.98, 38.21], "중공군 제27군", "red", 0.5), U([128.6, 38.21], "북한군 제5군단", "red", 0.8)]))
sc(2, m("bt", "bt", [front, D9, D3, red_a([[128.33, 38.3], [128.33, 38.2]]), red_a([[128.48, 38.33], [128.47, 38.22]], 0.5), inf]))
sc(1, m("bt", "zoom", [road, lock]))
next_act()

# ===== 제2막 =====
sc(2, m("east", "zoom", [HR], tilt=26), chapter={"num": "제2막", "title": "오마치고개의 함정"})
sc(2, m("bt", "bt", [front, D9, D3, HR]), callouts=top("제9사단장 최석 · 제3사단장 김종오", "blue"))
sc(2, m("bt", "bt", [front, road, HR]), callouts=top("군단의 유일한 보급로"))
sc(2, m("zoom", "zoom", [road, HR, lock], tilt=26), callouts=top(NOTE, "dark"))
sc(2, ai("omi_today"), label=DRAMA, callouts=top("오늘의 이름 · 오미재"))
sc(2, ai("trucks_pass"), label=DRAMA)
sc(3, ai("bottle"), label=DRAMA)
sc(2, black("왜 직접", "지키지 않았을까"))
sc(2, m("bt", "bt", [front, road, OM, HR, {"k": "line", "path": BND, "color": "#FF4B4B", "at": 0.2, "glow": True}, {"k": "badge", "p": [128.2, 37.96], "text": "미 제10군단 구역", "color": "red", "at": 0.6, "dy": 0}]), callouts=top("군단 경계선 · " + NOTE, "red"))
sc(1, black("자기 퇴로가", "남의 구역에"), sfx=[{"id": "hit", "at": 0.5, "volume": 0.4}])
sc(2, ai("yu_map"), label=DRAMA, callouts=top("제3군단장 유재흥 소장"))
sc(1, ph("almond", "50% 5%"), label="브리핑 중인 알몬드 등 미군 지휘부 (1950. 9. 17)", callouts=[{"text": "기록·증언 기준으로 전해짐", "style": "dark", "at": 0, "pos": "lower"}])
sc(2, text("경계선 = 가장 약한 곳", "red"))
sc(1, m("zoom", "zoom", [road, {"k": "lock", "p": "omachi", "at": 0.2, "text": "방비 허술"}], tilt=26))
sc(2, ai("road_only"), label=DRAMA)
sc(1, ph("rok_gun", "50% 0%"), label="105mm 포를 손질하는 국군 포병 (1950. 9)")
sc(2, cmp("국군", "도로 의존", "중공군", "산악 도보"))
sc(2, ai("pva_ridge"), label=DRAMA)
sc(1, black("길이 없는 곳에서", "가장 빠른 군대"))
sc(1, m("zoom", "zoom", [road, OM], tilt=26), callouts=top("1951년 5월 중순"))
next_act()

# ===== 제3막 =====
MID = [nid()]
sc(1, black("제3막", "28km 야간 침투"), pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(1, ai("barrage"), label=DRAMA, chapter={"num": "제3막", "title": "야간 침투, 28km"}, callouts=top("5. 16 오후 4시경", "red"), sfx=[{"id": "boom", "at": 0.3, "volume": 0.4}])
sc(2, m("bt", "bt", [front, D7, D9, D3, {"k": "shock", "pts": [[128.12, 38.13], [128.08, 38.12], [128.17, 38.14]], "at": 0.2, "period": 0.7}]))
sc(1, m("bt", "bt", [front, D7, red_a([[128.1, 38.3], [128.11, 38.17]], 0, 1.3), red_a([[128.02, 38.28], [128.08, 38.16]], 0.2, 1.1), red_a([[128.2, 38.28], [128.15, 38.17]], 0.4, 1.1)]), callouts=top("제7사단 정면 · 중공군 3개 사단", "red"))
sc(3, m("bt", "zoom", [road, lock, D7]))
sc(1, ai("seventh_chaos"), label=DRAMA, callouts=top("저녁 8시경 · 통신 두절", "red"))
sc(1, m("east", "east", [front, D5, red_a([[127.93, 38.25], [127.93, 38.0]])]))
sc(2, black("전선에", "구멍이 뚫렸다"), sfx=[{"id": "hit", "at": 0.5, "volume": 0.4}])
sc(3, {"type": "document", "org": "중공군 제20군", "head": "제60사단 제178연대 제2대대", "stamp": "임무", "rows": ["목표: 오마치고개", "임무: 퇴로 차단"], "note": "요지 · 재구성 화면"})
sc(2, ai("slip_between"), label=DRAMA)
sc(2, m("bt", "bt", [front, inf, OM]), callouts=top("28km · 기록에 따라 약 30km", "red"))
sc(2, text("칠십 리", "red", "산악 지대 · 하룻밤"))
sc(1, ai("night_march"), label=DRAMA)
sc(2, m("bt", "zoom", [inf, road, lock], tilt=26))
sc(2, ai("corps_cp"), label=DRAMA)
sc(1, m("bt", "bt", [front, D9, D3, inf]))
sc(6, {"type": "cta", "title": "지도 위의 이유를 끝까지 따라갑니다", "at": 0}, pauseBefore=0.3, sfx=[{"id": "pop", "at": 0.3, "volume": 0.45}])
sc(1, black("다시", "그 고개로"))
sc(2, ai("pass_night", "out"), label=DRAMA, callouts=top("5. 17 새벽 4시 · 첨병 중대", "red"))
sc(1, m("zoom", "zoom", [road, {"k": "marker", "p": "omachi", "color": "red", "at": 0}, {"k": "lock", "p": "omachi", "at": 0, "text": "피탈"}], tilt=26), sfx=[{"id": "hit", "at": 0.4, "volume": 0.4}])
sc(1, m("zoom", "zoom", [road, U("omachi", "제178연대 제2대대", "red", 0.1, pulse=True)], tilt=26), callouts=top("아침 7시 · 대대 주력 도착", "red"))
sc(2, black("코르크 마개가", "끼워졌다"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
next_act()

# ===== 제4막 =====
sc(2, m("bt", "bt", [front, {"k": "arrow", "path": [[128.33, 38.1], [128.32, 37.98]], "color": "blue", "at": 0.2, "width": 0.8}, {"k": "arrow", "path": [[128.47, 38.14], [128.34, 37.98]], "color": "blue", "at": 0.6, "width": 0.8}, HR, OM]), chapter={"num": "제4막", "title": "퇴로 차단과 공황"})
sc(2, m("bt", "zoom", [U("hyeonri", "제3군단 집결", "blue", 0.2, pulse=True), OM], tilt=26), callouts=[{"text": "5. 17 오후 1시경", "style": "blue", "at": 0, "pos": "lower"}])
sc(1, m("zoom", "zoom", [road, OM, {"k": "lock", "p": "omachi", "at": 0.2, "text": "이미 피탈"}], tilt=26), sid="s70b")
sc(1, text("현리에 뒤엉킨 부대들", "yellow", "제3·9사단 · 군단 직할 · 제7사단 제5연대 · 수도사단 일부"))
sc(2, ai("basin_jam"), label=DRAMA, callouts=top("2만 5천 명 안팎으로 전해짐"))
sc(2, black("오마치고개가", "적에게 넘어갔다"), sfx=[{"id": "hit", "at": 0.5, "volume": 0.4}])
sc(1, ai("rumor"), label=DRAMA)
sc(2, m("zoom", "zoom", [road, U("omachi", "적 1개 대대", "red"), U("hyeonri", "아군 2개 사단", "blue", 0.5)], tilt=26))
sc(2, cmp("현리", "2개 사단", "오마치고개", "1개 대대"))
sc(2, black("왜", "뚫지 못했을까"))
sc(3, ai("radio_dead"), label=DRAMA)
sc(2, ai("liaison_land"), label=DRAMA, callouts=top("유재흥 · 최석 · 김종오"))
sc(2, m("zoom", "zoom", [road, HR, OM, {"k": "arrow", "path": [[128.313, 37.95], [128.298, 37.936]], "color": "blue", "at": 0.3, "width": 0.5}], tilt=26), hudCta={"at": 0, "dur": 7.5})
sc(1, text("제30연대 + 제18연대", "yellow", "오마치 돌파 부대"))
sc(1, ai("liaison_fly"), label=DRAMA)
sc(1, ai("watch_plane"), label=DRAMA)
sc(2, black("군단장이", "도망쳤다"), sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(3, text("사실과 다른 소문", "yellow", "그러나 병사들은 믿어 버렸다"))
sc(1, m("zoom", "zoom", [road, OM, {"k": "arrow", "path": [[128.313, 37.95], [128.298, 37.936]], "color": "blue", "at": 0.1, "width": 0.7}], tilt=26), callouts=top("5. 17 오후 5시 30분경 · 돌파 시도", "blue"))
sc(2, m("bt", "cut", [road, U("omachi", "중공군", "red"), U("chimgyo", "중공군", "red", 0.5), {"k": "lock", "p": "chimgyo", "at": 0.8, "text": "침교"}]), callouts=top("2개 사단 규모로 증강 · 이중 차단", "red"))
sc(2, ai("attack_fizzle"), label=DRAMA)
sc(1, black("다른 선택지는", "없었을까"))
sc(3, m("zoom", "zoom", [HR, {"k": "radar", "p": "hyeonri", "at": 0.2, "size": 0.25, "color": "#00E5FF", "text": "사주 방어안"}], tilt=26))
sc(2, cmp("몇 시간 전", "1개 대대", "지금", "2개 사단 규모", "blue", "red"))
sc(1, ai("guns_close"), label=DRAMA)
sc(2, black("앞은 막혔고", "뒤는 밀려온다"))
next_act()

# ===== 제5막 =====
MID.append(nid())
sc(1, black("제5막", "방태산의 비극"), pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, m("zoom", "bang", [HR, {"k": "marker", "p": "bangtae", "color": "yellow", "at": 0.2}, {"k": "badge", "p": "bangtae", "text": "1,436m", "color": "red", "at": 0.5, "dy": -50}]), chapter={"num": "제5막", "title": "방태산의 비극"})
sc(2, ai("mountain_wall"), label=DRAMA)
sc(2, ai("destroy_gear"), label=DRAMA, callouts=top("장비 파기 명령", "red"))
sc(2, ai("scatter_up"), label=DRAMA)
sc(2, ph("wreck"), label="파괴되어 버려진 트럭과 155mm 곡사포 (한국전쟁)")
sc(2, ai("hide_mortar"), label=DRAMA)
sc(2, ph("napalm"), label="네이팜 폭격 (한국전쟁)", callouts=top("버려진 장비에 아군 폭격", "red"))
sc(2, ai("lost_valley"), label=DRAMA)
sc(1, quote("참전자 회고 요지", "지휘 체계가 무너지고 소규모로 흩어졌다"))
sc(1, text("계급장을 뗀 장교들", "red", "참전자 증언"))
sc(1, black("군대가", "무리로 돌아갔다"))
sc(1, quote("당시 학도병의 회고 요지", "지휘부 탈출 소문에 사기가 바닥까지"))
sc(2, ai("straggler_ridge"), label=DRAMA)
sc(2, ai("riceball"), label=DRAMA, callouts=top("전해지는 이야기"))
sc(2, m("flee", "flee", [{"k": "arrow", "path": [[128.33, 37.95], [128.42, 37.83], [128.53, 37.68]], "color": "yellow", "at": 0.2, "width": 1.0}, {"k": "marker", "p": "bangtae", "color": "yellow", "at": 0}, {"k": "marker", "p": "hajinbu", "color": "blue", "at": 0.6}]), callouts=top("약 70km 패주 · " + NOTE, "red"))
sc(1, m("flee", "flee", [U("hajinbu", "제3군단 잔여", "blue", 0.1, pulse=True)]), callouts=top("5. 19 오후", "blue"))
sc(1, ai("roll_call"), label=DRAMA)
sc(1, {"type": "bars", "note": "5월 20일 하진부리 집결 비율 · 한국 측 기록", "items": [{"label": "제9사단", "value": 40, "display": "40%", "color": "blue", "at": 0}, {"label": "제3사단", "value": 34.2, "display": "34.2%", "color": "red", "at": 0.5}]})
sc(2, ai("empty_ranks"), label=DRAMA)
sc(1, text("5월 27일까지 약 70% 수습", "yellow", "낙오병이 뒤늦게 복귀"))
sc(2, ai("stragglers"), label=DRAMA)
sc(2, black("비극은", "끝나지 않았다"))
next_act()

# ===== 제6막 =====
sc(1, ph("vanfleet", "50% 20%"), label="미 제8군 사령관 밴 플리트 (왼쪽)", chapter={"num": "제6막", "title": "뼈아픈 대가"})
sc(2, black("더 이상", "물러서지 마라"), sfx=[{"id": "hit", "at": 0.5, "volume": 0.4}])
sc(2, m("east", "east", [{"k": "marker", "p": "hajinbu", "color": "blue", "at": 0}, red_a([[128.4, 37.95], [128.6, 37.8], [128.85, 37.75]]), {"k": "marker", "p": "gangneung", "color": "yellow", "at": 0.5}]), callouts=top("동해안 제1군단 고립 위기", "red"))
sc(2, m("south", "south", [{"k": "marker", "p": "hajinbu", "color": "blue", "at": 0}, {"k": "arrow", "path": [[128.56, 37.63], [128.46, 37.2]], "color": "yellow", "at": 0.3, "width": 0.8}, {"k": "marker", "p": "daehwa", "color": "yellow", "at": 0.6}, {"k": "marker", "p": "yeongwol", "color": "yellow", "at": 0.9}]), callouts=[{"text": "5. 21 · 다시 철수", "style": "red", "at": 0, "pos": "lower"}])
sc(2, ai("vanfleet_angry"), label=DRAMA)
sc(2, text("하진부리의 재붕괴", "red", "해체를 부른 마지막 방아쇠"))
sc(1, m("east", "east", [front, {"k": "badge", "p": [128.5, 37.95], "text": "구역 인계", "color": "red", "at": 0.3, "dy": 0}]), callouts=top("5. 21 오후 6시", "red"))
sc(2, ai("meeting"), label=DRAMA, callouts=top("널리 전해지는 일화"))
sc(2, quote("밴 플리트 · 전해지는 대화", "당신의 군단은 어디에 있소"))
sc(2, quote("밴 플리트 · 전해지는 대화", "포와 수송 장비를 모두 잃었다는 말이오"))
sc(1, ai("meeting", "out"), label=DRAMA)
sc(1, black("당신의 군단을", "해체하겠소"), sfx=[{"id": "boom", "at": 0.5, "volume": 0.45}])
sc(2, text("1951. 5. 26 해체", "red", "창설 약 8개월 만"))
sc(1, ai("yu_alone", "out"), sid="s129b", label=DRAMA)
sc(2, black("이 패전 때문에", "작전권이 넘어갔다?"))
sc(2, {"type": "timeline", "items": [{"date": "1950. 7", "text": "작전 통제권 이양", "at": 0}, {"date": "1951. 5", "text": "제3군단 해체", "at": 0.6}]})
sc(2, ai("yu_alone"), label=DRAMA)
sc(1, black("그러나", "후폭풍은 있었다"))
sc(1, text("미 제8군 직접 통제", "red", "육군본부 작전 지휘권 축소 · 제1군단 포함"))
sc(1, ai("hq_map_dim"), label=DRAMA)
sc(1, m("east", "east", [front]))
sc(1, m("east", "east", [U([127.98, 37.9], "미 제2사단", "blue"), U([128.75, 37.95], "국군 제1군단", "blue", 0.5)]))
sc(2, m("east", "flee", [{"k": "arrow", "path": [[127.95, 37.55], [128.25, 37.6], [128.47, 37.63]], "color": "blue", "at": 0.2, "width": 1.0}, {"k": "marker", "p": "soksa", "color": "blue", "at": 0.8}]), callouts=top("미 제3사단 · 속사리", "blue"))
sc(2, ph("long_tom"), label="미군 155mm 롱 톰 포격 (한국전쟁)")
sc(1, m("east", "east", [{"k": "arrow", "path": [[128.1, 37.7], [128.15, 38.05]], "color": "blue", "at": 0.3, "width": 1.2}]), callouts=top("유엔군 반격", "blue"))
sc(2, text("기대에 못 미친 전과", "yellow", "중공군 종군기자 회고 · 5천 명 안팎"), sid="s140b")
sc(2, m("east", "east", [{"k": "arrow", "path": [[128.0, 37.8], [128.05, 38.2]], "color": "blue", "at": 0.1, "width": 1.2}, {"k": "arrow", "path": [[128.45, 37.85], [128.45, 38.2]], "color": "blue", "at": 0.4, "width": 1.2}]))
next_act()

# ===== 제7막 =====
MID.append(nid())
sc(1, black("제7막", "고개 하나의 교훈"), pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(1, cmp("병력 손실", "약 30%", "장비 손실", "약 70%", "red", "red"), chapter={"num": "제7막", "title": "고개 하나의 교훈"}, callouts=[{"text": "평가 기준 · 자료마다 차이", "style": "dark", "at": 1, "pos": "lower"}])
sc(2, ai("destroy_gear", "out"), label=DRAMA)
sc(1, black("현리는", "왜 무너졌나"))
sc(1, {"type": "factors", "head": "현리 패전의 네 가지 이유", "items": ["경계선", "도로에 묶인 군대", "시간", "지휘"], "at": 0})
sc(2, m("bt", "bt", [road, OM, {"k": "line", "path": BND, "color": "#FF4B4B", "at": 0, "glow": True}]), callouts=top("첫째 · 경계선", "red"))
sc(2, ai("trucks_left", "out"), label=DRAMA, callouts=top("둘째 · 도로에 묶인 군대", "red"))
sc(3, m("zoom", "zoom", [road, U("omachi", "대대 → 사단", "red", 0.3)], tilt=26), callouts=top("셋째 · 시간", "red"))
sc(5, {"type": "timeline", "items": [{"date": "5. 16 16시", "text": "공격 개시", "at": 0}, {"date": "5. 17 04시", "text": "고개 피탈", "at": 0.4}, {"date": "5. 17 17:30", "text": "돌파 시도", "at": 0.8}]}, sid="s149b")
sc(2, ai("radio_dead", "out"), label=DRAMA, callouts=top("넷째 · 지휘", "red"))
sc(1, black("비교해 볼", "전투"))
sc(2, ph("chosin"), label="장진호에서 철수하는 미 해병대 (1950. 12)")
sc(1, text("지휘가 살아 있으면", "yellow", "군대는 군대로 남는다"))
sc(2, black("무너진 건", "안쪽이었다"))
sc(2, ai("dawn_valley"), label=DRAMA)
sc(2, ph("training"), label="교육훈련 중인 국군 (1952. 11)", callouts=top("제9사단 · 1951년 8월부터 8주 야전 훈련"))
sc(1, m("east", "koreaN", [{"k": "marker", "p": "baekma", "color": "yellow", "at": 0.5}]), callouts=top("1952. 10 · 철원 서쪽 395고지"))
sc(2, ph("whitehorse"), label="백마고지 전적지 위령탑")
sc(2, black("같은 사단", "다른 군대"))
sc(2, ai("memorial"), label=DRAMA, callouts=top("인제군 현리 · 위령비"))
sc(2, ai("omi_today", "out"), label=DRAMA)
sc(1, m("koreaN", "cw", [{"k": "marker", "p": "gimhwa", "color": "yellow", "at": 0.4}]), callouts=top("다음 전장 · 강원도 금화"))
sc(1, black("EP 25", "수도고지 · 지형능선"), sfx=[{"id": "boom", "at": 0.5, "volume": 0.4}])
sc(2, ai("next_hill"), label=DRAMA, callouts=top("1952년 여름~가을 · 99일"))
sc(1, {"type": "cta", "title": "구독 · 알림으로 다음 편에서 만나요", "at": 0}, sfx=[{"id": "pop", "at": 0.2, "volume": 0.45}])
sc(1, {"type": "endcard", "title": "1951년 5월, 현리.\n돌아오지 못한 이들을 기억하며.", "q": pin("soyang")}, tail=1.0)
assert CUR["i"] == len(ACTS[6])

CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
KR = "South Korean soldiers whose heads are round balls painted as the South Korean Taegukgi flag, wearing plain olive American-style 1951 field uniforms and M1 steel helmets, NO stars and NO red insignia anywhere"
KR1 = "a South Korean soldier whose head is a round ball painted as the South Korean Taegukgi flag, wearing a plain olive American-style 1951 field uniform and M1 steel helmet, NO stars and NO red insignia anywhere"
OF = "a South Korean army general whose head is a round ball painted as the South Korean Taegukgi flag, wearing a plain khaki American-style field uniform with no collar tabs, no shoulder boards, no stars, no medals and absolutely no red on the uniform"
CN = "Chinese soldiers whose heads are round balls painted as the flag of the People's Republic of China, wearing padded mustard-khaki uniforms and soft caps, carrying rifles and rice bags"
US = "an American general whose head is a round ball painted as the USA flag, wearing a 1951 US Army field jacket"
END = ", leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
KR2 = KR.replace("NO stars and NO red insignia anywhere", "absolutely NO collar tabs, NO shoulder patches, NO arm patches, NO stars, and NO red anywhere on the uniform")
KR12 = KR1.replace("NO stars and NO red insignia anywhere", "absolutely NO collar tabs, NO shoulder patches, NO arm patches, NO stars, and NO red anywhere on the uniform")
LAND = "painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no people visible, no text, no letters."
AI = {
    "pass_night": CB + CN + " standing on a dark mountain pass with a single dirt road before dawn, blue-grey light, mountains behind" + END,
    "pva_company": CB + "a small company of " + CN + " spreading out quietly along a mountain road, setting a roadblock with logs, pre-dawn" + END,
    "trucks_left": "A line of abandoned 1950s American military trucks and towed howitzers left on a narrow Korean mountain road, doors open, mist, " + LAND,
    "pva_east": CB + "long columns of " + CN + " marching east at night through Korean mountains, avoiding the road, moonless sky" + END,
    "recon_map": CB + US + " and an American staff officer frowning over a large map of Korea with scattered reconnaissance photographs, lamp light" + END,
    "omi_today": "A quiet modern two-lane road winding over a gentle forested mountain pass in Gangwon Province, Korea, soft morning light, " + LAND,
    "trucks_pass": "A convoy of 1950s military trucks crawling up a narrow dirt road over a forested Korean mountain pass between pine-covered ridges, no rock arches, dust, " + LAND.replace("no people visible, ", ""),
    "bottle": CB + "a huge glass bottle lying on a table-top relief map of mountains, tiny " + KR + " crowded inside it, a giant cork hovering above the narrow neck" + END,
    "yu_map": CB + OF + " pointing at a field map in a tent command post, worried face, lantern" + END,
    "road_only": CB + KR + " pushing a truck and a towed howitzer on a muddy one-lane mountain road, steep slopes both sides" + END,
    "pva_ridge": CB + CN + " walking in single file along a steep forested ridgeline with no road, looking down at a distant valley road" + END,
    "barrage": "Artillery shells bursting along Korean mountain ridges at late afternoon, plumes of earth and smoke, a river valley below, " + LAND,
    "seventh_chaos": CB + KR2 + " falling back from a hilltop trench at dusk under fire, a radio operator shouting into a dead handset" + END,
    "slip_between": CB + CN + " quietly slipping through a dark valley between two hilltop positions, campfires of the unaware defenders visible on the ridges above" + END,
    "night_march": CB + CN + " marching fast along a dark mountain trail at night, carrying rifles and ammunition, exhausted but relentless" + END,
    "corps_cp": CB + OF + " and two South Korean staff officers with the same flag-ball heads around a map with blank areas in a command tent at night, telephones lying unanswered" + END,
    "basin_jam": "A narrow Korean mountain basin packed with 1950s military trucks, howitzers, and crowds of soldiers in a chaotic traffic jam, dust, afternoon, painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no text, no letters.",
    "rumor": CB + KR2 + " whispering to each other in a crowded column, one pointing back toward the mountains, fear on their faces" + END,
    "radio_dead": CB + KR12 + " cranking a field telephone and shouting into a radio in a cramped trench, cut wires on the ground, static sparks" + END,
    "liaison_land": CB + OF + " stepping out of a small 1950s liaison airplane on a dirt strip in a mountain valley, officers saluting" + END,
    "liaison_fly": "A small single-engine liaison airplane taking off from a dirt strip in a crowded Korean mountain valley, afternoon, " + LAND.replace("no people visible, ", ""),
    "watch_plane": CB + KR + " on the ground looking up at a small airplane flying away, seen from behind, dread in their posture" + END,
    "attack_fizzle": CB + KR + " halted on a road near a pass at dusk, officers looking for missing units, radio dead, confusion" + END,
    "guns_close": "Muzzle flashes and shell bursts approaching over dark mountain ridges behind a crowded valley at dusk, " + LAND,
    "mountain_wall": "A massive dark forested mountain rising above a small Korean valley at dusk, mist on its slopes, " + LAND,
    "destroy_gear": CB + KR + " sadly disabling a howitzer and setting fire to trucks on a mountain road at dusk" + END,
    "scatter_up": CB + KR + " climbing a steep forested mountain slope in disorder, no formation, dropping helmets and packs" + END,
    "hide_mortar": CB + KR + " hiding a mortar tube under a large rock on a forested mountain slope, covering it with branches" + END,
    "lost_valley": CB + KR12 + " alone in a deep forested valley at dusk, lost, looking around, no map, hungry" + END,
    "straggler_ridge": CB + "many " + KR + " scattered in small groups across several forested ridgelines, no formation, walking in different directions, dusk" + END,
    "riceball": CB + KR + " finding a few rice balls left on a flat rock beside a mountain trail, surprised and grateful, forest around" + END,
    "roll_call": CB + "a thin line of " + KR + " at roll call in a village square, large gaps in the ranks, an officer with a list" + END,
    "empty_ranks": CB + "a few " + KR2 + " sitting exhausted by a stream in a mountain village, many empty places around them, bandages" + END,
    "stragglers": CB + KR2 + " straggling one by one out of the forest onto a road, thin and tired, a sentry waving them in" + END,
    "vanfleet_angry": CB + US + " alone, furious, slamming his fist on a map table in a headquarters tent, nobody else in the scene, no other flags" + END,
    "meeting": CB + US + " questioning " + OF + " across a bare table in a tent, tense silence, the Korean general looking down" + END,
    "yu_alone": CB + OF.replace("absolutely no red on the uniform", "absolutely no red anywhere on the uniform, plain collar") + " standing alone in an empty command tent, a folded flag on the table, dim light" + END,
    "hq_map_dim": CB + "South Korean staff officers, heads round balls painted as the Taegukgi flag, plain khaki uniforms with no insignia, watching American officers take a map off their wall" + END,
    "dawn_valley": "A quiet Korean mountain valley at dawn, mist lifting, a few rusted wheel marks in a dirt road, " + LAND,
    "memorial": "A simple stone war memorial on a small hill in a Korean mountain village, white chrysanthemums at its base, soft afternoon light, " + LAND.replace("no text, no letters.", "no text, no letters, the stone is blank."),
    "next_hill": CB + KR + " holding a bare, shell-torn hilltop under fire, determined, flying dirt, a trench line" + END,
    "thumb_subject": "Photorealistic black-and-white 1951 Korean War documentary portrait of an exhausted young Korean man, clearly East Asian Korean face with black hair, a South Korean army soldier in a plain olive field jacket with no insignia and an M1 steel helmet, soot and sweat on his face, hollow anguished eyes looking into the distance, waist-up, face clearly visible and turned slightly toward the left of the frame, isolated on a plain pure white background, no shadows on the background, no text.",
}
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
board = {"title": "현리 전투", "subtitle": "1951. 5. 16 ~ 26", "target_sec": 1290, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap], "ai", len(used), "pins", len(PINS))
