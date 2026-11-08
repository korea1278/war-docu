# EP23 장사상륙작전 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
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
    ("천구백오십 년 구월 십사일", "1950년 9월 14일"), ("천구백오십 년 팔월", "1950년 8월"), ("천구백구십칠 년 삼월 육일", "1997년 3월 6일"), ("천구백오십일 년 팔월", "1951년 8월"),
    ("구월 이십일", "9월 20일"), ("구월 십사일", "9월 14일"), ("구월 십오일", "9월 15일"), ("구월 십육일", "9월 16일"), ("구월 십칠일", "9월 17일"), ("구월 십팔일", "9월 18일"), ("구월 십구일", "9월 19일"), ("구월 십일", "9월 10일"),
    ("새벽 다섯 시 삼십 분", "새벽 5시 30분"), ("새벽 다섯 시", "새벽 5시"), ("새벽 여섯 시", "새벽 6시"), ("오후 한 시 삼십삼 분", "오후 1시 33분"), ("오후 네 시", "오후 4시"), ("오후 세 시", "오후 3시"), ("아침 아홉 시", "아침 9시"),
    ("제백칠십사 호", "제174호"), ("백칠십사 호", "174호"), ("제사 부두", "제4부두"), ("사십칠 년", "47년"), ("칠백칠십이", "772"), ("칠백여 명", "700여 명"), ("칠백 명", "700명"), ("칠만 명", "7만 명"),
    ("제이군단", "제2군단"), ("제일군단", "제1군단"), ("제일유격대대", "제1유격대대"), ("제일중대", "제1중대"), ("제이중대", "제2중대"), ("제삼중대", "제3중대"), ("제오중대", "제5중대"), ("오소대", "5소대"), ("이 개 연대", "2개 연대"),
    ("엘에스티", "LST"), ("특공조 일곱 명", "특공조 7명"), ("일곱 명이", "7명이"), ("삼십 미터", "30미터"), ("사 킬로미터", "4km"), ("네 가닥", "4가닥"), ("오 인치", "5인치"),
    ("이백칠십일 고지", "271고지"), ("이백 고지", "200고지"), ("칠번 국도", "7번 국도"), ("교량 두 곳", "교량 2곳"), ("도로 여섯 곳", "도로 6곳"), ("토치카 아홉 곳", "토치카 9곳"),
    ("육십여 명", "60여 명"), ("구십여 명", "90여 명"), ("삼십 명", "30명"), ("서른아홉 명", "39명"), ("서른두 명", "32명"), ("육백사십여 명", "640여 명"), ("백삼십구 명", "139명"), ("구십이 명", "92명"),
    ("칠백육십사 명", "764명"), ("칠백육십 명", "760명"), ("이백칠십여 명", "270여 명"), ("포로 네 명", "포로 4명"), ("십팔 일", "18일"), ("일만 오천 명", "1만 5천 명"), ("이십사 화", "24화"), ("이 주 남짓", "2주 남짓"),
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


PH = {
    "munsan": "Changsadong Raid.jpg",
    "helena": "USS Helena (CA-75) firing at Chongjin, North Korea, on 12-13 October 1950 (NH 95822).jpg",
    "students": "한국전쟁-학도병 입대 (7445955888).jpg",
    "kezia": "Kezia 1950 track.png",
    "macarthur": "IncheonLandingMcArthur.jpg",
    "inchon_ladder": "Marines Landing at Inchon, Korea, 15 September 1950 (6185783412).jpg",
    "inchon_wave": "First wave landing craft approach Inchon, Korea, on 15 September 1950 (NH 96877).jpg",
    "t34": "North Korean T-34 tank (34641404212).jpg",
    "yongdok": "SC 345344 FEC-50-5046 - 29 July 1950 (52568421695).jpg",
    "wounded": "SC 343168 FEC-50-3525 - 1 July 1950 (52562477059).jpg",
    "lst": "USS LST-1123.jpg",
    "memorial": "KMEP 24 2 - Culture Tour (8596648).jpg",
}


def pin(key):
    sid = nid()
    PINS[f"{sid}-photo#0"] = "File:" + PH[key]
    return f"{sid}-photo"


def ph(key, pos=None):
    v = {"type": "photo", "kb": "in", "q": pin(key)}
    if pos:
        v["pos"] = pos
    return v


