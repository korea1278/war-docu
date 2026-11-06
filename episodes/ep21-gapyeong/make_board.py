# EP21 가평 전투 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent

# ---------------- 대본 문장 ----------------
raw = (HERE / "script.md").read_text(encoding="utf-8").split("\n---\n")[0]
ACTS = []
for a in raw.split("\n## ")[1:]:
    body = [l for l in a.split("\n")[1:] if l and not l.startswith((">", "#"))]
    ACTS.append([s for l in body for s in re.split(r"(?<=[.?])\s+", l.strip()) if s])

# 자막 표기(숫자) ← 낭독 발음
SUBS = [
    ("천구백오십일 년 사월 이십사일", "1951년 4월 24일"), ("천구백오십삼 년", "1953년"),
    ("사월 이십이일", "4월 22일"), ("사월 이십삼일", "4월 23일"), ("사월 이십사일", "4월 24일"), ("사월 이십오일", "4월 25일"),
    ("사월 말", "4월 말"), ("사월이 오면", "4월이 오면"), ("이월부터", "2월부터"),
    ("해발 오백사 미터", "해발 504m"), ("해발 육백칠십칠 미터", "해발 677m"),
    ("오백사 고지", "504고지"), ("육백칠십칠 고지", "677고지"),
    ("이천여 명", "2,000여 명"), ("약 만 명", "약 1만 명"), ("만 명 안팎", "1만 명 안팎"), ("삼십만", "30만"),
    ("제사십군", "제40군"), ("제백십팔사단", "제118사단"), ("제육사단", "제6사단"), ("제이십칠여단", "제27여단"),
    ("제삼대대", "제3대대"), ("제이대대", "제2대대"), ("제십육포병연대", "제16포병연대"), ("제이차 세계대전", "제2차 세계대전"),
    ("스물네 문", "24문"), ("서른두 명", "32명"), ("쉰아홉 명", "59명"), ("열 명이 전사", "10명이 전사"), ("스물세 명", "23명"),
    ("서른 명이 넘는", "30명이 넘는"), ("천 명이 넘는", "1,000명이 넘는"), ("밤 열 시", "밤 10시"), ("이십이 편", "22편"),
]


def L(say):
    t = say
    for a, b in SUBS:
        t = t.replace(a, b)
    return {"t": t, "say": say} if t != say else say


S = []
CUR = {"act": 0, "i": 0}


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


NUM = {"n": 0}  # 'b' 장면(나중에 끼운 장면)은 번호를 세지 않음 — 기존 장면 번호·TTS 재사용 유지


def nid():
    return f"s{NUM['n'] + 1:02d}"


def sc(n, visual, id=None, **kw):
    if id is None:
        id = nid()
        NUM["n"] += 1
    d = {"id": id, "lines": take(n), "visual": visual}
    d.update(kw)
    S.append(d)
    return d


def m(fr, to=None, items=None, **kw):
    v = {"type": "map", "from": fr, "to": to or fr, "items": items or []}
    v.update(kw)
    return v


def ai(img, kb="in"):
    return {"type": "ai", "img": img, "kb": kb}


PINS = {}
# 사진 후보 (스카우트 시트 확인 후 채움 — 비어 있으면 자동 검색 결과가 들어가므로 반드시 핀)
PH = {
    "title": "Chinese Spring Offensive, April to May 1951.PNG",
    "cpv": "195103 1950年朝鲜战争中国志愿军士兵.png",
    "peng": "General Peng Dehuai.jpg",
    "refugees": "Terror-stricken Koreans flee the advancing Chinese Communists (SC 355573), National Museum of Health and Medicine (3298815186).jpg",
    "aus1": "An unidentified soldier of the 3rd Battalion, The Royal Australian Regiment (3RAR), taken in the field in Korea. (2963846520).jpg",
    "aus2": "An unidentified soldier of the 3rd Battalion, The Royal Australian Regiment (3RAR), taken in the field in Korea. (2963845210).jpg",
    "aus3": "An unidentified soldier of the 3rd Battalion, The Royal Australian Regiment (3RAR), taken in the field in Korea. (2963001487).jpg",
    "can1": "Gapyeong Canada PPCLI Monument Text 02.jpg",
    "refugees2": "KoreanWarRefugeeWithBaby.jpg",
    "sherman": "Sherman-korea.jpg",
    "nz25": "H-19C US Army in Korea c1952.jpg",
    "airdrop": "Airdrop over Sunchon, 20 October 1950.jpg",
    "kagnew": "Ethiopian Soldiers Korean War.jpg",
    "today": "Gapyeong Railway Bridge October 15, 2019 Southward Gyeonggi-do Gangwon-do (48902273341).jpg",
    "mem1": "75th Anniversary of the Battle of the Commonwealth Kapyong Commemoration Ceremony (9637359).jpg",
    "mem2": "75th Anniversary of the Battle of the Commonwealth Kapyong Commemoration Ceremony (9637297).jpg",
    "end": "75th Anniversary of the Battle of the Commonwealth Kapyong Commemoration Ceremony (9637304).jpg",
}


def ph(key, label, sid=None):
    sid = sid or nid()
    if PH.get(key):
        PINS[f"{sid}-photo#0"] = "File:" + PH[key]
    return {"type": "photo", "kb": "in", "q": f"{sid}-photo"}, label


def pin(key):
    sid = nid()
    if PH.get(key):
        PINS[f"{sid}-photo#0"] = "File:" + PH[key]
    return f"{sid}-photo"


DRAMA = "재연 일러스트"

