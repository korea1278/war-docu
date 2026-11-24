"""나레이션 템포 다듬기: 긴 무음 단축 + 배속(atempo), 글자 타임스탬프도 같이 보정.

python pipeline/tighten.py yongmunsan
입력 : public/ep/<ep>/tts/<id>.mp3 + .json (일레븐랩스 원본, 보존)
출력 : public/ep/<ep>/tts_fast/<id>.mp3 + .json  (timeline.py 가 우선 사용)
환경변수: NARRATION_TEMPO(기본 1.05), MAX_PAUSE(기본 0.42초, 배속 전 기준), PAUSE_MIN(기본 0.45초)
"""
import hashlib
import json
import subprocess
import sys

import numpy as np

from common import ep_dirs, env, read_json, write_json

SR = 44100


def decode(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def silent_runs(x, min_len, trail_tol=0):
    """10ms 창 RMS 기준 무음 구간 [(시작초, 끝초)].
    trail_tol(창 개수): 끝에서 이만큼 안쪽까지 이어진 무음도 '끝 무음'으로 본다 (2026-11-24 EP34 — 막 단위 TTS를 장면으로 자를 때
    잘린 끝에 다음 숨소리·mp3 잔향이 몇 ms 남으면 끝 무음이 '문장 사이 쉼'으로 잘못 잡혀 max_pause(0.65초)만큼 남았고,
    자막이 목소리보다 0.65초 늦게 끝나 싱크 검사(±0.5초)에 걸림)"""
    win = int(SR * 0.01)
    n = len(x) // win
    if n == 0:
        return []
    rms = np.sqrt((x[: n * win].reshape(n, win) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms)
    thr = max(-52.0, db.max() - 38.0)
    quiet = db < thr
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= min_len or i == 0 or j == n:
                runs.append((i * 0.01, j * 0.01, i == 0, j >= n - trail_tol))
            i = j
        else:
            i += 1
    return runs


def main(ep):
    from common import load_board
    tempo = float(load_board(ep).get("tempo") or env("NARRATION_TEMPO", "1.05"))
    print(f"배속: {tempo}")
    # 2026-11-24: 보드 "max_pause"(초). 레퍼런스('지도사')는 문장 사이 0.5~0.8초 숨을 그대로 두어 사람 말처럼 들림 —
    # 0.42초로 다 깎으면 쉼 없이 몰아치는 기계음처럼 들린다. 새 표준 0.65 · tempo 1.0 (보드에 없으면 예전 값)
    max_pause = float(load_board(ep).get("max_pause") or env("MAX_PAUSE", "0.42"))
    pause_min = float(env("PAUSE_MIN", "0.45"))
    # 새 표준(보드 max_pause가 있는 편)만: 끝 0.2초 안쪽까지 이어진 무음은 끝 무음으로 보고 그 뒤를 통째로 잘라냄 (예전 편은 결과 그대로)
    trail_tol = 20 if load_board(ep).get("max_pause") else 0
    _, out = ep_dirs(ep)
    src, dst = out / "tts", out / "tts_fast"
    dst.mkdir(exist_ok=True)
    for meta_p in sorted(src.glob("*.json")):
        meta = read_json(meta_p)
        sid = meta_p.stem
        sig = hashlib.sha1(f"{meta['sig']}|{tempo}|{max_pause}|{pause_min}|v2{'|t2' if trail_tol else ''}".encode()).hexdigest()[:12]
        old = read_json(dst / f"{sid}.json", {})
        if old.get("sig") == sig and (dst / f"{sid}.mp3").exists():
            continue
        x = decode(src / f"{sid}.mp3")
        total = len(x) / SR
        # 잘라낼 구간 목록 (원본 시간축)
        cuts = []
        for a, b, lead, trail in silent_runs(x, pause_min, trail_tol):
            if lead:
                keep = 0.04
                if b - a > keep:
                    cuts.append((a, b - keep))
            elif trail:
                keep = 0.08
                end = total if trail_tol else b
                if end - a > keep:
                    cuts.append((a + keep, end))
            elif b - a > max_pause:
                half = max_pause / 2
                cuts.append((a + half, b - half))
        # 오디오 재조립 (경계 5ms 크로스페이드)
        pieces, pos = [], 0.0
        for a, b in cuts:
            pieces.append(x[int(pos * SR):int(a * SR)])
            pos = b
        pieces.append(x[int(pos * SR):])
        fade = int(SR * 0.005)
        y = pieces[0]
        for p in pieces[1:]:
            if len(y) > fade and len(p) > fade:
                ramp = np.linspace(0, 1, fade, dtype=np.float32)
                mid = y[-fade:] * (1 - ramp) + p[:fade] * ramp
                y = np.concatenate([y[:-fade], mid, p[fade:]])
            else:
                y = np.concatenate([y, p])

        def remap(t):
            shift = 0.0
            for a, b in cuts:
                if t >= b:
                    shift += b - a
                elif t > a:
                    shift += t - a
            return (t - shift) / tempo

        # 배속 (피치 유지) → mp3
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", f"atempo={tempo}", "-c:a", "libmp3lame", "-b:a", "192k", str(dst / f"{sid}.mp3")],
                       input=y.astype(np.float32).tobytes(), check=True)
        write_json(dst / f"{sid}.json", {
            "sig": sig, "text": meta["text"], "chars": meta["chars"],
            "starts": [round(remap(t), 4) for t in meta["starts"]],
            "ends": [round(remap(t), 4) for t in meta["ends"]],
            "orig_dur": round(total, 3), "new_dur": round((len(y) / SR) / tempo, 3),
        })
        print(f"{sid}: {total:.2f}s → {len(y) / SR / tempo:.2f}s (무음 {len(cuts)}곳 단축)")
    print("템포 다듬기 완료")


if __name__ == "__main__":
    main(sys.argv[1])
