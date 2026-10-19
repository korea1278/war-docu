"""스토리보드 + TTS 타임스탬프 + 자산 목록 → Remotion용 timeline.json.

python pipeline/timeline.py yongmunsan [--mock]
--mock : TTS 없이 글자 수로 길이를 추정 (레이아웃 미리보기용)
"""
import math
import re
import subprocess
import sys

from common import ROOT, ep_dirs, line_say, line_text, load_board, read_json, write_json

FPS = 30
GAP = 0.42          # 장면 사이 간격 (앞 장면 꼬리 0.08초 + 이 값 ≈ 0.4초)
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


def build(ep, mock=False):
    board = load_board(ep)
    _, out = ep_dirs(ep)
    lang = board.get("lang", "ko")
    aep = board.get("assets_ep") or ep          # 사진·그림·음악 출처 에피소드
    aout = ROOT / "public" / "ep" / aep
    photos = read_json(aout / "photos.json", {})
    ai = read_json(aout / "ai.json", {})
    global MAX_SUB
    MAX_SUB = 44 if lang != "ko" else 21
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
            for c, fa, fb in split_chunks(sub):
                if exact and len(sub) == len(disp.strip()):
                    cs = time_at(meta, a + int(fa * (b - a)))
                    ce = time_at(meta, a + max(int(fb * (b - a)) - 1, 0), end=True)
                else:
                    cs, ce = ls + fa * (le - ls), ls + fb * (le - ls)
                chunks.append({"text": c, "start": round(pre + cs, 3), "end": round(pre + ce, 3)})
            lines.append({"text": sub, "start": round(pre + ls, 3), "end": round(pre + le, 3), "chunks": chunks})
        dur = sc["dur"] if not sc["lines"] else pre + adur + GAP + sc.get("tail", 0)
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

        extra = []
        for v2 in sc.get("visuals", []):
            r = resolve(v2)
            fi = v2["atLine"]
            r["start"] = round(lines[fi]["start"] - 0.05, 3) if fi < len(lines) else 0
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
            "sfx": sc.get("sfx", []), "chapter": sc.get("chapter"), "flash": sc.get("flash", False),
            "visuals": extra,
        })
        t += dur
    idx = {s["id"]: s for s in scenes_out}
    music = []
    for cue in board.get("music", []):
        a, b = idx[cue["from"]], idx[cue["to"]]
        start, end = a["start"], b["start"] + b["dur"]
        f = aout / "music" / f"{cue['id']}.mp3"
        music.append({"id": cue["id"], "start": round(start, 3), "dur": round(end - start, 3),
                      "volume": round(cue["volume"] * MUSIC_GAIN, 3), "src": f"ep/{aep}/music/{cue['id']}.mp3" if f.exists() else None,
                      "fileDur": mp3_dur(f) if f.exists() else None})
    sfx_avail = sorted(p.stem for p in (ROOT / "public" / "sfx").glob("*.mp3"))
    tl = {"lang": lang, "fps": FPS, "duration": round(t, 3), "title": board["title"], "places": board["places"],
          "views": board["views"], "scenes": scenes_out, "music": music, "rasters": rasters, "sfx": sfx_avail,
          "hasWater": (ROOT / "public" / "geo" / "water.json").exists()}
    write_json(out / "timeline.json", tl)
    write_srt(scenes_out, out / f"{ep}.srt")
    print(f"timeline: {len(scenes_out)}장면, {t / 60:.1f}분")


if __name__ == "__main__":
    build(sys.argv[1], mock="--mock" in sys.argv)