# ---------------- 지도 ----------------
P = {
    "seoul": [126.978, 37.566, "서울"],
    "gapyeong": [127.51, 37.831, "가평"],
    "cheongpyeong": [127.424, 37.736, "청평"],
    "chuncheon": [127.73, 37.881, "춘천"],
    "sachang": [127.48, 38.085, "사창리"],
    "uijeongbu": [127.047, 37.738, "의정부"],
    "imjin": [126.93, 37.97, "임진강"],
    "h504": [127.553, 37.888, "504고지"],
    "h677": [127.497, 37.882, "677고지"],
    "hq3": [127.528, 37.872, "호주 대대 본부"],
    "tanks": [127.524, 37.878, "미군 전차"],
    "mx": [127.516, 37.856, "미들섹스 대대"],
    "nz": [127.51, 37.845, "뉴질랜드 포병"],
    "acoy": [127.556, 37.896, "A"],
    "bcoy": [127.541, 37.899, "B"],
    "dcoy": [127.562, 37.886, "D"],
    "pd": [127.488, 37.884, "D"],
    "pb": [127.502, 37.892, "B"],
    "pa": [127.505, 37.879, "A"],
    "pc": [127.494, 37.874, "C"],
}
V = {
    "korea": {"center": [127.6, 37.7], "span": 6.0},
    "central": {"center": [127.25, 37.85], "span": 1.4},
    "axis": {"center": [127.3, 37.82], "span": 0.9},
    "valley": {"center": [127.522, 37.872], "span": 0.17},
    "pass": {"center": [127.528, 37.874], "span": 0.11},
    "h504v": {"center": [127.55, 37.886], "span": 0.1},
    "h677v": {"center": [127.497, 37.882], "span": 0.1},
    "h677s": {"center": [127.497, 37.874], "span": 0.1},
    "gtown": {"center": [127.515, 37.85], "span": 0.17},
    "arty": {"center": [127.53, 37.862], "span": 0.17},
}
# 가평천·북한강·도로 (개략 좌표)
RIVER = [[127.47, 37.965], [127.485, 37.94], [127.502, 37.918], [127.515, 37.9], [127.522, 37.885], [127.522, 37.868], [127.517, 37.852], [127.512, 37.835]]
BUKHAN = [[127.36, 37.7], [127.42, 37.735], [127.465, 37.785], [127.5, 37.82], [127.535, 37.83], [127.58, 37.84], [127.64, 37.86], [127.73, 37.875]]
ROAD = [[127.49, 37.95], [127.505, 37.925], [127.52, 37.902], [127.527, 37.885], [127.526, 37.866], [127.519, 37.848], [127.512, 37.832]]
FRONT_APR = [[126.1, 37.8], [126.6, 37.95], [126.95, 38.02], [127.2, 38.15], [127.5, 38.12], [127.8, 38.15], [128.2, 38.25], [128.6, 38.35]]
RING504 = [[127.538, 37.902], [127.57, 37.9], [127.575, 37.882], [127.56, 37.872], [127.535, 37.876], [127.53, 37.89], [127.538, 37.902]]
RING677 = [[127.48, 37.896], [127.512, 37.9], [127.516, 37.878], [127.5, 37.866], [127.48, 37.87], [127.474, 37.884], [127.48, 37.896]]
NOLINE = [[126.7, 37.68], [126.9, 37.7], [127.1, 37.72], [127.3, 37.76], [127.45, 37.8], [127.6, 37.83]]

# ===================== 제1막 서막 (콜드 오프닝) =====================
sc(2, ai("valley_column"), label=DRAMA,
   callouts=[{"text": "1951. 4. 24 새벽 · 가평 계곡", "style": "yellow", "at": 0, "pos": "top"}], sfx=[{"id": "wind", "at": 0, "volume": 0.3}])
sc(3, {"type": "compare", "left": {"title": "영연방 제27여단", "big": "약 2천 명", "icon": "none", "color": "blue"},
       "right": {"title": "중공군 제118사단", "big": "약 1만 명", "icon": "none", "color": "red", "at": 1.0}},
   callouts=[{"text": "전방 투입 병력 · 대략 (기록마다 다름)", "style": "dark", "at": 2, "pos": "lower"}], sfx=[{"id": "hit", "at": 1.0, "volume": 0.45}])
sc(3, ai("radio_call"), label=DRAMA)
sc(2, {"type": "black", "text": "아군 머리 위로", "accent": "진내사격", "accentAt": 0.6}, pauseBefore=0.3, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, {"type": "titlecard", "title": "가평 전투", "sub": "영연방 제27여단 · 서울 진격을 막은 이틀 밤 1951", "at": 0, "q": pin("title")},
   flash=True, sfx=[{"id": "boom", "at": 0, "volume": 0.5}])