DRAMA = "재연 일러스트"
P = {
    "seoul": [126.978, 37.566, "서울"], "incheon": [126.62, 37.46, "인천"], "gunsan": [126.71, 35.97, "군산"], "busan": [129.04, 35.1, "부산"],
    "daegu": [128.6, 35.87, "대구"], "miryang": [128.75, 35.5, "밀양"], "pohang": [129.36, 36.03, "포항"], "angang": [129.23, 35.99, "안강"], "gyeongju": [129.21, 35.85, "경주"],
    "yeongdeok": [129.365, 36.415, "영덕"], "samcheok": [129.165, 37.45, "삼척"], "yanggu": [127.99, 38.11, "양구"],
    "jangsa": [129.376, 36.282, "장사리"], "munsan": [129.3815, 36.2815, "문산호"], "h200": [129.364, 36.276, "200고지"], "h271": [129.353, 36.293, "271고지"],
    "gang": [129.385, 36.36, "강구"],
}
V = {
    "korea": {"center": [127.8, 36.9], "span": 5.6}, "south": {"center": [128.8, 35.95], "span": 2.0},
    "koreaC": {"center": [127.8, 36.35], "span": 5.6}, "koreaN": {"center": [127.8, 37.35], "span": 5.6}, "ef": {"center": [129.3, 36.12], "span": 1.05}, "wide": {"center": [129.35, 36.285], "span": 0.26},
    "zoom": {"center": [129.371, 36.282], "span": 0.1},
}
PERI = [[128.42, 35.1], [128.35, 35.4], [128.42, 35.75], [128.5, 36.05], [128.85, 36.18], [129.15, 36.1], [129.45, 36.13]]
RT7 = [[129.345, 36.04], [129.35, 36.11], [129.38, 36.2], [129.369, 36.25], [129.37, 36.285], [129.382, 36.33], [129.385, 36.36], [129.365, 36.415]]
SHIP = [[129.3805, 36.2795], [129.3825, 36.2835]]
BLUE = "#00E5FF"


def o(p, n, text=None, at=0, **kw):
    d = {"k": "obj", "p": p, "n": n, "at": at}
    if text:
        d["text"] = text
    d.update(kw)
    return d


def ship(at=0):
    return [{"k": "line", "path": SHIP, "color": "#FFD000", "at": at, "glow": True}, {"k": "badge", "p": "munsan", "text": "문산호", "color": "blue", "at": at + 0.4, "dy": -60}]


rt7 = {"k": "line", "path": RT7, "color": "#FFD000", "at": 0, "glow": True}
H200 = o("h200", "200", "200고지")
PROF = {"type": "profile", "pts": [[0, 0], [0.06, 0], [0.1, 6], [0.18, 16], [0.3, 60], [0.42, 130], [0.52, 200], [0.6, 165], [0.7, 150], [0.82, 215], [0.92, 271], [1, 240]],
        "grid": [100, 200], "left": "동해", "right": "내륙", "note": "장사리 해안 단면 모식도 · 고도·거리 개략"}
red_n = {"k": "arrow", "path": [[129.385, 36.4], [129.382, 36.33], [129.372, 36.295]], "color": "red", "at": 0.3, "width": 0.7}

