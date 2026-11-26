"""목소리 ↔ 대본 대조 (2026-11-26 '다큐 설명 영상 스킬' 튜토리얼 분석에서 가져옴 · war-docu·map-of-war 공통)

일레븐랩스(특히 eleven_v3)는 가끔 단어를 빼먹거나, 같은 말을 되풀이하거나, 숫자를 엉뚱하게 읽는다.
글자 타임스탬프는 '입력한 글자'를 기준으로 돌려주기 때문에 이런 실수는 자막 싱크 검사로는 잡히지 않는다.
→ 막(act) 통 MP3를 무료 받아쓰기(Whisper large-v3-turbo · sherpa-onnx · MIT/Apache-2.0)로 다시 듣고
  대본(자막 표기 t — 숫자가 아라비아 숫자라 받아쓰기 결과와 맞음)과 글자 단위로 비교해 다른 곳을 목록으로 남긴다.

- 렌더를 멈추지 않는다 (경고만). 결과: logs/asr_check_<ep>.txt (+ 큰 차이는 logs/errors.txt)
- 받아쓰기 자체의 오인식(진동리→진동의 같은 한 글자 차이)은 걸러내고, 3글자 이상 빠짐·덧붙음(되풀이)·바뀜만 '확인 필요'로 표시
- 모델(약 1GB)은 GitHub 릴리스(k2-fsa/sherpa-onnx)에서 받아 .cache/models/whisper-turbo 에 둔다 (Actions 캐시로 재사용)
- 20분 편 기준 4코어 러너 약 3~5분

사용: python3 asr_check.py <ep> [act번호 ...]
"""
import difflib
import json
import re
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

from common import ROOT, ep_dirs, line_text, load_board, log_error, read_json

MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-turbo.tar.bz2"
MODEL_DIR = ROOT / ".cache" / "models" / "whisper-turbo"
CHUNK = 27.0  # Whisper 한 창 30초 — 장면 경계에서 27초 이하로 묶는다
MIN_FLAG = 3  # 이보다 짧은 차이는 받아쓰기 오인식으로 보고 무시


def ensure_model() -> Path:
    enc = MODEL_DIR / "turbo-encoder.int8.onnx"
    if enc.exists():
        return MODEL_DIR
    MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
    tmp = MODEL_DIR.parent / "whisper-turbo.tar.bz2"
    print(f"[asr] 모델 받는 중 {MODEL_URL}")
    urllib.request.urlretrieve(MODEL_URL, tmp)
    with tarfile.open(tmp, "r:bz2") as tf:
        for m in tf.getmembers():
            name = Path(m.name).name
            if m.isfile() and name.startswith("turbo-") and (name.endswith(".int8.onnx") or name.endswith("tokens.txt")):
                m.name = name
                tf.extract(m, MODEL_DIR)
    tmp.unlink()
    return MODEL_DIR


def norm(s: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", s)


def load_pcm(mp3: Path):
    import numpy as np

    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.int16).astype("float32") / 32768


def scene_display(sc) -> str:
    return " ".join(line_text(l).strip() for l in sc.get("lines", []))


def scene_say(sc) -> str:
    from common import line_say

    if sc.get("tts"):
        return sc["tts"]
    return " ".join(line_say(l).strip() for l in sc["lines"])


def chunks_for_act(group, meta):
    """장면 경계(글자 타임스탬프)에서 27초 이하 묶음으로 나눈다 → [(시작초, 끝초, [장면…])]"""
    chars, st, en = meta["chars"], meta["starts"], meta["ends"]
    joined = "".join(chars)
    spans, pos = [], 0
    for sc in group:
        t = scene_say(sc)
        j = joined.find(t, pos)
        if j < 0:
            j = pos
        spans.append((j, min(len(st), j + len(t))))
        pos = j + len(t)
    times = []
    for a0, a1 in spans:
        if a1 <= a0 or a0 >= len(st):
            times.append(None)
            continue
        times.append((st[a0], max(en[a0:a1])))
    out, cur, c0, prev_end = [], [], None, 0.0
    for sc, tm in zip(group, times):
        if tm is None:
            continue
        if cur and tm[1] - c0 > CHUNK:
            out.append((c0, prev_end, cur))
            cur, c0 = [], None
        if c0 is None:
            c0 = tm[0]
        cur.append(sc)
        prev_end = tm[1]
    if cur:
        out.append((c0, prev_end, cur))
    return out


def fmt_t(s: float) -> str:
    return f"{int(s // 60)}:{s % 60:04.1f}"


