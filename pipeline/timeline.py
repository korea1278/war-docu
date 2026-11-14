"""스토리보드 + TTS 타임스탬프 + 자산 목록 → Remotion용 timeline.json.

python pipeline/timeline.py yongmunsan [--mock]
--mock : TTS 없이 글자 수로 길이를 추정 (레이아웃 미리보기용)
"""
import json
import math
import re
import subprocess
import sys

from common import ROOT, ep_dirs, line_say, line_text, load_board, log_error, read_json, write_json

FPS = 30
GAP = 0.42          # 장면 사이 간격 (앞 장면 꼬리 0.08초 + 이 값 ≈ 0.4초)
GAP_MIN, GAP_MAX = 0.35, 0.55   # 자동 맞춤 시 장면 간격 허용 범위
TARGET_SEC = 500    # 목표 러닝타임 8분 20초 (스토리보드 target_sec 로 변경 가능)
MAX_PRE = 0.15      # 장면 앞 무음 상한
MUSIC_GAIN = 1.33   # 배경음악 +2.5dB
MAX_SUB = 21        # 자막 한 줄 최대 글자 수 (64px 기준)
MOCK_CPS = 6.8      # 목업용 초당 글자 수


CREDIT_EN = [("출처: ", "Source: "), ("미 육군", "U.S. Army"), ("미 해병대", "U.S. Marine Corps"), ("미 공군", "U.S. Air Force"),
             ("미 해군", "U.S. Navy"), ("미 국립문서기록관리청", "U.S. National Archives"), ("대한민국 국방부", "ROK Ministry of National Defense")]


def credit_tr(c, lang):
    if not c or lang == "ko":
        return c
    for a, b in CREDIT_EN:
        c = c.replace(a, b)
    return c


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(scenes, path):
    """화면 자막과 같은 단위로 SRT 생성 (유튜브 자막 업로드용)."""
    cues = [(sc["start"] + c["start"], sc["start"] + c["end"] + 0.15, c["text"])
            for sc in scenes for l in sc["lines"] for c in l["chunks"]]
    rows = []
    for n, (a, b, txt) in enumerate(cues, 1):
        if n < len(cues):
            b = min(b, cues[n][0] - 0.02)  # 다음 자막과 겹치지 않게
        rows.append(f"{n}\n{srt_time(max(0, a))} --> {srt_time(max(a + 0.3, b))}\n{txt}\n")
    path.write_text("\n".join(rows), encoding="utf-8")


def mp3_dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def clean_sub(t):
    t = t.replace("...", " ").replace("…", " ")
    return re.sub(r"\s+", " ", t).strip()


def split_chunks(t):
    """긴 자막을 쉼표/띄어쓰기 기준으로 균등 분할. 반환: [(chunk, start_frac, end_frac)]."""
    n = len(t)
    if n <= MAX_SUB:
        return [(t, 0.0, 1.0)]
    k = math.ceil(n / MAX_SUB)
    cuts = [0]
    for j in range(1, k):
        target = n * j / k
        best, bs = None, 1e9
        for i, ch in enumerate(t):
            if ch != " " or i <= cuts[-1] + 4:
                continue
            score = abs(i - target) - (6 if t[i - 1] in ",." else 0)
            if score < bs:
                best, bs = i, score
        if best is None:
            break
        cuts.append(best)
    cuts.append(n)
    out = []
    for a, b in zip(cuts, cuts[1:]):
        c = t[a:b].strip()
        if c:
            out.append((c, a / n, b / n))
    return out



