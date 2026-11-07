# EP22 포크찹 고지 전투 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
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

SUBS = [
    ("천구백오십삼 년 사월 십육일", "1953년 4월 16일"), ("천구백오십일 년 오월", "1951년 5월"), ("천구백오십 년 구월", "1950년 9월"),
    ("천구백칠십사 년", "1974년"), ("천구백오십삼 년", "1953년"),
    ("사월 십칠일 새벽 네 시 삼십 분", "4월 17일 새벽 4시 30분"), ("사월 십육일", "4월 16일"), ("사월 십팔일", "4월 18일"),
    ("삼월 이십삼일", "3월 23일"), ("오월 십오일부터 십팔일까지", "5월 15일부터 18일까지"), ("오월 십구일", "5월 19일"), ("오월 이십일", "5월 20일"),
    ("칠월 육일", "7월 6일"), ("칠월 십일일", "7월 11일"), ("칠월 이십칠일", "7월 27일"),
    ("이백오십삼 번", "253번"), ("이백오십오 고지", "255고지"), ("이백오십오 미터", "255m"), ("이백육십육 고지", "266고지"),
    ("제칠보병사단", "제7보병사단"), ("제삼십일연대", "제31연대"), ("제이백일연대", "제201연대"), ("제십칠연대", "제17연대"), ("제삼 강뉴 대대", "제3 강뉴 대대"),
    ("삼 년째", "3년째"), ("일 미터", "1미터"), ("백여 명", "100여 명"), ("밤 열한 시", "밤 11시"),
    ("삼천 명", "3,000명"), ("영하 이십 도", "영하 20도"), ("병사 여덟 명", "병사 8명"), ("여덟 명은 열 명이", "8명은 10명이"), ("칠백 미터", "700m"), ("포로 두 명", "포로 2명"),
    ("백삼십오 명", "135명"), ("백이십오 명", "125명"), ("열 명 가운데 아홉 명", "10명 가운데 9명"), ("열아홉 명", "19명"),
    ("칠만 칠천 발", "7만 7천 발"), ("사만 발", "4만 발"), ("네 번이나", "4번이나"), ("열다섯 명", "15명"), ("열네 명", "14명"), ("삼백 명", "300명"),
    ("백십 명", "110명"), ("백이십일 명", "121명"), ("오백삼십육 명", "536명"), ("삼 주", "3주"), ("칠백칠십이 명", "772명"), ("이십삼 화", "23화"),
    ("브이티", "VT"),
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
    "kag1": "Ethiopian Soldiers Korean War.jpg",
    "title": "DMZ view from Site 7 - looking west (279668935).jpg",
    "trench53": "Outpost Harry ridgeline photo.jpg",
    "panmun": "80-G-436371 Korean War Armistice Negotiations, Panmunjom, Korea.png",
    "thai": "Thailand in Korean War 1.jpg",
    "div7": "Korean War HA-SN-98-07010.jpg",
    "trudeau": "Arthur Trudeau.jpg",
    "bunker": "Old Baldy, March 1953.jpg",
    "colombia": "M2 4.2 in Mortar Korea.jpg",
    "howitzer": "155mm-howitzer-korea.jpg",
    "kag2": "Ethiopian soldiers Korea war.jpg",
    "selassie": "Haile Selassie I Coronation Portrait.jpg",
    "makonnen": "Mekonnen Welde Mikaél around 1901.jpg",
    "kag3": "USNS General J. H. McRae (T-AP-149).jpg",
    "marshall": "S.L.A. Marshall.jpg",
    "howitzer2": "8-inch-howitzer-korea-19510409.jpg",
    "wounded": "Medical-corpsmen-korea.jpg",
    "kag4": "Ethiopian soldiers Korea1951.JPG",
    "armistice": "Korean War Armistice Signing, 27 July 1953 (19864802878).jpg",
    "addis": "Kagnew battalion Korea war memorial.jpg",
    "vets": "에티오피아 참전용사 방문 (7445438568).jpg",
    "end": "20231226 Ethiopian한국전참전기념관 정문.jpg",
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

# ---------------- 지도 (고지·전초 좌표는 모두 개략) ----------------
P = {
    "seoul": [126.978, 37.566, "서울"],
    "panmun": [126.677, 37.956, "판문점"],
    "yeoncheon": [127.075, 38.096, "연천"],
    "cheorwon": [127.21, 38.24, "철원"],
    "chuncheon": [127.73, 37.881, "춘천"],
    "incheon": [126.62, 37.46, "인천"],
    "jangsa": [129.38, 36.28, "장사리"],
    "pc": [127.0194, 38.2414, "포크찹 (255고지)"],
    "ob": [127.003, 38.247, "올드 발디 (266고지)"],
    "tb": [126.985, 38.262, "티본 고지"],
    "hasak": [127.024, 38.254, "중공군 고지"],
    "kag": [126.972, 38.247, "강뉴 대대"],
    "yoke": [126.962, 38.256, "요크 고지"],
    "uncle": [126.977, 38.258, "엉클 고지"],
    "arty": [127.03, 38.21, "미군 포병"],
}
V = {
    "korea": {"center": [127.6, 37.5], "span": 6.0},
    "front53": {"center": [127.1, 38.15], "span": 1.2},
    "sector": {"center": [127.0, 38.243], "span": 0.16},
    "chop": {"center": [127.019, 38.243], "span": 0.1},
    "kagv": {"center": [126.972, 38.252], "span": 0.1},
    "east": {"center": [128.0, 37.0], "span": 4.0},
}
FRONT53 = [[126.1, 37.75], [126.6, 37.95], [126.9, 38.1], [127.0, 38.225], [127.1, 38.27], [127.2, 38.3], [127.4, 38.31], [127.6, 38.36], [127.85, 38.33], [128.1, 38.3], [128.35, 38.38], [128.6, 38.55]]
MLR = [[126.94, 38.233], [126.97, 38.236], [126.995, 38.232], [127.015, 38.235], [127.035, 38.233], [127.06, 38.238], [127.09, 38.242]]
CHOP = [[127.0165, 38.2405], [127.018, 38.2435], [127.0215, 38.2448], [127.0238, 38.2427], [127.0222, 38.2397], [127.0197, 38.2386], [127.019, 38.2362], [127.0185, 38.2386], [127.0168, 38.2392], [127.0165, 38.2405]]
HORSE = [[127.012, 38.2385], [127.011, 38.245], [127.016, 38.2495], [127.023, 38.2495], [127.028, 38.245], [127.027, 38.2385]]
RINGY = [[126.953, 38.262], [126.972, 38.264], [126.984, 38.258], [126.978, 38.25], [126.96, 38.249], [126.952, 38.255], [126.953, 38.262]]
MDL = [[126.94, 38.25], [126.97, 38.252], [127.0, 38.248], [127.02, 38.247], [127.05, 38.25], [127.09, 38.255]]
RED3 = [{"k": "arrow", "path": [[127.022, 38.262], [127.021, 38.25], [127.0205, 38.2445]], "color": "red", "at": 0.2, "width": 0.6},
        {"k": "arrow", "path": [[127.003, 38.252], [127.012, 38.247], [127.017, 38.243]], "color": "red", "at": 0.5, "width": 0.6},
        {"k": "arrow", "path": [[127.04, 38.252], [127.03, 38.247], [127.024, 38.243]], "color": "red", "at": 0.8, "width": 0.6}]


def o(p, n, text=None, at=0, **kw):
    d = {"k": "obj", "p": p, "n": n, "at": at}
    if text:
        d["text"] = text
    d.update(kw)
    return d


# ===================== 제1막 서막 (콜드 오프닝) =====================
sc(2, ai("night_barrage"), label=DRAMA,
   callouts=[{"text": "1953. 4. 16 밤 · 연천 북방", "style": "yellow", "at": 0, "pos": "top"}], sfx=[{"id": "boom", "at": 0.3, "volume": 0.35}])
sc(2, ai("radio_vt"), label=DRAMA)
v, lb = ph("kag1", "에티오피아 대대 병사들 · 미 제7사단 (1953)")
sc(2, v, label=lb)
sc(2, {"type": "black", "text": "253번의 전투", "accent": "포로 0명", "accentAt": 0.7}, pauseBefore=0.3, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, {"type": "titlecard", "title": "포크찹 고지 전투", "sub": "253전 253승 강뉴 대대의 전설 · 1953", "at": 0, "q": pin("title")},
   flash=True, sfx=[{"id": "boom", "at": 0, "volume": 0.5}])
v, lb = ph("trench53", "전초로 이어지는 능선 · 아웃포스트 해리 (1953)")
sc(2, v, label=lb, chapter={"num": "제1막", "title": "돼지갈비를 닮은 고지"})
v, lb = ph("panmun", "유엔군 휴전 회담 대표단 (1951. 11)")
sc(2, v, label=lb)
sc(2, m("korea", "front53", [{"k": "front", "path": FRONT53, "at": 0}, {"k": "marker", "p": "panmun", "color": "yellow", "at": 0.5},
                             {"k": "marker", "p": "seoul", "color": "blue", "at": 0.8}]),
   callouts=[{"text": "1953년 봄 · 전선 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, {"type": "text", "big": "고지전", "style": "red", "sub": "마지막 1미터의 땅을 위한 싸움", "subAt": 0.6})
sc(3, ai("ridge_shelled"), label=DRAMA)
sc(2, m("front53", "sector", [{"k": "front", "path": FRONT53, "at": 0}, {"k": "marker", "p": "yeoncheon", "color": "blue", "at": 0},
                              {"k": "marker", "p": "cheorwon", "color": "blue", "at": 0}, {"k": "marker", "p": "pc", "color": "yellow", "at": 1.0}]))
sc(2, m("sector", "chop", [o("pc", "255", "255고지", 0.3)], tilt=24),
   callouts=[{"text": "255고지 · 연천 북방 (개략)", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, m("chop", "chop", [{"k": "line", "path": CHOP, "color": "#FFD000", "at": 0.3, "glow": True},
                         {"k": "badge", "p": "pc", "text": "포크찹", "color": "blue", "at": 1.0, "dy": -70}], tilt=20),
   callouts=[{"text": "등고선 모양 = 돼지갈비 (모식)", "style": "dark", "at": 0, "pos": "lower"}])
sc(2, m("sector", "sector", [{"k": "line", "path": MLR, "color": "#00E5FF", "at": 0, "glow": True}, o("pc", "255", None, 0.3)] + RED3),
   callouts=[{"text": "주저항선 앞으로 튀어나온 전초 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, ai("outpost_fist"), label=DRAMA)
sc(2, m("sector", "sector", [o("pc", "255", None, 0), o("ob", "266", "올드 발디", 0.2), o("tb", "T", "티본 고지", 1.0)], tilt=22),
   callouts=[{"text": "올드 발디 · 티본 고지 (개략)", "style": "red", "at": 0, "pos": "top"}])
v, lb = ph("thai", "태국군 제21연대 제1대대 표지판 (한국전쟁)")
sc(1, v, label=lb)
sc(1, {"type": "quotes", "title": "태국군이 벙커 벽에 남긴 글", "items": [{"text": "우리 포크찹을 잘 지켜 달라", "at": 0}]})
v, lb = ph("div7", "미 제7보병사단 제32연대 병사 (한국전쟁)")
sc(2, v, label=lb)
next_act()

# ===================== 제2막 삼면이 적 =====================
sc(1, {"type": "person", "q": pin("trudeau"), "name": "아서 트루도", "years": "1902 - 1991", "role": "미 제7보병사단장"},
   chapter={"num": "제2막", "title": "삼면이 적, 피의 고지"})
sc(2, m("sector", "sector", [o("pc", "255", None, 0), o("ob", "266", None, 0.3), o([127.04, 38.238], "·", None, 0.6), o([126.985, 38.24], "·", None, 0.8)]),
   callouts=[{"text": "띄엄띄엄 세운 전초들 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(2, m("sector", "sector", [{"k": "line", "path": MLR, "color": "#00E5FF", "at": 0, "glow": True}, o("pc", "255", None, 0),
                             {"k": "radar", "p": "arty", "at": 0.6, "size": 0.6, "color": "#00E5FF", "text": "포병"}]),
   callouts=[{"text": "전초 1개 = 중대 1개 · 뒤에서 포병 엄호", "style": "blue", "at": 0, "pos": "top"}])
v, lb = ph("bunker", "올드 발디의 미군 진지 · 항공 촬영 (1953. 3. 22)")
sc(2, v, label=lb)
sc(2, m("sector", "sector", [o("pc", "255", None, 0), o("ob", "266", "올드 발디", 0),
                             {"k": "arrow", "path": [[126.995, 38.262], [127.0, 38.253], [127.003, 38.248]], "color": "red", "at": 0.4, "width": 0.6},
                             {"k": "clash", "p": "ob", "at": 1.0, "size": 0.8}]),
   callouts=[{"text": "1953. 3. 23 밤 · 올드 발디 함락", "style": "red", "at": 0, "pos": "top"}])
v, lb = ph("colombia", "철원 서쪽 적진에 사격하는 미 제31중박격포중대 (1953. 2)")
sc(2, v, label=lb)
sc(1, m("sector", "chop", [o("pc", "255", None, 0)] + RED3 + [{"k": "lock", "p": "pc", "at": 1.2, "text": "삼면 노출"}], tilt=24))
sc(2, ai("night_wire"), label=DRAMA)
sc(1, ai("trench_listen"), label=DRAMA)
sc(3, ai("night_carry"), label=DRAMA)
sc(2, ai("tunnel_cpv"), label=DRAMA)
sc(1, {"type": "black", "text": "하늘은 미군", "accent": "땅속은 중공군", "accentAt": 0.5})
v, lb = ph("howitzer", "미군 155mm 곡사포 사격 (한국전쟁)")
sc(2, v, label=lb)
sc(2, m("sector", "sector", [{"k": "radar", "p": "arty", "at": 0, "size": 0.7, "color": "#00E5FF", "text": "사격 원점"}, o("pc", "255", None, 0),
                             {"k": "badge", "p": "pc", "text": "플래시 사격", "color": "blue", "at": 1.2, "dy": -70}]))
sc(1, m("chop", "chop", [o("pc", "255", None, 0), {"k": "line", "path": HORSE, "color": "#00E5FF", "at": 0.2, "glow": True},
                         {"k": "shock", "pts": [[127.012, 38.243], [127.019, 38.2495], [127.027, 38.243]], "at": 0.6, "period": 0.8}], tilt=26),
   callouts=[{"text": "말발굽 모양 포탄의 벽 (모식)", "style": "blue", "at": 0, "pos": "lower"}])
sc(1, m("sector", "sector", [o("tb", "T", "티본 고지", 0), {"k": "unit", "p": "kag", "color": "blue", "text": "강뉴 대대", "at": 0.3, "pulse": True}]),
   callouts=[{"text": "티본 고지 맞은편 · 에티오피아 병사들 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(2, m("sector", "sector", [o("pc", "255", None, 0), o("tb", "T", None, 0), {"k": "badge", "p": [127.0, 38.256], "text": "골짜기", "color": "red", "at": 0.6, "dy": -50}], tilt=30))
next_act()

# ===================== 제3막 (미드롤 1 직전 암전) =====================
MID = [nid()]
sc(1, {"type": "black", "text": "제3막", "accent": "중공군의 야간 폭풍", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(1, ai("easy_trench"), label=DRAMA, chapter={"num": "제3막", "title": "중공군의 야간 폭풍"},
   callouts=[{"text": "4. 16 밤 · 미 제31연대 이지 중대", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, ai("quiet_night"), label=DRAMA)
sc(2, ai("ration_trench"), label=DRAMA)
sc(2, m("chop", "chop", [o("pc", "255", None, 0), {"k": "shock", "pts": [[127.019, 38.242], [127.021, 38.2435], [127.0175, 38.2405], [127.0225, 38.2412]], "at": 0.3, "period": 0.6}], tilt=28),
   callouts=[{"text": "밤 11시 무렵 · 중공군 포격 개시", "style": "red", "at": 0, "pos": "top"}], sfx=[{"id": "boom", "at": 0.2, "volume": 0.45}])
sc(2, ai("bugle_tunnel"), label=DRAMA)
sc(2, m("chop", "chop", [o("pc", "255", None, 0)] + RED3 + [{"k": "unit", "p": [127.022, 38.256], "color": "red", "text": "중공군 제201연대 1개 대대", "at": 0.4}], tilt=28),
   callouts=[{"text": "4. 16 밤 · 세 방향 돌격 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, ai("mg_hot"), label=DRAMA)
sc(1, ai("radio_dead"), label=DRAMA)
sc(2, m("chop", "chop", [o("pc", "255", None, 0), {"k": "clash", "p": "pc", "at": 0.2, "size": 0.9},
                         {"k": "lock", "p": "pc", "at": 0.8, "text": "참호선 붕괴"}], tilt=28))
sc(2, ai("bunker_inside"), label=DRAMA)
sc(3, {"type": "black", "text": "플래시 포크찹", "accent": "VT 사격 요청", "accentAt": 0.55}, pauseBefore=0.2, sfx=[{"id": "hit", "at": 0.5, "volume": 0.45}])
sc(2, {"type": "text", "big": "VT 신관", "style": "yellow", "sub": "땅에 닿기 전 공중에서 먼저 터지는 포탄", "subAt": 0.4})
sc(2, ai("vt_burst"), label=DRAMA)
sc(2, m("chop", "chop", [o("pc", "255", None, 0), {"k": "shock", "pts": [[127.018, 38.2425], [127.0205, 38.244], [127.022, 38.2415], [127.0175, 38.2398], [127.0198, 38.2405]], "at": 0, "period": 0.5}], tilt=30),
   callouts=[{"text": "아군 진지 위 진내사격 (모식)", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("chop", "chop", [o("pc", "255", None, 0), {"k": "line", "path": CHOP, "color": "#ff3b3b", "at": 0.2, "glow": True},
                         {"k": "lock", "p": "pc", "at": 0.8, "text": "고지 함락 직전"}], tilt=28),
   callouts=[{"text": "4. 17 새벽 · 벙커 몇 곳만 남아", "style": "red", "at": 0, "pos": "top"}])
sc(2, ai("command_decision"), label=DRAMA)
sc(2, ai("bunker_waiting"), label=DRAMA)
sc(4, {"type": "cta", "title": "잊혀 가는 격전의 기록, 함께 지켜 주십시오", "at": 0}, pauseBefore=0.3, sfx=[{"id": "pop", "at": 0.3, "volume": 0.45}])
next_act()

# ===================== 제4막 아프리카의 사자들 =====================
sc(2, m("sector", "kagv", [{"k": "unit", "p": "kag", "color": "blue", "text": "강뉴 대대", "at": 0}, {"k": "clash", "p": [126.968, 38.256], "at": 0.8, "size": 0.7}], tilt=24),
   chapter={"num": "제4막", "title": "아프리카의 사자들"}, callouts=[{"text": "4. 16 · 철원 서쪽 고지의 강뉴 대대 (개략)", "style": "blue", "at": 0, "pos": "top"}])
v, lb = ph("kag2", "에티오피아 병사들 (한국전쟁)")
sc(2, v, label=lb)
sc(2, {"type": "person", "q": pin("selassie"), "name": "하일레 셀라시에 1세", "years": "1892 - 1975", "role": "에티오피아 황제"})
sc(2, {"type": "person", "q": pin("makonnen"), "name": "라스 마콘넨", "years": "1852 - 1906", "role": "황제의 아버지 · 군마 '강뉴'의 주인"})
sc(2, {"type": "text", "big": "에티오피아", "style": "yellow", "sub": "아프리카에서 끝까지 독립을 지킨 나라", "subAt": 0.5})
sc(1, ai("emperor_decides"), label=DRAMA)
v, lb = ph("kag3", "한국에 도착한 에티오피아·네덜란드·그리스군 (1951. 5. 8)")
sc(2, v, label=lb, callouts=[{"text": "1951. 5 · 부산 도착", "style": "yellow", "at": 0, "pos": "top"}])
sc(1, {"type": "text", "big": "3,000명+", "style": "yellow", "sub": "전쟁 중 한국에 온 에티오피아 병사", "subAt": 0.3})
sc(3, ai("emperor_flag"), label=DRAMA, callouts=[{"text": "“이 깃발을 반드시 다시 가지고 돌아오라”", "style": "yellow", "at": 2, "pos": "top"}])
sc(2, ai("doubtful_officers"), label=DRAMA)
sc(2, ai("snow_ethiopian"), label=DRAMA)
sc(2, m("kagv", "kagv", [{"k": "unit", "p": "kag", "color": "blue", "text": "강뉴 대대", "at": 0, "pulse": True}, o("tb", "T", "티본 고지", 0.4)], tilt=26),
   hudCta={"at": 0, "dur": 7.5})
sc(2, ai("night_patrol_eth"), label=DRAMA)
sc(1, {"type": "person", "q": pin("marshall"), "name": "S. L. A. 마셜", "years": "1900 - 1977", "role": "미군 전쟁사가 · 『포크찹 고지』 저자"})
sc(2, m("kagv", "kagv", [{"k": "unit", "p": "kag", "color": "blue", "text": "에티오피아 8명", "at": 0},
                         {"k": "arrow", "path": [[126.972, 38.249], [126.977, 38.255], [126.983, 38.26]], "color": "blue", "at": 0.3, "width": 0.6}, o("tb", "T", "티본 고지", 0)], tilt=26),
   callouts=[{"text": "대낮 · 700m 넘는 무인지대 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(1, ai("tbone_raid"), label=DRAMA)
sc(2, {"type": "text", "big": "8명 → 10명", "style": "yellow", "sub": "중공군 포로 2명을 끌고 돌아오다", "subAt": 0.5})
sc(2, {"type": "quotes", "title": "마셜, 『포크찹 고지』", "items": [{"text": "다리를 지킨 호라티우스처럼", "at": 0}, {"text": "기자들이 놓친 에티오피아의 전공", "at": 1.0}]})
sc(2, ai("cpv_fear"), label=DRAMA)
sc(2, ai("carry_comrade"), label=DRAMA)
next_act()

# ===================== 제5막 (미드롤 2 직전 암전) =====================
MID.append(nid())
sc(1, {"type": "black", "text": "제5막", "accent": "아군 진지 위로 쏟아진 포탄", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(1, m("chop", "chop", [o("pc", "255", None, 0), {"k": "arrow", "path": [[127.019, 38.229], [127.0195, 38.235], [127.0195, 38.24]], "color": "blue", "at": 0.3, "width": 0.7}], tilt=28),
   chapter={"num": "제5막", "title": "아군 진지 위로 쏟아진 포탄"}, callouts=[{"text": "4. 17 새벽 4시 30분 · 역습", "style": "blue", "at": 0, "pos": "top"}])
sc(3, ai("clemons_lead"), label=DRAMA, callouts=[{"text": "킹 중대장 · 조지프 클레먼스 중위", "style": "blue", "at": 0, "pos": "top"}])
sc(2, ai("uphill_assault"), label=DRAMA)
sc(3, {"type": "compare", "left": {"title": "킹 중대 출발", "big": "135명", "icon": "none", "color": "blue"},
       "right": {"title": "죽거나 다친 병사", "big": "125명", "icon": "none", "color": "red", "at": 1.0}},
   callouts=[{"text": "영문 위키백과 집계 (자료마다 차이)", "style": "dark", "at": 2, "pos": "lower"}], sfx=[{"id": "hit", "at": 1.0, "volume": 0.45}])
sc(1, ai("captured_weapons"), label=DRAMA)
sc(2, ai("find_survivors"), label=DRAMA)
sc(3, ai("clemons_radio"), label=DRAMA)
sc(2, m("chop", "chop", [o("pc", "255", None, 0),
                         {"k": "arrow", "path": [[127.016, 38.229], [127.017, 38.235], [127.018, 38.2395]], "color": "blue", "at": 0.2, "width": 0.6},
                         {"k": "arrow", "path": [[127.022, 38.229], [127.021, 38.235], [127.0205, 38.2395]], "color": "blue", "at": 0.6, "width": 0.6}], tilt=28),
   callouts=[{"text": "4. 17 저녁 · 제17연대 증원 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(1, m("chop", "chop", [o("pc", "255", None, 0), {"k": "arrow", "path": [[127.028, 38.232], [127.029, 38.239], [127.025, 38.2435]], "color": "blue", "at": 0.2, "width": 0.6}], tilt=28),
   callouts=[{"text": "오른쪽으로 돌아 오른 중대 (개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(2, m("chop", "chop", [o("pc", "255", None, 0)] + RED3 + [{"k": "clash", "p": "pc", "at": 1.2, "size": 0.9}], tilt=28),
   callouts=[{"text": "4. 18 새벽 · 중공군 재공격", "style": "red", "at": 0, "pos": "top"}])
sc(2, ai("bayonet_melee"), label=DRAMA)
sc(2, m("chop", "chop", [o("pc", "255", None, 0), {"k": "shock", "pts": [[127.018, 38.2425], [127.0215, 38.2435], [127.0195, 38.2402], [127.023, 38.2418]], "at": 0, "period": 0.5}], tilt=30),
   callouts=[{"text": "다시 쏟아진 VT 포탄 (모식)", "style": "red", "at": 0, "pos": "top"}])
sc(2, {"type": "bars", "note": "4. 16~18 · 영문 위키백과 집계", "items": [{"label": "유엔군 포탄 · 세 전초 합계", "value": 77000, "display": "7만 7천 발+", "color": "blue", "at": 0},
                                                                     {"label": "4. 18 하루 · 포크찹", "value": 40000, "display": "약 4만 발", "color": "red", "at": 0.6}]})
v, lb = ph("howitzer2", "미군 8인치 곡사포 사격 (1951)")
sc(1, v, label=lb)
sc(2, m("chop", "chop", [o("pc", "255", "255고지", 0, takenAt=0), {"k": "badge", "p": "pc", "text": "고지 사수", "color": "blue", "at": 0.6, "dy": -70}], tilt=24),
   callouts=[{"text": "4. 18 저녁 · 중공군 퇴각", "style": "blue", "at": 0, "pos": "top"}])
v, lb = ph("wounded", "부상병을 돕는 미 제31연대 제1대대 의무병 (한국전쟁)")
sc(3, v, label=lb)
sc(2, ai("barren_crest"), label=DRAMA)
sc(1, m("sector", "kagv", [{"k": "unit", "p": "kag", "color": "blue", "text": "제3 강뉴 대대", "at": 0.3, "pulse": True}], tilt=22))
next_act()

# ===================== 제6막 253전 253승의 신화 =====================
sc(3, m("kagv", "kagv", [{"k": "unit", "p": "kag", "color": "blue", "text": "제3 강뉴 대대", "at": 0}, o("yoke", "Y", "요크 고지", 1.0)], tilt=26),
   chapter={"num": "제6막", "title": "253전 253승의 신화"}, callouts=[{"text": "1953. 5 · 요크 고지 (위치 개략)", "style": "blue", "at": 0, "pos": "top"}])
sc(2, m("kagv", "kagv", [o("yoke", "Y", None, 0),
                         {"k": "arrow", "path": [[126.958, 38.268], [126.96, 38.261], [126.961, 38.258]], "color": "red", "at": 0.2, "width": 0.5},
                         {"k": "arrow", "path": [[126.948, 38.262], [126.955, 38.258], [126.959, 38.257]], "color": "red", "at": 0.5, "width": 0.5},
                         {"k": "shock", "pts": [[126.96, 38.259], [126.957, 38.26]], "at": 0.9, "period": 0.8}]),
   callouts=[{"text": "5. 15~18 · 네 차례 공격 격퇴", "style": "blue", "at": 0, "pos": "top"}])
sc(2, ai("ambush_15"), label=DRAMA)
sc(2, m("kagv", "kagv", [o("yoke", "Y", "요크", 0), o("uncle", "U", "엉클", 0), {"k": "line", "path": RINGY, "color": "#ff3b3b", "at": 0.4, "glow": True},
                         {"k": "arrow", "path": [[126.945, 38.27], [126.95, 38.258], [126.958, 38.25]], "color": "red", "at": 0.2, "width": 0.5}]),
   callouts=[{"text": "5. 19 밤 · 매복조를 피해 우회 포위 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(1, {"type": "black", "text": "5월 20일 새벽", "accent": "요크 고지 백병전", "accentAt": 0.5}, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(2, ai("yoke_grenades"), label=DRAMA)
sc(2, ai("yoke_melee"), label=DRAMA)
sc(2, {"type": "quotes", "title": "참전 용사의 회고", "items": [{"text": "에티오피아 병사 14명과 미군 1명", "at": 0}, {"text": "300명 가까운 중공군에 포위", "at": 1.0}]})
sc(3, ai("shield_fallen"), label=DRAMA)
sc(2, m("kagv", "kagv", [o("yoke", "Y", "요크 고지", 0, takenAt=0), {"k": "badge", "p": "yoke", "text": "고지 사수", "color": "blue", "at": 0.4, "dy": -60}], tilt=24),
   callouts=[{"text": "적 110명 사망 · 퇴각 (국가보훈부 기록)", "style": "blue", "at": 0, "pos": "top"}])
sc(1, {"type": "text", "big": "대한민국 부대 표창", "style": "yellow", "sub": "요크 고지 전투 · 제3 강뉴 대대", "subAt": 0.3})
sc(2, ai("carry_down_dawn"), label=DRAMA)
sc(2, {"type": "black", "text": "살아서든 죽어서든", "accent": "반드시 함께 돌아간다", "accentAt": 0.5})
sc(2, {"type": "text", "big": "253전", "style": "yellow", "sub": "강뉴 대대가 한국에서 치른 전투", "subAt": 0.4})
sc(2, {"type": "text", "big": "253승", "style": "red", "sub": "명령 없이 내준 땅은 없었다", "subAt": 0.5})
sc(3, {"type": "compare", "left": {"title": "전사 · 부상", "big": "121 · 536명", "icon": "none", "color": "blue"},
       "right": {"title": "포로", "big": "0명", "icon": "none", "color": "red", "at": 1.0}},
   callouts=[{"text": "국가보훈부 · 유엔군사령부 집계", "style": "dark", "at": 2, "pos": "lower"}], sfx=[{"id": "hit", "at": 1.0, "volume": 0.45}])
v, lb = ph("kag4", "무반동총을 겨누는 에티오피아 병사들 (한국전쟁)")
sc(2, v, label=lb)
next_act()

# ===================== 제7막 에필로그 (미드롤 3 직전 암전) =====================
MID.append(nid())
sc(1, {"type": "black", "text": "제7막", "accent": "머나먼 땅에서 온 영웅들", "accentAt": 0.4}, pauseBefore=0.5, sfx=[{"id": "heartbeat", "at": 0, "volume": 0.4}])
sc(1, ai("rain_hill"), label=DRAMA, chapter={"num": "제7막", "title": "에필로그 · 머나먼 땅에서 온 영웅들"})
sc(2, m("chop", "chop", [o("pc", "255", None, 0)] + RED3 + [{"k": "shock", "pts": [[127.019, 38.242], [127.021, 38.2435]], "at": 1.0, "period": 0.7}], tilt=26),
   callouts=[{"text": "1953. 7. 6 밤 · 장맛비 속 재공격", "style": "red", "at": 0, "pos": "top"}])
sc(3, ai("mud_trench"), label=DRAMA)
sc(2, {"type": "black", "text": "1953. 7. 11", "accent": "포크찹 철수 결정", "accentAt": 0.4})
v, lb = ph("armistice", "휴전 협정에 서명하는 클라크 유엔군 사령관 (1953. 7. 27)")
sc(2, v, label=lb)
sc(2, m("sector", "sector", [o("pc", "255", None, 0), {"k": "line", "path": MDL, "color": "#ff3b3b", "at": 0.3, "glow": True},
                             {"k": "badge", "p": [127.05, 38.25], "text": "군사분계선", "color": "red", "at": 0.8, "dy": -50}]),
   callouts=[{"text": "휴전선 언저리로 사라진 포크찹 (개략)", "style": "red", "at": 0, "pos": "top"}])
sc(2, m("front53", "front53", [{"k": "front", "path": FRONT53, "at": 0}, {"k": "marker", "p": "yeoncheon", "color": "blue", "at": 0.3},
                               {"k": "marker", "p": "cheorwon", "color": "blue", "at": 0.5}, {"k": "marker", "p": "seoul", "color": "blue", "at": 0.9}]))
sc(2, ai("return_flag"), label=DRAMA)
v, lb = ph("addis", "아디스아바바의 강뉴 대대 기념비")
sc(2, v, label=lb)
sc(2, {"type": "black", "text": "1974 · 공산 군사 정권", "accent": "지워진 이름", "accentAt": 0.6})
sc(2, ai("old_veteran"), label=DRAMA)
v, lb = ph("vets", "춘천 에티오피아 한국전 참전기념관을 찾은 노병들 (2010)")
sc(2, v, label=lb)
sc(2, {"type": "quotes", "title": "70년 만에 방한한 노병들 (2023)", "items": [{"text": "목숨 걸고 싸운 일, 결코 헛되지 않았다", "at": 0.3}]})
sc(2, ai("memorial_flowers"), label=DRAMA)
sc(1, {"type": "black", "text": "또 다른", "accent": "이름 없는 영웅들", "accentAt": 0.4}, pauseBefore=0.3)
sc(3, m("korea", "east", [{"k": "marker", "p": "incheon", "color": "blue", "at": 0.2}, {"k": "marker", "p": "jangsa", "color": "yellow", "at": 0.8},
                          {"k": "badge", "p": "jangsa", "text": "장사리", "color": "red", "at": 1.2, "dy": -60}]),
   callouts=[{"text": "1950. 9 · 경북 영덕 장사리", "style": "yellow", "at": 0, "pos": "top"}])
sc(2, ai("student_soldiers"), label=DRAMA)
sc(2, m("east", "east", [{"k": "marker", "p": "incheon", "color": "blue", "at": 0}, {"k": "marker", "p": "jangsa", "color": "yellow", "at": 0},
                         {"k": "arrow", "path": [[129.9, 36.3], [129.6, 36.29], [129.4, 36.28]], "color": "blue", "at": 0.3, "width": 1.0},
                         {"k": "arrow", "path": [[125.8, 37.3], [126.2, 37.4], [126.58, 37.46]], "color": "blue", "at": 1.0, "width": 1.0}]),
   callouts=[{"text": "적의 눈을 동해안으로 · 양동 작전", "style": "blue", "at": 0, "pos": "top"}])
sc(2, {"type": "text", "big": "EP23 장사상륙작전", "style": "yellow", "sub": "인천을 살린 772명 학도병의 문산호 결사대 · 곧 공개", "subAt": 0.5})
sc(2, {"type": "endcard", "title": "1953년 봄, 포크찹 고지.\n253전 253승, 포로 0명.", "q": pin("end")}, tail=1.0)
next_act() if CUR["act"] < len(ACTS) - 1 else None
assert CUR["act"] == len(ACTS) - 1 and CUR["i"] == len(ACTS[-1]), ("남은 문장", CUR)

# ---------------- AI 그림 ----------------
CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
ETH = "Ethiopian soldiers whose heads are round balls painted as the 1950s Ethiopian imperial flag (green, yellow and red horizontal stripes with a golden crowned lion in the center), wearing 1953 American M1 steel helmets and olive drab uniforms"
ETH1 = "an Ethiopian soldier whose head is a round ball painted as the 1950s Ethiopian imperial flag (green, yellow and red horizontal stripes with a golden crowned lion in the center), wearing a 1953 American M1 steel helmet and olive drab uniform"
US = "American infantrymen whose heads are round balls painted as the USA flag, wearing 1953 M1 steel helmets and olive drab field jackets"
US1 = "an American infantry officer whose head is a round ball painted as the USA flag, wearing a 1953 M1 steel helmet and olive drab field jacket"
CN = "Chinese People's Volunteer Army soldiers whose heads are round balls painted as the red Chinese flag with yellow stars, wearing 1953 quilted khaki uniforms and caps"
END = ", leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic wide shot, dark desaturated palette, film grain, no people visible, no text, no letters."
AI = {
    "night_barrage": "A small barren Korean hill at night in April 1953 struck by a massive artillery barrage, sandbag bunkers and zigzag trenches on the crest, bright explosions and flares, smoke drifting, " + LAND,
    "radio_vt": CB + US1 + " crouching inside a dark log-and-sandbag bunker shouting into a field radio handset, dust falling from the ceiling, flashes of explosions through the firing slit" + END,
    "ridge_shelled": "A bare Korean ridge in 1953 churned into craters by endless shelling, broken tree stumps, collapsed trenches, grey dawn light, smoke, desolate, " + LAND,
    "outpost_fist": "A lonely fortified hilltop outpost in Korea in 1953 jutting out in front of the main defensive line, sandbag bunkers and barbed wire on the crest, enemy-held hills looming on three sides in the haze, " + LAND,
    "night_wire": CB + CN + " crawling through barbed wire at the foot of a hill at night, one cutting the wire with cutters, faint moonlight" + END,
    "trench_listen": CB + US + " crouching silently in a dark trench at night, one with his hand cupped behind his ear listening, rifles ready, faint mist" + END,
    "night_carry": CB + US + " climbing a steep dark hillside at night carrying heavy water cans and ammunition boxes on A-frame back packs, bent under the weight" + END,
    "tunnel_cpv": CB + CN + " pouring out of the dark mouth of a tunnel dug into a hillside at night, carrying submachine guns and grenades, lantern light inside the tunnel" + END,
    "easy_trench": CB + US + " manning a sandbagged trench on a small hilltop at dusk, looking out toward dark enemy hills, calm before a storm" + END,
    "quiet_night": "A quiet small Korean hilltop outpost at night under starlight in April 1953, bunkers and trenches silhouetted, enemy hills dark in the distance, eerie stillness, " + LAND,
    "ration_trench": CB + US + " eating cold ration cans in a trench at night, one dozing against the trench wall with his helmet tilted, a rifle propped beside him" + END,
    "bugle_tunnel": CB + CN + " blowing bugles and whistles while charging up a hillside at night in a dense wave, flares overhead, explosions" + END,
    "mg_hot": CB + US + " firing a machine gun from a sandbagged position at night, the barrel glowing red hot, cartridge cases piling up, tracer fire down the slope" + END,
    "radio_dead": CB + US1 + " shaking a silent field radio with a cut wire dangling from it in a trench at night, desperate, explosions in the background" + END,
    "bunker_inside": CB + US + " pressed against the walls inside a dark cramped log bunker at night, dust falling, a grenade rolling through the doorway, tense faces" + END,
    "vt_burst": "Artillery shells bursting in the air just above a small hilltop at night, bright airbursts raining shrapnel onto the trenches below, bunkers intact, attacking silhouettes on the slope, dramatic, painterly realistic digital illustration, cinematic wide shot, dark palette, film grain, no text, no letters.",
    "command_decision": CB + "American commanders, heads round balls painted as the USA flag, steel helmets, leaning over a map table in a lamp-lit command bunker before dawn, one pointing at a small hill on the map, grim faces" + END,
    "bunker_waiting": CB + "a few exhausted " + US + " hiding in the corner of a half-collapsed bunker at dawn, a wounded comrade bandaged, light seeping through the cracks, waiting for rescue" + END,
    "emperor_decides": CB + "an Ethiopian emperor, head a round ball painted as the 1950s Ethiopian imperial flag, wearing a dignified military uniform with medals and a cape, standing before a large world map in a palace hall, pointing at Korea" + END,
    "emperor_flag": CB + "an Ethiopian emperor, head a round ball painted as the 1950s Ethiopian imperial flag, in a dignified military uniform with medals, handing a large green-yellow-red battalion flag to a kneeling Ethiopian officer before rows of " + ETH + " on a parade ground" + END,
    "doubtful_officers": CB + "skeptical American officers, heads round balls painted as the USA flag, watching with folded arms as a column of " + ETH + " marches past in perfect order" + END,
    "snow_ethiopian": CB + ETH + " standing in deep snow on a Korean mountain in winter, one holding out his glove to catch falling snowflakes in wonder, breath steaming" + END,
    "night_patrol_eth": CB + ETH + " moving silently in a low crouch across a dark valley at night on patrol, rifles ready, faint moonlight" + END,
    "tbone_raid": CB + "eight " + ETH + " jumping into an enemy trench on a hillside in broad daylight, surprised " + CN + " raising their hands, smoke" + END,
    "cpv_fear": CB + CN + " whispering nervously to each other in a trench at night, glancing toward the dark enemy lines, fearful faces" + END,
    "carry_comrade": CB + ETH1 + " carrying a wounded comrade on his back down a steep hillside at dawn, refusing to leave him behind, smoke behind them" + END,
    "clemons_lead": CB + US1 + ", a young first lieutenant, leading his company up a dark cratered hillside before dawn, turning back to wave his men forward, flares overhead" + END,
    "uphill_assault": CB + US + " charging up a steep cratered hillside before dawn under exploding grenades and shells, one soldier waving his comrades forward" + END,
    "captured_weapons": CB + US + " in a battered trench firing captured Chinese submachine guns, empty magazines scattered, smoke" + END,
    "find_survivors": CB + US + " pulling dust-covered survivors out of a collapsed bunker at dawn, embracing exhausted comrades" + END,
    "clemons_radio": CB + US1 + " shouting into a field radio handset in a shattered hilltop trench, only a handful of soldiers left around him, smoke and craters" + END,
    "bayonet_melee": CB + US + " fighting hand to hand with " + CN + " in a hilltop trench at night with bayonets, rifle butts and entrenching shovels, explosions lighting the scene" + END,
    "barren_crest": "The crest of a small Korean hill after a terrible battle in April 1953, completely bare grey earth covered in overlapping shell craters, collapsed bunkers and broken logs, no grass left, smoke, " + LAND,
    "ambush_15": CB + "fifteen " + ETH + " lying in ambush in the grass in front of a hill at night, rifles pointed into the dark" + END,
    "yoke_grenades": CB + ETH + " in a hilltop trench at night as grenades fly in, flare light overhead, one throwing a grenade back, bayonets glinting" + END,
    "yoke_melee": CB + ETH + " fighting hand to hand with " + CN + " who leap into their hilltop trench at night, bayonets, darkness and smoke" + END,
    "shield_fallen": CB + ETH + " forming a protective ring around a fallen comrade in a trench at night, firing outward in every direction, refusing to give way" + END,
    "carry_down_dawn": CB + ETH + " carrying their dead and wounded comrades on their backs and on stretchers down a hillside at dawn in a solemn line, no one left behind" + END,
    "rain_hill": "A small battered Korean hilltop outpost in heavy monsoon rain at night in July 1953, flooded trenches, artillery flashes through the downpour, " + LAND,
    "mud_trench": CB + US + " standing knee-deep in muddy water in a flooded trench in pouring rain at night, firing rifles into the darkness" + END,
    "return_flag": CB + ETH + " marching proudly down a gangway from a troop ship carrying their green-yellow-red battalion flag home, cheering crowds below" + END,
    "old_veteran": CB + "an elderly Ethiopian Korean War veteran, head a round ball painted as the Ethiopian flag, wearing an old uniform jacket with medals, sitting alone in a modest room holding a faded photograph of his comrades in Korea, soft window light" + END,
    "memorial_flowers": "A quiet stone war memorial in a Korean city park in spring with fresh flowers laid at its base, an Ethiopian flag and a Korean flag side by side, soft morning light, painterly realistic digital illustration, no people, no text, no letters.",
    "student_soldiers": "Young Korean student soldiers in 1950 in ill-fitting uniforms and school caps holding old rifles on the deck of an old transport ship at night on a rough sea, nervous determined faces, painterly realistic digital illustration, cinematic, dark palette, film grain, no text, no letters.",
    "thumb_subject": "Photorealistic black-and-white 1953 Korean War documentary portrait of a fierce Ethiopian Imperial Bodyguard infantryman of the Kagnew Battalion, American M1 steel helmet, intense determined eyes, sweat and dust on his face, rifle with fixed bayonet held across his chest, waist-up, face clearly visible and turned slightly toward the right of the frame, sharp detail, high contrast monochrome, isolated on a plain pure white background, no shadows on the background, no text.",
}

used = {s["visual"]["img"] for s in S if s["visual"]["type"] == "ai"}
missing = used - set(AI)
assert not missing, missing
unused = set(AI) - used - {"thumb_subject"}
assert not unused, unused

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
board = {"title": "포크찹 고지 전투", "subtitle": "1953. 4 ~ 7", "target_sec": 1230, "voice": "U1cJYS4EdbaHmfR7YzHd",
         "midrolls": MID, "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")


def say(l):
    return l if isinstance(l, str) else l["say"]


n = sum(len(say(l)) for s in S for l in s["lines"])
print("scenes", len(S), "say chars", n, "mid", MID, "chapters", [sid(i) for i in chap], "ai", len(used))
print("photo q", [s["visual"].get("q") for s in S if s["visual"].get("q")])