def main(ep, only=None):
    t_all = time.time()
    board = load_board(ep)
    _, out = ep_dirs(ep)
    adir = out / "tts" / "acts"
    acts = {}
    for sc in board["scenes"]:
        if sc.get("lines") and sc.get("act") is not None:
            acts.setdefault(sc["act"], []).append(sc)
    if not acts or not adir.exists():
        print("[asr] 막 단위 TTS(tts/acts)가 없어 건너뜀")
        return
    import sherpa_onnx as so

    d = ensure_model()
    rec = so.OfflineRecognizer.from_whisper(
        encoder=str(d / "turbo-encoder.int8.onnx"), decoder=str(d / "turbo-decoder.int8.onnx"), tokens=str(d / "turbo-tokens.txt"),
        language=board.get("lang", "ko") if board.get("lang", "ko") in ("ko", "en") else "ko", task="transcribe", num_threads=4,
    )
    report, flags, tot_ref, tot_ok = [], [], 0, 0
    for n in sorted(acts):
        if only and str(n) not in only:
            continue
        mp3, meta = adir / f"act{n}.mp3", read_json(adir / f"act{n}.json", {})
        if not mp3.exists() or not meta.get("chars"):
            continue
        pcm = load_pcm(mp3)
        report.append(f"\n## act{n} ({meta.get('model', '?')})")
        for a, b, scs in chunks_for_act(acts[n], meta):
            s = rec.create_stream()
            s.accept_waveform(16000, pcm[int(max(0, a - 0.15) * 16000): int((b + 0.25) * 16000)])
            rec.decode_stream(s)
            heard = s.result.text.strip()
            ref = " ".join(scene_display(sc) for sc in scs)
            r, h = norm(ref), norm(heard)
            sm = difflib.SequenceMatcher(None, r, h, autojunk=False)
            tot_ref += len(r)
            tot_ok += sum(blk.size for blk in sm.get_matching_blocks())
            # 자막 표기(t: 숫자·km)와 읽는 말(say: 넉 달·킬로미터)이 다른 곳은 받아쓰기가 어느 쪽으로든 적을 수 있다
            # → 두 대본 모두와 다른 곳만 남긴다 (들린 말 위치가 겹치는지로 판단)
            rs = norm(" ".join(scene_say(sc) for sc in scs))
            say_bad = [(j1 - 2, j2 + 2) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, rs, h, autojunk=False).get_opcodes() if op != "equal" and max(i2 - i1, j2 - j1) >= MIN_FLAG]
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == "equal" or max(i2 - i1, j2 - j1) < MIN_FLAG:
                    continue
                if not any(x0 <= j2 and j1 <= x1 for x0, x1 in say_bad):
                    continue
                # 어느 장면인지: 대본 글자 위치로 찾기
                acc, sid = 0, scs[0]["id"]
                for sc in scs:
                    acc += len(norm(scene_display(sc)))
                    if i1 < acc:
                        sid = sc["id"]
                        break
                kind = {"delete": "빠짐", "insert": "덧붙음(되풀이?)", "replace": "바뀜"}[op]
                ctx_r = r[max(0, i1 - 6): i2 + 6]
                ctx_h = h[max(0, j1 - 6): j2 + 6]
                line = f"- [{kind}] {sid} (act{n} {fmt_t(a)}~) 대본 「{r[i1:i2] or '∅'}」 ↔ 들린 말 「{h[j1:j2] or '∅'}」   …{ctx_r}… / …{ctx_h}…"
                flags.append(line)
                report.append(line)
    acc = tot_ok / max(1, tot_ref)
    head = [
        f"# 목소리 ↔ 대본 대조 — {ep} ({time.strftime('%Y-%m-%d %H:%M')})",
        f"글자 일치율 {acc:.1%} · 확인 필요 {len(flags)}곳 (3글자 이상 차이만 · 한두 글자 차이는 받아쓰기 오인식으로 보고 생략)",
        "※ 받아쓰기도 틀릴 수 있다 — 목록의 시각으로 가서 귀로 확인하고, 정말 틀렸으면 그 막만 다시 생성(대본 문장 수정 또는 redo)",
    ]
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    (logs / f"asr_check_{ep}.txt").write_text("\n".join(head + report) + "\n", encoding="utf-8")
    print("\n".join(head))
    for f in flags[:40]:
        print(f)
    big = [f for f in flags if "빠짐" in f or "덧붙음" in f]
    if big:
        log_error(f"{ep}: 목소리↔대본 대조 — 빠짐·덧붙음 {len(big)}곳 (logs/asr_check_{ep}.txt 확인)")
    print(f"[asr] {time.time() - t_all:.0f}초")


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2:] or None)
    except Exception as e:  # 검사 실패로 렌더를 멈추지 않는다
        print(f"[asr] 건너뜀: {e}")
        log_error(f"{sys.argv[1]}: 목소리↔대본 대조 실패 — {e}")
