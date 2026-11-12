# EP08 (영문 《Map of War》) 장진호 전투 20분판 스토리보드 생성기 — 첫 생성용(기록). 나레이션은 script.md 문장을 순서대로 그대로 가져온다.
# ⚠️ storyboard.json을 손으로 고친 뒤에는 다시 돌리지 말 것 (수정 사항이 덮어써짐)
# 영문 단독 제작(번역판 아님): lang=en · Adam 1.02배속 · tts_mode=act (1막 = 일레븐랩스 1회 호출 통 MP3, 장면 분할은 tts.py가 글자 타임스탬프로)
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

# 자막 표기(숫자) ← 낭독 문장(단어) — 긴 것부터
SUBS = [
    ("November twenty-fourth", "November 24"), ("November twenty-seventh", "November 27"), ("November twenty-eighth", "November 28"),
    ("November twenty-ninth", "November 29"), ("December first", "December 1"), ("December second", "December 2"), ("December third", "December 3"),
    ("December sixth", "December 6"), ("December seventh", "December 7"), ("December eighth", "December 8"), ("December ninth", "December 9"),
    ("December eleventh", "December 11"),
    ("Hill twelve-eighty-two", "Hill 1282"), ("Hill twelve-forty", "Hill 1240"), ("Hill fourteen-oh-three", "Hill 1403"), ("Hill ten-eighty-one", "Hill 1081"),
    ("C-one-nineteen", "C-119"), ("Ten Corps", "X Corps"),
    ("one hundred twenty thousand", "120,000"), ("one hundred thousand", "100,000"), ("Fifteen thousand", "15,000"), ("Fourteen thousand", "14,000"),
    ("fourteen thousand", "14,000"), ("seventeen thousand", "17,000"), ("Ten thousand", "10,000"), ("three thousand", "3,000"), ("four thousand", "4,000"),
    ("a thousand", "1,000"), ("two hundred forty", "240"),
    ("Seventy-eight miles", "78 miles"), ("fourteen miles", "14 miles"), ("Fourteen miles", "14 miles"), ("eleven more miles", "11 more miles"),
    ("eleven miles", "11 miles"), ("four miles", "4 miles"), ("twenty-nine feet", "29 feet"),
    ("Twelve divisions", "12 divisions"), ("two Chinese divisions", "2 Chinese divisions"), ("forty degrees", "40 degrees"),
    ("twenty below zero", "20 below zero"), ("Then thirty below", "Then 30 below"), ("approached forty below", "approached 40 below"), ("Forty below", "40 below"),
    ("two and a half tons", "2.5 tons"), ("eight sections", "8 sections"), ("twelve passengers", "12 passengers"), ("Five babies", "5 babies"),
    ("eighty hours", "80 hours"), ("five days", "5 days"), ("two days", "2 days"), ("two weeks", "2 weeks"), ("Seventeen days", "17 days"),
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


def sc(n, visual, **kw):
    i = nid()
    NUM["n"] += 1
    d = {"id": i, "act": CUR["act"] + 1, "lines": take(n), "visual": visual}
    d.update(kw)
    S.append(d)


def m(fr, to=None, items=None, **kw):
    v = {"type": "map", "from": fr, "to": to or fr, "items": items or []}
    v.update(kw)
    return v


def ai(img, kb="in", **kw):
    v = {"type": "ai", "img": img, "kb": kb}
    v.update(kw)
    return v


# 사진: 이전 에피소드(EP06 장진호·EP15 흥남·EP18 군우리·EP11 인천)에서 검증한 핀을 파일명 앞부분으로 찾음
KNOWN = sorted({v for f in glob.glob(str(HERE.parent / "*" / "photo_pins.json")) if EP not in f for v in json.load(open(f, encoding="utf-8")).values()})
PH = {
    "macarthur": "Douglas MacArthur in Korea, 1950", "chosin": "Chosin.jpg", "smith": "Oliver P. Smith", "thanksgiving": "Thanksgiving, Hagaru-ri",
    "prisoners": "NARA 111-SC351718", "gear": "127-N-A4524", "tanks_koto": "Tanks on Road South of Koto-ri", "pow_sneakers": "Chinese POWs south of Koto-ri",
    "pow_padded": "NARA 127-N-A5387", "briefing": "Briefing, Generals Almond", "clear_ridge": "Marines Clear a Ridge", "corsair": "F4U Corsair fires rocket at Chosin",
    "yudam_hagaru": "Marines Between Yudam-ni and Hagaru-ri", "south_hagaru": "Marines South of Hagaru-ri", "puller": "Douglas MacArthur and Lewis Puller",
    "blown": "A5376", "c119": "C-119s Yonpo", "drop": "141218-F-BN648-004", "treadway": "A5408", "funchilin_road": "Marines on Road Between Funchilin Pass",
    "harbour": "Ships in Hungnam harbour", "meredith": "Korean refugees aboard SS Meredith Victory", "begor": "USS Begor", "cemetery": "1st Marine Division Cemetery",
    "memorial": "Chosin Few Memorial", "litzenberg": "Homer Litzenberg Addresses",
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


def black(a, b):
    return {"type": "black", "text": a, "accent": b, "accentAt": 0.5}


def text(big, style="yellow", sub=None):
    v = {"type": "text", "big": big, "style": style}
    if sub:
        v.update(sub=sub, subAt=0.4)
    return v


def cmp(lt, lb, rt, rb, lc="blue", rc="red"):
    return {"type": "compare", "left": {"title": lt, "big": lb, "icon": "none", "color": lc}, "right": {"title": rt, "big": rb, "icon": "none", "color": rc, "at": 0.6}}


def chap(n, title):
    return {"num": f"ACT {n}", "title": title}


DRAMA = "Dramatization"
top = lambda t, s="yellow", at=0: [{"text": t, "style": s, "at": at, "pos": "top"}]
low = lambda t, s="dark", at=0: [{"text": t, "style": s, "at": at, "pos": "lower"}]

P = {
    "seoul": [126.978, 37.566, "Seoul"], "inchon": [126.62, 37.47, "Inchon"], "pyongyang": [125.754, 39.02, "Pyongyang"],
    "sinuiju": [124.4, 40.1, "Yalu River"], "hyesan": [128.18, 41.4, "Hyesanjin"],
    "yudam": [127.12, 40.48, "Yudam-ni"], "toktong": [127.18, 40.43, "Toktong Pass"], "hagaru": [127.25, 40.38, "Hagaru-ri"],
    "kotori": [127.3, 40.29, "Koto-ri"], "bridge": [127.33, 40.24, "Funchilin Pass"], "chinhung": [127.37, 40.19, "Chinhung-ni"],
    "hamhung": [127.54, 39.92, "Hamhung"], "hungnam": [127.62, 39.83, "Hungnam"], "sudong": [127.42, 40.11, "Sudong"],
    "sinhung": [127.32, 40.46, "Sinhung-ni"], "reservoir": [127.22, 40.43, "Chosin Reservoir"],
    # 고지·지점 좌표는 개략 (EP06 jangjin 좌표 기준 + 모식 배치)
    "h1282": [127.105, 40.505, "Hill 1282"], "h1240": [127.14, 40.51, "Hill 1240"], "h1403": [127.085, 40.468, "Hill 1403"],
    "foxhill": [127.183, 40.437, "Fox Hill"], "easthill": [127.265, 40.388, "East Hill"], "hellfire": [127.275, 40.335, "Hell Fire Valley"],
    "h1081": [127.35, 40.232, "Hill 1081"], "strip": [127.245, 40.372, "Airstrip"],
}
V = {
    "korea": {"center": [127.3, 38.6], "span": 7.0}, "nk": {"center": [126.9, 40.2], "span": 4.2}, "route": {"center": [127.38, 40.15], "span": 1.0},
    "chosin": {"center": [127.22, 40.4], "span": 0.42}, "yudam": {"center": [127.125, 40.485], "span": 0.2}, "toktong": {"center": [127.18, 40.44], "span": 0.14},
    "hagaru": {"center": [127.25, 40.38], "span": 0.14}, "south": {"center": [127.28, 40.32], "span": 0.34}, "kotori": {"center": [127.31, 40.28], "span": 0.16},
    "pass": {"center": [127.33, 40.25], "span": 0.2}, "bridge": {"center": [127.345, 40.236], "span": 0.12}, "coast": {"center": [127.5, 39.98], "span": 0.75},
}
MSR = [[127.12, 40.48], [127.17, 40.44], [127.21, 40.41], [127.25, 40.38], [127.27, 40.34], [127.3, 40.29], [127.32, 40.25], [127.34, 40.22],
       [127.37, 40.19], [127.43, 40.08], [127.54, 39.92], [127.62, 39.83]]
msr = lambda at=0.2, c="#d98b2b": {"k": "line", "path": MSR, "color": c, "at": at}
U = lambda p, t, c="blue", at=0.2, **kw: dict({"k": "unit", "p": p, "color": c, "text": t, "at": at}, **kw)
red_a = lambda path, at=0.3, w=0.9: {"k": "arrow", "path": path, "color": "red", "at": at, "width": w}
blue_a = lambda path, at=0.3, w=0.9: {"k": "arrow", "path": path, "color": "blue", "at": at, "width": w}
swarm = lambda path, at=0.2, n=200, **kw: dict({"k": "swarm", "path": path, "at": at, "n": n}, **kw)
obj = lambda p, n, txt=None, at=0, c="red", **kw: dict({"k": "obj", "p": p, "n": n, "at": at, "color": c, **({"text": txt} if txt else {})}, **kw)
# 중공군 남하 축선 (압록강 → 장진호, 개략)
SOUTH_W = [[126.6, 41.0], [126.85, 40.75], [127.05, 40.55], [127.12, 40.5]]
SOUTH_E = [[127.6, 41.1], [127.45, 40.8], [127.33, 40.55], [127.3, 40.47]]

# ===== ACT 1 · The Trap in the Mountains =====
sc(2, m("korea", "korea", [blue_a([[126.62, 37.47], [126.9, 38.4], [125.8, 39.0]], 0.1), blue_a([[125.8, 39.1], [125.0, 39.8], [124.5, 40.0]], 0.6)]),
   callouts=top("AUTUMN 1950 · KOREA"))
sc(2, m("korea", "nk", [{"k": "marker", "p": "pyongyang", "color": "blue", "at": 0}, blue_a([[127.5, 39.9], [127.3, 40.5], [127.6, 41.1]], 0.4),
                        {"k": "marker", "p": "sinuiju", "color": "dark", "at": 0.6}]), callouts=top("RACE TO THE YALU", "blue"))
sc(3, ph("macarthur"), label="Gen. Douglas MacArthur in Korea (1950)", callouts=top("“HOME BY CHRISTMAS”", "yellow", 0.4))
sc(3, {"type": "titlecard", "title": "BATTLE OF CHOSIN RESERVOIR", "sub": "The 17-Day March Out of Frozen Hell · 1950", "at": 0, "q": pin("chosin")}, flash=True,
   sfx=[{"id": "boom", "at": 0, "volume": 0.5}])
sc(1, m("nk", "chosin", [{"k": "marker", "p": "hungnam", "color": "blue", "at": 0.1}, U("reservoir", "Chosin Reservoir", "blue", 0.5, pulse=True)]))
sc(2, ph("smith"), label="Maj. Gen. Oliver P. Smith · 1st Marine Division")
sc(5, m("chosin", "route", [msr(0.1), {"k": "marker", "p": "yudam", "color": "blue", "at": 0}, {"k": "marker", "p": "hungnam", "color": "dark", "at": 0.5}],
        flight=["chosin", "south", "route"], hud=True, tilt=28, temp="-8°F"), callouts=top("ONE ROAD · 78 MILES · THE MSR", "yellow", 0.3))
sc(3, cmp("ALMOND · X CORPS", "SPEED", "SMITH · 1ST MARDIV", "CAUTION", "red", "blue"))
sc(4, ph("thanksgiving"), label="Marines at Hagaru-ri on Thanksgiving (Nov 22, 1950)")
sc(1, black("THE MOUNTAINS", "WERE NOT EMPTY"), sfx=[{"id": "wind", "at": 0, "volume": 0.5}])
sc(4, m("nk", "chosin", [swarm(SOUTH_W, 0.15), swarm(SOUTH_E, 0.35), {"k": "marker", "p": "reservoir", "color": "red", "at": 0.6}], hud=True),
   callouts=top("CHINESE 9TH ARMY GROUP · ~120,000 MEN", "red"))
sc(4, ai("night_march"), label=DRAMA)
sc(4, ph("prisoners"), label="First Chinese prisoners in Korea (Oct–Nov 1950)", callouts=top("EARLY NOVEMBER · SUDONG", "yellow"))
sc(1, text("“CHINA WILL NOT\nINTERVENE IN FORCE”", "red", "MacArthur's headquarters · Tokyo"))
sc(3, ai("pva_ambush", bubbles=[{"text": "Cut the one road\nand it is over.", "x": 0.7, "y": 0.2, "at": 1}]), label=DRAMA)
sc(3, m("chosin", "chosin", [msr(0), red_a([[127.0, 40.56], [127.1, 40.49]], 0.2, 0.7), red_a([[127.05, 40.37], [127.17, 40.43]], 0.4, 0.7),
                            red_a([[127.36, 40.47], [127.26, 40.39]], 0.6, 0.7), red_a([[127.42, 40.3], [127.31, 40.3]], 0.8, 0.7)], tilt=30),
   callouts=top("MAO'S PLAN · CUT THE ROAD INTO PIECES", "red"))
sc(4, m("chosin", "chosin", [msr(0), U("yudam", "5th & 7th Marines", "blue", 0.1, pulse=True), U("hagaru", "Hagaru-ri garrison", "blue", 0.35),
                            U("kotori", "Koto-ri garrison", "blue", 0.55), U("sinhung", "Army RCT-31", "blue", 0.8)], hud=True, tilt=32, temp="-12°F"),
   callouts=top("LATE NOVEMBER 1950", "blue"))
sc(2, ai("hidden_ridges"), label=DRAMA)
next_act()

# ===== ACT 2 · Sub-Zero Nightmare =====
sc(3, m("route", "chosin", [msr(0)], hud=True, tilt=26, temp="-20°F"), chapter=chap(2, "SUB-ZERO NIGHTMARE"),
   callouts=top("SIBERIAN COLD FRONT", "blue"), sfx=[{"id": "wind", "at": 0, "volume": 0.55}])
sc(4, text("-40°F", "blue", "Chosin Reservoir · nights of late Nov–Dec 1950"))
sc(6, ai("frozen_night"), label=DRAMA)
sc(4, ph("gear"), label="7th Marines advance north in cold-weather gear (1950)")
sc(3, ai("frozen_rations"), label=DRAMA)
sc(4, ai("frostbite_aid"), label=DRAMA)
sc(4, ai("dig_foxhole"), label=DRAMA)
sc(4, {"type": "profile", "title": "THE MSR GORGE · CROSS-SECTION", "pts": [[0, 1500], [0.15, 1380], [0.32, 1180], [0.44, 1020], [0.5, 1000], [0.56, 1030], [0.68, 1200], [0.85, 1400], [1, 1520]],
       "bare": True, "yMin": 900, "yMax": 1600, "marks": [{"x": 0.5, "text": "MSR · ONE TRUCK WIDE", "style": "yellow"}, {"x": 0.18, "text": "ENEMY RIDGE", "style": "red", "lift": 40}, {"x": 0.82, "text": "ENEMY RIDGE", "style": "red", "lift": 40}],
       "arrows": [{"from": 0.2, "to": 0.48, "color": "red"}, {"from": 0.8, "to": 0.52, "color": "red"}], "left": "WEST", "right": "EAST", "note": "Schematic · not to scale"})
sc(2, ph("tanks_koto"), label="Tanks and trucks on the road south of Koto-ri (Dec 1950)")
sc(4, ph("pow_sneakers"), label="Chinese prisoners in canvas shoes near Koto-ri (Dec 1950)")
sc(3, ph("pow_padded"), label="Chinese prisoner in a quilted cotton uniform · Chosin (Dec 1950)")
sc(3, black("NOVEMBER 27, 1950", "THE BUGLES"), sfx=[{"id": "bugle", "at": 1.5, "volume": 0.4}])
next_act()

# ===== ACT 3 · The Ambush at Yudam-ni =====
MID = [nid()]
sc(5, black("ACT 3", "THE AMBUSH AT YUDAM-NI"), sfx=[{"id": "bugle", "at": 0.4, "volume": 0.45}])
sc(3, m("chosin", "yudam", [U("yudam", "5th & 7th Marines", "blue", 0), red_a([[127.08, 40.56], [127.11, 40.5]], 0.3, 0.7), red_a([[127.02, 40.46], [127.09, 40.47]], 0.5, 0.7),
                           red_a([[127.22, 40.5], [127.17, 40.45]], 0.75, 0.7)], hud=True, tilt=34, temp="-25°F"), chapter=chap(3, "THE AMBUSH AT YUDAM-NI"),
   callouts=top("NIGHT OF NOV 27 · 2 DIVISIONS ATTACK · 1 CUTS THE ROAD", "red"))
sc(5, m("yudam", "yudam", [obj("h1282", "1282", None, 0.3), obj("h1240", "1240", None, 0.45), obj("h1403", "1403", None, 0.6),
                          {"k": "clash", "p": "h1282", "at": 0.7}, {"k": "clash", "p": "h1240", "at": 0.9}, {"k": "clash", "p": "h1403", "at": 1.1}], hud=True, tilt=36),
   callouts=top("HILLS 1282 · 1240 · 1403 (approx.)", "yellow"))
sc(3, ai("wave_snow"), label=DRAMA, sfx=[{"id": "artillery_far", "at": 0.3, "volume": 0.35}])
sc(5, ai("cooks_hill"), label=DRAMA)
sc(3, ai("dawn_ridge"), label=DRAMA)
sc(6, m("chosin", "chosin", [msr(0), {"k": "shock", "pts": ["yudam", "foxhill", "hagaru", "sinhung"], "at": 0.2, "period": 0.9},
                            {"k": "marker", "p": "foxhill", "color": "blue", "at": 0.45}, {"k": "marker", "p": "strip", "color": "blue", "at": 0.6}], hud=True, tilt=30),
   callouts=top("STRUCK EVERYWHERE AT ONCE", "red"))
sc(4, m("chosin", "chosin", [msr(0), {"k": "lock", "p": "yudam", "at": 0.1}, {"k": "lock", "p": "foxhill", "at": 0.3}, {"k": "lock", "p": "hagaru", "at": 0.5},
                            {"k": "lock", "p": "kotori", "at": 0.7}, {"k": "lock", "p": "sinhung", "at": 0.9}], tilt=30), callouts=top("EACH ONE SURROUNDED", "red", 0.5))
sc(2, {"type": "document", "org": "GHQ FAR EAST COMMAND · TOKYO", "head": "TO: JOINT CHIEFS OF STAFF", "stamp": "SECRET",
       "rows": ["WE FACE AN ENTIRELY NEW WAR", "28 NOVEMBER 1950"], "note": "Reconstruction · gist of MacArthur's report"})
sc(6, m("south", "south", [msr(0), blue_a([[127.3, 40.29], [127.28, 40.33]], 0.1, 0.7), {"k": "clash", "p": "hellfire", "at": 0.5},
                          red_a([[127.22, 40.33], [127.27, 40.335]], 0.4, 0.6), red_a([[127.34, 40.34], [127.285, 40.335]], 0.55, 0.6),
                          {"k": "badge", "p": "hellfire", "text": "HELL FIRE VALLEY", "color": "red", "at": 0.7, "dy": -80}], tilt=32),
   callouts=top("NOV 29 · TASK FORCE DRYSDALE", "yellow"))
sc(4, m("chosin", "toktong", [{"k": "line", "path": MSR[:4], "color": "#ff5252", "at": 0.1}, U("yudam", "Yudam-ni", "blue", 0), U("hagaru", "Hagaru-ri", "blue", 0.2)], hud=True, tilt=28),
   callouts=top("14 MILES · ENEMY-HELD", "red"))
sc(1, black("EVERY ROAD CLOSED", "WHAT NOW?"))
sc(5, {"type": "cta", "title": "Follow every mile of the breakout on the map", "at": 0}, pauseBefore=0.3, sfx=[{"id": "pop", "at": 0.3, "volume": 0.45}])
next_act()

# ===== ACT 4 · "Retreat, Hell!" =====
sc(6, ph("briefing"), label="Almond, MacArthur and Smith (right) at Inchon (Sept. 1950)", chapter=chap(4, "“RETREAT, HELL!”"))
sc(8, m("chosin", "hagaru", [U("hagaru", "Hagaru-ri", "blue", 0, pulse=True), {"k": "marker", "p": "strip", "color": "blue", "at": 0.5}], flight=["chosin", "hagaru"], hud=True, tilt=34, temp="-24°F"),
   callouts=top("HAGARU-RI · HUB OF THE CAMPAIGN", "blue"))
sc(3, ai("hagaru_line"), label=DRAMA)
sc(4, m("hagaru", "hagaru", [U("hagaru", "3/1 Marines", "blue", 0), red_a([[127.2, 40.35], [127.24, 40.375]], 0.15, 0.6), obj("easthill", "E", "East Hill", 0.35),
                            red_a([[127.3, 40.4], [127.27, 40.39]], 0.5, 0.6), {"k": "clash", "p": "easthill", "at": 0.7}], tilt=36, hud=True),
   callouts=top("NOV 28–29 · HAGARU-RI PERIMETER", "red"))
sc(5, ai("airstrip"), label=DRAMA)
sc(5, text("4,000+ WOUNDED", "yellow", "flown out from the Hagaru-ri airstrip · Dec 1950"))
sc(7, ai("carry_dead"), label=DRAMA)
sc(3, cmp("FLY OUT", "ABANDON THE GUNS", "WALK OUT", "AS A DIVISION", "red", "blue"))
sc(4, ai("smith_quote", bubbles=[{"text": "Retreat, hell!", "x": 0.7, "y": 0.2, "at": 3}]), label=DRAMA)
sc(6, black("NO REAR", "ONLY A BREAKOUT"))
sc(3, ph("clear_ridge"), label="Marines clear a ridge during the breakout (Dec 1950)")
sc(5, m("hagaru", "chosin", [msr(0), blue_a([[127.12, 40.48], [127.17, 40.44], [127.21, 40.41], [127.25, 40.385]], 0.2, 0.8), obj("foxhill", "F", "Toktong Pass", 0.7)],
        hud=True, tilt=30, temp="-30°F"), callouts=top("DEC 1 · THE BREAKOUT BEGINS", "blue"))
next_act()

# ===== ACT 5 · The Breakout along the MSR =====
MID.append(nid())
sc(1, black("ACT 5", "THE BREAKOUT ALONG THE MSR"))
sc(4, m("chosin", "toktong", [obj("foxhill", "F", "Fox Hill", 0), swarm([[127.15, 40.47], [127.17, 40.45], [127.183, 40.438]], 0.3, 120),
                             swarm([[127.22, 40.41], [127.2, 40.425], [127.185, 40.436]], 0.5, 120)], hud=True, tilt=36, temp="-28°F"),
   chapter=chap(5, "THE BREAKOUT ALONG THE MSR"), callouts=top("FOX COMPANY · 2/7 MARINES · ~240 MEN", "blue"))
sc(5, ai("fox_hill"), label=DRAMA)
sc(5, ai("barber_stretcher"), label=DRAMA)
sc(4, m("toktong", "yudam", [U("yudam", "1/7 Marines · Davis", "blue", 0), {"k": "arrow", "path": [[127.12, 40.48], [127.14, 40.475], [127.16, 40.462], [127.175, 40.448], [127.183, 40.438]],
                                                                       "color": "blue", "at": 0.4, "width": 0.6}, obj("foxhill", "F", "Fox Hill", 0.2)], hud=True, tilt=36),
   callouts=top("CROSS-COUNTRY · AT NIGHT · OVER THE MOUNTAINS", "blue"))
sc(6, ai("davis_march"), label=DRAMA)
sc(3, ai("fox_relief"), label=DRAMA, callouts=top("MEDAL OF HONOR · BARBER & DAVIS", "yellow", 2))
sc(5, ph("corsair"), label="Marine Corsair fires rockets at Chosin (Dec 1950)")
sc(4, ph("yudam_hagaru"), label="Marines on the road between Yudam-ni and Hagaru-ri (Dec 1950)", callouts=top("~80 HOURS · 14 MILES", "yellow"))
sc(6, m("chosin", "chosin", [{"k": "clash", "p": "sinhung", "at": 0.1}, {"k": "arrow", "path": [[127.31, 40.44], [127.29, 40.41], [127.26, 40.39]], "color": "blue", "at": 0.5, "width": 0.5},
                            U("hagaru", "Marine lines", "blue", 0.3)], tilt=30), callouts=top("TASK FORCE FAITH · ~3,000 MEN · ~1,000 SURVIVORS", "red"))
sc(3, m("hagaru", "south", [msr(0), blue_a([[127.25, 40.38], [127.27, 40.34], [127.3, 40.295]], 0.3, 0.8), U("kotori", "Koto-ri", "blue", 0.6)], hud=True, tilt=30),
   callouts=top("NEXT · 11 MILES TO KOTO-RI", "yellow"))
next_act()

# ===== ACT 6 · The Miracle at Funchilin Pass =====
sc(3, ph("south_hagaru"), label="7th Marines just south of Hagaru-ri (Dec 6, 1950)", chapter=chap(6, "THE MIRACLE AT FUNCHILIN PASS"))
sc(7, ph("puller"), label="Col. Lewis “Chesty” Puller (right) with MacArthur (Sept. 1950)")
sc(3, m("kotori", "pass", [msr(0), U("kotori", "Koto-ri", "blue", 0), {"k": "marker", "p": "bridge", "color": "red", "at": 0.5}], flight=["kotori", "pass", "bridge"],
        hud=True, tilt=38, temp="-24°F"), callouts=top("FUNCHILIN PASS", "yellow"))
sc(5, ph("blown"), label="The blown bridge at Funchilin Pass (Dec 1950)", callouts=top("GAP · ~29 FEET", "red"))
sc(2, text("14,000 MEN\n1,000+ VEHICLES", "red", "trapped above the gap"))
sc(3, black("DROP A BRIDGE", "FROM THE SKY"))
sc(4, ph("c119"), label="C-119 Flying Boxcars at Yonpo airfield (Dec 1950)")
sc(5, ph("drop"), label="A bridge section falls from a C-119 over Koto-ri (Dec 7, 1950)", callouts=top("8 SECTIONS DROPPED · DEC 7", "blue"))
sc(5, m("pass", "bridge", [obj("h1081", "1081", "Hill 1081", 0.2), blue_a([[127.36, 40.205], [127.352, 40.226]], 0.4, 0.5), {"k": "clash", "p": "h1081", "at": 0.6},
                          {"k": "marker", "p": "bridge", "color": "red", "at": 0}], hud=True, tilt=40, temp="-30°F"), callouts=top("DEC 8–9 · HILL 1081 · BLIZZARD", "blue"))
sc(6, ph("treadway"), label="The treadway bridge in place at Funchilin Pass (Dec 9, 1950)")
sc(6, ai("bridge_crossing"), label=DRAMA)
sc(2, ai("bridge_drop"), label=DRAMA)
sc(3, ph("funchilin_road"), label="Marines on the road between Funchilin Pass and Chinhung-ni (Dec 1950)", callouts=top("DEC 11 · OUT OF THE MOUNTAINS", "blue"))
next_act()

# ===== ACT 7 · Epilogue & Legacy =====
MID.append(nid())
sc(2, black("ACT 7", "EPILOGUE & LEGACY"))
sc(3, ph("harbour"), label="Ships gathered off Hungnam (Dec 14, 1950)", chapter=chap(7, "EPILOGUE & LEGACY"), callouts=top("HUNGNAM EVACUATION · DEC 1950", "blue"))
sc(4, ph("meredith"), label="Refugees aboard SS Meredith Victory (Dec 1950)", callouts=top("~14,000 REFUGEES · ONE SHIP", "yellow"))
sc(2, ph("begor"), label="Demolition of Hungnam port (Dec 24, 1950)", sfx=[{"id": "boom", "at": 0.6, "volume": 0.4}])
sc(4, ph("cemetery"), label="1st Marine Division cemetery at Hamhung (Dec 13, 1950)", callouts=top("UN FORCES · ~17,000 CASUALTIES", "dark", 2))
sc(4, m("chosin", "nk", [{"k": "lock", "p": "reservoir", "at": 0.2, "text": "9TH ARMY GROUP"}, {"k": "marker", "p": "reservoir", "color": "red", "at": 0}]),
   callouts=top("OUT OF ACTION FOR MONTHS", "red"))
sc(6, cmp("MAO'S ORDER", "DESTROY THEM", "THE RESULT", "THEY CAME OUT", "red", "blue"))
sc(5, ph("memorial"), label="Chosin Few Memorial dedication")
sc(4, ai("chosin_today"), label=DRAMA)
sc(3, m("korea", "route", [msr(0.1)], flight=["nk", "chosin", "route"], hud=True, tilt=28, temp="-40°F"), callouts=top("17 DAYS · 78 MILES · 40 BELOW", "yellow"))
sc(3, ai("snow_column"), label=DRAMA)
sc(3, {"type": "cta", "title": "Which battle should we map next?", "at": 0}, pauseBefore=0.3, sfx=[{"id": "pop", "at": 0.3, "volume": 0.45}])
sc(1, {"type": "endcard", "title": "Chosin Reservoir · 1950\nIn memory of the Chosin Few.", "q": pin("litzenberg")}, tail=1.0)
next_act() if CUR["act"] + 1 < len(ACTS) else None
assert CUR["i"] == len(ACTS[-1]), ("남은 문장", ACTS[-1][CUR["i"]:])

# ===== 그림 =====
CB = "Semi-realistic dramatic digital illustration in the style of polished history-YouTube countryball cartoons: "
US = "American Marines whose heads are round balls painted as the United States flag, wearing 1950 M1 helmets with fur-lined parkas, frost on their gear"
US1 = "an American Marine whose head is a round ball painted as the United States flag, wearing a 1950 M1 helmet and a fur-lined parka, frost on his gear"
CN = "Chinese People's Volunteer Army soldiers whose heads are round balls painted as the red Chinese flag with yellow stars, wearing padded mustard-khaki quilted winter uniforms and fur-flap caps"
END = ", leaving calm uncluttered dark background area in the upper right, absolutely no speech bubbles, no balloons, no text boxes, no captions, no text, no letters."
LAND = "painterly realistic digital illustration, cinematic wide shot, cold desaturated icy palette, film grain, no people visible, no text, no letters."
AI = {
    "night_march": CB + "a long silent column of " + CN + " marching at night through deep snow in a pine forest in the North Korean mountains, no fires, no lights, moonlight on the snow, stealthy" + END,
    "hidden_ridges": CB + "hundreds of " + CN + " lying hidden in the snow along high ridgelines at dusk, looking down at a single narrow road in a frozen valley far below where tiny trucks move" + END,
    "frozen_rations": CB + US + " huddled around a tiny fire in a snowy foxhole trying to thaw frozen canned rations, ice crystals on the cans, breath steaming" + END,
    "frostbite_aid": CB + "a navy corpsman with " + US1[3:] + " treating another Marine's frostbitten feet inside a snowy tent by lantern light, rubber boots beside them" + END,
    "dig_foxhole": CB + US + " struggling to dig foxholes in rock-hard frozen ground on a snowy ridge, a shovel bouncing off the earth, one Marine setting a small explosive charge to blast a hole" + END,
    "cooks_hill": CB + "a group of cooks, clerks and truck drivers who are " + US + " grabbing rifles and climbing a steep snowy hill at night toward the sound of battle, tracers above" + END,
    "dawn_ridge": "Grey dawn over a snow-covered ridge above Yudam-ni, North Korea, after a night battle, smoke drifting, abandoned weapons and torn snow, a frozen lake in the distance, " + LAND,
    "hagaru_line": CB + "truck drivers, engineers and clerks who are " + US + " standing in a thin defensive line of shallow snow trenches around a supply camp at night, rifles ready, tents and supply crates behind them" + END,
    "barber_stretcher": CB + "a wounded Marine captain whose head is a round ball painted as the United States flag, lying on a stretcher carried by two Marines through snowy foxholes on a hilltop at night, pointing and directing the defense" + END,
    "davis_march": CB + "a long single-file column of " + US + " trudging cross-country through knee-deep snow over a mountain ridge at night under bright stars, no trail, exhausted but determined" + END,
    "fox_relief": CB + "exhausted, bandaged " + US + " climbing out of snowy foxholes on a hilltop at dawn to greet a relieving column of Marines arriving over the ridge, emotional reunion" + END,
    "bridge_crossing": CB + US + " guiding trucks, ambulances and a tank slowly across a narrow steel treadway bridge over a deep frozen gorge at night, a crowd of Korean refugees in white winter clothes following behind in the snow" + END,
    "chosin_today": "The frozen Chosin Reservoir in the North Korean mountains at dawn today, silent snow-covered peaks, soft pink light, a lonely empty mountain road winding beside the ice, peaceful and solemn, " + LAND,
    "thumb_subject": "Photorealistic black-and-white 1950 Korean War documentary portrait of a young American U.S. Marine at the Chosin Reservoir, wearing a hooded fur-lined M1951-style winter parka over an M1 steel helmet, frost and ice on his eyebrows and stubble, exhausted resolute eyes, waist-up, face clearly visible and turned slightly toward the left of the frame, isolated on a plain pure white background, no shadows on the background, no text.",
}
# EP06 jangjin 그림 재사용 (프롬프트·서명·파일 그대로 복사 → 재생성 비용 0)
REUSE = {k: "jangjin" for k in ("snow_column", "pva_ambush", "frozen_night", "wave_snow", "fox_hill", "smith_quote", "airstrip", "bridge_drop", "carry_dead")}
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
chap_i = [i for i, s in enumerate(S) if s.get("chapter")]
sid = lambda i: S[i]["id"]
first_of = lambda a: next(s["id"] for s in S if s["act"] == a)
last_of = lambda a: [s["id"] for s in S if s["act"] == a][-1]
music = [{"id": "drone", "from": "s01", "to": "s03", "volume": 0.2},
         {"id": "theme", "from": "s04", "to": last_of(1), "volume": 0.16},
         {"id": "tension", "from": first_of(2), "to": last_of(3), "volume": 0.17},
         {"id": "march", "from": first_of(4), "to": last_of(5), "volume": 0.15},
         {"id": "tension", "from": first_of(6), "to": last_of(6), "volume": 0.16},
         {"id": "somber", "from": first_of(7), "to": ids[-1], "volume": 0.17}]
(HERE / "photo_pins.json").write_text(json.dumps(PINS, ensure_ascii=False, indent=1), encoding="utf-8")
board = {"title": "Battle of Chosin Reservoir (1950): The 17-Day March Out of Frozen Hell", "subtitle": "Nov 27 – Dec 13, 1950", "target_sec": 1230,
         "lang": "en", "voice": "pNInz6obpgDQGcFmaJgB", "tempo": 1.02, "tts_mode": "act", "midrolls": MID,
         "places": P, "views": V, "music": music, "ai_images": AI, "scenes": S}
(HERE / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
say = lambda l: l if isinstance(l, str) else l["say"]
acts = {}
for s in S:
    acts[s["act"]] = acts.get(s["act"], 0) + sum(len(say(l)) for l in s["lines"])
print("scenes", len(S), "chars", sum(acts.values()), "per act", acts, "mid", MID, "chap", [sid(i) for i in chap_i],
      "ai new", len(set(AI) - set(REUSE)), "reuse", len(REUSE), "pins", len(PINS))