# ===== 제1막 =====
sc(2, ai("parade_boys"), label=DRAMA, callouts=[{"text": "1950. 9. 14 아침 · 부산", "style": "yellow", "at": 0, "pos": "top"}])
sc(3, ai("envelope"), label=DRAMA)
sc(2, ai("cut_hair"), label=DRAMA)
sc(2, {"type": "quotes", "title": "학도병 이영희 노병의 증언", "items": [{"text": "그 뜻을, 나중에야 알았다", "at": 0}]})
sc(2, {"type": "black", "text": "머리카락과 손톱", "accent": "살아서 남기는 유품", "accentAt": 0.5}, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, {"type": "text", "big": "버려진 봉투", "style": "red", "sub": "노병이 한참 뒤에야 들은 이야기", "subAt": 0.4})
sc(3, ai("busan_depart"), label=DRAMA, callouts=[{"text": "오후 4시 · 부산항 제4부두", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, {"type": "titlecard", "title": "장사상륙작전", "sub": "772명 문산호 결사대 · 1950", "at": 0, "q": pin("munsan")}, flash=True, sfx=[{"id": "boom", "at": 0, "volume": 0.5}])
sc(3, m("korea", "south", [{"k": "front", "path": PERI, "at": 0}, {"k": "marker", "p": "busan", "color": "blue", "at": 0.5}, {"k": "marker", "p": "daegu", "color": "blue", "at": 0.8}]),
   chapter={"num": "제1막", "title": "작전명 174호"}, callouts=[{"text": "1950년 8월 말 · 낙동강 방어선 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("south", "ef", [{"k": "front", "path": PERI, "at": 0}, {"k": "marker", "p": "pohang", "color": "red", "at": 0.2}, {"k": "marker", "p": "angang", "color": "red", "at": 0.4}, {"k": "marker", "p": "gyeongju", "color": "blue", "at": 0.6},
                        {"k": "arrow", "path": [[129.33, 36.2], [129.33, 36.05], [129.24, 35.9]], "color": "red", "at": 0.4, "width": 0.9}]),
   callouts=[{"text": "북한군 제2군단 · 경주·부산 위협", "style": "red", "at": 0, "pos": "top"}])
sc(2, ph("macarthur", "50% 20%"), label="인천 상륙 작전 지휘 중인 맥아더 (1950. 9)")
sc(2, {"type": "black", "text": "적이 눈치채면", "accent": "끝이다", "accentAt": 0.5})
sc(2, m("koreaC", "koreaC", [{"k": "marker", "p": "incheon", "color": "yellow", "at": 0}, {"k": "badge", "p": "gunsan", "text": "양동", "color": "red", "at": 0.5, "dy": -50}, {"k": "badge", "p": "jangsa", "text": "양동", "color": "red", "at": 1.2, "dy": -50}]))
sc(2, ai("hq_map"), label=DRAMA)
sc(3, ph("students"), label="열차로 입대하는 학도병들 (한국전쟁)")
sc(2, {"type": "text", "big": "772명", "style": "yellow", "sub": "독립 제1유격대대 · 대대장 이명흠 대위", "subAt": 0.4})
sc(3, {"type": "text", "big": "기록마다 다른 숫자", "style": "yellow", "sub": "772명 · 764명 · 760명", "subAt": 0.4}, sid="s16b")
sc(2, m("south", "south", [{"k": "marker", "p": "daegu", "color": "yellow", "at": 0.2}, {"k": "marker", "p": "miryang", "color": "blue", "at": 0.8}]), sid="s16c", callouts=[{"text": "대구에서 모병 · 밀양에서 편성", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, {"type": "document", "org": "육군본부", "head": "작전 명령 제174호", "stamp": "군사 극비 · 1950. 9. 10", "rows": ["부대: 독립 제1유격대대", "임무: 적 보급로 차단"], "note": "요지 · 재구성 화면"})
sc(2, {"type": "quotes", "title": "명령 요지", "items": [{"text": "동해안에 상륙해 적의 보급로를 끊어라", "at": 0}]})
sc(2, m("korea", "wide", [{"k": "marker", "p": "jangsa", "color": "yellow", "at": 0.2}], demSea=True), callouts=[{"text": "경북 영덕군 남정면 장사리", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, {"type": "black", "text": "명령서 어디에도", "accent": "인천은 없었다", "accentAt": 0.5}, sfx=[{"id": "hit", "at": 0.5, "volume": 0.4}])
next_act()

# ===== 제2막 =====
sc(3, ph("yongdok", "50% 15%"), label="영덕 전선 뒤의 국군 병사 (1950. 7)", chapter={"num": "제2막", "title": "태풍 속의 출항"},
   callouts=[{"text": "대원 약 80%가 18~19세 · 15세도", "style": "yellow", "at": 0, "pos": "top"}])
sc(3, ai("rice_warehouse"), label=DRAMA, callouts=[{"text": "밀양 · 약 2주 훈련", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, {"type": "black", "text": "군번도 계급도", "accent": "없었다", "accentAt": 0.5})
sc(2, ai("hands_question"), label=DRAMA)
sc(1, {"type": "quotes", "title": "학도병 류병추 노병의 기억", "items": [{"text": "손을 든 사람은 열에 하나도 안 됐다", "at": 0}]})
sc(2, ai("hands_down"), label=DRAMA)
sc(3, ph("lst"), label="해안에 뱃머리를 댄 LST들 · 원산 (1950. 10)")
sc(2, {"type": "compare", "left": {"title": "인천", "big": "수백 척", "icon": "none", "color": "blue"}, "right": {"title": "장사리", "big": "1척", "icon": "none", "color": "red", "at": 1.0}})
sc(2, {"type": "text", "big": "지원 요청 거절", "style": "red", "sub": "전차 중대 · 사전 포격 모두", "subAt": 0.4})
sc(2, ai("fake_division"), label=DRAMA)
sc(2, {"type": "text", "big": "대대 → 사단", "style": "yellow", "sub": "서류 위의 눈속임", "subAt": 0.4})
sc(3, ai("parade_boys", "out"), sid="s31b", label=DRAMA, callouts=[{"text": "9. 14 출정식 · 부산 시가지 행진", "style": "yellow", "at": 0, "pos": "top"}])
sc(3, ph("kezia"), label="태풍 케지아의 경로 (1950. 9)")
sc(3, ai("lst_storm"), label=DRAMA)
sc(2, ai("hold_seasick"), label=DRAMA)
sc(2, ai("hold_realize"), label=DRAMA)
sc(2, m("korea", "korea", [{"k": "arrow", "path": [[125.3, 35.6], [125.7, 36.8], [126.5, 37.42]], "color": "blue", "at": 0, "width": 1.6},
                           {"k": "arrow", "path": [[129.2, 35.05], [129.75, 35.7], [129.45, 36.26]], "color": "yellow", "at": 1.0, "width": 0.8}, {"k": "marker", "p": "incheon", "color": "blue", "at": 0}, {"k": "marker", "p": "jangsa", "color": "yellow", "at": 1.0}]))
sc(3, m("wide", "wide", [{"k": "marker", "p": "jangsa", "color": "yellow", "at": 0}, {"k": "arrow", "path": [[129.6, 36.22], [129.5, 36.26], [129.42, 36.28]], "color": "yellow", "at": 0.3, "width": 0.5}], demSea=True),
   callouts=[{"text": "9. 15 새벽 5시경 · 해안 4km 앞", "style": "yellow", "at": 0, "pos": "top"}])
next_act()

# ===== 제3막 =====
MID = [nid()]
sc(1, {"type": "black", "text": "제3막", "accent": "좌초된 문산호", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, ai("anchor_snap"), label=DRAMA, chapter={"num": "제3막", "title": "좌초된 문산호"}, callouts=[{"text": "새벽 5시 30분 · 닻줄 절단", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("zoom", "zoom", ship(0.2) + [{"k": "lock", "p": "munsan", "at": 1.0, "text": "해안과 나란히"}], tilt=26, demSea=True))
sc(2, ai("ship_aground"), label=DRAMA, callouts=[{"text": "새벽 6시경 · 암초에 좌초", "style": "red", "at": 0, "pos": "top"}], sfx=[{"id": "boom", "at": 0.8, "volume": 0.4}])
sc(2, ph("munsan"), label="장사 해안에 옆으로 누운 문산호 · 미 해군 촬영 (1950. 9)")
sc(3, m("zoom", "zoom", ship() + [{"k": "lock", "p": [129.374, 36.279], "at": 0.3, "text": "토치카"}, {"k": "arrow", "path": [[129.373, 36.281], [129.377, 36.2815], [129.38, 36.2815]], "color": "red", "at": 0.7, "width": 0.5}], tilt=26, demSea=True),
   callouts=[{"text": "해안 토치카의 기관총 사격 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(3, ai("deck_fire"), label=DRAMA)
sc(1, {"type": "quotes", "title": "류병추 노병", "items": [{"text": "대한민국 만세를 외치며 수장된 전우들", "at": 0}]})
sc(2, ai("crew_trapped"), label=DRAMA)
sc(3, {"type": "text", "big": "30미터", "style": "red", "sub": "해안까지 남은 거리", "subAt": 0.4})
sc(3, ai("seven_volunteer"), label=DRAMA)
sc(3, ai("swim_rope"), label=DRAMA, callouts=[{"text": "특공조 7명 · 밧줄 4가닥", "style": "yellow", "at": 1, "pos": "top"}])
sc(3, ai("rope_line"), label=DRAMA)
sc(5, {"type": "cta", "title": "잊힌 이름들을 함께 지켜 주십시오", "at": 0}, pauseBefore=0.3, sfx=[{"id": "pop", "at": 0.3, "volume": 0.45}])
sc(3, ai("lee_order"), label=DRAMA, callouts=[{"text": "“상륙하라”", "style": "yellow", "at": 2, "pos": "top"}])
sc(2, m("wide", "zoom", ship() + [{"k": "radar", "p": [129.402, 36.28], "at": 0, "size": 0.45, "color": BLUE, "text": "구축함 엔디코트"}, {"k": "shock", "pts": [[129.372, 36.279], [129.373, 36.284], [129.37, 36.281]], "at": 0.6, "period": 0.7}], demSea=True))
sc(1, ai("charge_smoke"), label=DRAMA)
next_act()

# ===== 제4막 =====
sc(2, ai("beach_hell"), label=DRAMA, chapter={"num": "제4막", "title": "7번 국도를 끊어라"})
sc(2, ai("lost_ammo"), label=DRAMA)
sc(3, ai("pillbox_grenade"), label=DRAMA)
sc(2, m("zoom", "zoom", [o([129.3745, 36.2785], "1", None, 0, takenAt=0), o([129.3755, 36.2825], "2", None, 0.3, takenAt=0), o([129.3735, 36.285], "3", None, 0.6, takenAt=0)], tilt=26, demSea=True),
   callouts=[{"text": "제1중대 · 토치카 3곳 파괴 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(2, ai("trench_melee"), label=DRAMA)
sc(2, ph("wounded"), label="부상당한 전우를 돌보는 국군 병사 (1950. 7)")
sc(2, {"type": "compare", "left": {"title": "첫날 전사", "big": "60여 명", "icon": "none", "color": "red"}, "right": {"title": "첫날 부상", "big": "90여 명", "icon": "none", "color": "red", "at": 0.6}},
   callouts=[{"text": "백운붕 대령 증언 (자료마다 차이)", "style": "dark", "at": 1, "pos": "lower"}])
sc(1, m("zoom", "zoom", ship()[:1] + [{"k": "unit", "p": "jangsa", "color": "blue", "text": "독립 제1유격대대", "at": 0, "pulse": True}], tilt=26, demSea=True), callouts=[{"text": "아침 9시경 · 상륙 완료", "style": "blue", "at": 0, "pos": "top"}])
sc(2, m("zoom", "zoom", [H200, {"k": "arrow", "path": [[129.374, 36.272], [129.366, 36.268], [129.363, 36.274]], "color": "blue", "at": 0.3, "width": 0.6}], tilt=26, demSea=True), callouts=[{"text": "제2중대 · 오른쪽 우회 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(2, dict(PROF, marks=[{"x": 0.52, "text": "200고지", "style": "blue"}, {"x": 0.92, "text": "271고지", "style": "red"}, {"x": 0.08, "text": "문산호", "style": "red"}], arrows=[{"from": 0.12, "to": 0.5, "color": "blue"}]),
   callouts=[{"text": "오후 3시경 · 200고지 점령", "style": "blue", "at": 0, "pos": "top"}])
sc(2, m("wide", "wide", [H200, o("h271", "271", "271고지", 0.4), {"k": "arrow", "path": [[129.364, 36.277], [129.36, 36.285], [129.354, 36.292]], "color": "blue", "at": 0.3, "width": 0.6}], demSea=True))
sc(2, m("wide", "wide", [H200, o("h271", "271", None, 0)], demSea=True))
sc(2, m("wide", "wide", [rt7, H200, {"k": "badge", "p": [129.378, 36.32], "text": "7번 국도", "color": "red", "at": 0.5, "dy": -40}], demSea=True), hudCta={"at": 0, "dur": 7.5})
sc(2, m("ef", "ef", [rt7, {"k": "marker", "p": "pohang", "color": "red", "at": 0}, {"k": "marker", "p": "jangsa", "color": "yellow", "at": 0}, {"k": "lock", "p": "jangsa", "at": 0.8, "text": "생명줄 차단"}]),
   callouts=[{"text": "북한군 제2군단의 보급로", "style": "red", "at": 0}])
sc(2, ai("blow_bridge"), label=DRAMA, callouts=[{"text": "교량 2곳 · 도로 6곳 파괴", "style": "yellow", "at": 1, "pos": "top"}])
sc(2, {"type": "text", "big": "토치카 9곳 파괴", "style": "yellow", "sub": "직사포 · 기관총 · 포탄 상자 노획", "subAt": 0.4})
sc(2, {"type": "black", "text": "같은 날 · 9월 15일", "accent": "인천", "accentAt": 0.6}, sfx=[{"id": "boom", "at": 0.6, "volume": 0.45}])
sc(2, ph("inchon_ladder"), label="사다리로 인천 방파제를 넘는 미 해병 (1950. 9. 15)")
sc(2, ph("inchon_wave"), label="인천으로 향하는 제1파 상륙정 (1950. 9. 15)")
sc(2, ai("waiting_trench"), label=DRAMA)
sc(2, m("wide", "wide", [rt7, H200, red_n], demSea=True), callouts=[{"text": "7번 국도 북쪽 · 적 접근 (개략)", "style": "red", "at": 0, "pos": "top"}])
next_act()

# ===== 제5막 =====
MID.append(nid())
sc(1, {"type": "black", "text": "제5막", "accent": "고립과 최후의 방어선", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, m("wide", "wide", [rt7, H200, red_n, {"k": "arrow", "path": [[129.335, 36.25], [129.35, 36.265], [129.36, 36.272]], "color": "red", "at": 0.8, "width": 0.7}], demSea=True),
   chapter={"num": "제5막", "title": "고립과 최후의 방어선"}, callouts=[{"text": "9. 15 저녁 · 북한군 반격", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("ef", "ef", [rt7, {"k": "unit", "p": [129.27, 36.28], "color": "red", "text": "북한군 2개 연대 + 전차", "at": 0.2}, {"k": "marker", "p": "jangsa", "color": "blue", "at": 0}]))
sc(3, ai("night_ring"), label=DRAMA)
sc(2, {"type": "black", "text": "탄약이", "accent": "없다", "accentAt": 0.5}, sfx=[{"id": "hit", "at": 0.5, "volume": 0.4}])
sc(2, ai("empty_ammo"), label=DRAMA)
sc(2, m("korea", "korea", [{"k": "marker", "p": "samcheok", "color": "yellow", "at": 0}, {"k": "marker", "p": "jangsa", "color": "blue", "at": 0}, {"k": "badge", "p": "samcheok", "text": "미 기동 전단 포격 명령", "color": "red", "at": 0.5, "dy": -50}]))
sc(2, ai("count_rounds"), label=DRAMA)
sc(2, ai("crew_fight"), label=DRAMA, callouts=[{"text": "문산호 선장 등 선원 7명 전사", "style": "red", "at": 1, "pos": "top"}])
sc(2, ai("trench_night"), label=DRAMA)
sc(2, m("south", "south", [{"k": "front", "path": PERI, "at": 0}, {"k": "arrow", "path": [[128.6, 35.75], [128.5, 36.1], [128.5, 36.45]], "color": "blue", "at": 0.3, "width": 1.0}, {"k": "marker", "p": "jangsa", "color": "yellow", "at": 0}]),
   callouts=[{"text": "9. 16 · 낙동강 대반격 개시", "style": "blue", "at": 0, "pos": "top"}])
sc(2, ph("t34"), label="격파된 북한군 T-34 전차 (한국전쟁)", callouts=[{"text": "9. 17 · 전차 앞세운 맹공", "style": "red", "at": 0, "pos": "top"}])
sc(3, ai("ridge_shelled"), label=DRAMA)
sc(2, m("wide", "zoom", [H200, {"k": "arrow", "path": [[129.352, 36.293], [129.358, 36.285], [129.363, 36.278]], "color": "blue", "at": 0.3, "width": 0.6}], demSea=True), callouts=[{"text": "9. 18 새벽 · 200고지로 집결", "style": "blue", "at": 0, "pos": "top"}])
sc(2, ai("cp_munsan"), label=DRAMA)
sc(3, ai("plea_navy"), label=DRAMA)
sc(2, ai("red_eyes"), label=DRAMA)
sc(3, ai("comrade_breathes"), label=DRAMA)
sc(3, {"type": "black", "text": "철수하라", "accent": "가장 잔인한 시험", "accentAt": 0.6})
next_act()

# ===== 제6막 =====
MID.append(nid())
sc(1, {"type": "black", "text": "제6막", "accent": "조치원호의 철수", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, ai("jochiwon_arrive"), label=DRAMA, chapter={"num": "제6막", "title": "조치원호의 철수와 에필로그"}, callouts=[{"text": "9. 19 아침 · LST 조치원호", "style": "yellow", "at": 0, "pos": "top"}])
sc(1, ph("helena"), label="주포를 쏘는 미 중순양함 헬레나 (1950. 10)")
sc(2, m("wide", "zoom", ship() + [{"k": "radar", "p": [129.402, 36.285], "at": 0, "size": 0.45, "color": BLUE, "text": "중순양함 헬레나"}, {"k": "shock", "pts": [[129.366, 36.28], [129.362, 36.285], [129.368, 36.273]], "at": 0.5, "period": 0.7}], demSea=True))
sc(2, ai("rope_evac"), label=DRAMA)
sc(2, {"type": "text", "big": "철수 순서", "style": "yellow", "sub": "1중대 → 5중대 → 본부 → 3중대 → 2중대", "subAt": 0.3})
sc(1, ai("rope_climb"), label=DRAMA)
sc(3, m("zoom", "zoom", ship() + [{"k": "shock", "pts": [[129.3825, 36.2775], [129.384, 36.281], [129.3815, 36.285]], "at": 0.3, "period": 0.6}], tilt=26, demSea=True), callouts=[{"text": "조치원호 주변 박격포탄 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, {"type": "text", "big": "정오", "style": "red", "sub": "해안에 남은 60여 명", "subAt": 0.4})
sc(3, ai("captain_argument"), label=DRAMA)
sc(3, ai("rearguard"), label=DRAMA, callouts=[{"text": "제2중대 5소대", "style": "red", "at": 0, "pos": "top"}])
sc(2, ai("rearguard2"), label=DRAMA)
sc(3, ai("ship_leaves"), label=DRAMA, callouts=[{"text": "오후 1시 33분경", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, {"type": "black", "text": "39명", "accent": "다른 기록은 32명", "accentAt": 0.6}, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, ai("left_behind"), label=DRAMA)
sc(3, m("korea", "korea", [{"k": "arrow", "path": [[129.45, 36.26], [129.75, 35.7], [129.2, 35.05]], "color": "blue", "at": 0.2, "width": 0.8}, {"k": "marker", "p": "busan", "color": "blue", "at": 0}]),
   callouts=[{"text": "9. 20 새벽 · 640여 명 귀환 (725명 기록도)", "style": "blue", "at": 0, "pos": "top"}])
sc(3, {"type": "compare", "left": {"title": "전사", "big": "139명", "icon": "none", "color": "red"}, "right": {"title": "부상", "big": "92명", "icon": "none", "color": "red", "at": 0.6}},
   callouts=[{"text": "한국 측 기록 · 행방불명 다수", "style": "dark", "at": 1, "pos": "lower"}])
sc(2, {"type": "compare", "left": {"title": "북한군 사살", "big": "270여 명", "icon": "none", "color": "blue"}, "right": {"title": "포로", "big": "4명", "icon": "none", "color": "blue", "at": 0.6}}, sid="s111b", callouts=[{"text": "한국 측 기록", "style": "dark", "at": 1, "pos": "lower"}])
sc(2, {"type": "text", "big": "평가는 엇갈린다", "style": "yellow", "sub": "기여인가, 실패한 습격인가", "subAt": 0.4})
sc(2, m("wide", "wide", [rt7, H200, {"k": "lock", "p": [129.37, 36.285], "at": 0.4, "text": "7번 국도 차단"}], demSea=True))
sc(2, ai("forgotten"), label=DRAMA)
sc(2, {"type": "quotes", "title": "류병추 노병", "items": [{"text": "아마도 우리들은 희생양이었던 것 같다", "at": 0}]})
sc(2, ai("diver_wreck"), label=DRAMA, callouts=[{"text": "1997. 3. 6 · 해병대 수색대", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, ai("ship_underwater"), label=DRAMA)
sc(1, ph("memorial"), label="문산호를 본뜬 장사상륙작전 전승기념관 앞 (2024)")
sc(3, ai("nameplates"), label=DRAMA)
sc(2, ai("beach_dawn"), label=DRAMA)
sc(2, m("koreaN", "koreaN", [{"k": "marker", "p": "yanggu", "color": "yellow", "at": 0.3}]), callouts=[{"text": "다음 전장 · 강원도 양구", "style": "yellow", "at": 0}])
sc(2, {"type": "black", "text": "EP 24", "accent": "피의 능선", "accentAt": 0.5}, sfx=[{"id": "boom", "at": 0.5, "volume": 0.4}])
sc(3, {"type": "endcard", "title": "1950년 9월, 장사리.\n772명의 소년들을 기억하며.", "q": pin("munsan")}, tail=1.0)
next_act() if False else None
assert CUR["i"] == len(ACTS[5])

CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
KR = "young South Korean student soldiers whose heads are round balls painted as the South Korean Taegukgi flag, wearing plain black high-school uniforms and mismatched steel helmets, NO stars and NO red insignia anywhere"
KR1 = "a young South Korean student soldier whose head is a round ball painted as the South Korean Taegukgi flag, wearing a plain black high-school uniform and an old steel helmet, NO stars and NO red insignia anywhere"
OF = "a South Korean army captain whose head is a round ball painted as the South Korean Taegukgi flag, wearing a plain khaki American-style field uniform with no collar tabs, no shoulder boards, no stars, no medals and absolutely no red on the uniform"
NK = "North Korean soldiers whose heads are round balls painted as the North Korean flag, wearing 1950 khaki uniforms and caps"
END = ", leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no people visible, no text, no letters."
LST = "a rusty old grey World War II tank landing ship"
AI = {
    "parade_boys": CB + "rows of " + KR + " standing at attention on a dusty army parade ground in morning light in Busan" + END,
    "envelope": CB + "a South Korean instructor, head a round ball painted as the Taegukgi flag, wearing a plain khaki American-style field uniform with no collar tabs, no shoulder boards, no stars, no medals and absolutely no red on the uniform, handing a small plain paper envelope to " + KR1 + " in a line, solemn mood" + END,
    "cut_hair": CB + KR1 + " quietly placing a lock of cut hair and nail clippings into a small plain paper envelope, others doing the same behind him" + END,
    "busan_depart": LST.capitalize() + " leaving a Busan pier in late afternoon of September 1950 under heavy grey clouds, crowded with small figures, wide shot, " + LAND.replace("no people visible, ", ""),
    "hq_map": CB + "South Korean staff officers, heads round balls painted as the Taegukgi flag, wearing a plain khaki American-style field uniform with no collar tabs, no shoulder boards, no stars, no medals and absolutely no red on the uniform, leaning over a map table in a lamp-lit headquarters, worried, no soldiers to spare" + END,
    "rice_warehouse": CB + KR + " training with old rifles inside a dim wooden rice warehouse, sacks stacked along the walls" + END,
    "hands_question": CB + "a South Korean instructor seen from behind, head a round ball painted as the Taegukgi flag, wearing a plain khaki American-style field uniform with no collar tabs, no shoulder boards, no stars, no medals and absolutely no red on the uniform, facing a crowd of " + KR + " in front of a rice warehouse, the boys silent and tense" + END,
    "hands_down": CB + "a line of " + KR + " standing firm with their hands at their sides and eyes forward, determined faces, dusk light" + END,
    "fake_division": CB + "a South Korean officer, head a round ball painted as the Taegukgi flag, wearing a plain khaki American-style field uniform with no collar tabs, no shoulder boards, no stars, no medals and absolutely no red on the uniform, stamping a paper at a desk with a sly look, a small group of " + KR + " visible through the window" + END,
    "lst_storm": LST.capitalize() + " pitching violently in huge storm waves at night on the East Sea, spray over the bow, lightning, typhoon clouds, " + LAND.replace("no people visible, ", ""),
    "hold_seasick": CB + KR + " huddled in the dark steel cargo hold of a ship, one seasick boy being patted on the back by his friend, lantern swinging" + END,
    "hold_realize": CB + KR + " listening in a dark ship hold to an officer, faces slowly realizing where they are going, lantern light" + END,
    "anchor_snap": "A thick stern anchor chain snapping on the deck of an old landing ship before dawn in huge waves, sparks and spray, " + LAND,
    "ship_aground": LST.capitalize() + " lying broadside and stranded on rocks close to a Korean beach at grey dawn, heavy surf smashing against her side, fog, " + LAND.replace("no people visible, ", ""),
    "deck_fire": CB + KR + " on the open deck of a stranded ship under machine-gun fire at dawn, some ducking behind steel plates, sparks of bullets on metal, waves" + END,
    "crew_trapped": CB + "ship sailors and " + KR + " crouching together behind the steel side of a stranded ship, bullets striking the hull, frightened but holding on" + END,
    "seven_volunteer": CB + "seven " + KR + " stepping forward on the deck with coils of rope over their shoulders, comrades watching" + END,
    "swim_rope": CB + KR1 + " swimming through crashing surf toward a beach with a rope tied around his waist, bullets splashing around him, grey dawn" + END,
    "rope_line": CB + KR + " hanging on a thick wet rope stretched from a stranded ship to the beach, moving hand over hand through waves under fire" + END,
    "lee_order": CB + OF + " shouting an order on the deck of a stranded ship, pointing at the beach, smoke behind him" + END,
    "charge_smoke": CB + KR + " running out of the surf onto a sandy beach through shell smoke, shouting, rifles raised" + END,
    "beach_hell": CB + KR + " lying flat on a wet sandy beach under fire, explosions throwing up sand, smoke" + END,
    "lost_ammo": "Wooden ammunition crates and rifles sinking in churning grey sea water near a beach, bubbles, light from above, " + LAND,
    "pillbox_grenade": CB + KR1 + " crawling up to a concrete and log pillbox on a coastal slope and throwing a grenade into the firing slit, machine gun barrel above him" + END,
    "trench_melee": CB + KR + " fighting hand to hand with " + NK + " inside a coastal trench with bayonets and rifle butts, smoke" + END,
    "blow_bridge": CB + KR + " setting off an explosion on a small concrete road bridge on a coastal highway, debris flying" + END,
    "waiting_trench": CB + KR + " sitting exhausted in a hilltop trench drying wet uniforms, looking out at the empty sea and waiting, sunset" + END,
    "night_ring": "Naval shells bursting in a ring along the hills around a dark Korean beach at night, a stranded ship silhouetted in the foreground, muzzle flashes far out at sea, " + LAND,
    "empty_ammo": CB + KR1 + " opening an empty ammunition box in a trench with a hollow look, a few cartridges in his palm" + END,
    "count_rounds": CB + KR + " counting their last few rifle cartridges one by one in a trench at dusk, tense faces" + END,
    "crew_fight": CB + "merchant sailors in dark work clothes, heads round balls painted as the Taegukgi flag, holding rifles and coming ashore from a stranded ship to join the fight on the beach" + END,
    "trench_night": CB + KR + " crouching in a hilltop trench at night beside a comrade covered with a blanket, distant flashes, grief" + END,
    "ridge_shelled": "A low hill above a Korean beach being pounded by artillery in daylight, earth fountaining along the ridge, tanks on the road below, " + LAND,
    "cp_munsan": CB + OF + " at a makeshift command post with a field map inside the dark tilted hull of a stranded ship, waves outside, lantern light" + END,
    "plea_navy": CB + OF + " pleading with an American naval officer, head a round ball painted as the USA flag, on the deck of a warship, sea and distant coastline behind them" + END,
    "red_eyes": CB + KR1 + " with bloodshot exhausted eyes gripping a rifle in a trench at dawn, close-up, dirt on his face" + END,
    "comrade_breathes": CB + "two " + KR + " leaning shoulder to shoulder in a trench, one bandaged, still awake and holding on, soft dawn light" + END,
    "jochiwon_arrive": "An old grey tank landing ship appearing on the horizon in the morning, approaching a smoky Korean beach with a stranded ship on it, a large warship far behind, " + LAND.replace("no people visible, ", ""),
    "rope_evac": CB + KR + " wading through surf and grabbing a rope hanging from a landing ship about thirty meters off the beach, morning light" + END,
    "rope_climb": CB + KR + " climbing up a rope ladder and ropes on the side of a landing ship, helping a wounded friend up" + END,
    "captain_argument": CB + OF + " arguing fiercely with a ship captain in a dark coat, head a round ball painted as the Taegukgi flag, on the bridge of a landing ship, shells splashing outside" + END,
    "rearguard": CB + KR + " firing rifles from behind low sand dunes on a beach with their backs to the sea, North Korean soldiers advancing in the distance" + END,
    "rearguard2": CB + KR1 + " glancing back once at a ship in the surf, then turning forward again to keep firing, dust and smoke" + END,
    "ship_leaves": "A landing ship backing away from a Korean beach in the early afternoon, ropes trailing in the water, small figures left on the sand, smoke, wide shot, painterly realistic digital illustration, dark desaturated palette, film grain, no text, no letters.",
    "left_behind": CB + "a few " + KR + " standing on an empty beach watching a distant ship sail away, seen from behind, long shadows" + END,
    "forgotten": "Dusty stacks of old military files in a dark archive room, a small faded group photo of unnamed boys left on a shelf, a single beam of light, painterly realistic digital illustration, dark palette, film grain, no text, no letters.",
    "diver_wreck": CB + "South Korean marine reconnaissance divers, heads round balls painted as the Taegukgi flag, in 1990s diving gear, discovering a huge rusted steel hull under murky water, flashlight beams" + END,
    "ship_underwater": "A huge rusted landing ship half buried in sand on the sea floor, shafts of light from above, small fish, " + LAND,
    "nameplates": "A museum wall densely covered from floor to ceiling with small blank metal plaques in soft warm light, some plaques empty, a white chrysanthemum on the floor, painterly realistic digital illustration, no people, no text, no letters, no writing on the plaques.",
    "beach_dawn": "An empty Korean east coast beach at quiet dawn, calm waves, soft pink light, a coastal road in the distance, " + LAND,
    "thumb_subject": "Photorealistic black-and-white 1950 Korean War documentary portrait of a very young South Korean student volunteer in a plain black high-school uniform with no insignia and an old American M1 steel helmet, soot and sweat on his face, intense determined eyes, holding an old M1 rifle across his chest, waist-up, face clearly visible and turned slightly toward the right of the frame, isolated on a plain pure white background, no shadows on the background, no text.",
}
used = {s["visual"]["img"] for s in S if s["visual"]["type"] == "ai"}
assert not used - set(AI), used - set(AI)
assert not set(AI) - used - {"thumb_subject"}, set(AI) - used

ids = [s["id"] for s in S]
chap = [i for i, s in enumerate(S) if s.get("chapter")]
sid = lambda i: S[i]["id"]
music = [{"id": "drone", "from": "s01", "to": sid(chap[0] - 1), "volume": 0.2},
         {"id": "theme", "from": sid(chap[0]), "to": sid(chap[1] + 11), "volume": 0.16},
         {"id": "tension", "from": sid(chap[1] + 12), "to": sid(chap[3] - 1), "volume": 0.17},
         {"id": "march", "from": sid(chap[3]), "to": sid(chap[4] - 2), "volume": 0.15},
         {"id": "tension", "from": MID[1], "to": sid(chap[5] - 2), "volume": 0.17},
         {"id": "somber", "from": MID[2], "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "장사상륙작전", "subtitle": "1950. 9. 14 ~ 20", "target_sec": 1200, "voice": "U1cJYS4EdbaHmfR7YzHd", "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
print("scenes", len(S), "chars", sum(len(say(l)) for s in S for l in s["lines"]), "mid", MID, "chap", [sid(i) for i in chap], "ai", len(used), "pins", len(PINS))