# ===================== style 2 (2026-11-12 사용자 지시 · 레퍼런스 영상 방식) =====================
# 보드에 "style": 2 를 켠 새 에피소드에만 적용 (기존 편은 그대로)
#  1) 뜻 단위 자막: 쉼표·문장 끝·이음말에서 우선 끊고, 이름·숫자+단위·조사 '의' 뒤는 끊지 않음 (최소 비용 분할)
#  2) 숫자로 바꿔 쓴 자막(t≠say)도 단어 대응으로 실제 발음 시각에 맞춤 (자막이 말보다 먼저 넘어가지 않게)
#  3) "on": "단어" — 콜아웃·말풍선·지도 아이템·효과음·visuals 어디든 그 단어를 말하는 순간에 맞춰 나타남
STYLE = 1
KO_CONN = ("는데", "지만", "면서", "니까", "어서", "아서", "해서", "다가", "려고", "도록", "으며", "고", "며", "면", "서", "데")
KO_AUX = ("있", "없", "않", "못", "싶", "버리", "버렸", "주", "줬", "보", "봤", "말", "놓", "두")
KO_PART = ("에서", "으로", "에게", "부터", "까지", "은", "는", "이", "가", "을", "를", "에", "로", "와", "과", "도", "만")
EN_CONJ = {"and", "but", "which", "who", "when", "while", "because", "so", "as", "after", "before", "until", "where", "then", "or", "yet", "though"}
EN_PREP = {"in", "on", "at", "of", "from", "with", "for", "by", "across", "over", "into", "toward", "towards", "through", "under", "against", "to", "that"}


def _brk_cost(w, nxt, lang):
    """단어 w 뒤(다음 단어 nxt 앞)에서 끊을 때의 비용 — 낮을수록 자연스러운 끊김."""
    core = w.rstrip("\"'”’)")
    if core and core[-1] in ",.?!…;:":
        return 0.0
    if any(ch.isdigit() for ch in w) and nxt and not any(ch.isdigit() for ch in nxt):
        return 8.0  # 숫자 + 단위/명사
    if lang == "ko":
        if nxt and nxt.startswith(KO_AUX) and core.endswith(("고", "어", "아", "지", "게", "해")):
            return 10.0  # 보조 용언 (~고 있다, ~지 않다, ~어 버리다)
        if core.endswith("의"):
            return 7.0
        if core.endswith(KO_CONN):
            return 1.5
        if core.endswith(KO_PART):
            return 3.0
        return 6.0
    a, b = core.strip("\"'“‘("), nxt.strip("\"'“‘(")
    if a[:1].isupper() and b[:1].isupper():
        return 20.0  # 사람·부대·지명 이름 안
    if b.lower() in EN_CONJ:
        return 1.5
    if b.lower() in EN_PREP:
        return 3.0
    if a.lower() in {"the", "a", "an", "of", "to", "in", "on", "at", "his", "her", "their", "its"}:
        return 12.0
    return 5.0


def split_phrase(t, lang):
    """뜻 단위 최소 비용 분할. 반환: [(chunk, start_frac, end_frac)] — split_chunks와 같은 형식."""
    n = len(t)
    if n <= MAX_SUB:
        return [(t, 0.0, 1.0)]
    words = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", t)]
    W = len(words)
    short = 6 if lang == "ko" else 12
    INF = 1e18
    best = [INF] * (W + 1)
    prev = [0] * (W + 1)
    best[0] = 0.0
    for j in range(1, W + 1):
        for i in range(j - 1, -1, -1):
            ln = words[j - 1][2] - words[i][1]
            if ln > MAX_SUB + 3 and j - i > 1:
                break
            c = best[i] + 2.0 + max(0, ln - MAX_SUB) * 3.0 + ((ln - 0.62 * MAX_SUB) / MAX_SUB) ** 2 * 3.0
            if j < W:
                c += _brk_cost(words[j - 1][0], words[j][0], lang)
            if ln < short and W > 1:
                c += 4.0
            if c < best[j]:
                best[j], prev[j] = c, i
    cuts, j = [], W
    while j > 0:
        cuts.append((prev[j], j))
        j = prev[j]
    out = []
    for i, j in reversed(cuts):
        a, b = words[i][1], words[j - 1][2]
        out.append((t[a:b], a / n, b / n))
    return out


def _norm(w):
    return re.sub(r"[^\w]", "", w.lower())