v, lb = ph("cpv", "중공군 병사 (1951. 3)")
sc(2, v, label=lb, chapter={"num": "제1막", "title": "서울 동쪽을 노린 춘계 대공세"})
sc(1, m("korea", "central", [{"k": "front", "path": FRONT_APR, "at": 0},
                             {"k": "arrow", "path": [[126.7, 38.3], [126.85, 38.05], [126.95, 37.78]], "color": "red", "at": 0.2, "width": 1.2},
                             {"k": "arrow", "path": [[127.3, 38.45], [127.25, 38.15], [127.1, 37.85]], "color": "red", "at": 0.4, "width": 1.1},
                             {"k": "arrow", "path": [[127.6, 38.5], [127.5, 38.2], [127.5, 37.9]], "color": "red", "at": 0.6, "width": 1.1},
                             {"k": "marker", "p": "seoul", "color": "blue", "at": 0.8}]),
   callouts=[{"text": "1951. 4. 22 · 중공군 춘계 공세 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, {"type": "person", "q": pin("peng"), "name": "펑더화이", "years": "1898 - 1974", "role": "중공군 사령관"})
sc(3, m("central", "central", [{"k": "front", "path": FRONT_APR, "at": 0},
                               {"k": "arrow", "path": [[126.8, 38.2], [126.9, 38.0], [126.95, 37.8]], "color": "red", "at": 0.3, "width": 1.1},
                               {"k": "badge", "p": "imjin", "text": "임진강 · 정면", "color": "red", "at": 0.6, "dy": -60},
                               {"k": "arrow", "path": [[127.5, 38.25], [127.49, 38.05], [127.51, 37.86]], "color": "red", "at": 1.0, "width": 1.1},
                               {"k": "badge", "p": [127.55, 38.0], "text": "가평 · 옆구리", "color": "red", "at": 1.3, "dy": -60}]),
   callouts=[{"text": "두 갈래의 공세 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("central", "axis", [{"k": "unit", "p": "sachang", "color": "blue", "text": "국군 제6사단", "at": 0},
                            {"k": "clash", "p": "sachang", "at": 1.0, "size": 1.0},
                            {"k": "arrow", "path": [[127.45, 38.2], [127.47, 38.12], [127.49, 38.05]], "color": "red", "at": 1.2, "width": 1.0}]),
   callouts=[{"text": "4. 22 밤 · 사창리 전선 붕괴 (개략)", "style": "red", "at": 0, "pos": "top"}])
v, lb = ph("refugees", "중공군을 피해 남쪽으로 향하는 피란민 (한국전쟁)")
sc(3, v, label=lb)
sc(3, {"type": "text", "big": "한 달 뒤, 용문산", "style": "yellow", "sub": "국군 제6사단의 설욕 · 격전의 지도 첫 편", "subAt": 0.6})
sc(3, ai("cpv_column"), label=DRAMA, callouts=[{"text": "중공군 제40군 제118사단", "style": "red", "at": 0, "pos": "top"}])
sc(3, m("axis", "axis", [{"k": "marker", "p": "sachang", "color": "red", "at": 0}, {"k": "line", "path": RIVER, "color": "#00E5FF", "at": 0, "glow": True},
                         {"k": "arrow", "path": [[127.48, 38.08], [127.48, 37.98], [127.5, 37.9], [127.51, 37.84], [127.43, 37.74], [127.2, 37.65], [127.05, 37.6]], "color": "red", "at": 0.6, "width": 1.2},
                         {"k": "marker", "p": "gapyeong", "color": "yellow", "at": 1.0}, {"k": "marker", "p": "seoul", "color": "blue", "at": 1.4}]),
   callouts=[{"text": "중공군 제118사단 진격로 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("axis", "axis", [{"k": "arrow", "path": [[126.93, 38.0], [126.97, 37.85], [127.0, 37.7]], "color": "red", "at": 0, "width": 1.2},
                         {"k": "arrow", "path": [[127.5, 37.95], [127.45, 37.78], [127.2, 37.66]], "color": "red", "at": 0.3, "width": 1.2},
                         {"k": "marker", "p": "seoul", "color": "blue", "at": 0}, {"k": "lock", "p": "seoul", "at": 1.0, "text": "집게"}]))
sc(2, {"type": "black", "text": "집게가 닫혔다면", "accent": "서울, 세 번째 함락", "accentAt": 0.8}, pauseBefore=0.3)
sc(1, m("axis", "gtown", [{"k": "marker", "p": "gapyeong", "color": "yellow", "at": 0}, {"k": "badge", "p": "gapyeong", "text": "가평", "color": "blue", "at": 0.4, "dy": -60}], tilt=26))
next_act()

# ===================== 제2막 가평 계곡의 방패 =====================
sc(2, ai("brigade_rest"), label=DRAMA, chapter={"num": "제2막", "title": "가평 계곡의 방패"})
sc(2, {"type": "text", "big": "영연방 제27여단", "style": "yellow", "sub": "영국 · 오스트레일리아 · 캐나다 · 뉴질랜드", "subAt": 0.3})
v, lb = ph("aus1", "오스트레일리아 왕립연대 제3대대 병사 (1952)")
sc(2, v, label=lb)
sc(2, ai("rest_camp"), label=DRAMA)
sc(2, m("axis", "axis", [{"k": "arrow", "path": [[127.38, 37.7], [127.45, 37.76], [127.5, 37.83], [127.52, 37.88]], "color": "blue", "at": 0.2, "width": 1.0},
                         {"k": "arrow", "path": [[127.48, 38.05], [127.5, 37.95], [127.51, 37.88]], "color": "#8fa3b8", "at": 0.8, "width": 0.8},
                         {"k": "marker", "p": "gapyeong", "color": "yellow", "at": 0}]),
   callouts=[{"text": "4. 23 · 제27여단 가평 계곡으로 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(1, ai("burke_map"), label=DRAMA)
sc(3, m("valley", "h504v", [{"k": "obj", "p": "h504", "n": "504", "at": 0.3, "text": "504고지"},
                            {"k": "unit", "p": [127.548, 37.895], "color": "blue", "text": "오스트레일리아 제3대대", "at": 1.0, "pulse": True}], tilt=24),
   callouts=[{"text": "가평천 동쪽 · 504고지 (개략)", "style": "blue", "at": 0, "pos": "top"}])
v, lb = ph("aus2", "오스트레일리아 왕립연대 제3대대 병사 (한국)")
sc(1, v, label=lb)
sc(2, ai("digger_mates"), id="s25b", label=DRAMA)
sc(3, m("valley", "h677v", [{"k": "obj", "p": "h677", "n": "677", "at": 0.3, "text": "677고지"},
                            {"k": "unit", "p": [127.497, 37.89], "color": "blue", "text": "캐나다 제2대대", "at": 1.0, "pulse": True}], tilt=24),
   callouts=[{"text": "가평천 서쪽 · 677고지 (개략)", "style": "blue", "at": 0, "pos": "top"}])
v, lb = ph("can1", "가평 캐나다 기념비 · 패트리샤 경보병연대 비문")
sc(1, v, label=lb)
sc(3, m("valley", "valley", [{"k": "obj", "p": "h677", "n": "677", "at": 0}, {"k": "obj", "p": "h504", "n": "504", "at": 0},
                             {"k": "badge", "p": [127.522, 37.905], "text": "가평 계곡", "color": "blue", "at": 1.2, "dy": -50}], tilt=30))
sc(1, m("valley", "valley", [{"k": "obj", "p": "h677", "n": "677", "at": 0}, {"k": "obj", "p": "h504", "n": "504", "at": 0},
                             {"k": "arrow", "path": [[127.505, 37.93], [127.52, 37.895], [127.524, 37.865], [127.513, 37.836]], "color": "red", "at": 0.3, "width": 1.0},
                             {"k": "marker", "p": "gapyeong", "color": "yellow", "at": 0.6}]))
sc(2, m("valley", "valley", [{"k": "unit", "p": "nz", "color": "blue", "text": "뉴질랜드 포병", "at": 0},
                             {"k": "radar", "p": "nz", "at": 0.2, "size": 0.6, "color": "#00E5FF", "text": "24문"},
                             {"k": "unit", "p": "tanks", "color": "blue", "text": "미군 전차 중대", "at": 0.6},
                             {"k": "unit", "p": "mx", "color": "blue", "text": "미들섹스 · 예비", "at": 1.0}]),
   callouts=[{"text": "제27여단 배치 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(3, ai("digging_rock"), label=DRAMA)
sc(2, m("valley", "valley", [{"k": "obj", "p": "h677", "n": "677", "at": 0}, {"k": "obj", "p": "h504", "n": "504", "at": 0},
                             {"k": "lock", "p": [127.524, 37.888], "at": 0.6, "text": "빈 골짜기"}]))
sc(2, {"type": "profile", "pts": [[0, 250], [0.12, 520], [0.22, 677], [0.32, 450], [0.42, 150], [0.5, 110], [0.58, 140], [0.68, 380], [0.78, 504], [0.88, 400], [1, 300]],
       "grid": [200, 400, 600], "yMin": 0, "yMax": 800, "title": "677고지 → 가평천 → 504고지 동서 단면", "note": "모식도 (높이 과장)",
       "left": "서 · 캐나다 대대", "right": "동 · 오스트레일리아 대대",
       "marks": [{"x": 0.22, "text": "677고지", "style": "dark", "at": 0, "lift": 70}, {"x": 0.5, "text": "가평천 · 도로", "style": "dark", "at": 0.4, "lift": 70},
                 {"x": 0.78, "text": "504고지", "style": "dark", "at": 0.8, "lift": 70}]})
v, lb = ph("refugees2", "피란민 남매와 전차 (1951 · 행주)")
sc(2, v, label=lb)
sc(1, ai("dusk_valley"), label=DRAMA)
next_act()

# ===================== 제3막 (미드롤 1 직전 암전) =====================
MID = [nid()]
sc(1, {"type": "black", "text": "제3막", "accent": "504고지의 혈전", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, ai("bugle_gong"), label=DRAMA, chapter={"num": "제3막", "title": "504고지의 혈전"})
sc(2, {"type": "black", "text": "나팔 · 꽹과리 · 호루라기", "accent": "보이지 않는 공포", "accentAt": 0.6})
sc(2, ai("flare_slope"), label=DRAMA)
sc(2, m("pass", "pass", [{"k": "unit", "p": "hq3", "color": "blue", "text": "대대 본부", "at": 0}, {"k": "unit", "p": "tanks", "color": "blue", "text": "전차", "at": 0},
                         {"k": "arrow", "path": [[127.515, 37.91], [127.522, 37.893], [127.526, 37.878]], "color": "red", "at": 0.3, "width": 0.8},
                         {"k": "clash", "p": "hq3", "at": 1.0, "size": 0.8}], tilt=28),
   callouts=[{"text": "4. 23 밤 · 계곡 도로 기습 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("pass", "pass", [{"k": "unit", "p": "hq3", "color": "blue", "text": "대대 본부", "at": 0}, {"k": "lock", "p": "hq3", "at": 0.3, "text": "노출"}]))
sc(2, ai("tank_night"), label=DRAMA)
sc(1, m("h504v", "h504v", [{"k": "obj", "p": "h504", "n": "504", "at": 0},
                           {"k": "arrow", "path": [[127.545, 37.915], [127.552, 37.903], [127.556, 37.896]], "color": "red", "at": 0.2, "width": 0.8},
                           {"k": "arrow", "path": [[127.565, 37.915], [127.56, 37.903], [127.557, 37.897]], "color": "red", "at": 0.5, "width": 0.8}], tilt=32))
sc(3, ai("aus_mg"), label=DRAMA)
sc(2, m("h504v", "h504v", [{"k": "obj", "p": "h504", "n": "504", "at": 0},
                           {"k": "arrow", "path": [[127.535, 37.91], [127.54, 37.898], [127.546, 37.89]], "color": "red", "at": 0.3, "width": 0.6},
                           {"k": "arrow", "path": [[127.575, 37.905], [127.568, 37.894], [127.562, 37.888]], "color": "red", "at": 0.6, "width": 0.6},
                           {"k": "arrow", "path": [[127.58, 37.885], [127.57, 37.88], [127.562, 37.882]], "color": "red", "at": 0.9, "width": 0.6}]),
   callouts=[{"text": "틈으로 스며드는 침투 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, ai("melee_504"), label=DRAMA)
sc(1, m("h504v", "h504v", [{"k": "obj", "p": "acoy", "n": "A", "at": 0, "text": "에이 중대"}, {"k": "obj", "p": "bcoy", "n": "B", "at": 0.2, "text": "비 중대"},
                           {"k": "obj", "p": "dcoy", "n": "D", "at": 0.4, "text": "디 중대"},
                           {"k": "clash", "p": "acoy", "at": 0.3, "size": 0.7}, {"k": "clash", "p": "dcoy", "at": 0.6, "size": 0.7}]))
sc(2, ai("aus_radio_night"), label=DRAMA)
v, lb = ph("aus3", "오스트레일리아 왕립연대 제3대대 병사 (1951. 11)")
sc(3, v, label=lb)
sc(2, ai("dawn_slope"), label=DRAMA)
sc(2, {"type": "gauges", "big": "4. 24 새벽 · 504고지", "items": [{"label": "탄약", "at": 0}, {"label": "부상병", "at": 0.5}]})
sc(2, m("h504v", "h504v", [{"k": "obj", "p": "h504", "n": "504", "at": 0},
                           {"k": "line", "path": RING504, "color": "#ff3b3b", "at": 0.6, "glow": True},
                           {"k": "arrow", "path": [[127.53, 37.87], [127.54, 37.878]], "color": "red", "at": 1.0, "width": 0.6},
                           {"k": "arrow", "path": [[127.575, 37.868], [127.566, 37.876]], "color": "red", "at": 1.2, "width": 0.6}]),
   callouts=[{"text": "4. 24 아침 · 옆과 뒤로 돌아든 적 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(3, {"type": "cta", "title": "격전의 기록, 함께 지켜 주십시오", "at": 0}, pauseBefore=0.3, sfx=[{"id": "pop", "at": 0.3, "volume": 0.45}])
next_act()

# ===================== 제4막 삼백육십 도 완전 포위 =====================
sc(2, m("h504v", "h504v", [{"k": "obj", "p": "h504", "n": "504", "at": 0}, {"k": "line", "path": RING504, "color": "#ff3b3b", "at": 0, "glow": True},
                           {"k": "lock", "p": "h504", "at": 0.6, "text": "완전 포위"}], tilt=30),
   chapter={"num": "제4막", "title": "360도 완전 포위"})
sc(2, m("pass", "pass", [{"k": "arrow", "path": [[127.528, 37.872], [127.522, 37.862], [127.518, 37.855]], "color": "blue", "at": 0.6, "width": 0.7},
                         {"k": "unit", "p": "mx", "color": "blue", "text": "미들섹스", "at": 0.6}]),
   callouts=[{"text": "끊긴 도로 · 대대 본부 후퇴 (개략)", "style": "red", "at": 0, "pos": "top"}])
v, lb = ph("sherman", "미 제72전차대대 셔먼 전차 (한국전쟁)")
sc(3, v, label=lb)
v, lb = ph("nz25", "영연방 25파운더 포진지에 포탄 보급 (1952)")
sc(3, v, label=lb)
sc(2, m("arty", "arty", [{"k": "unit", "p": "nz", "color": "blue", "text": "뉴질랜드 포병", "at": 0},
                             {"k": "radar", "p": "nz", "at": 0, "size": 0.7, "color": "#00E5FF", "text": "사격 원점"},
                             {"k": "shock", "pts": [[127.552, 37.9], [127.562, 37.893], [127.545, 37.905]], "at": 1.0, "period": 0.9}]),
   hudCta={"at": 0, "dur": 7.5}, callouts=[{"text": "뉴질랜드 제16포병연대 탄막 (개략)", "style": "blue", "at": 0, "pos": "lower"}])
sc(3, m("h504v", "h504v", [{"k": "obj", "p": "h504", "n": "504", "at": 0},
                           {"k": "shock", "pts": [[127.552, 37.905], [127.565, 37.896], [127.545, 37.9], [127.57, 37.885]], "at": 0, "period": 0.8}], tilt=30))
sc(3, {"type": "black", "text": "지금 물러나야 한다", "accent": "버크 준장의 결단", "accentAt": 0.6})
sc(2, ai("ammo_low"), label=DRAMA)
sc(2, {"type": "text", "big": "포위 속 철수", "style": "red", "sub": "전쟁에서 가장 어려운 작전", "subAt": 0.6})
sc(2, ai("stretcher_descent"), label=DRAMA)
sc(2, m("h504v", "h504v", [{"k": "obj", "p": "acoy", "n": "A", "at": 0}, {"k": "obj", "p": "bcoy", "n": "B", "at": 0}, {"k": "obj", "p": "dcoy", "n": "D", "at": 0},
                           {"k": "arrow", "path": [[127.541, 37.899], [127.535, 37.888], [127.53, 37.878]], "color": "blue", "at": 0.3, "width": 0.6},
                           {"k": "arrow", "path": [[127.556, 37.896], [127.547, 37.884], [127.535, 37.874]], "color": "blue", "at": 0.8, "width": 0.6},
                           {"k": "arrow", "path": [[127.562, 37.886], [127.55, 37.876], [127.537, 37.868]], "color": "blue", "at": 1.3, "width": 0.6}]),
   callouts=[{"text": "중대별 차례 철수 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(2, m("h504v", "pass", [{"k": "arrow", "path": [[127.556, 37.892], [127.545, 37.878], [127.53, 37.865], [127.52, 37.857]], "color": "blue", "at": 0.5, "width": 0.8}]))
sc(3, ai("withdraw_smoke"), label=DRAMA)
sc(2, m("pass", "pass", [{"k": "unit", "p": "mx", "color": "blue", "text": "미들섹스 대대", "at": 0},
                         {"k": "arrow", "path": [[127.535, 37.868], [127.525, 37.86], [127.516, 37.852]], "color": "blue", "at": 0.3, "width": 0.8}]),
   callouts=[{"text": "4. 24 밤 · 호주 대대 철수 완료", "style": "blue", "at": 0, "pos": "top"}])
sc(1, {"type": "quotes", "title": "오스트레일리아 제3대대", "items": [{"text": "질서를 지킨 철수", "at": 0}, {"text": "적에게 등을 보이지 않은 대대", "at": 0.5}]})
sc(3, m("valley", "h677v", [{"k": "obj", "p": "h677", "n": "677", "at": 0},
                            {"k": "arrow", "path": [[127.545, 37.9], [127.53, 37.9], [127.515, 37.895]], "color": "red", "at": 0.4, "width": 0.9},
                            {"k": "lock", "p": "h677", "at": 1.2, "text": "다음 목표"}], tilt=26))
next_act()

# ===================== 제5막 (미드롤 2 직전 암전) =====================
MID.append(nid())
sc(1, {"type": "black", "text": "제5막", "accent": "677고지의 사투", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, m("h677v", "h677v", [{"k": "unit", "p": [127.497, 37.886], "color": "blue", "text": "캐나다 제2대대", "at": 0, "pulse": True},
                           {"k": "line", "path": RING677, "color": "#ff3b3b", "at": 0.6, "glow": True}], tilt=30),
   chapter={"num": "제5막", "title": "677고지의 사투"})
sc(2, ai("canada_alone"), label=DRAMA)
sc(3, m("h677v", "h677v", [{"k": "obj", "p": "pa", "n": "A", "at": 0}, {"k": "obj", "p": "pb", "n": "B", "at": 0.2}, {"k": "obj", "p": "pc", "n": "C", "at": 0.4},
                           {"k": "obj", "p": "pd", "n": "D", "at": 0.6}, {"k": "badge", "p": "h677", "text": "사방 방어 진지", "color": "blue", "at": 1.2, "dy": -70}]),
   callouts=[{"text": "캐나다 대대 원형 방어 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(1, {"type": "text", "big": "스톤 중령", "style": "yellow", "sub": "캐나다 제2대대장 · 제2차 세계대전 참전 지휘관", "subAt": 0.5})
sc(3, {"type": "black", "text": "물러서지도, 항복하지도 않는다", "accent": "이 고지는 우리가 지킨다", "accentAt": 1.0}, id="s74b")
sc(2, m("h677v", "h677v", [{"k": "obj", "p": "pb", "n": "B", "at": 0},
                           {"k": "arrow", "path": [[127.51, 37.905], [127.505, 37.897], [127.502, 37.893]], "color": "red", "at": 0.2, "width": 0.7},
                           {"k": "clash", "p": "pb", "at": 0.6, "size": 0.7}]),
   callouts=[{"text": "4. 24 밤 10시 · 비 중대 피격", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("h677s", "h677s", [{"k": "arrow", "path": [[127.49, 37.86], [127.494, 37.868], [127.496, 37.874]], "color": "red", "at": 0, "width": 0.7},
                           {"k": "shock", "pts": [[127.495, 37.87], [127.49, 37.866]], "at": 0.8, "period": 0.8}]),
   callouts=[{"text": "고지 뒤쪽 침투 · 사격 구역 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("h677v", "h677v", [{"k": "obj", "p": "pd", "n": "D", "at": 0, "text": "디 중대"},
                           {"k": "arrow", "path": [[127.47, 37.895], [127.478, 37.889], [127.485, 37.885]], "color": "red", "at": 0.4, "width": 0.8},
                           {"k": "arrow", "path": [[127.47, 37.878], [127.478, 37.882], [127.485, 37.884]], "color": "red", "at": 0.7, "width": 0.8}], tilt=32))
sc(2, ai("melee_677"), label=DRAMA)
sc(2, ai("radio_urgent"), label=DRAMA)
sc(3, ai("mills_radio"), label=DRAMA)
sc(2, {"type": "black", "text": "진내사격", "accent": "아군 진지 위로 포탄을", "accentAt": 0.6}, pauseBefore=0.3, sfx=[{"id": "hit", "at": 0, "volume": 0.45}])
sc(1, ai("trench_shelter"), label=DRAMA)
sc(2, m("valley", "h677v", [{"k": "radar", "p": "nz", "at": 0, "size": 0.6, "color": "#00E5FF", "text": "포병"},
                            {"k": "lock", "p": "pd", "at": 0.8, "text": "디 중대 진지"}]))
sc(3, m("h677v", "h677v", [{"k": "obj", "p": "pd", "n": "D", "at": 0},
                           {"k": "shock", "pts": [[127.488, 37.884], [127.484, 37.887], [127.491, 37.881], [127.482, 37.882]], "at": 0, "period": 0.7}], tilt=30),
   callouts=[{"text": "4. 25 새벽 · 디 중대 진내사격 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(3, ai("shells_ridge"), label=DRAMA)
sc(2, {"type": "quotes", "title": "밀스 대위의 결단", "items": [{"text": "지금 우리 진지 위로", "at": 0}, {"text": "절망이 아닌, 계산된 선택", "at": 1.0}]})
sc(2, ai("dawn_677"), label=DRAMA)
next_act()

# ===================== 제6막 전선의 붕괴를 막다 =====================
sc(2, ai("dawn_supply_wait"), label=DRAMA, chapter={"num": "제6막", "title": "전선의 붕괴를 막다"})
v, lb = ph("airdrop", "C-119 수송기 공중 투하 (1950. 10)")
sc(2, v, label=lb)
sc(3, ai("crates"), label=DRAMA)
sc(2, {"type": "black", "text": "멈춰 선 공격", "accent": "1951. 4. 25", "accentAt": 0.6})
sc(3, ai("exhausted_cpv"), label=DRAMA)
sc(3, {"type": "bars", "note": "중공군 사상자는 추정 (기록마다 다름) · 영연방은 두 보병대대 전사자",
       "items": [{"label": "중공군 사상자 추정", "value": 1000, "display": "1천 명 이상", "color": "red", "at": 0},
                 {"label": "호주·캐나다 대대 전사", "value": 42, "display": "42명", "color": "blue", "at": 2.0}]})
sc(3, {"type": "text", "big": "공세 종말점", "style": "red", "sub": "등에 지고 온 며칠 치 보급이 끝나다", "subAt": 0.8})
sc(2, m("valley", "valley", [{"k": "obj", "p": "h677", "n": "677", "at": 0}, {"k": "obj", "p": "h504", "n": "504", "color": "red", "at": 0},
                             {"k": "arrow", "path": [[127.505, 37.93], [127.515, 37.905]], "color": "red", "at": 0, "width": 1.0},
                             {"k": "lock", "p": [127.517, 37.9], "at": 0.6, "text": "진격 차단"}]))
sc(2, ai("helmet_off"), label=DRAMA)
sc(2, m("axis", "axis", [{"k": "line", "path": NOLINE, "color": "#00E5FF", "at": 0.2, "glow": True},
                         {"k": "badge", "p": [127.15, 37.72], "text": "서울 북방 새 방어선", "color": "blue", "at": 0.8, "dy": 60},
                         {"k": "marker", "p": "seoul", "color": "blue", "at": 0}]),
   callouts=[{"text": "1951. 4 말 · 서울 북방 방어선 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(1, m("axis", "axis", [{"k": "badge", "p": "imjin", "text": "서쪽 문 · 임진강", "color": "blue", "at": 0, "dy": -60},
                         {"k": "badge", "p": "gapyeong", "text": "동쪽 문 · 가평", "color": "blue", "at": 0.4, "dy": -60},
                         {"k": "marker", "p": "seoul", "color": "blue", "at": 0}]))
sc(2, {"type": "timeline", "items": [{"date": "4. 22", "text": "춘계 공세", "at": 0}, {"date": "4. 23", "text": "504고지 혈전", "at": 0.3},
                                     {"date": "4. 24", "text": "호주군 철수", "at": 0.6}, {"date": "4. 25", "text": "677고지 사수", "at": 0.9},
                                     {"date": "4월 말", "text": "공세 중지", "at": 1.3}]})
sc(3, {"type": "bars", "note": "오스트레일리아 전쟁기념관 · 캐나다 측 기록 기준",
       "items": [{"label": "호주 3대대 전사", "value": 32, "display": "32명", "color": "blue", "at": 1.0}, {"label": "호주 3대대 부상", "value": 59, "display": "59명", "color": "blue", "at": 1.3},
                 {"label": "캐나다 2대대 전사", "value": 10, "display": "10명", "color": "red", "at": 2.0}, {"label": "캐나다 2대대 부상", "value": 23, "display": "23명", "color": "red", "at": 2.3}]})
sc(2, ai("helmets_row"), label=DRAMA)
sc(2, {"type": "document", "org": "미국 대통령", "head": "대통령 부대표창", "stamp": "1951",
       "rows": ["오스트레일리아 왕립연대 제3대대", "캐나다 프린세스 패트리샤 경보병연대 제2대대", "미 제72전차대대 에이 중대"], "note": "수여 부대 · 재구성 화면"})
sc(2, {"type": "quotes", "title": "표창장이 기린 것", "items": [{"text": "압도적인 적 앞의 비범한 용기", "at": 0}, {"text": "다섯 배의 적을 막아선 이틀 밤", "at": 1.0}]})
next_act()

# ===================== 제7막 에필로그 (미드롤 3 직전 암전) =====================
MID.append(nid())
sc(1, {"type": "black", "text": "제7막", "accent": "가평의 기적", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, ai("valley_sunset"), label=DRAMA, chapter={"num": "제7막", "title": "에필로그 · 가평의 기적"})
sc(1, {"type": "factors", "head": "다섯 배의 열세, 어떻게 뒤집었나", "items": ["지형", "포병", "침착함", "하나 된 힘"], "at": 0})
sc(2, m("valley", "valley", [{"k": "obj", "p": "h677", "n": "677", "at": 0}, {"k": "obj", "p": "h504", "n": "504", "at": 0},
                             {"k": "badge", "p": [127.522, 37.905], "text": "첫째 · 지형", "color": "blue", "at": 0, "dy": -50}], tilt=28))
sc(3, m("valley", "valley", [{"k": "radar", "p": "nz", "at": 0, "size": 0.7, "color": "#00E5FF", "text": "둘째 · 포병"},
                             {"k": "shock", "pts": [[127.552, 37.9], [127.488, 37.884]], "at": 0.5, "period": 0.9}]))
sc(2, {"type": "quotes", "title": "셋째 · 침착함", "items": [{"text": "포위 속에서도 질서 있는 철수", "at": 0}, {"text": "자기 머리 위로 부른 포탄", "at": 1.0}]})
sc(3, ai("four_nations"), label=DRAMA)
sc(1, {"type": "black", "text": "하나라도 빠졌다면", "accent": "무너졌을 계곡", "accentAt": 0.6})
v, lb = ph("mem1", "가평 전투 75주년 · 오스트레일리아군 (2026. 4)")
sc(3, v, label=lb)
v, lb = ph("mem2", "가평 전투 75주년 추모식 · 참전 노병 (2026. 4)")
sc(2, v, label=lb)
sc(2, {"type": "quotes", "title": "가평의 기적", "items": [{"text": "남반구와 북미 대륙에서 온 청년들", "at": 0}, {"text": "서울로 가는 길을 지켜내다", "at": 0.6}]}, pauseBefore=0.3)
sc(3, ai("veterans"), label=DRAMA)
v, lb = ph("today", "오늘의 가평 · 북한강 철교 (2019)", sid="s115b")
sc(2, v, id="s115b", label=lb)
sc(2, ai("porkchop_teaser"), label=DRAMA, callouts=[{"text": "다음 편 · EP22 포크찹 고지 전투", "style": "yellow", "at": 0, "pos": "top"}])
v, lb = ph("kagnew", "에티오피아 대대 병사들 (1953)")
sc(2, v, label=lb)
sc(2, {"type": "text", "big": "EP22 포크찹 고지 전투", "style": "yellow", "sub": "강뉴 대대의 전설 · 곧 공개", "subAt": 0.5})
sc(2, {"type": "endcard", "title": "1951년 4월, 가평.\n다섯 배의 적을 막아선 이틀 밤.", "q": pin("end")}, tail=1.0)
next_act() if CUR["act"] < len(ACTS) - 1 else None
assert CUR["act"] == len(ACTS) - 1 and CUR["i"] == len(ACTS[-1]), ("남은 문장", CUR)

# ---------------- AI 그림 ----------------
CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
AUS = "Australian soldiers whose heads are round balls painted as the Australian flag (dark blue with the Union Jack and white Southern Cross stars), wearing 1951 slouch hats or steel helmets and khaki battledress"
CAN = "Canadian soldiers whose heads are round balls painted as the 1951 Canadian Red Ensign flag (red with the Union Jack in the corner), wearing 1951 British-style steel helmets and khaki battledress"
NZ = "New Zealand artillerymen whose heads are round balls painted as the New Zealand flag (dark blue with the Union Jack and four red stars), wearing 1951 khaki uniforms"
US = "American tank crewmen whose heads are round balls painted as the USA flag, wearing 1951 tanker helmets"
BR = "British soldiers whose heads are round balls painted as the British Union Jack flag, wearing 1951 berets and khaki battledress"
CN = "Chinese People's Volunteer Army soldiers whose heads are round balls painted as the red Chinese flag with yellow stars, wearing 1951 quilted khaki uniforms and caps"
END = ", leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no people visible, no text, no letters."
AI = {
    "valley_column": "A narrow Korean mountain valley at dawn in April 1951, a dirt road beside a river, an endless dark column of figures streaming down the road from the north, smoke on the ridges on both sides, cold blue light, painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no text, no letters.",
    "radio_call": CB + "a Canadian infantry officer, head a round ball painted as the 1951 Canadian Red Ensign flag, crouching in a hilltop trench at night shouting into a field radio handset, flares and tracer fire behind him, determined" + END,
    "cpv_column": CB + "a long column of " + CN + " marching at night along a mountain path under moonlight, carrying rifles and heavy packs on their backs, endless line disappearing into the dark hills" + END,
    "brigade_rest": CB + "a group of " + BR + ", " + AUS + ", and " + CAN + " resting together around a small campfire in a Korean valley in spring, mugs of tea, rifles stacked, relaxed but weary" + END,
    "rest_camp": CB + AUS + " washing, shaving and cleaning rifles beside tents in a quiet Korean valley in April, spring blossoms, a messenger running toward them with a paper order" + END,
    "burke_map": CB + "a British brigadier, head a round ball painted as the British Union Jack flag, wearing a beret, pointing at two hills on a large paper map spread on the bonnet of a jeep, officers of Australia and Canada (heads round balls painted as their flags) leaning in, dusk" + END,
    "digging_rock": CB + AUS + " digging trenches with picks into rocky hard ground on a steep spring hillside, sweat, a valley and a winding river below" + END,
    "dusk_valley": "A Korean mountain valley at dusk in April 1951 seen from a hilltop trench, a dirt road and river below, a long line of refugees walking south, dark ridges on both sides, ominous red sky, " + LAND.replace("no people visible, ", ""),
    "bugle_gong": CB + CN + " blowing long brass bugles, striking gongs and blowing whistles on a dark ridge at night, more soldiers behind them waiting to charge, eerie moonlight and mist" + END,
    "flare_slope": CB + AUS + " looking out from a hilltop trench as a parachute flare lights up the night sky, revealing countless shadowy figures climbing the slope below" + END,
    "tank_night": CB + "an American M4 Sherman tank on a narrow valley road at night with its hatches closed, firing its machine gun at shadowy figures in the dark, " + US + " inside visible through a vision port, tracer fire" + END,
    "aus_mg": CB + AUS + " firing a Vickers machine gun from a sandbagged hilltop position at night, the barrel glowing red hot, empty cartridge cases piling up, tracer fire down the slope" + END,
    "melee_504": CB + AUS + " fighting hand to hand with " + CN + " in a hilltop trench at night, bayonets and grenades, explosions lighting the scene" + END,
    "aus_radio_night": CB + "an Australian radio operator, head a round ball painted as the Australian flag, slouch hat, shouting into a field radio in a dark trench, a wounded comrade beside him, flares above" + END,
    "dawn_slope": CB + "exhausted " + AUS + " in a battered hilltop trench at dawn after a night battle, smoke on the slope below, empty ammunition boxes, cold blue light" + END,
    "ammo_low": CB + AUS + " in a trench counting the last few rifle magazines and grenades on an empty ammunition box, bandaged wounded comrades lying behind them, tense faces, morning" + END,
    "stretcher_descent": CB + AUS + " carrying wounded comrades on stretchers and a heavy radio down a steep rocky ridge in the late afternoon, enemy fire kicking up dust nearby, smoke" + END,
    "withdraw_smoke": CB + AUS + " moving in a disciplined file down a ridge at dusk through drifting artillery smoke, one group kneeling and firing to cover the others" + END,
    "canada_alone": CB + CAN + " crouching in a ring of trenches on a high rocky hilltop at dusk, looking outward in every direction, smoke rising from the valleys all around, isolated" + END,
    "melee_677": CB + CAN + " fighting hand to hand with " + CN + " who leap into their hilltop trenches at night, bayonets and grenades, explosions" + END,
    "radio_urgent": CB + "a Canadian signaller, head a round ball painted as the 1951 Canadian Red Ensign flag, pressing headphones to his ears in a trench at night, wide eyes, enemy silhouettes very close above the trench edge" + END,
    "mills_radio": CB + "a calm Canadian company commander, head a round ball painted as the 1951 Canadian Red Ensign flag, wearing a steel helmet, speaking firmly into a field radio handset while his men crouch low in the trench around him, artillery flashes on the horizon" + END,
    "trench_shelter": CB + CAN + " pressing themselves flat at the bottom of a deep trench with arms over their helmets while artillery shells burst in bright flashes just above the trench at night" + END,
    "shells_ridge": "A rocky Korean hill ridge at night struck by a barrage of artillery shells bursting in the air above the trenches, bright flashes and smoke, silhouettes of attacking soldiers swept away, dramatic, painterly realistic digital illustration, cinematic wide shot, dark palette, film grain, no text, no letters.",
    "dawn_677": CB + CAN + " slowly raising their heads out of a smoking hilltop trench at grey dawn, silence, scattered debris on the slope, exhausted but alive" + END,
    "dawn_supply_wait": CB + CAN + " sitting exhausted in hilltop trenches in the morning, empty water bottles and empty ammunition pouches, looking up at the sky" + END,
    "crates": CB + CAN + " dragging parachute supply crates across a hilltop and handing out ammunition boxes to comrades in trenches, white and colored parachutes on the ground, morning light" + END,
    "exhausted_cpv": CB + "exhausted " + CN + " huddled in a rocky ravine at the foot of a hill, empty ration bags, thin and tired, no more strength to attack, grey morning" + END,
    "helmet_off": CB + CAN + " taking off their steel helmets and sitting down in a trench in afternoon sunlight after the battle, one lighting a cigarette, a road in the valley below now open with vehicles" + END,
    "helmets_row": "A row of steel helmets resting on rifles planted in the ground on a Korean hillside at sunset in spring, wild flowers, solemn, " + LAND,
    "digger_mates": CB + AUS + " sharing a cigarette and a canteen in a hillside trench, one bandaging a mate's arm, rough but loyal comradeship, afternoon light" + END,
    "valley_sunset": "The peaceful Gapyeong river valley in Korea at sunset in spring, a river and road between two high hills, soft golden light, " + LAND,
    "four_nations": CB + "soldiers of Australia, Canada, New Zealand, Britain and the USA, heads round balls painted as their national flags of 1951, standing shoulder to shoulder on a hilltop at dawn, an artillery gun and a tank behind them, united" + END,
    "veterans": "Elderly Commonwealth war veterans with berets and medals, seen from behind, laying flowers at a stone war memorial in a green Korean valley in spring, soft light, painterly realistic digital illustration, no text, no letters.",
    "porkchop_teaser": "A small scarred Korean hill at night in 1953 under heavy artillery fire, trenches and sandbag bunkers on the crest, searchlights and flares, dramatic, painterly realistic digital illustration, cinematic wide shot, dark palette, film grain, no text, no letters.",
    "thumb_subject": "Photorealistic black-and-white 1951 Korean War documentary portrait of a weary but defiant Commonwealth infantry officer, steel helmet, dirt- and smoke-streaked face, holding a field radio handset to his mouth as if shouting an order, determined eyes, battledress with webbing, waist-up, face clearly visible and turned slightly toward the right of the frame, sharp detail, high contrast monochrome, isolated on a plain pure white background, no shadows on the background, no text.",
}

used = {s["visual"]["img"] for s in S if s["visual"]["type"] == "ai"}
missing = used - set(AI)
assert not missing, missing

ids = [s["id"] for s in S]
chap = [i for i, s in enumerate(S) if s.get("chapter")]


def sid(i):
    return S[i]["id"]


music = [{"id": "drone", "from": "s01", "to": "s05", "volume": 0.2},
         {"id": "theme", "from": sid(chap[0]), "to": sid(chap[2] - 2), "volume": 0.16},
         {"id": "tension", "from": MID[0], "to": sid(chap[3] - 1), "volume": 0.17},
         {"id": "march", "from": sid(chap[3]), "to": sid(chap[4] - 2), "volume": 0.15},
         {"id": "tension", "from": MID[1], "to": sid(chap[5] - 1), "volume": 0.17},
         {"id": "march", "from": sid(chap[5]), "to": sid(chap[6] - 2), "volume": 0.15},
         {"id": "somber", "from": MID[2], "to": ids[-1], "volume": 0.17}]

(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "가평 전투", "subtitle": "1951. 4. 22 ~ 4. 25", "target_sec": 1230, "voice": "U1cJYS4EdbaHmfR7YzHd",
         "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")


def say(l):
    return l if isinstance(l, str) else l["say"]


n = sum(len(say(l)) for s in S for l in s["lines"])
print("scenes", len(S), "say chars", n, "mid", MID, "chapters", [sid(i) for i in chap], "ai", len(used))
print("photo q", [s["visual"].get("q") for s in S if s["visual"].get("q")])