def disp2say(disp, say, pos):
    """자막 글자 위치 pos → 낭독 문장(say)의 글자 위치 (단어 대응, 숫자 표기가 달라도)."""
    import difflib
    dw = [(m.start(), m.end(), _norm(m.group())) for m in re.finditer(r"\S+", disp)]
    sw = [(m.start(), m.end(), _norm(m.group())) for m in re.finditer(r"\S+", say)]
    if not dw or not sw:
        return round(pos / max(1, len(disp)) * len(say))
    k = next((i for i, (a, b, _) in enumerate(dw) if b > pos), len(dw))
    if k >= len(dw):
        return len(say)
    sm = difflib.SequenceMatcher(a=[x[2] for x in dw], b=[x[2] for x in sw], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if i1 <= k < i2:
            if tag == "equal":
                return sw[j1 + (k - i1)][0]
            if j2 > j1:
                jj = j1 + int((k - i1) / max(1, i2 - i1) * (j2 - j1))
                return sw[min(jj, j2 - 1)][0]
            return sw[min(j1, len(sw) - 1)][0]
    return len(say)

def line_spans(text, says):
    """tts 전체 텍스트에서 각 줄의 [시작, 끝) 글자 위치."""
    spans, pos = [], 0
    for s in says:
        s = s.strip()
        i = text.find(s, pos)
        if i < 0:
            spans = None
            break
        spans.append((i, i + len(s)))
        pos = i + len(s)
    if spans:
        return spans
    # 사용자 지정 tts 문장: 길이 비율로 배분
    total = sum(len(s) for s in says)
    spans, acc = [], 0
    for s in says:
        a = round(acc / total * len(text))
        acc += len(s)
        spans.append((a, round(acc / total * len(text))))
    return spans


def time_at(meta, idx, end=False):
    arr = meta["ends"] if end else meta["starts"]
    idx = max(0, min(idx, len(arr) - 1))
    return arr[idx]


def build(ep, mock=False, gap=None):
    GAP_ = GAP if gap is None else gap
    board = load_board(ep)
    _, out = ep_dirs(ep)
    lang = board.get("lang", "ko")
    aep = board.get("assets_ep") or ep          # 사진·그림·음악 출처 에피소드
    aout = ROOT / "public" / "ep" / aep
    photos = read_json(aout / "photos.json", {})
    ai = read_json(aout / "ai.json", {})
    global MAX_SUB
    # 2026-11-13 롱폼 표준(LONGFORM_STANDARD 3): 한 줄 25~35자 — 스토리보드 "sub_max"로 지정 (EP27부터 28, 없으면 예전 21)
    MAX_SUB = 44 if lang != "ko" else int(board.get("sub_max", 21))
    global STYLE
    STYLE = int(board.get("style", 1))
    rasters = read_json(ROOT / "public" / "geo" / "rasters.json", [])
    scenes_out = []
    t = 0.0
    for sc in board["scenes"]:
        says = [line_say(l) for l in sc["lines"]]
        texts = [line_text(l) for l in sc["lines"]]
        tts_text = sc.get("tts") or " ".join(s.strip() for s in says)
        tdir = "tts_fast" if (out / "tts_fast" / f"{sc['id']}.json").exists() else "tts"
        meta = None if mock else read_json(out / tdir / f"{sc['id']}.json")
        if not sc["lines"]:
            audio, adur, spans = None, 0.0, []
        elif meta:
            audio = f"ep/{ep}/{tdir}/{sc['id']}.mp3"
            adur = mp3_dur(out / tdir / f"{sc['id']}.mp3")
            spans = line_spans(meta["text"], says)
        else:
            audio = None
            adur = len(tts_text) / MOCK_CPS + 0.3 * tts_text.count(",") + 0.5 * tts_text.count("...")
            spans = line_spans(tts_text, says)
            L = len(tts_text)
            meta = {"starts": [i / L * adur for i in range(L)], "ends": [(i + 1) / L * adur for i in range(L)]}
        pre = min(sc.get("pauseBefore", 0.0), MAX_PRE)
        lines = []
        for li, ((a, b), disp, say) in enumerate(zip(spans, texts, says)):
            ls, le = time_at(meta, a), time_at(meta, b - 1, end=True)
            sub = clean_sub(disp)
            chunks = []
            exact = disp.strip() == say.strip() and not sc.get("tts")
            if STYLE >= 2:
                parts = split_phrase(sub, lang)
                starts_s = [disp2say(sub, say, round(fa * len(sub))) for _, fa, _ in parts]
                for ci, (c, fa, fb) in enumerate(parts):
                    sa = a + min(starts_s[ci], b - a - 1)
                    sb = (a + starts_s[ci + 1] - 1) if ci + 1 < len(parts) else b - 1
                    cs = time_at(meta, sa)
                    ce = time_at(meta, max(sa, sb), end=True)
                    chunks.append({"text": c, "start": round(pre + cs, 3), "end": round(pre + ce, 3)})
            for c, fa, fb in ([] if STYLE >= 2 else split_chunks(sub)):
                if exact and len(sub) == len(disp.strip()):
                    cs = time_at(meta, a + int(fa * (b - a)))
                    ce = time_at(meta, a + max(int(fb * (b - a)) - 1, 0), end=True)
                else:
                    cs, ce = ls + fa * (le - ls), ls + fb * (le - ls)
                chunks.append({"text": c, "start": round(pre + cs, 3), "end": round(pre + ce, 3)})
            lines.append({"text": sub, "start": round(pre + ls, 3), "end": round(pre + le, 3), "chunks": chunks})
        dur = sc["dur"] if not sc["lines"] else pre + adur + GAP_ + sc.get("tail", 0)
        def resolve(vis):
            vis = dict(vis)
            if vis.get("q"):
                pk = f"{vis['q']}#{vis.get('alt', 0)}"
                ph = photos.get(pk) or {}
                vis["src"] = f"ep/{aep}/{ph['file']}" if ph.get("file") else None
                vis["credit"] = credit_tr(ph.get("credit"), lang)
            if vis["type"] == "ai":
                vis["src"] = f"ep/{aep}/ai/{vis['img']}.jpg" if vis["img"] in ai else None
                vis["credit"] = None
            return vis

        # "on": "단어" → 그 단어를 말하는 시각을 atSec 형식(줄 번호 + 줄 안 비율)의 at 값으로 바꿈
        say_full = (meta.get("text") if isinstance(meta, dict) and meta.get("text") else tts_text) or ""

        def word_time(w):
            wl = w.lower()
            for li2, ((a2, b2), disp2, say2) in enumerate(zip(spans, texts, says)):
                j = say2.lower().find(wl)
                if j < 0:
                    jd = disp2.lower().find(wl)
                    if jd < 0:
                        continue
                    j = disp2say(disp2, say2, jd)
                return pre + time_at(meta, min(a2 + j, max(a2, b2 - 1)))
            j = say_full.lower().find(wl)
            if j >= 0:
                return pre + time_at(meta, j)
            log_error(f"{ep} {sc['id']}: on 단어를 대사에서 못 찾음 — '{w}'")
            return None

        def sec2at(s):
            if not lines:
                return 0
            for li2 in range(len(lines) - 1, -1, -1):
                l = lines[li2]
                if s >= l["start"] - 1e-6 or li2 == 0:
                    span = max(0.6, l["end"] - l["start"])
                    return round(li2 + min(0.999, max(0.0, (s - l["start"]) / span)), 4)
            return 0

        def apply_on(o):
            if isinstance(o, list):
                return [apply_on(x) for x in o]
            if not isinstance(o, dict):
                return o
            o = {k: apply_on(v) for k, v in o.items()}
            for key, tgt in (("on", "at"), ("untilOn", "until"), ("takenOn", "takenAt"), ("checkOn", "checkAt"), ("xOn", "xAt")):
                if isinstance(o.get(key), str):
                    s = word_time(o[key])
                    if s is not None:
                        o[tgt] = sec2at(s)
                        if key == "on":
                            o["_onSec"] = round(s, 3)
                    del o[key]
            return o

        if STYLE >= 2 or '"on":' in json.dumps(sc, ensure_ascii=False):
            sc = apply_on(sc)

        extra = []
        for v2 in sc.get("visuals", []):
            r = resolve(v2)
            fi = v2.get("atLine", 0)
            r["start"] = round(lines[fi]["start"] - 0.05, 3) if fi < len(lines) else 0
            if v2.get("_onSec") is not None:
                r["start"] = round(v2["_onSec"] - 0.05, 3)
            extra.append(r)
        vis = dict(sc["visual"])
        if vis.get("q"):
            pk = f"{vis['q']}#{vis.get('alt', 0)}"
            ph = photos.get(pk) or {}
            vis["src"] = f"ep/{aep}/{ph['file']}" if ph.get("file") else None
            vis["credit"] = credit_tr(ph.get("credit"), lang)
        if vis["type"] == "teaser":
            vis["items"] = [dict(it, src=f"ep/{aep}/ai/{it['img']}.jpg" if it["img"] in ai else None) for it in vis["items"]]
        if vis["type"] == "ai":
            vis["src"] = f"ep/{aep}/ai/{vis['img']}.jpg" if vis["img"] in ai else None
            vis["credit"] = None
        scenes_out.append({
            "id": sc["id"], "start": round(t, 3), "dur": round(dur, 3), "audio": audio, "audioAt": pre, "tempo": 1,
            "lines": lines, "visual": vis, "label": sc.get("label"), "callouts": sc.get("callouts", []),
            "sfx": sc.get("sfx", []), "chapter": sc.get("chapter"), "flash": sc.get("flash", False), "hudCta": sc.get("hudCta"),
            "visuals": extra,
        })
        t += dur
    idx = {s["id"]: s for s in scenes_out}
    # 롱폼 표준 (docs/LONGFORM_STANDARD.md, 2026-11-13): bgm_rel_db = 나레이션 대비 BGM 음량(dB, 예 -24)
    rel = board.get("bgm_rel_db")
    policy = board.get("sfx_policy")
    narr = loud = None
    if rel is not None or policy == "doc":
        narr = narration_lufs([ROOT / "public" / s["audio"] for s in scenes_out if s.get("audio")])
    if rel is not None:
        loud = read_json(ROOT / "public" / "bgm" / "loudness.json", {})
        print(f"BGM: 나레이션 {narr:.1f} LUFS 기준 {rel} dB")
    if policy == "doc":
        doc_sfx(scenes_out, narr)
    music = []
    for cue in board.get("music", []):
        a, b = idx[cue["from"]], idx[cue["to"]]
        start, end = a["start"], b["start"] + b["dur"]
        f = aout / "music" / f"{cue['id']}.mp3"
        src = f"ep/{aep}/music/{cue['id']}.mp3"
        if not f.exists():  # 공용 BGM 라이브러리 (public/bgm)
            f = ROOT / "public" / "bgm" / f"{cue['id']}.mp3"
            src = f"bgm/{cue['id']}.mp3"
        vol = cue["volume"] * MUSIC_GAIN
        if rel is not None and cue["id"] in loud:
            vol = min(1.0, 10 ** ((narr + rel - loud[cue["id"]]) / 20))
        music.append({"id": cue["id"], "start": round(start, 3), "dur": round(end - start, 3),
                      "volume": round(vol, 4), "src": src if f.exists() else None,
                      "fileDur": mp3_dur(f) if f.exists() else None})
    sfx_avail = sorted(p.stem for p in (ROOT / "public" / "sfx").glob("*.mp3"))
    if board.get("sfx") is False:  # 효과음 전부 끔 (장면 sfx·자동 pop/whoosh 모두 — Video.tsx가 목록에 있는 것만 재생)
        sfx_avail = []
    tl = {"lang": lang, "fps": FPS, "duration": round(t, 3), "title": board["title"], "places": board["places"],
          "views": board["views"], "scenes": scenes_out, "music": music, "rasters": rasters, "sfx": sfx_avail,
          "sfxPolicy": policy,
          "hasWater": (ROOT / "public" / "geo" / "water.json").exists(),
          # 화면 업그레이드 2단계: 캐릭터 라이브러리에 있는 그림 목록 (없으면 stage 화면이 SVG 볼 캐릭터로 대체)
          "chars": sorted(p.stem for p in (ROOT / "public" / "chars").glob("*.png"))}
    write_json(out / "timeline.json", tl)
    write_srt(scenes_out, out / f"{ep}.srt")
    print(f"timeline: {len(scenes_out)}장면, {int(t // 60)}분 {t % 60:.1f}초 (장면 간격 {GAP_:.3f}초)")
    return t, sum(1 for x in scenes_out if x["lines"]), board.get("target_sec", TARGET_SEC)


# ===== 절제된 다큐멘터리 SFX 기준 (docs/LONGFORM_STANDARD.md 2번, 2026-11-13 사용자 수정 지시) =====
SFX_BAN = {"boom", "hit", "artillery", "mg", "drum", "pop"}   # '꽝' 타격·근거리 폭발·UI pop 금지
SFX_KIND_DB = {"whoosh": -26, "ping": -26, "artillery_far": -30, "wind": -30, "tank": -30, "water": -32, "birds": -32}
SFX_COOLDOWN = 15.0  # 같은 효과음 최소 간격(초)


def _at_sec(sc, at):
    ls = sc["lines"]
    if at is None:
        return 0.0
    if not ls:
        return float(at)
    i = int(math.floor(at))
    if i >= len(ls):
        return ls[-1]["end"]
    l = ls[max(0, i)]
    return l["start"] + (at - i) * max(0.6, l["end"] - l["start"])


def doc_sfx(scenes, narr):
    """장면 sfx를 다큐 기준으로 정리: 금지 효과음 삭제, 막 전환(chapter)마다 저음 스윕 whoosh 1회 자동,
    같은 효과음 15초 쿨다운, 볼륨은 나레이션 대비 -24~-32dB (효과음별 LUFS: public/sfx/loudness.json).
    결과는 장면 기준 절대 초(sec)로 기록 — Video.tsx는 sfxPolicy doc이면 자동 pop/whoosh를 더하지 않는다."""
    loud = read_json(ROOT / "public" / "sfx" / "loudness.json", {})
    last, kept, dropped = {}, 0, 0
    for sc in scenes:
        evs = []
        if sc.get("chapter"):
            evs.append({"id": "whoosh", "at": -1})
        evs += [e for e in sc.get("sfx", [])]
        out = []
        for e in evs:
            sid = e["id"]
            if sid in SFX_BAN or sid not in loud:
                dropped += 1
                continue
            rel_s = 0.0 if (e.get("at") is not None and e["at"] < 0) else _at_sec(sc, e.get("at"))
            abs_t = sc["start"] + sc.get("audioAt", 0) + rel_s
            if abs_t - last.get(sid, -1e9) < SFX_COOLDOWN:
                dropped += 1
                continue
            last[sid] = abs_t
            db = max(-32, min(-24, e.get("db", SFX_KIND_DB.get(sid, -28))))
            vol = min(1.0, 10 ** ((narr + db - loud[sid]) / 20))
            out.append({"id": sid, "sec": round(rel_s, 3), "volume": round(vol, 4)})
            kept += 1
        sc["sfx"] = out
    print(f"효과음(다큐 기준): {kept}개 사용 · {dropped}개 제외(금지·쿨다운)")


def narration_lufs(files):
    """나레이션 통합 음량(LUFS) — 파일 최대 24개를 이어 붙여 ffmpeg ebur128로 측정. 실패하면 -18."""
    files = [f for f in files if f.exists()]
    if not files:
        return -18.0
    pick = files[:: max(1, len(files) // 24)][:24]
    lst = ROOT / "logs" / "_lufs_list.txt"
    lst.write_text("".join(f"file '{f}'\n" for f in pick), encoding="utf-8")
    try:
        r = subprocess.run(["ffmpeg", "-nostats", "-f", "concat", "-safe", "0", "-i", str(lst), "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True, timeout=300)
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
        return float(m[-1]) if m else -18.0
    except Exception:  # noqa: BLE001
        return -18.0
    finally:
        lst.unlink(missing_ok=True)


def fit(ep, mock=False):
    """러닝타임을 목표(기본 8분 20초)에 가깝게: 장면 간격을 0.35~0.55초 안에서 자동 조정."""
    t, n, target = build(ep, mock)
    if mock or not n:
        return
    gap = min(GAP_MAX, max(GAP_MIN, GAP + (target - t) / n))
    if abs(gap - GAP) > 0.001:
        t, _, _ = build(ep, mock, gap)
    if abs(t - target) > 10:
        msg = f"{ep}: 러닝타임 {int(t // 60)}분 {t % 60:.0f}초 — 목표 {int(target // 60)}분 {target % 60:.0f}초와 10초 이상 차이 (대본 분량 조정 필요)"
        print("  ! " + msg)
        from common import log_error
        log_error(msg)


if __name__ == "__main__":
    fit(sys.argv[1], mock="--mock" in sys.argv)
